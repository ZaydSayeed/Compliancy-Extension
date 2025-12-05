"""
Shariah Compliance Checker - FastAPI Backend

This API provides endpoints for checking Shariah compliance of stocks.
It aggregates data from multiple sources:
1. Zoya (priority 1)
2. Muslim Xchange (priority 2)
3. Musaffa (priority 3)
4. AAOIFI rule-based screening (fallback)
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import re

from scrapers import check_zoya, check_muslim_xchange, check_musaffa
from screening import aaoifi_screening


app = FastAPI(
    title="Shariah Compliance Checker API",
    description="Check if stocks are Shariah-compliant using multiple sources",
    version="1.0.0",
)

# Enable CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for extension
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BreakdownItem(BaseModel):
    """Individual compliance rule check result."""
    rule: str
    value: str
    limit: str
    passed: bool
    reason: Optional[str] = None


class ComplianceResponse(BaseModel):
    """Response model for compliance check."""
    ticker: str
    status: str  # "compliant", "not_compliant", "doubtful"
    source: str  # "Zoya", "Muslim Xchange", "Musaffa", "AAOIFI"
    breakdown: List[BreakdownItem]


def validate_ticker(ticker: str) -> str:
    """
    Validate and normalize ticker symbol.
    
    Args:
        ticker: Raw ticker input
        
    Returns:
        Normalized uppercase ticker
        
    Raises:
        HTTPException if ticker is invalid
    """
    # Remove whitespace
    ticker = ticker.strip().upper()
    
    # Validate format (1-5 letters, optionally with numbers)
    if not re.match(r'^[A-Z]{1,5}$', ticker):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ticker format: {ticker}. Must be 1-5 letters."
        )
    
    return ticker


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Shariah Compliance Checker API is running",
        "docs": "/docs"
    }


@app.get("/check", response_model=ComplianceResponse)
async def check_compliance(ticker: str = Query(..., description="Stock ticker symbol (e.g., AAPL)")):
    """
    Check Shariah compliance for a stock ticker.
    
    Screening priority:
    1. Zoya - Most trusted source
    2. Muslim Xchange - Secondary source
    3. Musaffa - Tertiary source  
    4. AAOIFI - Fallback rule-based screening
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
        
    Returns:
        ComplianceResponse with status, source, and breakdown
    """
    # Validate ticker
    ticker = validate_ticker(ticker)
    
    # Try sources in priority order
    
    # 1. Try Zoya first
    result = await check_zoya(ticker)
    if result:
        return ComplianceResponse(
            ticker=ticker,
            status=result["status"],
            source=result["source"],
            breakdown=[BreakdownItem(**item) for item in result.get("breakdown", [])]
        )
    
    # 2. Try Muslim Xchange
    result = await check_muslim_xchange(ticker)
    if result:
        return ComplianceResponse(
            ticker=ticker,
            status=result["status"],
            source=result["source"],
            breakdown=[BreakdownItem(**item) for item in result.get("breakdown", [])]
        )
    
    # 3. Try Musaffa
    result = await check_musaffa(ticker)
    if result:
        return ComplianceResponse(
            ticker=ticker,
            status=result["status"],
            source=result["source"],
            breakdown=[BreakdownItem(**item) for item in result.get("breakdown", [])]
        )
    
    # 4. Fallback to AAOIFI screening
    result = await aaoifi_screening(ticker)
    return ComplianceResponse(
        ticker=ticker,
        status=result["status"],
        source=result["source"],
        breakdown=[BreakdownItem(**item) for item in result.get("breakdown", [])]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
