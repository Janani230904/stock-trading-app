from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import mysql.connector

app = Flask(__name__)
# CORS allows your index.html to communicate with this Python server
CORS(app)

# Database Connection Helper
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Janani@23", 
        database="stock_simulator"
    )

@app.route('/get_dashboard', methods=['GET'])
def get_dashboard():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # 1. Fetch User Balance
        cursor.execute("SELECT balance FROM users WHERE id = 1")
        balance_row = cursor.fetchone()
        balance = balance_row['balance'] if balance_row else 0
        
        # 2. Fetch Portfolio (Individual trades to calculate P&L)
        cursor.execute("SELECT id, symbol, quantity, buy_price FROM portfolio WHERE user_id = 1")
        portfolio = cursor.fetchall()
        
        return jsonify({
            "balance": round(float(balance), 2),
            "portfolio": portfolio
        })
    finally:
        db.close()

@app.route('/get_price', methods=['GET'])
def get_price():
    symbol = request.args.get('symbol').upper()
    try:
        ticker = yf.Ticker(symbol)
        # Fast info gives us the real-time last traded price
        price = ticker.fast_info['last_price']
        return jsonify({"symbol": symbol, "price": round(price, 2)})
    except Exception as e:
        return jsonify({"error": "Stock not found"}), 404

@app.route('/top_movers', methods=['GET'])
def top_movers():
    # A mix of Indian and Global stocks for the sidebar
    symbols = ["TATASTEEL.NS", "RELIANCE.NS", "INFY.NS", "AAPL", "TSLA", "GAIL.NS", "BTC-USD"]
    movers = []
    for s in symbols:
        try:
            t = yf.Ticker(s)
            hist = t.history(period="2d")
            if len(hist) < 2: continue
            # Calculate % change from yesterday's close
            prev_close = hist['Close'].iloc[-2]
            current_close = hist['Close'].iloc[-1]
            change = ((current_close - prev_close) / prev_close) * 100
            movers.append({
                "symbol": s, 
                "price": round(current_close, 2), 
                "change": round(change, 2)
            })
        except: continue
    # Sort by highest absolute change
    return jsonify(sorted(movers, key=lambda x: abs(x['change']), reverse=True)[:4])

@app.route('/add_funds', methods=['POST'])
def add_funds():
    data = request.json
    amount = float(data.get('amount', 0))
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE users SET balance = balance + %s WHERE id = 1", (amount,))
        db.commit()
        cursor.execute("SELECT balance FROM users WHERE id = 1")
        new_balance = cursor.fetchone()[0]
        return jsonify({"success": True, "new_balance": round(float(new_balance), 2)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        db.close()

@app.route('/buy_stock', methods=['POST'])
def buy_stock():
    data = request.json
    symbol = data['symbol']
    qty = int(data['quantity'])
    price = float(data['price'])
    total_cost = qty * price

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT balance FROM users WHERE id = 1")
        balance = float(cursor.fetchone()['balance'])
        
        if balance >= total_cost:
            # Deduct from balance
            cursor.execute("UPDATE users SET balance = balance - %s WHERE id = 1", (total_cost,))
            # Add to portfolio
            cursor.execute("INSERT INTO portfolio (user_id, symbol, quantity, buy_price) VALUES (1, %s, %s, %s)", 
                           (symbol, qty, price))
            db.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Insufficient Balance"})
    finally:
        db.close()

@app.route('/sell_stock', methods=['POST'])
def sell_stock():
    data = request.json
    trade_id = data['id']
    current_price = float(data['current_price'])
    qty = int(data['quantity'])
    total_return = qty * current_price

    db = get_db_connection()
    cursor = db.cursor()
    try:
        # Remove the specific trade
        cursor.execute("DELETE FROM portfolio WHERE id = %s", (trade_id,))
        # Add the money back to the wallet
        cursor.execute("UPDATE users SET balance = balance + %s WHERE id = 1", (total_return,))
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        db.close()

if __name__ == '__main__':
    # Running on port 5000 is the standard for Flask
    app.run(debug=True, port=5000)