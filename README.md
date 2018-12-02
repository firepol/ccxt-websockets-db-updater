# CCXT websockets DB updater

A Python 3 command line program to subscribe cryptocurrency exchanges websockets and save order books in real time in a database.

This project is based on [CCXT lfern/websockets-multiple fork](https://github.com/lfern/ccxt/tree/feature/websockets-multiple).  
Credits for the websockets implementations: **lfern** and his collaborators.

If you are looking for a java alternative, check my other similar project: [Cryptows](https://github.com/firepol/crypto-websockets).

The database saving part is work in progress, but to get an idea how it will work, check _Cryptows_. I will use SQLAlchemy ORM in order to support several databases.

## Installation

Clone this repository:

```
git clone https://github.com/firepol/ccxt-websockets-db-updater.git
```

cd in the repository and create a folder called `data`, this is needed to store exchange settings and websockets you want to subscribe to.

```
cd ccxt-websockets-db-updater
mkdir data
```

Create a virtual environment (I called mine _ccxtws_) for this project (e.g. I create all my environments in `~/env`:  

```
virtualenv -p /usr/bin/python3.6 ~/env/ccxtws
```

Then run:  

```
source ~/env/ccxtws/bin/activate
```

## Quick start

Inside the repo, you can run this command to get an overview of all the command line parameters:

```
./ob_tester.py -h
```

Then test the BTC/USDT websocket connection to [binance](https://www.binance.com/?ref=15877893):

```
./ob_tester.py -e binance -s ETH/BTC --verbose
```

## Database updater usage

**This is still work in progress: for now nothing is saved into a database, yet.**

To configure the exchanges and pairs you want to fetch, copy the `samples/settings_ws.json` file to the `data` folder and edit it.

Some exchanges (like cex.io) need to be authenticated via api key / secret. To configure your api keys, copy the `samples/settingss.json` file to the `data` folder and edit it. Each exchange value should be an array of pairs, uppercase, e.g. `"bitstamp": ["BTC/EUR", "BTC/USD"]`.

The usage of the websocket database updater is quite straightforward:

```
./ob_updater.py
``` 

The program checks the exchanges configured in the `data/settings_ws.json` file and create a websocket connection for each pair.

Add `--debug` to see when an order book update occurs;  
Add `--verbose` to see the order book update values.

## Donations / support

**I won't ask donations, but I will share my referral links** to a few echanges and bots I tested and that I can recommend, thank you for registering using my links:

[coinbase](https://www.coinbase.com/join/596c62efa795880085a1a1a7) this is where I started. A must have exchange where you should NOT trade if you are a noob ;) Instead, after making your first deposit, trade via [Coinbase Pro](https://pro.coinbase.com) using a limit order: like that you will pay **0% fees** on the trade, which is quite awesome. Coinbase Pro is funded via coinbase accounts and needs a coinbase account to login.

[cex.io](https://cex.io/r/0/up113994371/0/) despite the funny name and simple website design, this is a solid exchange which has a killer feature I like a lot, the ability to withdraw money on your credit card.

[BitMEX](https://www.bitmex.com/register/CceysA) this is a famous cryptocurrency exchange where you can do margin trading up to 100x. You can double your portfolio or make huge gains with a few trades, or lose it all. Learn what is the liquidation price meaning and use a low leverage or no leverage at all to begin.

[3commas.io](https://3commas.io/?c=tc69129) you don't need to apply for a monthly subscribtion, you can use it on the go, which means you'll pay a commission on your profits (you need to prepay this before using the bot, but the bot is free to try for 3 days, so you get an idea). Worth to give it a try.

[ARBITRAGING](https://www.arbitraging.co/platform/register/affiliate/02C6WRhI) website offers an interesting product called **aBOT**, designed for **long term investments** (if you want to try it just for 1-2 months and then take out all your investments, you can do that, but you will probably lose money). aBOT has a stop price, research what that means before investing.  
The minimum amount to invest is 250 USD (in ETH). If this is too much for you, don't try aBOT. Else it's quite a good platform for passive income: invest and forget about it, you can automatically re-invest 0, 25%, 50%, 75% or 100% of the daily profits (in ARB) or keep the ARB tokens for later.  
What I do is to keep the ARB tokens and I trade them weekly against ETH.  
What I suggest to get started is to deposit some ETH, trade them to get some ARB tokens, then trade the ARBs for ETH (try to sell always at a higher price), like this you may actually make some profits with some test trades, as the spread between buy & sell often can be 5% or more. Then do a test withdrawal. Like this you get a feeling how it woks to get the money out of the platform.

**Disclaimer**: I'm no financial advisor, do your own research before using any of the bots, exchanges or investing platforms linked above, or using my tools. I won't be held responsible for any of your losses.

## License

[MIT License](LICENSE)
