# CCXT websockets DB updater

A Python 3 command line program to subscribe cryptocurrency exchanges websockets and save order books in real time in a database.

This project is based on [CCXT lfern/websockets-multiple fork](https://github.com/lfern/ccxt/tree/feature/websockets-multiple).

To speed up installation, as the CCXT repository is huge and takes a long time to download, I created a repository containing just the transpiled files from lfern's branch: https://github.com/firepol/ccxt-websockets
When the branch will be forked in the [official CCXT project](https://github.com/ccxt/ccxt), this temporary branch won't be needed anymore.

Credits for the websockets implementations: **lfern** and his collaborators.

If you are looking for an alternative in Java, check my other similar project: [Cryptows](https://github.com/firepol/crypto-websockets).

## Installation

```
# Clone this repository
git clone https://github.com/firepol/ccxt-websockets-db-updater.git

# Enter the repository dir
cd ccxt-websockets-db-updater

# Create a `data` directory (needed to store exchange settings and websockets you want to subscribe to)
mkdir data

# Copy the sample settings.ini into data/
cp samples/settings.ini data/

# Create a python 3.6 virtual environment
virtualenv -p /usr/bin/python3.6 env

# Activate the python virtual environment
source ~/env/ccxtws/bin/activate

# Install all required dependencies
pip install -r requirements.txt

```

## Update

To get the latest updates from https://github.com/firepol/ccxt-websockets:

```
# Unintall the old version of CCXT
pip uninstall ccxt

# Get all missing dependencies (this will fetch the latest CCXT version linked in requirements.txt)
pip install -r requirements.txt
```

## Quick start

**Note**: If you are using Windows the python commands written in this document may not work for you. In that case just call the command prefixed with `python`, like this:

```
python script_name.py
```


Inside the repo, you can run this command to get an overview of all the command line parameters:

```
./ob_tester.py -h
```

Then test the BTC/USDT websocket connection to [binance](https://www.binance.com/?ref=15877893):

```
./ob_tester.py -e binance -s ETH/BTC --verbose
```

## Configuration

First of all, copy `samples/settings.ini` to `data/settings.ini`.

`[config]`: this is the main configuration section.

`db_url`: database connection string.

Examples:
- PostgreSQL: `postgres://postgres:postgres@localhost:5432/cryptows`
- SQLite: `sqlite:///cryptows.db`

`order_book_entries`: (by default: `1`) limit of order books to fetch (e.g. 5 means 5 bids and 5 asks).

Exchanges and pairs you want to fetch:in square brackets write the exchange name, in the following line insert a list of symbols, as follows:

```
[bitstamp]
symbols: ETH/BTC
         BTC/USD
         ETH/USD
```

You can comment (with ";" at the beginning of the line) sections and single lines, e.g.:

```
[bitstamp]
symbols: ETH/BTC
;         BTC/USD
         ETH/USD
```

Some exchanges (like cex.io) need to be authenticated via api key / secret. Add your api keys in the `data/exchange_api_keys.json` file (you find a template in the samples folder).

## Usage

The usage of the websocket database updater is quite straightforward:

```
./ob_updater.py
``` 

The program checks the exchanges configured in the `data/settings.ini` file and creates a websocket connection for each pair.

Add `--debug` to see when an order book update occurs.  
Add `--verbose` to see the order book update values.
Add `--reset_db` to delete all records in the `order_book` table before subscribing the websockets.

## Donations / support

**I won't ask donations, but I'm sharing a few referral links** for echanges and bots I tested and that I can recommend. Thank you for registering to these services using my links:

[coinbase](https://www.coinbase.com/join/596c62efa795880085a1a1a7) this is where I started. A must have exchange where you should NOT trade if you are a noob ;) Instead, after making your first deposit, trade via [Coinbase Pro](https://pro.coinbase.com) using a limit order: like that you will pay **0% fees** on the trade, which is quite awesome. Coinbase Pro is funded via coinbase accounts and needs a coinbase account to login.

[binance](https://www.binance.com/?ref=15877893) is maybe the most popular crypto exchange, if you don't have an account yet, register immediately, you don't even need to go through the KYC (know your customer) procedure to start trading here. Be sure to buy some BNB (binance coin) and adjust the settings to use BNB to pay less fees.

[cex.io](https://cex.io/r/0/up113994371/0/) despite the funny name and simple website design, this is a solid exchange which has a killer feature I like a lot, the ability to withdraw money on Visa and MasterCard credit cards.

[BitMEX](https://www.bitmex.com/register/CceysA) this is a famous cryptocurrency exchange where you can do margin trading up to 100x. You can double your portfolio or make huge gains with a few trades, or lose it all. Learn what is the liquidation price meaning and use a low leverage or no leverage at all to begin. If you use 10x leverage, you will make 10% profits on a 1% change. This can be very risky, so be sure (by watching bitmex & leverage tutorials etc.) to know what you are doing. I don't recommend using more than 2x leverage at the beginning (once you are experienced you can increase it).

[3commas.io](https://3commas.io/?c=tc69129) you don't need to apply for a monthly subscription, you can use it on the go, which means you'll pay a commission on your profits (you need to prepay this before using the bot, but the bot is free to try for 3 days, so you get an idea). Worth to give it a try.

[ARBITRAGING](https://www.arbitraging.co/platform/register/affiliate/02C6WRhI) website offers an interesting product called **aBOT**, designed for **long term investments** (if you want to try it just for 1-2 months and then take out all your investments, you can do that, but you will probably lose money). aBOT has a stop price, research what that means before investing.  
The minimum amount to invest is 250 USD (in ETH). If this is too much for you, don't try aBOT. Else it's quite a good platform for passive income: invest and forget about it, you can automatically re-invest 0, 25%, 50%, 75% or 100% of the daily profits (in ARB) or keep the ARB tokens for later.  
What I do is to keep the ARB tokens and I trade them weekly against ETH.  
What I suggest to get started is to deposit some ETH, trade them to get some ARB tokens, then trade the ARBs for ETH (try to sell always at a higher price), like this you may actually make some profits with some test trades, as the spread between buy & sell often can be 5% or more. Then do a test withdrawal. Like this you get a feeling how it woks to get the money out of the platform.

**Disclaimer**: I'm no financial advisor, do your own research before using any of the services linked above, or using my tools. I won't be held responsible for any of your losses.

## License

[MIT License](LICENSE)
