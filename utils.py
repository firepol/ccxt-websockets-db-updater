import json
import logging
import re

import ccxt.async_support as ccxt

# exchanges that in CCXT must be instantiated with a class ending with "2"

EXCHANGES_API_V2 = ['hitbtc', 'bitfinex']
# CCXT ids of exchanges using USDT instead of USD
USDT_EXCHANGE_IDS = ['binance']

FORMAT = "[%(asctime)s, %(levelname)s] %(message)s"
logging.basicConfig(filename='websockets.log', level=logging.INFO, format=FORMAT)


def get_exchange_settings(exchange_name):
    settings = {}
    file_path = './data/exchange_api_keys.json'
    try:
        settings_root = json.load(open(file_path))
        settings = settings_root.get(exchange_name, {})
    except FileNotFoundError:
        print(f'Could not find {file_path}')
        pass
    return settings


def get_ccxt_exchange(exchange_name, settings, **kwargs):
    try:
        exchange_type = settings.get('type')
        # If you have several accounts at the same exchange, CCXT class name is the type (if the account name differs)
        class_name = exchange_type or exchange_name
        # Some exchanges, like hitbtc and bitfinex, need to use the newest class name, e.g. bitfinex2
        if exchange_name in EXCHANGES_API_V2:
            class_name = exchange_name + '2'
        exchange_class = getattr(ccxt, class_name)
        ccxt_settings = {'enableRateLimit': True}
        ccxt_settings.update(kwargs)
        # Some exchanges, like 'cex', need authentication also for websockets
        if settings:
            ccxt_settings.update(settings.get('api'))
        return exchange_class(ccxt_settings)
    except:
        logging.warning(f'Exchange {exchange_name} not supported, ignoring...')


def get_currency(symbol, position=1):
    pattern = re.compile("(\w+)/(\w+)")
    match = re.match(pattern, symbol)
    if match:
        return match.group(position)


def fix_symbol(exchange_id, symbol):
    """
    Fix (to UPPERCASE & "/" delimiter) quickly typed symbols, and exchanges using stable coins instead of fiat
    e.g. btc-usd -> BTC/USD, btc/eur -> BTC/EURT
    """
    result = symbol.upper().replace('-', '/')
    # Replace USD with USDT
    if exchange_id in USDT_EXCHANGE_IDS and (result.endswith('/USD' or result.endswith('/EUR'))):
        result = result.replace('/USD', '/USDT')
        result = result.replace('/EUR', '/EURT')
    return result
