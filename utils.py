import json
import logging
import sys
import traceback

import ccxt.async_support as ccxt


def get_exchange_settings(exchange_name):
    settings = {}
    file_path = './data/settings.json'
    try:
        settings_root = json.load(open(file_path))
        settings = settings_root['accounts'][exchange_name]
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
        if exchange_name in ['hitbtc', 'bitfinex']:
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


async def subscribe_ws(event, exchange, symbols, limit, loop, pp, debug=False, verbose=False):
    @exchange.on('err')
    def websocket_error(err, conxid):  # pylint: disable=W0612
        print(type(err).__name__ + ":" + str(err))
        traceback.print_tb(err.__traceback__)
        traceback.print_stack()
        loop.stop()

    @exchange.on(event)
    def websocket_ob(symbol, data):  # pylint: disable=W0612
        if debug:
            print(f'{event} received from: {exchange.id} {symbol}')
        if verbose:
            pp.pprint(data)
        sys.stdout.flush()

    sys.stdout.flush()

    for symbol in symbols:
        await exchange.websocket_subscribe(event, symbol, {'limit': limit})
        print(f'subscribed: {exchange.id} {symbol}')
