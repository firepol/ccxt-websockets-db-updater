# CCXT websockets DB updater

A Python 3 command line program to subscribe cryptocurrency exchanges websockets and save order books in real time in a database.

[![YouTube Demo](https://img.youtube.com/vi/0UIvIBUiqQQ/0.jpg)](https://www.youtube.com/watch?v=0UIvIBUiqQQ)

This project is based on [CCXT lfern/websockets-multiple fork](https://github.com/lfern/ccxt/tree/feature/websockets-multiple).

To speed up installation, as the CCXT repository is huge and takes a long time to download, I created a repository containing just the transpiled files from lfern's branch: https://github.com/firepol/ccxt-websockets
When the branch will be forked in the [official CCXT project](https://github.com/ccxt/ccxt), this temporary branch won't be needed anymore.

**Note:** in the `requirements.txt` file, in the 1st line you see a dependency to the `ccxt-websockets` repository, which could not be up to date. In case you want to update it yourself, you have to
1. fork the `ccxt-websockets` repository
1. clone lfern's fork
1. checkout lfern's `websockets-multiple` branch
1. build lfern's `websockets-multiple` branch as follows (if you prefer `npm` than `yarn`, adjust the commands accordingly):
    ```
    yarn
    yarn export-exchanges
    yarn transpile
    ```
1. overwrite the `python` folder of the `ccxt-websockets` repository with the one you just updated; do the same with the `package.json` file
1. commit and push (you must add the remote pointing to your own fork and push there)
1. change the 1st line of the `requirements.txt` to point to your fork of the `ccxt-websockets` repository
1. `pip uninstall ccxt`
1. `pip install -r requirements.txt`

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

## License

[MIT License](LICENSE)
