# Shariah Compliance Checker

A Chrome Extension + FastAPI backend that helps Muslim investors check if stocks are Shariah-compliant before investing.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **Hover Detection**: Automatically detects stock tickers when hovering over text on any webpage
- **Floating Widget**: Displays instant compliance status (Halal ✅ / Not Halal ❌) next to the cursor
- **Detailed Breakdown**: Click to see full compliance analysis with pass/fail for each rule
- **Multiple Data Sources**: Aggregates data from trusted Shariah screening providers:
  - 🥇 Zoya (Primary)
  - 🥈 Muslim Xchange (Secondary)
  - 🥉 Musaffa (Tertiary)
  - 📊 AAOIFI Rule-based Screening (Fallback)

## 📁 Folder Structure

```
.
├── backend/
│   ├── app.py                    # FastAPI main application
│   ├── requirements.txt          # Python dependencies
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── zoya.py              # Zoya scraper
│   │   ├── muslim_xchange.py    # Muslim Xchange scraper
│   │   └── musaffa.py           # Musaffa scraper
│   ├── screening/
│   │   ├── __init__.py
│   │   └── aaoifi.py            # AAOIFI rule-based screening
│   └── utils/
│       ├── __init__.py
│       └── fetch_financials.py  # Financial data fetching
│
├── extension/
│   ├── manifest.json            # Chrome extension manifest (v3)
│   ├── background.js            # Service worker for API calls
│   ├── content.js               # Ticker detection on pages
│   ├── floatingWidget.js        # Floating compliance badge
│   ├── floatingWidget.css       # Widget styles
│   ├── popup.html               # Extension popup UI
│   └── popup.js                 # Popup interaction logic
│
└── README.md
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Google Chrome browser
- Node.js (optional, for development)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the server:
   ```bash
   uvicorn app:app --reload --port 8000
   ```

5. Verify it's running by visiting: http://localhost:8000

### Chrome Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`

2. Enable **Developer mode** (toggle in top-right corner)

3. Click **Load unpacked**

4. Select the `extension/` folder

5. The extension icon should appear in your toolbar

## 📖 Usage

### Hover Detection

1. Navigate to any webpage with stock ticker mentions (e.g., news articles, Reddit, Twitter)
2. Hover over a ticker symbol (e.g., `AAPL`, `TSLA`, `MSFT`)
3. A floating widget will appear showing the compliance status:
   - ✅ **Halal** - Compliant with Shariah standards
   - ❌ **Not Halal** - Non-compliant
   - ⚠️ **Doubtful** - Requires further review

### Manual Check

1. Click the extension icon in Chrome toolbar
2. Enter a ticker symbol (e.g., `AAPL`)
3. Click **Check** to see detailed compliance breakdown

## 🔌 API Reference

### Check Compliance

```
GET /check?ticker=AAPL
```

**Response:**
```json
{
  "ticker": "AAPL",
  "status": "not_compliant",
  "source": "AAOIFI",
  "breakdown": [
    {
      "rule": "Debt Ratio",
      "value": "42.0%",
      "limit": "< 30%",
      "passed": false,
      "reason": "Exceeds limit"
    },
    {
      "rule": "Cash Ratio",
      "value": "27.0%",
      "limit": "< 30%",
      "passed": true,
      "reason": null
    },
    {
      "rule": "Non-Halal Revenue",
      "value": "3.0%",
      "limit": "< 5%",
      "passed": true,
      "reason": null
    },
    {
      "rule": "Sector",
      "value": "Technology",
      "limit": "Allowed",
      "passed": true,
      "reason": null
    }
  ]
}
```

### Status Values

| Status | Description |
|--------|-------------|
| `compliant` | Stock passes all Shariah screening criteria |
| `not_compliant` | Stock fails one or more criteria |
| `doubtful` | Stock has questionable aspects requiring review |

## 🧪 AAOIFI Screening Rules

The AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions) screening uses these criteria:

| Rule | Threshold | Description |
|------|-----------|-------------|
| Debt Ratio | < 30% | Total Debt / Market Cap |
| Cash Ratio | < 30% | (Cash + Interest-bearing Securities) / Market Cap |
| Non-Halal Revenue | < 5% | Non-permissible income / Total Revenue |
| Business Sector | Allowed | Must not be in prohibited industries |

### Prohibited Sectors

- Alcohol
- Tobacco
- Gambling
- Adult Entertainment
- Pork Products
- Conventional Finance/Banking
- Weapons Manufacturing
- Conventional Insurance

## 🗺️ Roadmap

- [ ] **Real Scraper Implementations**: Connect to actual Zoya, Muslim Xchange, and Musaffa APIs
- [ ] **Live Financial Data**: Integrate Yahoo Finance or Alpha Vantage for real-time data
- [ ] **Watchlist Feature**: Save and track multiple tickers
- [ ] **Notifications**: Alert when compliance status changes
- [ ] **Portfolio Analysis**: Analyze entire portfolio for compliance
- [ ] **Mobile App**: React Native companion app
- [ ] **Historical Data**: Show compliance history over time
- [ ] **Scholar Opinions**: Include fatwa references for edge cases

## 🛠️ Development

### Backend Development

```bash
cd backend
uvicorn app:app --reload --port 8000
```

The `--reload` flag enables hot-reloading during development.

### Extension Development

After making changes to extension files:
1. Go to `chrome://extensions/`
2. Click the refresh icon on the extension card

### API Documentation

FastAPI auto-generates interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This tool is for informational purposes only and should not be considered financial or religious advice. Always consult with qualified Islamic scholars and financial advisors before making investment decisions.
