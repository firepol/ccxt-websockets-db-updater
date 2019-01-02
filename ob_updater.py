#!/usr/bin/env python3.6
# coding=utf-8

import argparse
import asyncio
import logging
import pprint
import configparser

import book_utils
import utils
from db_model import get_db_session
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
            ob_subscriptions[exchange.id] = asyncio.ensure_future(utils.subscribe_ws('ob', exchange, symbols,
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
