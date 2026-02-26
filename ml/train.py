"""
Train ticket category and priority models.

Steps:
- Load data/tickets.csv
- Preprocess text (lowercase, stopword removal, lemmatization)
- TF-IDF vectorization
- Train 3 classifiers (LogReg, RandomForest, Linear SVM) for each task
- Evaluate (accuracy, F1, confusion matrix)
- Optionally run simple hyperparameter search
- Save best models and vectorizer to models/
- Write report to reports/model_report.txt
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split, GridSearchCV

import spacy

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "tickets.csv"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_spacy_model() -> "spacy.language.Language":
    """Load spaCy model with a clear error if not installed."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError as exc:  # model not downloaded
        raise RuntimeError(
            "spaCy model 'en_core_web_sm' is not installed. "
            "Install it with: python -m spacy download en_core_web_sm"
        ) from exc


def preprocess_texts(texts: List[str], nlp: "spacy.language.Language") -> List[str]:
    """
    Lowercase, remove stopwords and punctuation, lemmatize tokens.

    Returns cleaned string per document.
    """
    cleaned: List[str] = []
    for doc in nlp.pipe(texts, batch_size=64, n_process=1):
        tokens = [
            tok.lemma_.lower()
            for tok in doc
            if not tok.is_stop and not tok.is_punct and tok.lemma_.strip()
        ]
        cleaned.append(" ".join(tokens))
    return cleaned


def build_vectorizer() -> TfidfVectorizer:
    """Configure TF-IDF vectorizer."""
    return TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=10000,
        min_df=2,
    )


def train_and_evaluate_models(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    task_name: str,
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, str], Dict[str, np.ndarray], str]:
    """
    Train 3 models for a classification task and evaluate them.

    Returns:
    - metrics_per_model: {model_name: {accuracy, f1}}
    - reports_per_model: {model_name: classification_report_str}
    - confusion_matrices: {model_name: ndarray}
    - best_model_name: name among LogisticRegression / RandomForest / LinearSVM
    """
    models = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, n_jobs=-1, class_weight="balanced"
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, max_depth=None, n_jobs=-1, class_weight="balanced"
        ),
        "LinearSVM": LinearSVC(class_weight="balanced"),
    }

    metrics_per_model: Dict[str, Dict[str, float]] = {}
    reports_per_model: Dict[str, str] = {}
    confusion_matrices: Dict[str, np.ndarray] = {}

    for name, clf in models.items():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        metrics_per_model[name] = {"accuracy": acc, "f1_weighted": f1}
        reports_per_model[name] = classification_report(y_test, y_pred)
        confusion_matrices[name] = confusion_matrix(y_test, y_pred)
        print(f"\n=== {task_name} - {name} ===")
        print(f"Accuracy: {acc:.4f}, F1 (weighted): {f1:.4f}")

    # Choose best by F1 score
    best_model_name = max(
        metrics_per_model.items(), key=lambda kv: kv[1]["f1_weighted"]
    )[0]
    print(f"\nBest {task_name} model: {best_model_name}")
    return metrics_per_model, reports_per_model, confusion_matrices, best_model_name


def simple_hyperparameter_search(
    X_train: np.ndarray,
    y_train: np.ndarray,
    base_model: str,
    task_name: str,
) -> Tuple[object, Dict[str, float]]:
    """
    Optional small GridSearchCV for bonus step.
    Returns best estimator and its CV metrics.
    """
    if base_model == "LogisticRegression":
        clf = LogisticRegression(max_iter=1000, n_jobs=-1, class_weight="balanced")
        param_grid = {"C": [0.5, 1.0, 2.0]}
    elif base_model == "RandomForest":
        clf = RandomForestClassifier(
            n_jobs=-1, class_weight="balanced", random_state=42
        )
        param_grid = {
            "n_estimators": [150, 250],
            "max_depth": [None, 20],
        }
    else:
        raise ValueError(f"Unsupported base_model for tuning: {base_model}")

    grid = GridSearchCV(
        clf,
        param_grid=param_grid,
        scoring="f1_weighted",
        cv=3,
        n_jobs=-1,
        verbose=0,
    )
    print(f"\nRunning GridSearchCV for {task_name} / {base_model} ...")
    grid.fit(X_train, y_train)
    print(f"Best params: {grid.best_params_}")
    print(f"Best CV F1 (weighted): {grid.best_score_:.4f}")
    return grid.best_estimator_, {
        "best_cv_f1_weighted": float(grid.best_score_),
        "best_params": grid.best_params_,
    }


