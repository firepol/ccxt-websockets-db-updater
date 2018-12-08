#!/usr/bin/env python3.6
# coding=utf-8

import argparse
import asyncio
import logging
import pprint
import configparser

import utils
from db_model import get_db_session
from ws_exception import WsError

FORMAT = "[%(asctime)s, %(levelname)s] %(message)s"
logging.basicConfig(filename='websockets.log', level=logging.INFO, format=FORMAT)


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

    ob_subscriptions = {}

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

            # make a list of tasks by exchange id
            ob_subscriptions[exchange.id] = asyncio.ensure_future(utils.subscribe_ws('ob', exchange, symbols, limit,
                                                     pp, args.debug, args.verbose, session))

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
        session.close()

    print('ob_updater stopped.')


if __name__ == '__main__':
    main()
