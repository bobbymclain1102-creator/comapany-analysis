import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Company Analysis Masterclass App", layout="wide", page_icon="📊")

st.title("📊 Company & Financial Analysis Masterclass Dashboard")
st.markdown("""
Enter a stock ticker to get a structured analysis covering business overview, financial statements, key ratios, valuation, analyst views, institutional ownership, and more.
**This is for educational purposes only — not investment advice.**
""")

ticker_input = st.text_input("Enter Ticker Symbol (e.g., AAPL, MSFT, TSLA):", "AAPL").upper().strip()

if ticker_input:
    with st.spinner(f"Fetching data for {ticker_input}..."):
        try:
            ticker = yf.Ticker(ticker_input)
            info = ticker.info
            if not info or 'longName' not in info:
                st.error("Could not find data for this ticker. Please check the symbol.")
                st.stop()

            # Basic info
            long_name = info.get('longName', ticker_input)
            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')
            website = info.get('website', 'N/A')
            summary = info.get('longBusinessSummary', 'No summary available.')

            st.header(f"{long_name} ({ticker_input})")
            col1, col2, col3 = st.columns(3)
            col1.metric("Sector", sector)
            col2.metric("Industry", industry)
            col3.metric("Website", website if website != 'N/A' else "—")

            # Tabs for categories
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "1. Business Overview", 
                "2. Financial Statements", 
                "3. Key Ratios & Returns", 
                "4. Charts & Trends", 
                "5. Valuation", 
                "6. Analysts & Institutions", 
                "7. Sources & Notes"
            ])

            with tab1:
                st.subheader("Business Description")
                st.write(summary)
                st.subheader("Key Stats")
                metrics = {
                    "Market Cap": info.get('marketCap'),
                    "Enterprise Value": info.get('enterpriseValue'),
                    "Employees": info.get('fullTimeEmployees'),
                    "Beta": info.get('beta'),
                    "52-Week High": info.get('fiftyTwoWeekHigh'),
                    "52-Week Low": info.get('fiftyTwoWeekLow'),
                }
                for k, v in metrics.items():
                    if v:
                        if isinstance(v, (int, float)) and v > 1e9:
                            st.write(f"**{k}:** ${v/1e9:.2f}B")
                        else:
                            st.write(f"**{k}:** {v}")

            with tab2:
                st.subheader("Income Statement (Annual)")
                try:
                    income = ticker.financials
                    if not income.empty:
                        st.dataframe(income.T.head(5), use_container_width=True)
                    else:
                        st.info("Income statement not available.")
                except:
                    st.info("Could not load income statement.")

                st.subheader("Balance Sheet (Annual)")
                try:
                    balance = ticker.balance_sheet
                    if not balance.empty:
                        st.dataframe(balance.T.head(5), use_container_width=True)
                except:
                    st.info("Could not load balance sheet.")

                st.subheader("Cash Flow Statement (Annual)")
                try:
                    cashflow = ticker.cashflow
                    if not cashflow.empty:
                        st.dataframe(cashflow.T.head(5), use_container_width=True)
                except:
                    st.info("Could not load cash flow.")

            with tab3:
                st.subheader("Key Profitability & Return Metrics")
                # Calculate some ratios if possible
                try:
                    # Trailing metrics from info
                    pe = info.get('trailingPE')
                    forward_pe = info.get('forwardPE')
                    pb = info.get('priceToBook')
                    ps = info.get('priceToSalesTrailing12Months')
                    ev_ebitda = info.get('enterpriseToEbitda')
                    profit_margin = info.get('profitMargins')
                    op_margin = info.get('operatingMargins')
                    gross_margin = info.get('grossMargins')
                    roe = info.get('returnOnEquity')
                    roa = info.get('returnOnAssets')

                    ratio_data = {
                        "Trailing P/E": pe,
                        "Forward P/E": forward_pe,
                        "P/B": pb,
                        "P/S": ps,
                        "EV/EBITDA": ev_ebitda,
                        "Gross Margin": f"{gross_margin*100:.1f}%" if gross_margin else None,
                        "Operating Margin": f"{op_margin*100:.1f}%" if op_margin else None,
                        "Net Profit Margin": f"{profit_margin*100:.1f}%" if profit_margin else None,
                        "ROE": f"{roe*100:.1f}%" if roe else None,
                        "ROA": f"{roa*100:.1f}%" if roa else None,
                    }
                    ratio_df = pd.DataFrame(list(ratio_data.items()), columns=["Metric", "Value"])
                    st.dataframe(ratio_df, use_container_width=True, hide_index=True)

                    st.markdown("**Interpretation tips:** Compare margins and returns to industry peers and historical trends. High and stable ROE/margins often indicate a quality business. ROIC (not always directly available) > WACC signals value creation.")
                except Exception as e:
                    st.warning(f"Some ratios unavailable: {e}")

            with tab4:
                st.subheader("Price History (1 Year)")
                hist = ticker.history(period="1y")
                if not hist.empty:
                    fig = px.line(hist, x=hist.index, y="Close", title=f"{ticker_input} Price History")
                    st.plotly_chart(fig, use_container_width=True)

                # Revenue trend if available
                st.subheader("Revenue Trend (from financials)")
                try:
                    if not income.empty and 'Total Revenue' in income.index:
                        rev = income.loc['Total Revenue'].dropna().sort_index()
                        fig2 = px.bar(x=rev.index.strftime('%Y'), y=rev.values/1e9, labels={'x':'Year', 'y':'Revenue ($B)'}, title="Annual Revenue")
                        st.plotly_chart(fig2, use_container_width=True)
                except:
                    st.info("Revenue chart not available.")

            with tab5:
                st.subheader("Valuation Snapshot")
                val_metrics = {
                    "Trailing P/E": info.get('trailingPE'),
                    "Forward P/E": info.get('forwardPE'),
                    "PEG Ratio": info.get('pegRatio'),
                    "Price to Book": info.get('priceToBook'),
                    "Enterprise to Revenue": info.get('enterpriseToRevenue'),
                    "Enterprise to EBITDA": info.get('enterpriseToEbitda'),
                    "Dividend Yield": info.get('dividendYield'),
                }
                st.json({k: v for k, v in val_metrics.items() if v is not None})
                st.markdown("""
                **Notes on Valuation:**
                - Relative valuation (multiples) should be compared to peers and own history.
                - For intrinsic value, consider building a DCF using projected free cash flows discounted at WACC.
                - Always apply a margin of safety.
                """)

            with tab6:
                st.subheader("Analyst Recommendations")
                try:
                    recs = ticker.recommendations
                    if recs is not None and not recs.empty:
                        st.dataframe(recs.tail(10), use_container_width=True)
                    else:
                        st.info("No recent recommendations data.")
                except:
                    st.info("Recommendations not available.")

                st.subheader("Analyst Price Targets")
                try:
                    targets = ticker.analyst_price_targets
                    if targets:
                        st.write(targets)
                except:
                    st.info("Price targets not available.")

                st.subheader("Major Holders / Institutional Ownership")
                try:
                    inst = ticker.institutional_holders
                    if inst is not None and not inst.empty:
                        st.dataframe(inst.head(10), use_container_width=True)
                    major = ticker.major_holders
                    if major is not None:
                        st.write("Major Holders Summary:")
                        st.dataframe(major)
                except:
                    st.info("Holders data not available.")

                st.subheader("Retail Investor Sentiment (Proxies & Links)")
                st.markdown(f"""
                Direct real-time retail sentiment requires specialized feeds. Here are useful links:
                - [Yahoo Finance Community](https://finance.yahoo.com/quote/{ticker_input}/community)
                - [Reddit Search: {ticker_input}](https://www.reddit.com/search/?q={ticker_input}&sort=new)
                - [StockTwits](https://stocktwits.com/symbol/{ticker_input})
                - [Seeking Alpha](https://seekingalpha.com/symbol/{ticker_input})
                
                **Note:** Retail sentiment can be noisy. Cross-reference with fundamentals.
                """)

            with tab7:
                st.subheader("Sources & Further Reading")
                st.markdown(f"""
                - **SEC Filings (10-K, 10-Q):** [SEC EDGAR Search for {ticker_input}](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker_input}&type=&dateb=&owner=include&count=10)
                - **Company Investor Relations:** Check the website linked above or search "{long_name} investor relations"
                - **Yahoo Finance:** [Full page for {ticker_input}](https://finance.yahoo.com/quote/{ticker_input})
                - **As of:** {datetime.now().strftime('%Y-%m-%d')}
                
                **Masterclass Reminder:**
                1. Understand the business and moat first.
                2. Analyze trends in financials and cash flow quality.
                3. Check ROIC vs. cost of capital, margins stability.
                4. Look for red flags (earnings vs. cash divergence, rising receivables).
                5. Value with margin of safety.
                6. Read primary sources (filings) yourself.
                
                Data sourced primarily from Yahoo Finance via yfinance. Always verify with official filings.
                """)

        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.info("Try a well-known ticker like AAPL, MSFT, or GOOGL. Some private or foreign tickers may have limited data.")

st.sidebar.markdown("""
### How to Use
1. Enter a ticker.
2. Explore the tabs matching the analysis framework.
3. Cross-check with official SEC filings.
4. This app computes and visualizes public data — deepen it with your own qualitative research.
""")
