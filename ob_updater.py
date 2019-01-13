#!/usr/bin/env python3.6
# coding=utf-8

import argparse
import asyncio
import datetime
import logging
import pprint
import configparser
import sys
import traceback

import book_utils
import utils
from db_model import get_db_session
from utils import fix_symbol
from ws_exception import WsError

FORMAT = "[%(asctime)s, %(levelname)s] %(message)s"
logging.basicConfig(filename='websockets.log', level=logging.INFO, format=FORMAT)


def main():
    parser = argparse.ArgumentParser(description='Order books updater')
    parser.add_argument('--reset_db', help='Delete order_book DB records before starting', action="store_true")
    parser.add_argument('--debug', help='Show when an order book update occurs', action="store_true")
    parser.add_argument('--verbose', help='Show the order book values', action="store_true")
    args = parser.parse_args()

    pp = pprint.PrettyPrinter(depth=6)
    loop = asyncio.get_event_loop()

    settings = configparser.ConfigParser()
    settings.read('./data/settings.ini')

    limit = int(settings['config']['order_book_entries_limit'])

    ob_subscriptions = {}
    order_books = {}

    if args.reset_db:
        book_utils.truncate_table('order_book')

    try:
        sections_to_ignore = ['config']
        for exchange_name in settings.sections():
            if exchange_name in sections_to_ignore:
                continue

            order_books[exchange_name] = {}

            symbols = settings[exchange_name].get('symbols')
            if symbols:
                symbols = symbols.split('\n')

                for symbol in symbols:
                    order_books[exchange_name][symbol] = {}

            exchange_settings = utils.get_exchange_settings(exchange_name)
            exchange = utils.get_ccxt_exchange(exchange_name, exchange_settings)

            # make a list of tasks by exchange id
            ob_subscriptions[exchange.id] = asyncio.ensure_future(subscribe_ws('ob', exchange, symbols,
                                                                               order_books, limit, pp, args.debug, args.verbose))

        asyncio.ensure_future(process_order_books(order_books))

        loop.run_forever()

    except WsError as wse:
        print(f'Canceling: {wse}')
        ob_subscriptions[wse].cancel()
    except KeyboardInterrupt:
        message = 'Keyboard interrupt. Stopped.'
        print(message)
        logging.info(message)
        pass
    finally:
        print('Closing Loop')
        loop.close()

    print('ob_updater stopped.')


async def subscribe_ws(event, exchange, symbols, order_books, limit, pp, debug=False, verbose=False):
    @exchange.on('err')
    async def websocket_error(err, conxid):  # pylint: disable=W0612
        error_stack = traceback.extract_stack()
        # TODO: log and handle errors https://github.com/firepol/ccxt-websockets-db-updater/issues/4
        print(f'{exchange.id}, {datetime.datetime.now()}, {error_stack}')

    @exchange.on(event)
    def websocket_ob(symbol, data):  # pylint: disable=W0612
        ob_datetime = data.get('datetime') or str(datetime.datetime.now())

        if debug:
            # printing just 1 ask & 1 bid
            print(f"{event} {exchange.id} {symbol}, {ob_datetime}: ask {data['asks'][0]}; bid: {data['bids'][0]}")
        if verbose:
            print(f"{event} {exchange.id} {symbol}:")
            pp.pprint(data)
        sys.stdout.flush()

        # Get rid of the surplus order book entries and respect the chosen limit
        asks = data['asks'][:limit]
        bids = data['bids'][:limit]

        # TODO: check if there are exchanges ending with 2 & in that case don't truncate the last character
        exchange_name = exchange.id
        if exchange.id.endswith('2'):
            exchange_name = exchange.id[:-1]

        order_books[exchange_name][symbol] = {'asks': asks, 'bids': bids, 'datetime': ob_datetime}

    sys.stdout.flush()

    for symbol in symbols:
        symbol = fix_symbol(exchange.id, symbol)
        await exchange.websocket_subscribe(event, symbol, {'limit': limit})
        print(f'subscribed: {exchange.id} {symbol}')
        logging.info(f'subscribed: {exchange.id} {symbol}')


async def process_order_books(order_books):
    """This works as a buffer: order_books are saved to the DB every 0.1s"""
    session = get_db_session()
    while True:
        await asyncio.sleep(0.1)
        for exchange_name, symbols in order_books.items():
            # print(f'{exchange_name}: {symbols}')
            for symbol, values in symbols.items():
                try:
                    if not values:
                        continue
                    book_utils.insert_or_update(session, values.get('asks'), values.get('bids'),
                                                exchange_name, symbol, values.get('datetime'))
                except Exception as e:
                    print(e)


if __name__ == '__main__':
    main()
