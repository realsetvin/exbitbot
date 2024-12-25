import os
import requests
import json
import time

# API Setup
API_KEY = 'YOUR_API_KEY'  # Replace this with your actual API key
BASE_URL = "https://api.exbitron.digital/api/v1"
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Logging Setup
LOG_FILE = "exbitbot.log"

# Utility function to log messages to a file and print to console
def log_message(message):
    """Logs a message to both a file and the console."""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{time.ctime()}: {message}\n")
    print(message)

# Helper Functions

def make_request(endpoint, method="GET", data=None, params=None):
    """Handles API requests to Exbitron with error handling."""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, headers=HEADERS, json=data, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_message(f"API Error: {e}")
        return None

def validate_input(prompt, expected_type, min_value=None, max_value=None):
    """Ensures user input is valid and within specified bounds."""
    while True:
        try:
            value = expected_type(input(prompt).strip())
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}. Try again.")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}. Try again.")
                continue
            return value
        except ValueError:
            print(f"Invalid input. Please enter a {expected_type.__name__}.")

def get_balance():
    """Fetches the user's account balances."""
    balances = make_request("/balances", params={"zero": False})
    if balances and "data" in balances:
        try:
            currencies = balances["data"].get("user", {}).get("currencies", [])
            formatted = {
                cur["id"]: float(cur["balance"])
                for cur in currencies
                if cur.get("enabled", False)
            }
            if not formatted:
                log_message("No balances available. User has $0.")
                return {"USD": 0}
            return formatted
        except (KeyError, TypeError, ValueError) as e:
            log_message(f"Error parsing balances data: {e}")
    log_message("Unexpected response format for balances or no data returned.")
    return {"USD": 0}

def get_order_book(market):
    """Fetches the order book for a given market."""
    order_book = make_request(f"/orderbook/{market}")
    if order_book and "bids" in order_book and "asks" in order_book:
        return order_book
    log_message(f"Failed to fetch order book for {market}")
    return None

def display_order_book(order_book):
    """Display the order book in a human-readable format."""
    bids = order_book.get("bids", [])
    asks = order_book.get("asks", [])

    log_message(f"\n--- Order Book ---")
    log_message(f"Top Bids (Buy Orders):")
    for bid in bids[:5]:  # Display top 5 bids
        log_message(f"Price: {bid[0]} | Volume: {bid[1]}")
    
    log_message(f"\nTop Asks (Sell Orders):")
    for ask in asks[:5]:  # Display top 5 asks
        log_message(f"Price: {ask[0]} | Volume: {ask[1]}")
    
    log_message(f"-------------------\n")

def get_center_price(order_book):
    """Calculates the center price from the order book."""
    bids = order_book.get("bids", [])
    asks = order_book.get("asks", [])
    
    if bids and asks:
        best_bid = float(bids[0][0])  # Highest buy price
        best_ask = float(asks[0][0])  # Lowest sell price
        
        # Calculate the center price as the average of best bid and ask
        center_price = (best_bid + best_ask) / 2  # Middle price
        return center_price
    
    log_message("Could not determine center price.")
    return None

def get_market_info(market):
    """Fetches market details such as minimum trade amount."""
    info = make_request(f"/trading/info/{market}")
    if info and "data" in info and "market" in info["data"]:
        return float(info["data"]["market"].get("trading_min_amount", 0))
    log_message(f"Failed to fetch market info for {market}")
    return None

