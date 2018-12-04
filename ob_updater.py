#!/usr/bin/env python3.6
# coding=utf-8

import argparse
import json
import pprint
import asyncio
import utils


def main():
    parser = argparse.ArgumentParser(description='Order books updater')
    parser.add_argument('--debug', help='Show when an order book update occurs', action="store_true")
    parser.add_argument('--verbose', help='Show the order book values', action="store_true")
    args = parser.parse_args()

    pp = pprint.PrettyPrinter(depth=6)
    loop = asyncio.get_event_loop()

    settings_ws = json.load(open('./data/settings_ws.json'))
    subscriptions = settings_ws['subscriptions']
    limit = settings_ws['limit']

    try:
        for exchange_name, symbols in subscriptions.items():

            settings = utils.get_exchange_settings(exchange_name)
            exchange = utils.get_ccxt_exchange(exchange_name, settings)

            asyncio.ensure_future(utils.subscribe_ws('ob', exchange, symbols, limit,
                                                     loop, pp, args.debug, args.verbose))

        loop.run_forever()

    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()

    print("After complete")


if __name__ == '__main__':
    main()
