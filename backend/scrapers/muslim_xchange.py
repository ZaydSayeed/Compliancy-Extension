"""
Muslim Xchange scraper for Shariah compliance data.
Muslim Xchange is the second priority source for compliance checks.
"""

import httpx
from bs4 import BeautifulSoup
import re
from models import ScreeningResponse, RuleBreakdown

BASE_URL = "https://muslimxchange.com/"


async def get_muslim_xchange_screening(ticker: str):
    """
    Check Shariah compliance status from Muslim Xchange.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        ScreeningResponse if verdict found, None otherwise.
    """
    url = f"{BASE_URL}{ticker.lower()}/"

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url)
            print(f"[Muslim Xchange] HTTP {resp.status_code} for {ticker} (URL: {resp.url})")
            if resp.status_code != 200:
                return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Strategy 1: Check the page title for compliance indicators
        # Example: "Is INTC - Intel Corp Halal and Shariah Compliant to Invest?"
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.text.lower()
            print(f"[Muslim Xchange] Page title: {title_tag.text[:80]}")
            
            # Look for "halal" in the title
            if "halal" in title_text and "not halal" not in title_text:
                print(f"[Muslim Xchange] Found 'Halal' in title for {ticker}")
                return ScreeningResponse(
                    ticker=ticker.upper(),
                    status="compliant",
                    source="Muslim Xchange",
                    breakdown=[
                        RuleBreakdown(
                            rule="Screening Source",
                            value="Muslim Xchange",
                            limit="N/A",
                            passed=True
                        )
                    ]
                )
            elif "not halal" in title_text or "haram" in title_text:
                print(f"[Muslim Xchange] Found 'Not Halal' in title for {ticker}")
                return ScreeningResponse(
                    ticker=ticker.upper(),
                    status="not_compliant",
                    source="Muslim Xchange",
                    breakdown=[
                        RuleBreakdown(
                            rule="Screening Source",
                            value="Muslim Xchange",
                            limit="N/A",
                            passed=False
                        )
                    ]
                )
        
        # Strategy 2: Check meta description
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc:
            desc_content = meta_desc.get("content", "").lower()
            print(f"[Muslim Xchange] Meta description found")
            
            if "halal" in desc_content and "not halal" not in desc_content:
                print(f"[Muslim Xchange] Found 'Halal' in meta description for {ticker}")
                return ScreeningResponse(
                    ticker=ticker.upper(),
                    status="compliant",
                    source="Muslim Xchange",
                    breakdown=[
                        RuleBreakdown(
                            rule="Screening Source",
                            value="Muslim Xchange",
                            limit="N/A",
                            passed=True
                        )
                    ]
                )
        
        # Strategy 3: Look for any element with compliance-related text
        page_text = soup.get_text().lower()
        
        # Check for explicit non-compliance indicators first
        if "not shariah compliant" in page_text or "non-compliant" in page_text:
            print(f"[Muslim Xchange] Found 'Not Compliant' in page for {ticker}")
            return ScreeningResponse(
                ticker=ticker.upper(),
                status="not_compliant",
                source="Muslim Xchange",
                breakdown=[
                    RuleBreakdown(
                        rule="Screening Source",
                        value="Muslim Xchange",
                        limit="N/A",
                        passed=False
                    )
                ]
            )
        
        # Check for compliance
        if "shariah compliant" in page_text or ("halal" in page_text and "invest" in page_text):
            print(f"[Muslim Xchange] Found compliance indicators in page for {ticker}")
            return ScreeningResponse(
                ticker=ticker.upper(),
                status="compliant",
                source="Muslim Xchange",
                breakdown=[
                    RuleBreakdown(
                        rule="Screening Source",
                        value="Muslim Xchange",
                        limit="N/A",
                        passed=True
                    )
                ]
            )
        
        print(f"[Muslim Xchange] No verdict found for {ticker}")
        return None

    except Exception as e:
        print(f"[Muslim Xchange] Scraper error: {e}")
        return None