def place_order(market, side, volume, price):
    """Places an order on Exbitron."""
    data = {
        "amount": volume,
        "market": market,
        "price": price,
        "side": side,  # "buy" or "sell"
        "type": "limit"  # Assuming limit order, can be changed to other types if necessary
    }

    url = f"{BASE_URL}/order"
    try:
        # Sending POST request
        response = requests.post(url, headers=HEADERS, data=json.dumps(data))
        response.raise_for_status()  # Check for errors

        # Check the response
        if response.status_code == 200:
            order_data = response.json()
            log_message(f"Order placed successfully: {order_data}")
            return order_data  # Return order details for tracking
        else:
            log_message(f"Error placing order: {response.status_code} - {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        log_message(f"API Error: {e}")
        time.sleep(5)  # Wait before retrying in case of failure
        return None

def create_spread(market, center_price, min_volume, levels):
    """Creates buy and sell orders around the center price, starting from the minimum price."""
    spread_orders = []
    market_min_price = get_market_info(market)

    if not market_min_price:
        log_message(f"Failed to fetch market minimum price for {market}.")
        return spread_orders

    log_message(f"Starting spread orders from market minimum price: {market_min_price}")

    for i in range(1, levels + 1):
        spread = 0.00125 * i  # Spread increment (0.125% per level)
        volume_multiplier = 1 + (0.125 * i)  # Volume increases by 12.5% per level

        # Start the first order from the market minimum
        buy_price = round(market_min_price * (1 - spread), 8)  # Ensure no conflict
        buy_volume = round(min_volume * volume_multiplier, 8)
        spread_orders.append((market, "buy", buy_volume, buy_price))

        # Sell order around the center price
        sell_price = round(center_price * (1 + spread), 8)
        sell_volume = round(min_volume * volume_multiplier, 8)
        spread_orders.append((market, "sell", sell_volume, sell_price))

    return spread_orders

def place_spread_orders(spread_orders):
    """Places all orders in the spread."""
    for order in spread_orders:
        market, side, volume, price = order
        order_data = place_order(market, side, volume, price)
        if order_data:
            log_message(f"Successfully placed order: {order_data}")
        else:
            log_message(f"Failed to place order: {order}")

def cancel_unfilled_orders(market):
    """Cancel only unfilled orders, keeping partially filled orders active."""
    open_orders = make_request(f"/order/market/{market}", params={"status": "open"})
    if open_orders and isinstance(open_orders, list):
        for order in open_orders:
            if order.get("status") != "partially_filled":  # Skip partially filled orders
                cancel_order(order.get("id", ""))
    else:
        log_message("No open orders to cancel or failed to fetch order data.")

def track_orders(market):
    """Logs all currently open orders."""
    orders = make_request(f"/order/market/{market}", params={"status": "open"})
    if orders and isinstance(orders, list):
        log_message(f"Open Orders: {orders}")
    else:
        log_message("No open orders or failed to fetch order status.")

# Trading Logic

def resubmit_orders(market, min_volume, levels):
    """Resubmit orders every 5 minutes based on the latest mid-price."""
    while True:
        log_message("Resubmitting orders based on the latest mid-price...")

        # Fetch current center price from order book
        order_book = get_order_book(market)
        if not order_book:
            log_message(f"Unable to fetch order book for {market}. Skipping resubmission.")
            time.sleep(300)  # Wait 5 minutes and retry
            continue

        display_order_book(order_book)  # Show the order book

        center_price = get_center_price(order_book)
        if not center_price:
            log_message(f"Unable to fetch center price for {market}. Skipping resubmission.")
            time.sleep(300)  # Wait 5 minutes and retry
            continue

        # Cancel only unfilled orders
        log_message("Canceling unfilled orders, keeping partially filled orders active...")
        cancel_unfilled_orders(market)

        # Create and place new orders
        spread_orders = create_spread(market, center_price, min_volume, levels)
        place_spread_orders(spread_orders)

        log_message("Orders resubmitted. Waiting 5 minutes for next cycle.")
        time.sleep(300)  # Wait 5 minutes before resubmitting

def calculate_pnl(trade_history):
    """Calculates profit and loss based on trade history."""
    pnl = 0.0
    for trade in trade_history or []:
        if trade.get("side") == "buy":
            pnl -= float(trade.get("price", 0)) * float(trade.get("volume", 0))
        elif trade.get("side") == "sell":
            pnl += float(trade.get("price", 0)) * float(trade.get("volume", 0))
    return pnl

# Command-Line Interface

def exbitbot_cli():
    """Main command-line interface for the bot."""
    global API_KEY, HEADERS

    print("Welcome to ExbitBot!")
    API_KEY = input("Please enter your private API key: ").strip()
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Verify API Key and Fetch Balances
    balance = get_balance()
    if not balance:
        print("Invalid API key or unable to fetch balances. Exiting...")
        return

    print("Your current balances:")
    for currency, amount in balance.items():
        print(f"{currency}: {amount}")

    while True:
        print("\nMenu:")
        print("1. Start Spread Trading")
        print("2. Track Open Orders")
        print("3. Exit")
        choice = validate_input("Enter your choice: ", int, 1, 3)

        if choice == 1:
            market = input("Enter the trading pair (e.g., xmr_usdt): ").strip()
            order_book = get_order_book(market)
            if not order_book:
                print(f"Failed to fetch order book for {market}. Try again.")
                continue

            display_order_book(order_book)  # Show the order book

            center_price = get_center_price(order_book)
            if not center_price:
                print(f"Failed to fetch center price for {market}. Try again.")
                continue

            min_volume = get_market_info(market)
            if not min_volume:
                print(f"Failed to fetch minimum trade volume for {market}. Try again.")
                continue

            levels = validate_input("Enter the number of levels (e.g., 10): ", int, 1, 50)
            print(f"Starting spread trading for {market}...")
            try:
                resubmit_orders(market, min_volume, levels)
            except KeyboardInterrupt:
                print("\nStopped spread trading. Returning to menu.")

        elif choice == 2:
            market = input("Enter the trading pair to track (e.g., xmr_usdt): ").strip()
            print(f"Tracking open orders for {market}...")
            track_orders(market)

        elif choice == 3:
            print("Exiting ExbitBot. Goodbye!")
            break

if __name__ == "__main__":
    exbitbot_cli()
