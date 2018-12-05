#!/usr/bin/env python3.6
# coding=utf-8

import argparse
import asyncio
import pprint
import configparser

import utils
from db_model import get_db_session


def main():
    parser = argparse.ArgumentParser(description='Order books updater')
    parser.add_argument('--debug', help='Show when an order book update occurs', action="store_true")
    parser.add_argument('--verbose', help='Show the order book values', action="store_true")
    args = parser.parse_args()

    pp = pprint.PrettyPrinter(depth=6)
    loop = asyncio.get_event_loop()

    settings = configparser.ConfigParser()
    settings.read('./data/settings.ini')

    limit = int(settings['config']['order_book_entries_limit'])

    session = get_db_session()

    try:
        sections_to_ignore = ['config']
        for exchange_name in settings.sections():
            if exchange_name in sections_to_ignore:
                continue

            symbols = settings[exchange_name].get('symbols')
            if symbols:
                symbols = symbols.split('\n')

            exchange_settings = utils.get_exchange_settings(exchange_name)
            exchange = utils.get_ccxt_exchange(exchange_name, exchange_settings)

            asyncio.ensure_future(utils.subscribe_ws('ob', exchange, symbols, limit,
                                                     loop, pp, args.debug, args.verbose, session))

        loop.run_forever()

    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()

    print("After complete")


if __name__ == '__main__':
    main()
