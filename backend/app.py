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
import re

from models import ScreeningResponse, RuleBreakdown
from scrapers.zoya import get_zoya_screening
from scrapers.muslim_xchange import get_muslim_xchange_screening
from scrapers.musaffa import get_musaffa_screening
from screening.aaoifi import run_aaoifi_screening


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


@app.get("/check", response_model=ScreeningResponse)
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
        ScreeningResponse with status, source, and breakdown
    """
    # Validate ticker
    ticker = validate_ticker(ticker)
    
    print(f"\n{'='*50}")
    print(f"[API] Checking compliance for: {ticker}")
    print(f"{'='*50}")
    
    # Try sources in priority order
    
    # 1. Try Zoya first
    result = await get_zoya_screening(ticker)
    if result:
        print(f"[API] ✓ Returning Zoya result")
        return result
    
    # 2. Try Muslim Xchange
    result = await get_muslim_xchange_screening(ticker)
    if result:
        print(f"[API] ✓ Returning Muslim Xchange result")
        return result
    
    # 3. Try Musaffa
    result = await get_musaffa_screening(ticker)
    if result:
        print(f"[API] ✓ Returning Musaffa result")
        return result
    
    # 4. Fallback to AAOIFI screening
    print(f"[API] Using AAOIFI fallback")
    result = await run_aaoifi_screening(ticker)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
