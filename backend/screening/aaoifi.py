"""
AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions)
rule-based Shariah screening.

This is the fallback screening method when no external sources provide data.
"""

from typing import Dict, Any, List
from utils.fetch_financials import fetch_financials
from models import ScreeningResponse, RuleBreakdown


# AAOIFI Shariah screening thresholds
DEBT_RATIO_LIMIT = 30.0  # Debt / Market Cap < 30%
CASH_RATIO_LIMIT = 30.0  # (Cash + Interest-bearing securities) / Market Cap < 30%
NON_HALAL_REVENUE_LIMIT = 5.0  # Non-permissible income / Total Revenue < 5%

# Non-compliant business sectors
NON_COMPLIANT_SECTORS = [
    "alcohol",
    "tobacco",
    "gambling",
    "adult entertainment",
    "pork",
    "conventional finance",
    "weapons",
    "conventional insurance",
]


async def run_aaoifi_screening(ticker: str) -> ScreeningResponse:
    """
    Perform AAOIFI-based Shariah compliance screening.
    
    AAOIFI screening rules:
    1. Debt Ratio: Total Debt / Market Cap < 30%
    2. Cash Ratio: (Cash + Interest-bearing securities) / Market Cap < 30%
    3. Non-Halal Revenue: Non-permissible income / Total Revenue < 5%
    4. Business Sector: Must not be in prohibited industries
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        ScreeningResponse with compliance status and detailed breakdown
    """
    print(f"[AAOIFI] Using fallback screening for {ticker}")
    
    # Fetch financial data
    financials = await fetch_financials(ticker)
    
    breakdown: List[RuleBreakdown] = []
    all_passed = True
    
    # 1. Debt Ratio Check
    debt_ratio = financials.get("debt_ratio", 0)
    debt_passed = debt_ratio < DEBT_RATIO_LIMIT
    if not debt_passed:
        all_passed = False
    
    breakdown.append(RuleBreakdown(
        rule="Debt Ratio",
        value=f"{debt_ratio:.1f}%",
        limit=f"< {DEBT_RATIO_LIMIT:.0f}%",
        passed=debt_passed,
        reason="Exceeds limit" if not debt_passed else None
    ))
    
    # 2. Cash Ratio Check
    cash_ratio = financials.get("cash_ratio", 0)
    cash_passed = cash_ratio < CASH_RATIO_LIMIT
    if not cash_passed:
        all_passed = False
    
    breakdown.append(RuleBreakdown(
        rule="Cash Ratio",
        value=f"{cash_ratio:.1f}%",
        limit=f"< {CASH_RATIO_LIMIT:.0f}%",
        passed=cash_passed,
        reason="Exceeds limit" if not cash_passed else None
    ))
    
    # 3. Non-Halal Revenue Check
    non_halal_revenue = financials.get("non_halal_revenue", 0)
    revenue_passed = non_halal_revenue < NON_HALAL_REVENUE_LIMIT
    if not revenue_passed:
        all_passed = False
    
    breakdown.append(RuleBreakdown(
        rule="Non-Halal Revenue",
        value=f"{non_halal_revenue:.1f}%",
        limit=f"< {NON_HALAL_REVENUE_LIMIT:.0f}%",
        passed=revenue_passed,
        reason="Exceeds limit" if not revenue_passed else None
    ))
    
    # 4. Business Sector Check
    sector = financials.get("sector", "Unknown")
    sector_lower = sector.lower()
    sector_passed = not any(prohibited in sector_lower for prohibited in NON_COMPLIANT_SECTORS)
    if not sector_passed:
        all_passed = False
    
    breakdown.append(RuleBreakdown(
        rule="Sector",
        value=sector,
        limit="Allowed",
        passed=sector_passed,
        reason="Prohibited industry" if not sector_passed else None
    ))
    
    status = "compliant" if all_passed else "not_compliant"
    print(f"[AAOIFI] Returning result for {ticker}: {status}")
    
    return ScreeningResponse(
        ticker=ticker.upper(),
        status=status,
        source="AAOIFI",
        breakdown=breakdown
    )
