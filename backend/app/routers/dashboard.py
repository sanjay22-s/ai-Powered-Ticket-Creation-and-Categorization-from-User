"""
Dashboard statistics endpoint.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Ticket, TicketStatus, TicketPriority
from app.schemas import DashboardStats
from app.routers.deps import require_agent

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user=Depends(require_agent),
):
    """Return dashboard statistics for tickets."""
    total = db.query(func.count(Ticket.id)).scalar() or 0
    open_count = (
        db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.OPEN.value).scalar()
        or 0
    )
    in_progress = (
        db.query(func.count(Ticket.id))
        .filter(Ticket.status == TicketStatus.IN_PROGRESS.value)
        .scalar()
        or 0
    )
    resolved = (
        db.query(func.count(Ticket.id))
        .filter(Ticket.status == TicketStatus.RESOLVED.value)
        .scalar()
        or 0
    )
    high_priority = (
        db.query(func.count(Ticket.id))
        .filter(
            Ticket.priority.in_(
                [TicketPriority.HIGH.value, TicketPriority.CRITICAL.value]
            )
        )
        .scalar()
        or 0
    )
    return DashboardStats(
        total_tickets=total,
        open_tickets=open_count,
        in_progress=in_progress,
        resolved=resolved,
        high_priority=high_priority,
    )
