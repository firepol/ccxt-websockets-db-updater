import configparser
import warnings

from sqlalchemy import Column, String, BigInteger, DECIMAL, Integer, DateTime
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

warnings.filterwarnings('ignore', r".*support Decimal objects natively", SAWarning, r'^sqlalchemy\.sql\.sqltypes$')

Base = declarative_base()

# SQLAlchemy does not map BigInt to Int by default on the sqlite dialect.
BigIntegerType = BigInteger()
BigIntegerType = BigIntegerType.with_variant(postgresql.BIGINT(), 'postgresql')
BigIntegerType = BigIntegerType.with_variant(sqlite.INTEGER(), 'sqlite')


class OrderBook(Base):
    __tablename__ = 'order_book'
    id = Column(BigIntegerType, primary_key=True, autoincrement=True)
    exchange_name = Column(String(20), nullable=False)  # exchange name, lowercase, e.g. bitfinex
    base = Column(String(10), nullable=False)  # asset to get (e.g. BTC)
    quote = Column(String(10), nullable=False)  # currency to offer or to get profits (mostly fiat: e.g. USD)
    side = Column(String(3), nullable=False)  # ask / bid
    price = Column(DECIMAL, nullable=False)
    volume = Column(DECIMAL, nullable=False)
    sort = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)


def get_db_url():
    # Get connection string from the settings
    settings = configparser.ConfigParser()
    settings.read('./data/settings.ini')
    return settings['config']['db_url']


# Engine is called each time db_model is imported
try:
    db_url = get_db_url()
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
except:
    # Not raising an exception, as this is used also by ob_tester.py, which doesn't need a DB
    print('Could not find ./data/settings.ini file')


def get_db_session():
    return sessionmaker(bind=engine)()
