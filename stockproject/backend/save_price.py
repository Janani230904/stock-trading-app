import yfinance as yf

# 1. Ask the user for a stock
symbol = input("Enter a stock symbol (e.g., TSLA, NVDA, BTC-USD): ").upper()

try:
    # 2. Fetch the data
    print(f"Searching for {symbol}...")
    stock = yf.Ticker(symbol)
    
    # Get the price and the 'longName' (Company Name)
    price = stock.fast_info['last_price']
    company_name = stock.info.get('longName', symbol)

    print("-" * 30)
    print(f"COMPANY: {company_name}")
    print(f"LIVE PRICE: ${price:.2f}")
    print("-" * 30)

    # 3. Quick Logic Check
    balance = 1000.00  # Let's pretend you have $1000 in your database
    if price > balance:
        print(f"❌ You cannot afford this. You need ${price - balance:.2f} more.")
    else:
        print(f"✅ You can afford this! Remaining balance would be: ${balance - price:.2f}")

except Exception:
    print("❌ Invalid symbol. Please try again (e.g., AAPL).")