"""
Generate a synthetic IT helpdesk ticket dataset.

Output CSV: data/tickets.csv

Columns:
- text: user complaint text
- category: one of predefined categories
- priority: Low / Medium / High / Critical
"""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_CSV = DATA_DIR / "tickets.csv"

CATEGORIES = [
    "Hardware Issue",
    "Software Bug",
    "Network Problem",
    "Access Request",
    "Account Issue",
    "Security Incident",
    "Performance Issue",
]

PRIORITIES = ["Low", "Medium", "High", "Critical"]


def _maybe_typo(word: str) -> str:
    """Introduce a simple typo in a word with small probability."""
    if len(word) <= 3 or random.random() > 0.15:
        return word
    # random deletion or swap
    chars = list(word)
    if random.random() < 0.5 and len(chars) > 3:
        i = random.randint(1, len(chars) - 2)
        chars.pop(i)
    else:
        i = random.randint(0, len(chars) - 2)
        chars[i], chars[i + 1] = chars[i + 1], chars[i]
    return "".join(chars)


def _noisify(text: str) -> str:
    """Apply simple noise: typos and casual wording."""
    words = text.split()
    words = [_maybe_typo(w) for w in words]
    # occasional extra tokens
    if random.random() < 0.1:
        words.append(random.choice(["pls", "asap", "urgnt", "tnx"]))
    return " ".join(words)


def _sample_hardware(priority: str) -> str:
    templates = [
        "My laptop keeps shutting down randomly while working on VPN.",
        "The keyboard on my desktop is not responding, tried reconnecting USB.",
        "Monitor flickers and sometimes goes completely black during meetings.",
        "USB ports on the docking station stopped working after last restart.",
        "Printer in floor 3 is jammed and shows error code E{code}.",
    ]
    base = random.choice(templates)
    if "{code}" in base:
        base = base.format(code=random.randint(100, 999))
    if priority in ("High", "Critical"):
        base += " This is blocking my work and I have deadlines today."
    return base


def _sample_software(priority: str) -> str:
    templates = [
        "Getting error 'NullReferenceException' whenever I try to save in the CRM.",
        "Outlook keeps crashing with error 0x80070005 when sending emails.",
        "The finance app throws HTTP 500 internal server error on login.",
        "After the latest update, our ERP client freezes on the login screen.",
        "Excel plugin for reporting fails with stacktrace: {code}.",
    ]
    base = random.choice(templates)
    if "{code}" in base:
        base = base.format(code=f"ORA-{random.randint(1000, 9999)}")
    if priority in ("High", "Critical"):
        base += " Needs immediate fix, critical business process impacted."
    return base


def _sample_network(priority: str) -> str:
    ip = f"10.0.{random.randint(0, 20)}.{random.randint(1, 254)}"
    templates = [
        f"Cannot reach VPN, connection timed out while pinging {ip}.",
        f"WiFi keeps dropping every few minutes in meeting room A.",
        f"Latency to our database server at {ip} is over 300ms.",
        "Users in branch office report 'DNS_PROBE_FINISHED_NXDOMAIN' on intranet.",
        "Getting intermittent packet loss when accessing remote desktop.",
    ]
    base = random.choice(templates)
    if priority in ("High", "Critical"):
        base += " Entire team is unable to access critical systems."
    return base


def _sample_access(priority: str) -> str:
    systems = ["SAP", "Salesforce", "Jira", "Confluence", "VPN", "HR portal"]
    user = random.choice(["jdoe", "asmith", "r.kumar", "m.garcia"])
    system = random.choice(systems)
    templates = [
        f"New joiner {user} needs access to {system} with standard permissions.",
        f"Please grant read-only access to {system} for user {user}.",
        f"I lost access to {system} after role change, getting access denied.",
        f"Requesting VPN access for contractor {user} for the next 3 months.",
    ]
    base = random.choice(templates)
    if priority in ("High", "Critical"):
        base += " User is blocked from on-boarding tasks."
    return base


def _sample_account(priority: str) -> str:
    templates = [
        "My AD account is locked, can't log into Windows or email.",
        "Password reset link for my account has expired multiple times.",
        "Getting 'account disabled' message when trying to sign in.",
        "SSO login fails with 'invalid credentials' even after password reset.",
    ]
    base = random.choice(templates)
    if priority in ("High", "Critical"):
        base += " Need urgent help to join production call."
    return base


def _sample_security(priority: str) -> str:
    ips = f"192.168.{random.randint(0, 10)}.{random.randint(1, 254)}"
    templates = [
        f"Antivirus detected Trojan on my machine connecting to {ips}.",
        "Received phishing email asking for bank details from fake IT support.",
        "Multiple failed login attempts detected on my account overnight.",
        "Noticed unknown software installed that I did not approve.",
    ]
    base = random.choice(templates)
    if priority in ("High", "Critical"):
        base += " Potential security breach, please investigate immediately."
    return base


def _sample_performance(priority: str) -> str:
    templates = [
        "Laptop is extremely slow, apps take minutes to open.",
        "SAP transactions are timing out and running very slowly today.",
        "Remote desktop to production server is laggy and unusable.",
        "Reports in BI dashboard take over 5 minutes to load.",
    ]
    base = random.choice(templates)
    if priority in ("High", "Critical"):
        base += " This is delaying critical month-end processing."
    return base


CATEGORY_SAMPLERS = {
    "Hardware Issue": _sample_hardware,
    "Software Bug": _sample_software,
    "Network Problem": _sample_network,
    "Access Request": _sample_access,
    "Account Issue": _sample_account,
    "Security Incident": _sample_security,
    "Performance Issue": _sample_performance,
}


def generate_dataset(n_per_category: int = 160) -> pd.DataFrame:
    """
    Generate a balanced synthetic dataset.

    n_per_category * len(CATEGORIES) samples total (>= 1000 by default).
    """
    rows = []
    for category in CATEGORIES:
        sampler = CATEGORY_SAMPLERS[category]
        for _ in range(n_per_category):
            # Bias priorities depending on category
            if category in {"Security Incident", "Network Problem"}:
                priority = random.choices(
                    PRIORITIES,
                    weights=[0.1, 0.2, 0.4, 0.3],
                    k=1,
                )[0]
            elif category in {"Access Request", "Account Issue"}:
                priority = random.choices(
                    PRIORITIES,
                    weights=[0.3, 0.5, 0.15, 0.05],
                    k=1,
                )[0]
            else:
                priority = random.choices(
                    PRIORITIES,
                    weights=[0.2, 0.4, 0.3, 0.1],
                    k=1,
                )[0]

            text = sampler(priority)

            # Add some shorter / longer / mixed style variants
            if random.random() < 0.2:
                text = text.split(".")[0]
            if random.random() < 0.2:
                text = "Hi team, " + text

            text = _noisify(text)
            rows.append({"text": text, "category": category, "priority": priority})

    df = pd.DataFrame(rows)
    return df.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)


def main() -> None:
    df = generate_dataset()
    print(f"Generated {len(df)} synthetic tickets.")
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved dataset to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

