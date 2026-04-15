import os
import time
import hmac
import hashlib
import logging
import requests
import argparse
from urllib.parse import urlencode

BASE_URL = "https://testnet.binancefuture.com"
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Logger setup
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def get_server_time():
    url = BASE_URL + "/fapi/v1/time"
    return requests.get(url).json()['serverTime']
def sign(params):
    query_string = urlencode(params)
    signature = hmac.new(
        API_SECRET.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def place_order(symbol, side, order_type, quantity, price=None):
    url = BASE_URL + "/fapi/v1/order"

    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
        "timestamp": get_server_time()
    }

    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"

    params["signature"] = sign(params)

    headers = {"X-MBX-APIKEY": API_KEY}

    response = requests.post(url, headers=headers, params=params)

    logging.info(f"Request: {params}")
    logging.info(f"Response: {response.text}")

    return response.json()

def main():
    print("=== Binance Futures CLI ===")

    print("\nSelect Order Type:")
    print("1. MARKET")
    print("2. LIMIT")

    choice = input("Enter choice (1/2): ")

    symbol = input("Enter Symbol (e.g., BTCUSDT): ").upper()
    side = input("Enter Side (BUY/SELL): ").upper()
    quantity = float(input("Enter Quantity: "))

    order_type = "MARKET"
    price = None

    if choice == "2":
        order_type = "LIMIT"
        price = float(input("Enter Price: "))

    print("\n=== ORDER REQUEST ===")
    print(symbol, side, order_type, quantity, price)

    try:
        response = place_order(symbol, side, order_type, quantity, price)

        print("\n=== ORDER RESPONSE ===")
        print(f"Order ID: {response.get('orderId')}")
        print(f"Status: {response.get('status')}")
        print(f"Executed Qty: {response.get('executedQty')}")
        print(f"Avg Price: {response.get('avgPrice')}")

        print("\nSUCCESS ✅")

    except Exception as e:
        print("\nERROR ❌:", str(e))
if __name__ == "__main__":
    main()