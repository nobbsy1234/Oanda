import requests
import time
from datetime import datetime

# Define API constants
API_URL = "https://api-fxtrade.oanda.com/v3"
API_KEY = "Your api key here"
ACCOUNT_ID = "your account id here."
INSTRUMENT_EURUSD = "EUR_USD"
INSTRUMENT_USDCAD = "USD_CAD"
TAKE_PROFIT_PIPS = 3

def place_trade(instrument, units, is_buy):
    try:
        ask_price = get_ask_price(instrument)
        if ask_price is None:
            print(f"Failed to retrieve ask price for {instrument}. Exiting...")
            return False

        take_profit_price = round(ask_price + TAKE_PROFIT_PIPS * 0.0001, 5)

        url = f"{API_URL}/accounts/{ACCOUNT_ID}/orders"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "order": {
                "instrument": instrument,
                "units": str(units),
                "type": "MARKET",
                "positionFill": "DEFAULT",
                "takeProfitOnFill": {
                    "price": str(take_profit_price)
                }
            }
        }
        if not is_buy:
            data["order"]["positionFill"] = "REDUCE_FIRST"

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() 
        print(f"{'Buy' if is_buy else 'Sell'} order for {instrument} placed successfully. Units: {units}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while placing the order: {e}")
        return False

def get_ask_price(instrument):
    try:
        url = f"{API_URL}/accounts/{ACCOUNT_ID}/pricing"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        params = {
            "instruments": instrument
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  
        data = response.json()
        if "prices" in data and data["prices"]:
            return float(data["prices"][0]["asks"][0]["price"])
        else:
            print(f"No ask price found in response for {instrument}.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while retrieving ask price: {e}")
        return None

def should_trade():
    # Get current time in AEST
    now = datetime.now()
    now_aest = now.strftime("%H%M")

    # Check if current time is between 06:00 and 09:00 AEST
    return "0600" > now_aest or now_aest > "0900"

def main():
    while True:
        if should_trade():
            place_trade(INSTRUMENT_EURUSD, 1, is_buy=True)
            time.sleep(10)  # Wait for 10 minutes before placing the next EUR/USD trade

            place_trade(INSTRUMENT_USDCAD, 1, is_buy=True)
            time.sleep(600)  # Wait for 10 minutes before placing the next USD/CAD trade
        else:
            print("Not trading between 06:00 AM AEST and 09:00 AM AEST.")
            time.sleep(600)  # Check every 10 minutes if trading should resume

if __name__ == "__main__":
    main()
