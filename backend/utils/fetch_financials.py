"""
Utility module for fetching financial data for AAOIFI screening.
"""

import httpx
from typing import Dict, Any


# Mock financial data for demonstration
# In production, this would fetch from Yahoo Finance, Alpha Vantage, or similar APIs
MOCK_FINANCIALS: Dict[str, Dict[str, Any]] = {
    "AAPL": {
        "debt_ratio": 42.0,
        "cash_ratio": 27.0,
        "non_halal_revenue": 3.0,
        "sector": "Technology",
    },
    "TSLA": {
        "debt_ratio": 15.0,
        "cash_ratio": 22.0,
        "non_halal_revenue": 0.0,
        "sector": "Automotive",
    },
    "MSFT": {
        "debt_ratio": 25.0,
        "cash_ratio": 28.0,
        "non_halal_revenue": 2.0,
        "sector": "Technology",
    },
    "JPM": {
        "debt_ratio": 85.0,
        "cash_ratio": 45.0,
        "non_halal_revenue": 80.0,
        "sector": "Conventional Finance",
    },
    "BUD": {
        "debt_ratio": 35.0,
        "cash_ratio": 10.0,
        "non_halal_revenue": 95.0,
        "sector": "Alcohol",
    },
}

# Default values for unknown tickers
DEFAULT_FINANCIALS: Dict[str, Any] = {
    "debt_ratio": 25.0,
    "cash_ratio": 20.0,
    "non_halal_revenue": 2.0,
    "sector": "Unknown",
}


async def fetch_financials(ticker: str) -> Dict[str, Any]:
    """
    Fetch financial data for a given ticker.
    
    In production, this would:
    1. Query Yahoo Finance API or similar
    2. Calculate debt ratio from Total Debt / Market Cap
    3. Calculate cash ratio from (Cash + Securities) / Market Cap
    4. Estimate non-halal revenue percentage
    5. Get the business sector
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        Dict with financial metrics:
        {
            "debt_ratio": float,      # Percentage
            "cash_ratio": float,      # Percentage
            "non_halal_revenue": float,  # Percentage
            "sector": str,
        }
    """
    ticker_upper = ticker.upper()
    
    # Return mock data if available
    if ticker_upper in MOCK_FINANCIALS:
        return MOCK_FINANCIALS[ticker_upper]
    
    # For unknown tickers, return default values
    # In production, this would make an actual API call
    return DEFAULT_FINANCIALS.copy()


async def fetch_from_yahoo_finance(ticker: str) -> Dict[str, Any]:
    """
    Placeholder for Yahoo Finance API integration.
    
    This would fetch real financial data including:
    - Total Debt
    - Market Capitalization
    - Cash and Cash Equivalents
    - Revenue breakdown
    - Sector classification
    """
    # Placeholder - would need Yahoo Finance API key
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # This is a placeholder URL
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
            params = {"modules": "financialData,summaryDetail,assetProfile"}
            
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                return DEFAULT_FINANCIALS.copy()
            
            data = response.json()
            # Parse and calculate ratios...
            return DEFAULT_FINANCIALS.copy()
            
    except Exception as e:
        print(f"[Yahoo Finance] Error fetching {ticker}: {e}")
        return DEFAULT_FINANCIALS.copy()
