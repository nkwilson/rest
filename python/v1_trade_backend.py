# -*- coding: utf-8 -*-

from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture

import json
import logging

import locale
default_encoding = locale.getpreferredencoding(False)

startup_notify = ''
shutdown_notify = ''

limit_direction = ''  # 'buy'/'sell'
def check_limit_direction(direction):
    return limit_direction == '' or limit_direction == direction
limit_price = 0
limit_symbol = ''
limit_amount = 0

#import trade_elite
import json

#初始化apikey，secretkey,url
#apikey = 'd8da16f9-a531-4853-b9ee-ab07927c4fef'
#secretkey = '4752BE55655A6233A7254628FB7E9F50'
#okcoinRESTURL = 'www.okcoin.com'   #请求注意：国内账号需要 修改为 www.okcoin.cn
#apikey = 'fd07e7f8-519a-4ba3-8289-af9881181a96'
#secretkey = 'E0EACE4FB14A8CBDFE271E87D6FA2B6C'
#okcoinRESTURL = 'www.okcoin.cn'
apikey = 'e2625f5d-6227-4cfd-9206-ffec43965dab'
secretkey = "27BD16FD606625BCD4EE6DCA5A8459CE"
okcoinRESTURL = 'www.okex.com'

alt_apikey = ''
alt_secretkey = ''
alt_okcoinRESTRUL = ''

#现货API
okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)

#期货API
okcoinFuture = OKCoinFuture(okcoinRESTURL,apikey,secretkey)

def open_order_sell_rate(symbol, contract, amount, price='', lever_rate='10'):
    return okcoinFuture.future_trade(symbol, contract, '', amount, '2',
                                     '1', '10')

def close_order_sell_rate(symbol, contract, amount, price='', lever_rate='10'):
    return okcoinFuture.future_trade(symbol, contract, '', amount, '4',
                                     '1', '10')

def open_order_buy_rate(symbol, contract, amount, price='', lever_rate='10'):
    return okcoinFuture.future_trade(symbol, contract, '', amount, '1',
                                     '1', '10')

def close_order_buy_rate(symbol, contract, amount, price='', lever_rate='10'):
    return okcoinFuture.future_trade(symbol, contract, '', amount, '3',
                                     '1', '10')

def cancel_order(symbol, contract, order_id):
    return okcoinFuture.future_cancel(symbol, contract, order_id)

def query_orderinfo(symbol, contract, order_id):
    return okcoinFuture.future_orderinfo(symbol,contract, order_id,'0','1','2')

def query_kline(symbol, period, contract, ktype):
    return okcoinFuture.future_kline(symbol, period, contract, ktype)

def check_holdings_profit(symbol, contract, direction):
    nn = (0,0)
    loops = 5
    while loops > 0: # try some times
        try:
            holding=json.loads(okcoinFuture.future_position_4fix(symbol, contract, '1'))
            if holding['result'] != True:
                time.sleep(1) # in case something wrong, try again
                holding=json.loads(okcoinFuture.future_position_4fix(symbol, contract, '1'))
                if holding['result'] != True:
                    return nn
            else:
                break
        except Exception as ex:
            pass
        loops -= 1
    if loops == 0 or len(holding['holding']) == 0:
        return nn
    # print (holding['holding'])
    for data in holding['holding']:
        if data['symbol'] == symbol:
            if data['%s_amount' % direction] == 0 :
                return nn
            else :
                loss = float(data['%s_profit_lossratio' % direction])
                amount = int(data['%s_amount' % direction])
                return (loss, amount)
    return nn

# Figure out current holding's open price, zero means no holding
def real_open_price_and_cost(symbol, contract, direction):
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, contract, '1'))
    if holding['result'] != True:
        return 0
    if len(holding['holding']) == 0:
        return 0
    # print (holding['holding'])
    for data in holding['holding']:
        if data['symbol'] == symbol and data['%s_amount' % direction] != 0:
            avg = float(data['%s_price_avg' % direction])
            real= float(data['profit_real'])
            return (avg, avg*real)
    return 0

def query_bond(symbol, contract, direction):
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, contract, '1'))
    if holding['result'] != True:
        return 0.0 # 0 means failed
    if len(holding['holding']) == 0:
        return 0.0
    for data in holding['holding']:
        if data['symbol'] == symbol:
            if data['%s_amount' % direction] > 0:
                return data['%s_bond' % direction]/data['%s_amount' % direction]
    return 0.0

def query_balance(symbol):
    coin = symbol[0:symbol.index('_')]
    result=json.loads(okcoinFuture.future_userinfo_4fix())
    if result['result'] != True:
        return 0.0
    return float(result['info'][coin]['rights'])

