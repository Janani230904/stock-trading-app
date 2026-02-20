import yfinance as yf
import mysql.connector

# 1. Connect to your MySQL Database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD",  # Change this to your password!
    database="stock_simulator"
)
cursor = db.cursor()

# 2. Get User Balance (Assuming user with ID 1 exists)
cursor.execute("SELECT balance FROM players WHERE id = 1")
result = cursor.fetchone()
current_balance = result[0] if result else 0.0

# 3. Ask for Stock Input
symbol = input("Enter Stock Symbol (e.g., TSLA, NVDA): ").upper()
print(f"Checking price for {symbol}...")

try:
    stock = yf.Ticker(symbol)
    price = stock.fast_info['last_price']
    
    print("-" * 30)
    print(f"SYMBOL: {symbol}")
    print(f"PRICE:  ${price:.2f}")
    print(f"YOUR BALANCE: ${current_balance:.2f}")
    print("-" * 30)

    if current_balance >= price:
        print("✅ You have enough money to buy 1 share!")
    else:
        print(f"❌ Low Balance. You need ${price - current_balance:.2f} more.")

except Exception:
    print(" Could not find that stock. Check the spelling!")

cursor.close()
db.close()