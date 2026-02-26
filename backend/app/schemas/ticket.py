"""
Pydantic schemas for Ticket and TicketNote.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Ticket schemas
class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: str = "Medium"
    status: str = "Open"


class TicketCreate(TicketBase):
    created_by: Optional[int] = None


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class TicketListResponse(BaseModel):
    id: int
    title: str
    category: Optional[str] = None
    priority: str
    status: str
    created_at: datetime
    assigned_to: Optional[int] = None
    assignee_name: Optional[str] = None

    class Config:
        from_attributes = True


class TicketDetailResponse(TicketBase):
    id: int
    created_by: Optional[int] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator_name: Optional[str] = None
    assignee_name: Optional[str] = None
    notes: List["TicketNoteResponse"] = []

    class Config:
        from_attributes = True


# TicketNote schemas
class TicketNoteCreate(BaseModel):
    note: str


class TicketNoteResponse(BaseModel):
    id: int
    ticket_id: int
    agent_id: int
    note: str
    created_at: datetime
    agent_name: Optional[str] = None

    class Config:
        from_attributes = True


class TicketAssignRequest(BaseModel):
    assigned_to: Optional[int] = None  # None = unassign


# Fix forward reference
TicketDetailResponse.model_rebuild()
