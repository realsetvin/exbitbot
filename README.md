Here’s an updated version of the README with a note indicating that the project is experimental and may require updates or fixes:

---

# ExbitBot - Automated Spread Trading Bot for Exbitron

**ExbitBot** is an experimental, automated trading bot designed to perform spread trading on the **Exbitron** exchange. This bot fetches the order book for a specified market, calculates a center price, and places buy and sell orders around this price to create a spread. It handles order placement, cancellation of unfilled orders, and includes robust error handling to ensure smooth operation.

> **Note**: This project is experimental and may require updates or fixes. Please use with caution and keep in mind that it is still under active development.

## Features

- **Spread Trading**: Automatically places buy and sell orders based on the center price of the market.
- **Dynamic Order Placement**: Orders are placed starting from the market minimum and progressively adjusted according to market conditions.
- **Error Handling**: Includes error handling for common issues such as rate limits (429) and conflicts (409).
- **Order Tracking**: Provides visibility into the open orders and handles the cancellation of unfilled orders.
- **Real-Time Updates**: Fetches real-time market data and continuously resubmits orders based on updated prices.

## Requirements

- Ubuntu VPS or Virtual Machine (running Ubuntu 18.04 or higher)
- Python 3.x
- `requests` library (install via `pip install requests`)
- A valid **Exbitron API Key**

## Installation Instructions

Follow these steps to install and run **ExbitBot** on your Ubuntu VPS or virtual machine.

### 1. Connect to Your Ubuntu VPS

First, connect to your Ubuntu VPS or Virtual Machine using SSH.

```bash
ssh username@your-vps-ip
```

Replace `username` and `your-vps-ip` with your actual SSH username and VPS IP address.

### 2. Update System Packages

Ensure your system packages are up to date by running the following commands:

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Install Python 3

ExbitBot requires **Python 3**. If you don’t have it installed, run the following command to install Python 3:

```bash
sudo apt install python3 python3-pip -y
```

### 4. Install Required Python Libraries

Install the **requests** library, which is required for making HTTP requests:

```bash
pip3 install requests
```

### 5. Clone the Repository

Clone the **ExbitBot** repository from GitHub:

```bash
git clone https://github.com/yourusername/exbitbot.git
```

Replace `yourusername` with your actual GitHub username.

Navigate to the cloned repository:

```bash
cd exbitbot
```

### 6. Set Up Your API Key

Open the `exbitbot.py` script with a text editor (e.g., `nano`):

```bash
nano exbitbot.py
```

In the script, find the line where the `API_KEY` is defined:

```python
API_KEY = 'YOUR_API_KEY'  # Replace this with your actual API key
```

Replace `'YOUR_API_KEY'` with your actual **Exbitron API key**. Make sure to keep the API key secure.

### 7. Configure Trading Settings

In the same `exbitbot.py` script, you can adjust the following settings to match your trading preferences:

- **Market Pair**: Set the trading pair you want to trade (e.g., `XMR-USDT`).
- **Order Parameters**: Adjust spread levels, minimum order volume, and other configurations based on your preferences.

### 8. Run the Bot

To start the bot, simply run the following command:

```bash
python3 exbitbot.py
```

The bot will prompt you to enter your **Exbitron API key** and display your balances. It will then allow you to choose between starting spread trading, tracking open orders, or exiting the application.

### 9. Monitor the Bot

Once the bot is running, it will display logs of the orders placed, errors encountered, and the current status of the trading process.

The bot will automatically fetch the order book, calculate the center price, place orders, and adjust them based on market conditions.

To stop the bot, press `Ctrl + C`.

### 10. Optional: Run as a Background Process

If you want to run the bot as a background process on your VPS or Virtual Machine, you can use **screen** or **tmux**.

To use **screen**:

1. Install screen (if not already installed):

   ```bash
   sudo apt install screen -y
   ```

2. Start a new screen session:

   ```bash
   screen -S exbitbot
   ```

3. Run the bot in the screen session:

   ```bash
   python3 exbitbot.py
   ```

4. Detach from the session by pressing `Ctrl + A` followed by `D`.

To reattach to the session later, run:

```bash
screen -r exbitbot
```

### Troubleshooting

- **API Errors**: If you encounter errors like **409 Conflict** or **429 Too Many Requests**, the bot handles them gracefully by retrying the request or skipping conflicting orders.
- **Order Not Placed**: Ensure your account has sufficient funds for the trades you're attempting to place.
- **Rate Limiting**: The bot includes delay handling for API rate limits, but if the rate is exceeded too quickly, consider lowering the frequency of orders or increasing the delay between submissions.

### 11. Additional Notes

- **API Rate Limits**: Ensure you don't hit the rate limits for the Exbitron API. The bot has built-in retries for 429 errors, but you should always be mindful of the Exbitron rate limits.
- **Security**: Keep your **API key** secure. If you plan to deploy this bot on a shared VPS, make sure the API key is never exposed.

## License

This project is licensed under the MIT License 

---
