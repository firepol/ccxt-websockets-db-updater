#!/usr/bin/env python3.6
# coding=utf-8

import argparse
import pprint
import asyncio

import ob_updater
import utils


def main():
    parser = argparse.ArgumentParser(description='Order books websocket tester')
    parser.add_argument('-e', '--exchange', help='Exchange', default='bitfinex')
    parser.add_argument('-ev', '--event', help='Event', default='ob')
    parser.add_argument('-s', '--symbol', help='Symbol (you can add more e.g. -s BTC/USD -s ETH/USD)', action='append')
    parser.add_argument('-l', '--limit', help='Limit', default=5)
    parser.add_argument('--debug', help='Show when an order book update occurs', action="store_true")
    parser.add_argument('--verbose', help='Show the order book values', action="store_true")
    args = parser.parse_args()

    if not args.symbol:
        print('You must specify at least one symbol with the `-s` parameter, e.g.: -s BTC/USD')
        return

    loop = asyncio.get_event_loop()

    settings = utils.get_exchange_settings(args.exchange)
    exchange = utils.get_ccxt_exchange(args.exchange, settings)

    try:
        asyncio.ensure_future(ob_updater.subscribe_ws(args.event, exchange, args.symbol, args.limit,
                                                      args.debug, args.verbose, None))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()

    print("After complete")


if __name__ == '__main__':
    main()
