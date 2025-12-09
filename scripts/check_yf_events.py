
import yfinance as yf
import json

def check_events(ticker_symbol):
    print(f"Checking {ticker_symbol}...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        
        print("\n--- Calendar ---")
        try:
            print(ticker.calendar)
        except Exception as e:
            print(f"Error fetching calendar: {e}")

        print("\n--- News ---")
        try:
            # News is usually a list of dicts
            news = ticker.news
            if news:
                print(f"Found {len(news)} news items.")
                print(news[0])
            else:
                print("No news found")
        except Exception as e:
            print(f"Error fetching news: {e}")

        print("\n--- Actions (Dividends/Splits) ---")
        try:
            # Actions is a DataFrame
            actions = ticker.actions
            if not actions.empty:
                print(f"Found {len(actions)} actions.")
                print(actions.tail(3))
            else:
                print("No actions found")
        except Exception as e:
            print(f"Error fetching actions: {e}")

    except Exception as e:
        print(f"Error creating ticker: {e}")

if __name__ == "__main__":
    # Check an index (NIFTY) and a stock (TCS)
    check_events("^NSEI")
    check_events("TCS.NS")
