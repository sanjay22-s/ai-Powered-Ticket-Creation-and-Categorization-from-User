"""
Seed script: create tables and insert dummy users + tickets.
Run from project root: python scripts/seed_data.py
Ensure BACKEND .env has correct DATABASE_URL and backend deps are installed.
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend))

# Load .env from backend
env_file = backend / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

from sqlalchemy import create_engine
from app.database import Base
from app.models import User, Ticket, TicketNote
from app.core.config import get_settings
from app.core.security import get_password_hash

# Use same default as app (SQLite in backend folder) so seed and backend share the DB
DATABASE_URL = os.environ.get("DATABASE_URL") or get_settings().DATABASE_URL


def main():
    connect_args = {}
    if DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    db = Session()

    # Create users if not exist
    if db.query(User).count() == 0:
        agent = User(
            name="Support Agent",
            email="agent@example.com",
            password_hash=get_password_hash("agent123"),
            role="agent",
        )
        admin = User(
            name="Admin User",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
        )
        db.add(agent)
        db.add(admin)
        db.commit()
        db.refresh(agent)
        db.refresh(admin)
        print("Created users: agent@example.com / agent123, admin@example.com / admin123")
    else:
        agent = db.query(User).filter(User.email == "agent@example.com").first()
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not agent:
            agent = db.query(User).first()
        if not admin:
            admin = agent

    # Create dummy tickets
    if db.query(Ticket).count() == 0:
        tickets_data = [
            ("Login not working", "User cannot log in with correct password.", "Technical", "High", "Open"),
            ("Billing inquiry", "Question about last month invoice.", "Billing", "Medium", "In Progress"),
            ("Feature request", "Add dark mode to dashboard.", "Feature", "Low", "Open"),
            ("Server down", "Production server returning 502.", "Technical", "Critical", "Open"),
            ("Password reset", "User forgot password.", "Technical", "Low", "Resolved"),
        ]
        for title, desc, cat, pri, status in tickets_data:
            t = Ticket(
                title=title,
                description=desc,
                category=cat,
                priority=pri,
                status=status,
                created_by=agent.id if agent else None,
                assigned_to=agent.id if agent else None,
            )
            db.add(t)
        db.commit()
        # Add a note to first ticket
        first = db.query(Ticket).first()
        if first and agent:
            n = TicketNote(ticket_id=first.id, agent_id=agent.id, note="Checking credentials and session storage.")
            db.add(n)
            db.commit()
        print("Created sample tickets and one note.")
    else:
        print("Tickets already exist, skipping.")

    db.close()
    print("Seed done.")


if __name__ == "__main__":
    main()
