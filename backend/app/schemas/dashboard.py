"""
Dashboard statistics schema.
"""
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress: int
    resolved: int
    high_priority: int
