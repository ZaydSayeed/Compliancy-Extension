"""
Shared Pydantic models for the Shariah Compliance Checker backend.
These are defined separately to avoid circular imports between app.py and scrapers.
"""

from pydantic import BaseModel
from typing import List, Optional


class RuleBreakdown(BaseModel):
    """Individual compliance rule check result."""
    rule: str
    value: str
    limit: str
    passed: bool
    reason: Optional[str] = None


class ScreeningResponse(BaseModel):
    """Response model for compliance check."""
    ticker: str
    status: str  # "compliant", "not_compliant", "doubtful"
    source: str  # "Zoya", "Muslim Xchange", "Musaffa", "AAOIFI"
    breakdown: List[RuleBreakdown]
