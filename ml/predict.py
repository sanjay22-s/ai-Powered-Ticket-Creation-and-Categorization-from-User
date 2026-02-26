"""
Prediction pipeline for ticket classification.

Function:
    predict_ticket(text: str) -> dict

Loads:
- models/tfidf_vectorizer.pkl
- models/category_model.pkl
- models/priority_model.pkl

Returns structured ticket JSON with entities and confidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any

import joblib
import numpy as np
import spacy

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"

_VEC_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
_CAT_MODEL_PATH = MODELS_DIR / "category_model.pkl"
_PRI_MODEL_PATH = MODELS_DIR / "priority_model.pkl"


@dataclass
class _ModelBundle:
    vectorizer: Any
    category_model: Any
    priority_model: Any
    nlp: "spacy.language.Language"


_BUNDLE: _ModelBundle | None = None


def _load_nlp() -> "spacy.language.Language":
    try:
        return spacy.load("en_core_web_sm")
    except OSError as exc:
        raise RuntimeError(
            "spaCy model 'en_core_web_sm' is not installed. "
            "Install it with: python -m spacy download en_core_web_sm"
        ) from exc


def _load_models() -> _ModelBundle:
    global _BUNDLE
    if _BUNDLE is not None:
        return _BUNDLE

    if not (_VEC_PATH.exists() and _CAT_MODEL_PATH.exists() and _PRI_MODEL_PATH.exists()):
        raise FileNotFoundError(
            f"Model files not found in {MODELS_DIR}. "
            "Run ml/train.py to train and save models."
        )

    print(f"Loading models from {MODELS_DIR}")
    vectorizer = joblib.load(_VEC_PATH)
    category_model = joblib.load(_CAT_MODEL_PATH)
    priority_model = joblib.load(_PRI_MODEL_PATH)
    nlp = _load_nlp()

    _BUNDLE = _ModelBundle(
        vectorizer=vectorizer,
        category_model=category_model,
        priority_model=priority_model,
        nlp=nlp,
    )
    return _BUNDLE


def _short_title(text: str, max_words: int = 8) -> str:
    words = text.strip().split()
    return " ".join(words[:max_words]) if words else "Ticket from user input"


def _preprocess_single(text: str, nlp: "spacy.language.Language") -> str:
    """Mirror training-time preprocessing for a single document."""
    doc = nlp(text)
    tokens = [
        tok.lemma_.lower()
        for tok in doc
        if not tok.is_stop and not tok.is_punct and tok.lemma_.strip()
    ]
    return " ".join(tokens)


def _extract_entities(text: str, nlp: "spacy.language.Language") -> Dict[str, List[str]]:
    """
    Extract simple entities using spaCy + regex/rules:
    - error_codes: things like ORA-1234, 0x80070005, HTTP 500, ERR1234
    - ip_addresses: IPv4 addresses
    - usernames: words after 'user', 'username', or patterns like jdoe, a.smith
    - systems: ORG/PRODUCT entities and simple keyword-based system names
    """
    entities: Dict[str, List[str]] = {
        "error_codes": [],
        "ip_addresses": [],
        "usernames": [],
        "systems": [],
    }

    # Regex-based
    error_patterns = [
        r"\b(?:ORA|ERR|SQL|E)-?\d{3,6}\b",
        r"\b0x[0-9a-fA-F]+\b",
        r"\bHTTP\s+(?:4|5)\d{2}\b",
    ]
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    username_pattern = r"\b[a-zA-Z][a-zA-Z0-9._-]{2,15}\b"

    for pat in error_patterns:
        entities["error_codes"].extend(re.findall(pat, text))
    entities["ip_addresses"].extend(re.findall(ip_pattern, text))

    # spaCy NER for ORG/PRODUCT/SYSTEM-like entities
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in {"ORG", "PRODUCT", "GPE"}:
            entities["systems"].append(ent.text)

    # Simple system keyword extraction
    system_keywords = [
        "SAP",
        "Salesforce",
        "Jira",
        "Confluence",
        "VPN",
        "Oracle",
        "CRM",
        "ERP",
        "Outlook",
        "Windows",
        "Linux",
    ]
    upper_text = text.upper()
    for kw in system_keywords:
        if kw.upper() in upper_text:
            entities["systems"].append(kw)

    # Username detection around 'user'/'username'
    lowered = text.lower()
    for match in re.finditer(r"(user|username)\s*[:=]?\s*(" + username_pattern + ")", text, flags=re.IGNORECASE):
        entities["usernames"].append(match.group(2))

    # Generic username-like tokens
    for candidate in re.findall(username_pattern, text):
        if any(ch.isdigit() for ch in candidate) or "." in candidate or "_" in candidate:
            entities["usernames"].append(candidate)

    # Deduplicate
    entities = {k: sorted(set(v)) for k, v in entities.items()}
    return entities


def _predict_with_confidence(model: Any, X_vec: Any) -> (str, float):
    """Return predicted label and confidence score (probability if available)."""
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_vec)[0]
        idx = int(np.argmax(proba))
        label = model.classes_[idx]
        confidence = float(proba[idx])
        return label, confidence
    # Fallback: use decision_function if available
    y_pred = model.predict(X_vec)[0]
    if hasattr(model, "decision_function"):
        scores = model.decision_function(X_vec)[0]
        if isinstance(scores, np.ndarray):
            # scale to 0-1 range
            scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)
            confidence = float(scores.max())
        else:
            confidence = float(1 / (1 + np.exp(-scores)))
    else:
        confidence = 1.0
    return y_pred, confidence


def predict_ticket(text: str) -> Dict[str, Any]:
    """
    Run full prediction pipeline on a free-form ticket text.

    Returns:
        {
          "title": "...",
          "description": "...",
          "category": "...",
          "priority": "...",
          "entities": {...},
          "confidence_score": float
        }
    """
    bundle = _load_models()
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Input text is empty.")

    preprocessed = _preprocess_single(clean_text, bundle.nlp)
    X_vec = bundle.vectorizer.transform([preprocessed])

    cat_label, cat_conf = _predict_with_confidence(bundle.category_model, X_vec)
    pri_label, pri_conf = _predict_with_confidence(bundle.priority_model, X_vec)

    entities = _extract_entities(text, bundle.nlp)

    # Combine confidences conservatively
    confidence_score = float(min(cat_conf, pri_conf))

    return {
        "title": _short_title(text),
        "description": text,
        "category": cat_label,
        "priority": pri_label,
        "entities": entities,
        "confidence_score": round(confidence_score, 4),
    }


if __name__ == "__main__":
    example = "User jdoe cannot login to SAP, getting HTTP 500 error from CRM at 10.0.0.5."
    print(predict_ticket(example))

