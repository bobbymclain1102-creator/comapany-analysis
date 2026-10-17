# Company Analysis Masterclass App

Interactive Streamlit dashboard that takes a stock ticker and generates a structured analysis covering:

- Business overview
- Financial statements (income, balance sheet, cash flow)
- Key ratios and returns
- Charts and trends
- Valuation metrics
- Analyst recommendations and institutional holders
- Links to sources (SEC, Yahoo Finance, community sentiment)

## How to Run

1. Ensure you have Python 3.8+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run company_analysis_app.py
   ```
4. Open the URL shown in the terminal (usually http://localhost:8501).

## Data Sources
- Primary: Yahoo Finance via the `yfinance` library.
- Links provided to SEC EDGAR for official filings.
- Analyst and institutional data from public sources.

**Disclaimer:** Educational tool only. Not investment advice. Verify all data with official sources. Markets involve risk of loss.

Built to implement the structured company analysis framework from the masterclass.
