"""
Ticket CRUD and notes/assign endpoints.
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Ticket, TicketNote, User
from app.schemas import (
    TicketListResponse,
    TicketDetailResponse,
    TicketUpdate,
    TicketNoteCreate,
    TicketNoteResponse,
    TicketAssignRequest,
)
from app.routers.deps import require_agent

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _ticket_to_list(t: Ticket) -> TicketListResponse:
    assignee_name = None
    if t.assignee:
        assignee_name = t.assignee.name
    return TicketListResponse(
        id=t.id,
        title=t.title,
        category=t.category,
        priority=t.priority,
        status=t.status,
        created_at=t.created_at,
        assigned_to=t.assigned_to,
        assignee_name=assignee_name,
    )


def _ticket_to_detail(t: Ticket) -> TicketDetailResponse:
    creator_name = t.creator.name if t.creator else None
    assignee_name = t.assignee.name if t.assignee else None
    notes_data = [
        TicketNoteResponse(
            id=n.id,
            ticket_id=n.ticket_id,
            agent_id=n.agent_id,
            note=n.note,
            created_at=n.created_at,
            agent_name=n.agent.name if n.agent else None,
        )
        for n in t.notes
    ]
    return TicketDetailResponse(
        id=t.id,
        title=t.title,
        description=t.description,
        category=t.category,
        priority=t.priority,
        status=t.status,
        created_by=t.created_by,
        assigned_to=t.assigned_to,
        created_at=t.created_at,
        updated_at=t.updated_at,
        creator_name=creator_name,
        assignee_name=assignee_name,
        notes=notes_data,
    )


@router.get("", response_model=List[TicketListResponse])
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """List tickets with optional filters and pagination."""
    q = db.query(Ticket).options(joinedload(Ticket.assignee))
    if status:
        q = q.filter(Ticket.status == status)
    if priority:
        q = q.filter(Ticket.priority == priority)
    if category:
        q = q.filter(Ticket.category == category)
    if search:
        q = q.filter(Ticket.title.ilike(f"%{search}%"))
    q = q.order_by(Ticket.updated_at.desc())
    tickets = q.offset(skip).limit(limit).all()
    return [_ticket_to_list(t) for t in tickets]


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent),
):
    """Get single ticket with notes."""
    ticket = (
        db.query(Ticket)
        .options(
            joinedload(Ticket.creator),
            joinedload(Ticket.assignee),
            joinedload(Ticket.notes).joinedload(TicketNote.agent),
        )
        .filter(Ticket.id == ticket_id)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return _ticket_to_detail(ticket)


@router.put("/{ticket_id}", response_model=TicketDetailResponse)
def update_ticket(
    ticket_id: int,
    body: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent),
):
    """Update ticket fields (status, priority, category, etc.)."""
    ticket = (
        db.query(Ticket)
        .options(
            joinedload(Ticket.creator),
            joinedload(Ticket.assignee),
            joinedload(Ticket.notes).joinedload(TicketNote.agent),
        )
        .filter(Ticket.id == ticket_id)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ticket, key, value)
    db.commit()
    db.refresh(ticket)
    return _ticket_to_detail(ticket)


@router.post("/{ticket_id}/notes", response_model=TicketNoteResponse)
def add_note(
    ticket_id: int,
    body: TicketNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent),
):
    """Add internal note to ticket."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    note = TicketNote(
        ticket_id=ticket_id,
        agent_id=current_user.id,
        note=body.note,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return TicketNoteResponse(
        id=note.id,
        ticket_id=note.ticket_id,
        agent_id=note.agent_id,
        note=note.note,
        created_at=note.created_at,
        agent_name=current_user.name,
    )


@router.put("/{ticket_id}/assign", response_model=TicketDetailResponse)
def assign_ticket(
    ticket_id: int,
    body: TicketAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_agent),
):
    """Assign ticket to user (or unassign if assigned_to is null)."""
    ticket = (
        db.query(Ticket)
        .options(
            joinedload(Ticket.creator),
            joinedload(Ticket.assignee),
            joinedload(Ticket.notes).joinedload(TicketNote.agent),
        )
        .filter(Ticket.id == ticket_id)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    # assigned_to: use provided value (None = unassign); frontend sends current user id for "Assign to me"
    ticket.assigned_to = body.assigned_to
    db.commit()
    db.refresh(ticket)
    return _ticket_to_detail(ticket)