def save_report(
    metrics: Dict[str, Dict[str, float]],
    reports: Dict[str, str],
    conf_mats: Dict[str, np.ndarray],
    best_category_model: str,
    best_priority_model: str,
    tuning_info: Dict[str, Dict[str, float]],
) -> None:
    """Save a human-readable report to reports/model_report.txt."""
    report_lines: List[str] = []
    report_lines.append("Ticket Classification Model Report\n")
    report_lines.append("=================================\n\n")

    report_lines.append("Metrics per model (category & priority):\n")
    for task_model, m in metrics.items():
        report_lines.append(f"- {task_model}: {json.dumps(m, indent=2)}\n")

    report_lines.append("\nBest selected models:\n")
    report_lines.append(f"- Category: {best_category_model}\n")
    report_lines.append(f"- Priority: {best_priority_model}\n")

    if tuning_info:
        report_lines.append("\nHyperparameter tuning (GridSearchCV):\n")
        for key, info in tuning_info.items():
            report_lines.append(f"- {key}: {json.dumps(info, indent=2)}\n")

    report_lines.append("\nDetailed classification reports:\n")
    for key, rep in reports.items():
        report_lines.append(f"\n=== {key} ===\n{rep}\n")

    report_lines.append("\nConfusion matrices:\n")
    for key, mat in conf_mats.items():
        report_lines.append(f"\n=== {key} ===\n{mat}\n")

    out_path = REPORTS_DIR / "model_report.txt"
    out_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\nSaved evaluation report to {out_path}")


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}. Run ml/generate_dataset.py first."
        )

    print(f"Loading dataset from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["text", "category", "priority"])

    nlp = load_spacy_model()
    print("Preprocessing texts with spaCy...")
    df["clean_text"] = preprocess_texts(df["text"].tolist(), nlp)

    # Train / test split
    X_train_text, X_test_text, y_cat_train, y_cat_test, y_pri_train, y_pri_test = train_test_split(
        df["clean_text"].values,
        df["category"].values,
        df["priority"].values,
        test_size=0.2,
        random_state=42,
        stratify=df["category"].values,
    )

    # Vectorization
    vectorizer = build_vectorizer()
    print("Fitting TF-IDF vectorizer...")
    X_train_vec = vectorizer.fit_transform(X_train_text)
    X_test_vec = vectorizer.transform(X_test_text)

    # Category models
    cat_metrics, cat_reports, cat_conf, best_cat_name = train_and_evaluate_models(
        X_train_vec, y_cat_train, X_test_vec, y_cat_test, task_name="Category"
    )

    # Priority models
    pri_metrics, pri_reports, pri_conf, best_pri_name = train_and_evaluate_models(
        X_train_vec, y_pri_train, X_test_vec, y_pri_test, task_name="Priority"
    )

    # Optional: Hyperparameter tuning for best LogisticRegression / RandomForest
    tuning_info: Dict[str, Dict[str, float]] = {}
    cat_best_for_tuning = (
        "LogisticRegression"
        if "LogisticRegression" in cat_metrics
        else list(cat_metrics.keys())[0]
    )
    pri_best_for_tuning = (
        "LogisticRegression"
        if "LogisticRegression" in pri_metrics
        else list(pri_metrics.keys())[0]
    )

    cat_tuned_model, cat_tuning = simple_hyperparameter_search(
        X_train_vec, y_cat_train, cat_best_for_tuning, "Category"
    )
    pri_tuned_model, pri_tuning = simple_hyperparameter_search(
        X_train_vec, y_pri_train, pri_best_for_tuning, "Priority"
    )
    tuning_info["Category"] = cat_tuning
    tuning_info["Priority"] = pri_tuning

    # For deployment we prefer models with predict_proba support
    def _choose_deploy_model(
        tuned_model: object,
        models_metrics: Dict[str, Dict[str, float]],
        X_test: np.ndarray,
        y_test: np.ndarray,
        task_label: str,
    ) -> Tuple[object, str]:
        if hasattr(tuned_model, "predict_proba"):
            return tuned_model, f"{task_label}-Tuned-{tuned_model.__class__.__name__}"
        # Fallback: best among LogisticRegression / RandomForest with predict_proba
        candidates = []
        for name in ["LogisticRegression", "RandomForest"]:
            if name in models_metrics:
                clf = {
                    "LogisticRegression": LogisticRegression(
                        max_iter=1000, n_jobs=-1, class_weight="balanced"
                    ),
                    "RandomForest": RandomForestClassifier(
                        n_estimators=200,
                        max_depth=None,
                        n_jobs=-1,
                        class_weight="balanced",
                    ),
                }[name]
                clf.fit(X_train_vec, y_cat_train if task_label == "Category" else y_pri_train)
                y_pred = clf.predict(X_test)
                f1 = f1_score(y_test, y_pred, average="weighted")
                candidates.append((f1, name, clf))
        if not candidates:
            return tuned_model, f"{task_label}-Tuned-{tuned_model.__class__.__name__}"
        best_f1, best_name, best_clf = max(candidates, key=lambda t: t[0])
        print(f"Selected {task_label} deploy model: {best_name} (F1={best_f1:.4f})")
        return best_clf, f"{task_label}-Deploy-{best_name}"

    cat_deploy_model, cat_deploy_name = _choose_deploy_model(
        cat_tuned_model, cat_metrics, X_test_vec, y_cat_test, "Category"
    )
    pri_deploy_model, pri_deploy_name = _choose_deploy_model(
        pri_tuned_model, pri_metrics, X_test_vec, y_pri_test, "Priority"
    )

    # Combine metrics keys for report
    combined_metrics: Dict[str, Dict[str, float]] = {}
    combined_metrics.update({f"Category-{k}": v for k, v in cat_metrics.items()})
    combined_metrics.update({f"Priority-{k}": v for k, v in pri_metrics.items()})

    combined_reports: Dict[str, str] = {}
    combined_reports.update({f"Category-{k}": v for k, v in cat_reports.items()})
    combined_reports.update({f"Priority-{k}": v for k, v in pri_reports.items()})

    combined_conf: Dict[str, np.ndarray] = {}
    combined_conf.update({f"Category-{k}": v for k, v in cat_conf.items()})
    combined_conf.update({f"Priority-{k}": v for k, v in pri_conf.items()})

    save_report(
        metrics=combined_metrics,
        reports=combined_reports,
        conf_mats=combined_conf,
        best_category_model=cat_deploy_name,
        best_priority_model=pri_deploy_name,
        tuning_info=tuning_info,
    )

    # Save vectorizer and models
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.pkl")
    joblib.dump(cat_deploy_model, MODELS_DIR / "category_model.pkl")
    joblib.dump(pri_deploy_model, MODELS_DIR / "priority_model.pkl")
    print(f"Saved models to {MODELS_DIR}")


if __name__ == "__main__":
    main()

