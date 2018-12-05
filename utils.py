import json
import logging
import re
import sys
import traceback

import ccxt.async_support as ccxt

import book_utils

# exchanges that in CCXT must be instantiated with a class ending with "2"
EXCHANGES_API_V2 = ['hitbtc', 'bitfinex']
# CCXT ids of exchanges using USDT instead of USD
USDT_EXCHANGE_IDS = ['binance', 'bitfinex2']


def get_exchange_settings(exchange_name):
    settings = {}
    file_path = './data/exchange_api_keys.json'
    try:
        settings_root = json.load(open(file_path))
        settings = settings_root[exchange_name]
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


async def subscribe_ws(event, exchange, symbols, limit, loop, pp, debug=False, verbose=False, session=None):
    @exchange.on('err')
    def websocket_error(err, conxid):  # pylint: disable=W0612
        print(type(err).__name__ + ":" + str(err))
        traceback.print_tb(err.__traceback__)
        traceback.print_stack()
        loop.stop()

    @exchange.on(event)
    def websocket_ob(symbol, data):  # pylint: disable=W0612
        ob_datetime = data.get('datetime')

        if debug:
            # printing just 1 ask & 1 bid
            print(f"{event} {exchange.id} {symbol}, {ob_datetime}: ask {data['asks'][0]}; bid: {data['bids'][0]}")
        if verbose:
            print(f"{event} {exchange.id} {symbol}:")
            pp.pprint(data)
        sys.stdout.flush()

        if session:
            # Get rid of the surplus order book entries and respect the chosen limit
            asks = data['asks'][:limit]
            bids = data['bids'][:limit]

            # TODO: check if there are exchanges ending with 2 & in that case don't truncate the last character
            exchange_name = exchange.id
            if exchange.id.endswith('2'):
                exchange_name = exchange.id[:-1]

            book_utils.insert_or_update(session, asks, bids, exchange_name, symbol, ob_datetime)

    sys.stdout.flush()

    for symbol in symbols:
        symbol = fix_symbol(exchange.id, symbol)
        await exchange.websocket_subscribe(event, symbol, {'limit': limit})
        print(f'subscribed: {exchange.id} {symbol}')


def get_currency(symbol, position=1):
    pattern = re.compile("(\w+)/(\w+)")
    match = re.match(pattern, symbol)
    if match:
        return match.group(position)


def fix_symbol(exchange_id, symbol):
    """Fix (to UPPERCASE & "/" delimiter) quickly typed symbols, e.g. btc-usd -> BTC/USD"""
    result = symbol.upper().replace('-', '/')
    # Replace USD with USDT
    if exchange_id in USDT_EXCHANGE_IDS and result.endswith('/USD'):
        result = result.replace('/USD', '/USDT')
    return result
