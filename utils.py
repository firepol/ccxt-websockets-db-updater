import json
import logging
import re
import sys
import traceback
import datetime

import ccxt.async_support as ccxt
import dateutil

import book_utils

# exchanges that in CCXT must be instantiated with a class ending with "2"
from ws_exception import WsError

EXCHANGES_API_V2 = ['hitbtc', 'bitfinex']
# CCXT ids of exchanges using USDT instead of USD
USDT_EXCHANGE_IDS = ['binance', 'bitfinex2']

FORMAT = "[%(asctime)s, %(levelname)s] %(message)s"
logging.basicConfig(filename='websockets.log', level=logging.INFO, format=FORMAT)


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


def name_to_num(name):
    name_sum = sum(ord(character) - 96 for character in name.lower() if character != " ")
    if name_sum > 9:
        return int(name_sum / 10)
    return name_sum


def allow_continue(exchange_id, ob_datetime):
    # This is a temporary workaround to skip OBs based on the decimal of second of the actual time
    # The goal is to minimize DB writes, because some exchanges like bitfinex flood the system...

    if exchange_id == 'bitstamp':
        return True

    # TODO: ideally save only if an update is newer than e.g. 0.1s
    # Create a dictionary exchange -> pair -> last update (datetime) and compare to that
    ob_datetime_object = dateutil.parser.parse(ob_datetime, ignoretz=True)
    ob_microsecond = ob_datetime_object.microsecond
    ds = int(str(ob_microsecond)[0])

    if exchange_id in ['cex', 'bitfinex2', 'binance']:
        if exchange_id == 'cex':
            if ds % 3 == 0:
                return True

        if exchange_id == 'bitfinex2':
            if (ds + 1) % 3 == 0:
                return True

        if exchange_id == 'binance':
            if (ds + 2) % 3 == 0:
                return True
    else:
        name_num = name_to_num(exchange_id)
        if name_num % ds == 0:
            return True

    return False


async def subscribe_ws(event, exchange, symbols, limit, pp, debug=False, verbose=False, session=None):
    @exchange.on('err')
    async def websocket_error(err, conxid):  # pylint: disable=W0612
        error_message = type(err).__name__ + ":" + str(err)
        error_stack = traceback.extract_stack()
        logging.error(f'{exchange.id}: {error_message}')
        logging.error(error_stack)
        print(f'{exchange.id}, {datetime.datetime.now()}, {error_stack}')
        await exchange.close()
        raise WsError(exchange.id)

    @exchange.on(event)
    def websocket_ob(symbol, data):  # pylint: disable=W0612
        ob_datetime = data.get('datetime') or str(datetime.datetime.now())

        if not allow_continue(exchange.id, ob_datetime):
            return

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
        logging.info(f'subscribed: {exchange.id} {symbol}')


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
