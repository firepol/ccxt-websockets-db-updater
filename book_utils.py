import datetime
import logging

import dateutil.parser

import utils
from db_model import OrderBook


def get_db_order_books(session, exchange, base, quote, side):
    return session.query(OrderBook) \
        .filter(OrderBook.exchange_name == exchange) \
        .filter(OrderBook.base == base) \
        .filter(OrderBook.quote == quote) \
        .filter(OrderBook.side == side) \
        .order_by(OrderBook.sort).all()


def update_db_records_properties(db_records, order_books, ob_datetime):
    """
    Update price, volume, date of db order books, given matching order books (same sort order) fetched via api
    """
    for idx, db_ob in enumerate(db_records):
        db_ob.price = order_books[idx][0]
        db_ob.volume = order_books[idx][1]
        db_ob.datetime = ob_datetime


def insert_order_books(session, order_books, exchange, base, quote, side, ob_datetime):
    for idx, ob in enumerate(order_books):
        db_ob = OrderBook(exchange_name=exchange, base=base, quote=quote, price=ob[0], volume=ob[1], side=side,
                          datetime=ob_datetime, sort=idx)
        session.add(db_ob)


def is_datetime_acceptable(ob_datetime, tolerated_seconds):
    """Returns true, if the datetime is recent enough (tolerated_seconds), false if it isn't"""
    tz_info = ob_datetime.tzinfo
    # Some OBs may come with the wrong datetime, let's check it and fix it if necessary
    # https://stackoverflow.com/questions/796008/cant-subtract-offset-naive-and-offset-aware-datetimes
    datetime_tolerated = datetime.datetime.now(tz=tz_info) - datetime.timedelta(seconds=tolerated_seconds)

    if ob_datetime < datetime_tolerated:
        return False
    return True


def insert_or_update(session, asks, bids, exchange, symbol, ob_datetime=None):
    if ob_datetime:  # Example: '2018-12-13T19:49:42.000Z'
        ob_datetime = dateutil.parser.parse(ob_datetime, ignoretz=True)

        if not is_datetime_acceptable(ob_datetime, 60):
            # TODO: to avoid log spam, uncomment this only when you want to debug wrong datetimes
            # logging.warning(f'{exchange} {symbol} outdated datetime: {ob_datetime}')
            ob_datetime = datetime.datetime.now()
    else:
        ob_datetime = datetime.datetime.now()

    base = utils.get_currency(symbol, 1).upper()
    quote = utils.get_currency(symbol, 2).upper()

    _insert_or_update(session, asks, exchange, base, quote, 'ask', ob_datetime)
    _insert_or_update(session, bids, exchange, base, quote, 'bid', ob_datetime)

    session.commit()


def _insert_or_update(session, orders, exchange, base, quote, side, ob_datetime):
    """
    Fetch from DB orders matching exchange, base, quote, side. First time: insert new order, else update existing ones
    """
    db_records = get_db_order_books(session, exchange, base, quote, side)
    if len(db_records) > 0:
        update_db_records_properties(db_records, orders, ob_datetime)
    if len(db_records) == 0:
        insert_order_books(session, orders, exchange, base, quote, side, ob_datetime)
