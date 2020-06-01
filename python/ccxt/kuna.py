# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.acx import acx
import math
from ccxt.base.errors import ArgumentsRequired


class kuna(acx):

    def describe(self):
        return self.deep_extend(super(kuna, self).describe(), {
            'id': 'kuna',
            'name': 'Kuna',
            'countries': ['UA'],
            'rateLimit': 1000,
            'version': 'v2',
            'has': {
                'CORS': False,
                'fetchTickers': True,
                'fetchOHLCV': 'emulated',
                'fetchOpenOrders': True,
                'fetchMyTrades': True,
                'withdraw': False,
            },
            'timeframes': None,
            'urls': {
                'referral': 'https://kuna.io?r=kunaid-gvfihe8az7o4',
                'logo': 'https://user-images.githubusercontent.com/1294454/31697638-912824fa-b3c1-11e7-8c36-cf9606eb94ac.jpg',
                'api': 'https://kuna.io',
                'www': 'https://kuna.io',
                'doc': 'https://kuna.io/documents/api',
                'fees': 'https://kuna.io/documents/api',
            },
            'fees': {
                'trading': {
                    'taker': 0.25 / 100,
                    'maker': 0.25 / 100,
                },
                'funding': {
                    'withdraw': {
                        'UAH': '1%',
                        'BTC': 0.001,
                        'BCH': 0.001,
                        'ETH': 0.01,
                        'WAVES': 0.01,
                        'GOL': 0.0,
                        'GBG': 0.0,
                        # 'RMC': 0.001 BTC
                        # 'ARN': 0.01 ETH
                        # 'R': 0.01 ETH
                        # 'EVR': 0.01 ETH
                    },
                    'deposit': {
                        # 'UAH': (amount) => amount * 0.001 + 5
                    },
                },
            },
        })

    def fetch_markets(self, params={}):
        quotes = ['btc', 'eth', 'eurs', 'rub', 'uah', 'usd', 'usdt', 'gol']
        pricePrecisions = {
            'UAH': 0,
        }
        markets = []
        response = self.publicGetTickers(params)
        ids = list(response.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            for j in range(0, len(quotes)):
                quoteId = quotes[j]
                index = id.find(quoteId)
                slice = id[index:]
                if (index > 0) and (slice == quoteId):
                    baseId = id.replace(quoteId, '')
                    base = self.safe_currency_code(baseId)
                    quote = self.safe_currency_code(quoteId)
                    symbol = base + '/' + quote
                    precision = {
                        'amount': 6,
                        'price': self.safe_integer(pricePrecisions, quote, 6),
                    }
                    markets.append({
                        'id': id,
                        'symbol': symbol,
                        'base': base,
                        'quote': quote,
                        'baseId': baseId,
                        'quoteId': quoteId,
                        'precision': precision,
                        'limits': {
                            'amount': {
                                'min': math.pow(10, -precision['amount']),
                                'max': math.pow(10, precision['amount']),
                            },
                            'price': {
                                'min': math.pow(10, -precision['price']),
                                'max': math.pow(10, precision['price']),
                            },
                            'cost': {
                                'min': None,
                                'max': None,
                            },
                        },
                        'active': None,
                        'info': None,
                    })
                    break
        return markets

    def fetch_l3_order_book(self, symbol, limit=None, params={}):
        return self.fetch_order_book(symbol, limit, params)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchOpenOrders requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'market': market['id'],
        }
        response = self.privateGetOrders(self.extend(request, params))
        # todo emulation of fetchClosedOrders, fetchOrders, fetchOrder
        # with order cache + fetchOpenOrders
        # as in BTC-e, Liqui, Yobit, DSX, Tidex, WEX
        return self.parse_orders(response, market, since, limit)

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(self.safe_string(trade, 'created_at'))
        symbol = None
        if market:
            symbol = market['symbol']
        side = self.safe_string_2(trade, 'side', 'trend')
        if side is not None:
            sideMap = {
                'ask': 'sell',
                'bid': 'buy',
            }
            side = self.safe_string(sideMap, side)
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'volume')
        cost = self.safe_float(trade, 'funds')
        orderId = self.safe_string(trade, 'order_id')
        id = self.safe_string(trade, 'id')
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': None,
            'side': side,
            'order': orderId,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': None,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'market': market['id'],
        }
        response = self.publicGetTrades(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchOpenOrders requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'market': market['id'],
        }
        response = self.privateGetTradesMy(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limits=None, params={}):
        self.load_markets()
        trades = self.fetch_trades(symbol, since, limits, params)
        ohlcvc = self.build_ohlcvc(trades, timeframe, since, limits)
        result = []
        for i in range(0, len(ohlcvc)):
            ohlcv = ohlcvc[i]
            result.append([
                ohlcv[0],
                ohlcv[1],
                ohlcv[2],
                ohlcv[3],
                ohlcv[4],
                ohlcv[5],
            ])
        return result
