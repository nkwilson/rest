# -*- coding: utf-8 -*-

import sys
import getopt
import traceback

import pandas
import numpy
import datetime

import os
import os.path as path
import time
import random
import math
import datetime
from datetime import datetime as dt

import pipes

from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture

import subprocess
from subprocess import PIPE, run

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

#print (u'K线信息')
# print (okcoinSpot.kline('btc_cny'))

#print (u' 现货行情 ')
#print (okcoinSpot.ticker('btc_usd'))

#print (u' 现货深度 ')
#print (okcoinSpot.depth('btc_usd'))

#print (u' 现货历史交易信息 ')
#print (okcoinSpot.trades())

#print (u' 用户现货账户信息 ')
#print (okcoinSpot.userinfo())

#print (u' 现货下单 ')
#print (okcoinSpot.trade('ltc_usd','buy','0.1','0.2'))

#print (u' 现货批量下单 ')
#print (okcoinSpot.batchTrade('ltc_usd','buy','[{price:0.1,amount:0.2},{price:0.1,amount:0.2}]'))

#print (u' 现货取消订单 ')
#print (okcoinSpot.cancelOrder('ltc_usd','18243073'))

#print (u' 现货订单信息查询 ')
#print (okcoinSpot.orderinfo('ltc_usd','18243644'))

#print (u' 现货批量订单信息查询 ')
#print (okcoinSpot.ordersinfo('ltc_usd','18243800,18243801,18243644','0'))

#print (u' 现货历史订单信息查询 ')
#print (okcoinSpot.orderHistory('ltc_usd','0','1','2'))

#print (u' 期货行情信息')
#print (okcoinFuture.future_ticker('btc_usd','quarter'))

#print (u' 期货k线信息')
#print (okcoinFuture.future_kline('btc_usd','4hour', 'quarter', '1'))
#[[1560038400000, 7904.03, 7941.03, 7828, 7852.97, 694211, 8821.79293212]]

#print (u' 期货市场深度信息')
#print (okcoinFuture.future_depth('btc_usd','this_week','6'))

#print (u'期货交易记录信息') 
#print (okcoinFuture.future_trades('ltc_usd','this_week'))

#print (u'期货指数信息')
#print (okcoinFuture.future_index('ltc_usd'))

#print (u'美元人民币汇率')
#print (okcoinFuture.exchange_rate())

#print (u'获取预估交割价') 
#print (okcoinFuture.future_estimated_price('ltc_usd'))

#print (u'获取全仓账户信息')
#print (okcoinFuture.future_userinfo())

#print (u'获取全仓持仓信息')
#print (okcoinFuture.future_position('btc_usd','quarter'))  # works


# |参数名|	参数类型|	必填|	描述|
# | :-----    | :-----   | :-----    | :-----   |
# |symbol|String|是|btc\_usd   ltc\_usd    eth\_usd    etc\_usd    bch\_usd|
# |contract\_type|String|是|合约类型: this\_week:当周   next\_week:下周   quarter:季度|
# |api_key|String|是|用户申请的apiKey|
# |sign|String|是|请求参数的签名|
# |price|String|是|价格|
# |amount|String|是|委托数量|
# |type|String|是|1:开多 2:开空 3:平多 4:平空|
# |match_price|String|否|是否为对手价 0:不是    1:是   ,当取值为1时,price无效|
# |lever_rate|String|否|杠杆倍数，下单时无需传送，系统取用户在页面上设置的杠杆倍数。且“开仓”若有10倍多单，就不能再下20倍多单|
#future_trade(self,symbol,contractType,price='',amount='',tradeType='',matchPrice='',leverRate='') tradeType=2 best match price
#print (u'期货下单')
#print (okcoinFuture.future_trade('btc_usd','quarter','','1','1','1','10')) # works

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

#print (u'期货批量下单')
#print (okcoinFuture.future_batchTrade('ltc_usd','this_week','[{price:0.1,amount:1,type:1,match_price:0},{price:0.1,amount:3,type:1,match_price:0}]','20'))

#print (u'期货取消订单')
#print (okcoinFuture.future_cancel('ltc_usd','this_week','47231499'))

#print (u'期货获取订单信息')
#print (okcoinFuture.future_orderinfo('ltc_usd','this_week','47231812','0','1','2'))

def query_orderinfo(symbol, contract, order_id):
    return okcoinFuture.future_orderinfo(symbol,contract, order_id,'0','1','2')

#print (u'期货逐仓账户信息')
#print (json.loads(okcoinFuture.future_userinfo_4fix()))

#print (u'期货逐仓持仓信息')
#print (json.loads(okcoinFuture.future_position_4fix('ltc_usd','quarter', '1')))

#print (quarter_auto_bond('ltc_usd'), quarter_auto_balance('ltc_usd'))
#os.sys.exit(0)

# demo: ok_sub_futureusd_btc_kline_quarter_4hou
def figure_out_symbol_info(path):
    path = os.path.splitext(path)[0]
    start_pattern = 'ok_sub_future'
    end_pattern = '_kline_'
    start = path.index(start_pattern) + len(start_pattern)
    end = path.index(end_pattern)
    print ('symbol is %s' % (path[start:end]))
    return path[start:end]

def figure_out_contract_info(path):
    path = os.path.splitext(path)[0]
    start_pattern = 'kline_'
    end_pattern = '_'
    start = path.index(start_pattern) + len(start_pattern)
    end = path.rindex(end_pattern)
    print ('contract is %s' % (path[start:end]))
    return path[start:end]

def figure_out_period_info(path):
    path = os.path.splitext(path)[0]
    start_pattern = '_'
    start = path.rindex(start_pattern) + len(start_pattern)
    print ('period is %s' % (path[start:]))
    return path[start:]

# {'result': True, 'holding': [{'buy_price_avg': 176.08158274, 'symbol': 'eth_usd', 'lever_rate': 10, 'buy_available': 0, 'contract_id': 201906280020041, 'sell_risk_rate': '99.36', 'buy_amount': 0, 'buy_risk_rate': '1,000,000.00', 'profit_real': -1.847e-05, 'contract_type': 'quarter', 'sell_flatprice': '178.453', 'buy_bond': 0, 'sell_profit_lossratio': '-0.66', 'buy_flatprice': '0.000', 'buy_profit_lossratio': '0.00', 'sell_amount': 1, 'sell_bond': 0.00615942, 'sell_price_cost': 162.388, 'buy_price_cost': 176.08158274, 'create_date': 1552656509000, 'sell_price_avg': 162.388, 'sell_available': 1}]}
# if current order is permit to issue
def check_holdings_profit(symbol, contract, direction):
    nn = (0,0)
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, contract, '1'))
    if holding['result'] != True:
        time.sleep(1) # in case something wrong, try again
        holding=json.loads(okcoinFuture.future_position_4fix(symbol, contract, '1'))
        if holding['result'] != True:
            return nn
    if len(holding['holding']) == 0:
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

order_infos = {'usd_btc':'btc_usd',
               'usd_ltc':'ltc_usd',
               'usd_eth':'eth_usd',
               'usd_eos':'eos_usd',                              
               'usd_bch':'bch_usd',
               'sell':{'open':open_order_sell_rate,
                       'close':close_order_sell_rate},
               'buy':{'open':open_order_buy_rate,
                      'close':close_order_buy_rate}}

# {'result': True, 'orders': [{'symbol': 'eth_usd', 'lever_rate': 10, 'amount': 1, 'fee': -1.131e-05, 'contract_name': 'ETH0517', 'unit_amount': 10, 'type': 3, 'price_avg': 265.304, 'deal_amount': 1, 'price': 265.304, 'create_date': 1557968404000, 'order_id': 2833278863744000, 'status': 2}]}
reissuing_order = 0
def issue_order_now(symbol, contract, direction, amount, action):
    global reissuing_order
    # print (symbol, direction, amount, action)
    raw_result = order_infos[direction][action](symbol, contract, amount)
    result = json.loads(raw_result)
    print (result)
    if result['result'] == False:
        reissuing_order = 0
        return False
    order_id = str(result['order_id']) # no exceptions, means successed
    #print (order_id)
    time.sleep(1) # wait a second
    order_info = json.loads(query_orderinfo(symbol, contract, order_id))
    print (order_info)
    if order_info['orders'][0]['amount'] != order_info['orders'][0]['deal_amount']:
        amount -= int(order_info['orders'][0]['deal_amount'])
        reissuing_order += 1
    else:
        return
    if reissuing_order > 5: # more than 5 , quit
        reissuing_order = 0
        return
    print ('try to cancel pending order and reissue')
    cancel_order(symbol, contract, order_id)
    issue_order_now(symbol, contract, direction, amount, action)

def issue_order_now_conditional(symbol, contract, direction, amount, action, must_positive=True):
    (loss, t_amount) = check_holdings_profit(symbol, contract, direction)
    if t_amount == 0:
        return
    elif must_positive == True and loss <= 0:
        print ('loss ratio=%f%%, keep holding' % (loss))
        return
    print ('loss ratio=%f%%, %s' % (loss, 'yeap' if loss > 0 else 'tough'))
    if amount == 0:
        amount = t_amount
    issue_order_now(symbol, contract, direction, amount, action)

def issue_quarter_order_now(symbol, direction, amount, action):
    print ('issue quarter order: ', action, symbol, direction, amount)
    issue_order_now(symbol, 'quarter', direction, amount, action)

def issue_quarter_order_now_conditional(symbol, direction, amount, action, must_positive=True):
    print ('issue quarter order conditional: ', action, symbol, direction, amount)
    issue_order_now_conditional(symbol, 'quarter', direction, amount, action, must_positive)

def issue_thisweek_order_now(symbol, direction, amount, action):
    print ('issue thisweek order: ', action, symbol, direction, amount)
    issue_order_now(symbol, 'this_week', direction, amount, action)

def issue_thisweek_order_now_conditional(symbol, direction, amount, action, must_positive=True):
    print ('issue thisweek order conditional: ', action, symbol, direction, amount)
    issue_order_now_conditional(symbol, 'this_week', direction, amount, action, must_positive)

# apikey = 'e2625f5d-6227-4cfd-9206-ffec43965dab'
# secretkey = "27BD16FD606625BCD4EE6DCA5A8459CE"
# okcoinRESTURL = 'www.okex.com'
    
# #现货API
# okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)

# #期货API
# okcoinFuture = OKCoinFuture(okcoinRESTURL,apikey,secretkey)

def main(argv):
    print (argv)

    matplotlib.rcParams['font.sans-serif'] = ['AR PL KaitiM GB'] # SimHei is common Chinese font on macOS. ttc is not ok.
#fonts-arphic-gkai00mp/xenial 2.11-15 all
#  "AR PL KaitiM GB" Chinese TrueType font by Arphic Technology

# after install new font, must delete this file: /root/.cache/matplotlib/fontList.cache  to let matplotlib update font cache

    if len(argv) == 1:
        __main()
        return

    # 1 args: all_stocks | selected
    if len(argv) == 2:
            globals()[argv[1]]()
    # 2 args: one_stock ######, last year
    elif len(argv) == 3:
            end = pandas.datetime.now();
            start=end-datetime.timedelta(365)

            globals()[argv[1]](argv[2],start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    # 3 args: one_stock ######, start, until now
    elif len(argv) == 4:
            globals()[argv[1]](argv[2], argv[3], pandas.datetime.now().strftime('%Y-%m-%d'))
    elif len(argv) == 5:
    # 4 args: one_stock ######, start, end
            globals()[argv[1]](argv[2], argv[3], argv[4])
    else:
            print ("Usage: program [one_stock [stock [start [end]]]]")


close_mean = pandas.Series()
close_upper = pandas.Series()
close_lower = pandas.Series()

old_open_price = 0
old_close_mean = 0
trade_file = ''
default_fee_threshold = 0.0001# baesed on one order's fee
fee_threshold = default_fee_threshold
levage_rate = 20

# if fee is bigger than lost, then delay it to next signal
def check_close_sell_fee_threshold(open_price, current_price, amount=1):
    l_amount = amount if options.fee_amount else 1
    return abs((current_price - open_price) / open_price) * l_amount > fee_threshold

def check_close_sell_half_fee_threshold(open_price, current_price, amount=1):
    l_amount = amount if options.fee_amount else 1
    return abs((current_price - open_price) / open_price) * l_amount > (fee_threshold / 2.0)

symbols_mapping = { 'usd_btc': 'btc_usd',
                    'usd_ltc': 'ltc_usd',
                    'usd_eth': 'eth_usd',
                    'usd_eos': 'eos_usd',                     
                    'usd_bch': 'bch_usd'}

reverse_dirs = { 'buy': {'reverse_dir':'sell', 'gate': lambda order_price, current_price, amount:
                         (order_price > current_price) and check_close_sell_half_fee_threshold(order_price, current_price, amount)},
                         
                 'sell': {'reverse_dir':'buy', 'gate': lambda order_price, current_price, amount:
                        (order_price < current_price) and check_close_sell_half_fee_threshold(current_price, order_price, amount)}}

def figure_out_symbol_info(path):
    start_pattern = 'ok_sub_future'
    end_pattern = '_kline_'
    start = path.index(start_pattern) + len(start_pattern)
    end = path.index(end_pattern)
    # print (path[start:end])
    return path[start:end]

# future_position_4fix return format
# 期货逐仓持仓信息
# {'result': True, 'holding': [{'buy_price_avg': 75.221, 'symbol': 'ltc_usd', 'lever_rate': 10, 'buy_available': 1, 'contract_id': 201906280010015, 'sell_risk_rate': '1,000,000.00', 'buy_amount': 1, 'buy_risk_rate': '99.84', 'profit_real': -3.988e-05, 'contract_type': 'quarter', 'sell_flatprice': '0.000', 'buy_bond': 0.01329151, 'sell_profit_lossratio': '0.00', 'buy_flatprice': '69.011', 'buy_profit_lossratio': '-0.14', 'sell_amount': 0, 'sell_bond': 0, 'sell_price_cost': 92.37172398, 'buy_price_cost': 75.221, 'create_date': 1552656524000, 'sell_price_avg': 92.37172398, 'sell_available': 0}]
# {'result': True, 'holding': [{'buy_price_avg': 176.08158274, 'symbol': 'eth_usd', 'lever_rate': 10, 'buy_available': 0, 'contract_id': 201906280020041, 'sell_risk_rate': '99.36', 'buy_amount': 0, 'buy_risk_rate': '1,000,000.00', 'profit_real': -1.847e-05, 'contract_type': 'quarter', 'sell_flatprice': '178.453', 'buy_bond': 0, 'sell_profit_lossratio': '-0.66', 'buy_flatprice': '0.000', 'buy_profit_lossratio': '0.00', 'sell_amount': 1, 'sell_bond': 0.00615942, 'sell_price_cost': 162.388, 'buy_price_cost': 176.08158274, 'create_date': 1552656509000, 'sell_price_avg': 162.388, 'sell_available': 1}]}
# if current order is permit to issue
def check_open_order_gate(symbol, direction, current_price):
    if options.emulate:
        return True
    if options.skip_gate_check:
        return True
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, 'quarter', '1'))
    if holding['result'] != True:
        return False
    if len(holding['holding']) == 0:
        return True
    # print (holding['holding'])
    for data in holding['holding']:
        if data['symbol'] == symbol:
            dirs = reverse_dirs[direction]
            # print (dirs, dirs['gate'])
            if data['%s_amount' % dirs['reverse_dir']] == 0 :
                return True;
            else :
                return dirs['gate'](data['%s_price_avg' % dirs['reverse_dir']], current_price, amount)
    return False

def query_bond(symbol, contract, direction):
    if options.emulate:
        return 0.0
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

# future_userinfo_4fix format
# {'result': True, 'info': {'btc': {'balance': 0.10077745, 'rights': 0.19425753, 'contracts': [{'contract_type': 'this_week', 'freeze': 0, 'balance': 0, 'contract_id': 201905170000013, 'available': 0.1116, 'profit': 0.0108896, 'bond': 0, 'unprofit': 0}, {'contract_type': 'quarter', 'freeze': 0, 'balance': 0, 'contract_id': 201906280000012, 'available': 0.1614, 'profit': 0.09122745, 'bond': 0.03053532, 'unprofit': -0.0087}]}, 'bsv': {'balance': 0, 'rights': 0, 'contracts': []}, 'etc': {'balance': 0, 'rights': 0, 'contracts': []}, 'bch': {'balance': 0.83989472, 'rights': 2.34665722, 'contracts': [{'contract_type': 'this_week', 'freeze': 0, 'balance': 0, 'contract_id': 201905173010074, 'available': 0.8664, 'profit': 0.02652685, 'bond': 0, 'unprofit': 0}, {'contract_type': 'quarter', 'freeze': 0, 'balance': 0, 'contract_id': 201906283010075, 'available': 2.1309, 'profit': 1.69430244, 'bond': 0.40325632, 'unprofit': -0.2141}]}, 'xrp': {'balance': 0, 'rights': 0, 'contracts': []}, 'eth': {'balance': 2.13255958, 'rights': 4.62345877, 'contracts': [{'contract_type': 'this_week', 'freeze': 0, 'balance': 0, 'contract_id': 201905170020042, 'available': 2.153, 'profit': 0.02053667, 'bond': 0, 'unprofit': 0}, {'contract_type': 'quarter', 'freeze': 0, 'balance': 0, 'contract_id': 201906280020041, 'available': 3.9439, 'profit': 2.53135193, 'bond': 0.71997122, 'unprofit': -0.0611}]}, 'eos': {'balance': 0.10395966, 'rights': 0.40952573, 'contracts': [{'contract_type': 'quarter', 'freeze': 0, 'balance': 0.17428396, 'contract_id': 201906280200053, 'available': 0.10395966, 'profit': -0.00052201, 'bond': 0.17376195, 'unprofit': 0.1318}]}, 'ltc': {'balance': 1.9931993, 'rights': 4.29178602, 'contracts': [{'contract_type': 'this_week', 'freeze': 0, 'balance': 0, 'contract_id': 201905170010016, 'available': 2.784, 'profit': 0.79088871, 'bond': 0, 'unprofit': 0}, {'contract_type': 'quarter', 'freeze': 0, 'balance': 0, 'contract_id': 201906280010015, 'available': 3.0551, 'profit': 1.68104735, 'bond': 0.61906728, 'unprofit': -0.1734}]}}}
def query_balance(symbol):
    if options.emulate:
        return 0.0
    coin = symbol[0:symbol.index('_')]
    result=json.loads(okcoinFuture.future_userinfo_4fix())
    if result['result'] != True:
        return 0.0
    return float(result['info'][coin]['rights'])

#print ('quarter buy bond ', query_bond('eth_usd', 'quarter', 'buy'))
#print ('quarter sell bond ', query_bond('eth_usd', 'quarter', 'sell'))
#print ('rights ', query_balance('eth_usd'))
#sys.exit(0)

# check if close is in the ratio of boll std
def check_close_to_mean(bolls, close, ratio=0.3, threshold=0.01):
    return True
    v0 = abs(bolls[0] - close) / bolls[0]
    if v0 <= threshold : # less than threshold is ok
        return True
    v1 = abs(bolls[1] - bolls[0]) * ratio # boll[0] is mean, bolls[1] is upper
    v2 = abs(close - bolls[0])
    return (v1 > v2)
    
def trade_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# open sell order now
def signal_open_order_with_sell(l_index, filename, close, multiple=False):
    if not options.emulate and os.path.isfile(filename) == True: # already ordered
        return
    mode = 'w' if multiple == False else 'a'
    append = '' if multiple == False else '\n'
    line = '%s sell at %0.7f%s' % (l_index, close, append)
    with open(filename, mode) as f:
        f.write(line)
        f.close()
    print (trade_timestamp(), line.rstrip('\n'))
    global trade_notify
    with open(trade_notify, 'w') as f:
        f.write('%s.open' % filename)
        f.close()

# close sell order now
def signal_close_order_with_buy(l_index, filename, close):
    if os.path.isfile(filename) == False: # no order opened
        return
    line = ' closed at %s with %0.7f\n' % (l_index, close)
    with open(filename, 'a') as f:
        f.write(line)
        f.close()
    print (trade_timestamp(), line.rstrip('\n'), flush=True)
    global trade_notify
    with open(trade_notify, 'w') as f:
        f.write('%s.close' % filename)
        f.close()


# open buy order now
def signal_open_order_with_buy(l_index, filename, close, multiple=False):
    if not options.emulate and os.path.isfile(filename) == True: # already ordered
        return
    mode = 'w' if multiple == False else 'a'
    append = '' if multiple == False else '\n'
    line = '%s buy at %0.7f%s' % (l_index, close, append)
    with open(filename, mode) as f:
        f.write(line)
        f.close()
    print (trade_timestamp(), line.rstrip('\n'))
    global trade_notify
    with open(trade_notify, 'w') as f:
        f.write('%s.open' % filename)
        f.close()

# close buy order now
def signal_close_order_with_sell(l_index, filename, close):
    if os.path.isfile(filename) == False: # no order opened
        return
    line = ' closed at %s with %0.7f\n' % (l_index, close)
    with open(filename, 'a') as f:
        f.write(line)
        f.close()
    print (trade_timestamp(), line.rstrip('\n'), flush=True)
    global trade_notify
    with open(trade_notify, 'w') as f:
        f.write('%s.close' % filename)
        f.close()

def generate_trade_filename_new(dir, l_index, order_type, prefix=''):
    fname = '%s-%strade.%s' % (l_index, prefix, order_type)
    return os.path.join(dir, fname)

def generate_trade_filename(dir, l_index, order_type):
        global l_prefix
        global new_trade_file
        if new_trade_file == True:
            return generate_trade_filename_new(dir, l_index, order_type, l_prefix)
        fname = '%s-trade-%s.%s' % (os.path.basename(dir), l_index, order_type)
        #print (trade_file)
        return os.path.join(os.path.dirname(dir), fname)

# format: mean, upper, lower
def read_boll(filename):
    boll = 0
    try:
        with open(filename, 'r') as f:
            line = f.readline().rstrip('\n')
            boll = [float(x) for x in line.split(',')]
            f.close()
    except Exception as ex:
        print ('read_boll: %s\n' % filename)
    return boll

#  '6179.63', '6183.09', '6178.98', '6180.34', '3148.0', '50.936313653924'
# format: open, high, low, close, volume, total-value
def read_close(filename):
    close = 0
    # drop '.boll' suffix
    filename = os.path.splitext(filename)[0]
    # print (filename)
    if os.path.isfile(filename) == False: # in case not exist
        return close
    try:
        with open(filename, 'r') as f:
            line = eval(f.readline().rstrip('\n'))  # can't just copy from boll
            close = float(line[3])
            f.close()
            # close = eval(f.readline())[3]
    except Exception as ex:
        print ('read_close: %s' % filename)
    # print (close)
    return close

new_trade_file = True

def try_to_pick_old_order():
    global trade_notify, trade_file
    global old_open_price
    # first check trade_notify
    if os.path.isfile(trade_notify) and os.path.getsize(trade_notify) > 0:
        with open(trade_notify, 'r') as f:
            line=f.readline().rstrip('\n')
            f.close()
            # print (line)
            pathext = os.path.splitext(line)
            # print (pathext)
            if pathext[1][1:] == 'open': # means pending order
                trade_file = pathext[0]
                with open(trade_file, 'r') as f:
                   old_open_price = float(f.readline().split(' ')[3].split(',')[0])
                   f.close()
                return

# if close is reversed, signal open signal            
def boll_greedy_policy():
    pass

# open, high, low, close == 4 prices
def read_4prices(filename):
    prices = None
    # drop suffix
    filename = os.path.splitext(filename)[0]
    # print (filename)
    if os.path.isfile(filename) == False: # in case not exist
        return prices
    try:
        with open(filename, 'r') as f:
            line=f.readline().rstrip('\n')
            # print (line, eval(line))
            prices = [float(x) for x in eval(line)]
            # print (prices)
            f.close()
            # close = eval(f.readline())[3]
    except Exception as ex:
        print ('read_4prices: %s' % filename)
    # print (close)
    return prices

open_price = 0
previous_close = 0
open_start_price = 0
last_bond = 0 # means uninitialized
last_balance = 0

ID_OPEN=0
ID_HIGH=1
ID_LOW=2
ID_CLOSE=3

# Whether symbol holding is closed forecly
def check_forced_close(symbol, direction, prices):
    if prices != None: # when do emulation
        if direction == 'buy' and open_price > prices[ID_LOW]:
            return ((open_price - prices[ID_LOW]) / open_price) >= 0.1  # rate is 10
        elif direction == 'sell' and open_price > 0 and open_price < prices[ID_HIGH]:
            return ((open_price - prices[ID_HIGH]) / open_price) <= -0.1  # rate is 10
        else:
            return False
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, 'quarter', '1'))
    if holding['result'] != True:
        return False
    if len(holding['holding']) == 0:
        return False
    # print (holding['holding'])
    for data in holding['holding']:
        if data['symbol'] == symbol:
            return data['%s_amount' % direction] == 0
    pass

# Check price and return calcuated profit, zero means do greedy open otherwite close holding
def check_with_direction(close, previous_close, open_price, open_start_price, l_dir, open_greedy):
    if l_dir == 'buy':
        if close > previous_close:
            if open_greedy == False:
                return (close - open_price) 
            else:
                if close > open_price: # already positive profit
                    return (close - open_price)
                else: # negative profit
                    if close < open_start_price:
                        return (close - open_start_price)
                    else:
                        return 0.0
        elif close < previous_close:
            if open_greedy == False:
                if close > open_start_price: # positive profit
                    return 0.0
                else:
                    return (close - open_start_price)
            else:
                if close > open_start_price: # positive profit
                    return 0.0
                else:
                    return (close - open_start_price)
    elif l_dir == 'sell':
        if close < previous_close:
            if open_greedy == False:
                return -(close - open_price) 
            else:
                if close < open_price: # already positive profit
                    return -(close - open_price)
                else: # negative profit
                    if close > open_start_price:
                        return -(close - open_start_price)
                    else:
                        return 0.0
        elif close > previous_close:
            if open_greedy == False:
                if close < open_start_price: # positive profit
                    return 0.0
                else:
                    return -(close - open_start_price)
            else:
                if close < open_start_price: # positive profit
                    return 0.0
                else:
                    return -(close - open_start_price)
    return 0.0

# Figure out current holding's amount
def calculate_amount(symbol):
    if last_bond == 0.0:
        return 1  # in case error, just process 1 ticket
    last_balance = quarter_auto_balance(symbol)
    if last_balance == 0.0:
        return 1 # just in case
    return int(last_balance / last_bond / 10 + 0.5)
    pass

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
            real= float(data['profit_real']) * 2
            return (avg, avg*real)
    return 0

def try_loadsave_with_names(status, names, load):
    for name in globals()[names]:
        if load: # from status to individual names
            globals()[name] = globals()[status][name]
        else: # collect individual names to status
            globals()[status][name] = globals()[name]

def loadsave_status(signal, load):
    if load: # load from file
        mode = 'r'
    else: # save to file
        mode = 'w'
    # process file
    with open(globals()['status_file'], mode) as f:
        if load:
            globals()['trade_status'] = json.load(f)
            try_loadsave_with_names('trade_status', 'names_%s' % signal, load)
        else:
            try_loadsave_with_names('trade_status', 'names_%s' % signal, load)
            json.dump(globals()['trade_status'], f)
        f.close()

names_tit2tat = ['trade_file',
                 'previous_close',
                 'open_start_price',
                 'open_price',
                 'open_cost',
                 'open_greedy',
                 'quarter_amount',
                 'thisweek_amount_pending',
                 'last_balance',
                 'last_bond',
                 'amount_ratio'];
def save_status_tit2tat():
    loadsave_status('tit2tat', load=False)

def load_status_tit2tat():
    loadsave_status('tit2tat', load=True)

quarter_amount = 1
thisweek_amount_pending = 0
close_greedy = False
open_greedy = False
def try_to_trade_tit2tat(subpath):
    global trade_file, old_close_mean
    global old_open_price
    global close_mean, close_upper, close_lower
    global old_close, bins, direction
    global l_trade_file
    global previous_close
    global open_greedy, close_greedy 
    global open_price, open_start_price
    global open_cost
    global quarter_amount, thisweek_amount_pending
    global last_bond, last_balance
    
    #print (subpath)
    event_path=subpath
    l_index = os.path.basename(event_path)
    # print (l_index, event_path)
    if True: # type 256, new file event
        prices = read_4prices(event_path)
        close = prices[ID_CLOSE]
        l_dir = ''
        reverse_follow_dir = ''
        if trade_file == '':
            print ('%9.3f' % close, '-')
        elif trade_file.endswith('.sell') == True: # sell order
            l_dir = 'sell'
            reverse_follow_dir = 'buy'
            print ('%8.3f' % -close, '%9.3f' % open_price, l_dir, 'gate %9.3f' % open_start_price)
        elif trade_file.endswith('.buy') == True: # buy order
            l_dir = 'buy'
            reverse_follow_dir = 'sell'
            print ('%9.3f' % close, '%8.3f' % -open_price, l_dir, 'gate %9.3f' % open_start_price)
        if close == 0: # in case read failed
            return
        if True:
            if True:
                if previous_close == 0:
                    previous_close = close
                    close_greedy = False
                    return
                
                symbol=symbols_mapping[figure_out_symbol_info(event_path)]
                
                new_open = True
                forced_close = False
                new_open_start_price = 0
                if trade_file != '':
                    new_open = False
                    if l_dir == 'buy':
                        t_amount = 0 if ((open_price - prices[ID_LOW]) / open_price) > 0.1 else 1
                        new_open_start_price = prices[ID_LOW]
                    else: # sell
                        t_amount = 0 if ((prices[ID_HIGH] - open_price) / open_price) > 0.1 else 1
                        new_open_start_price = prices[ID_HIGH]
                    if not options.emulate: # if emualtion, figure it manually
                        (loss, t_amount) = check_holdings_profit(symbol, 'quarter', l_dir)
                    if t_amount == 0:
                        forced_close = True
                if forced_close:
                    forced_close = False
                    open_greedy = True
                    # suffered forced close
                    globals()['signal_close_order_with_%s' % l_dir](l_index, trade_file, close)
                    print (trade_timestamp(), 'detected forced close signal %s at %s => %s' % (l_dir, previous_close, close))
                    # action likes new_open equals true, but take original l_dir as it
                    issue_quarter_order_now(symbol, l_dir, 1, 'open')
                    (open_price, open_cost) = real_open_price_and_cost(symbol, 'quarter', l_dir) if options.emulate else (close, 0.001)
                    if l_dir == 'buy' and open_start_price < new_open_start_price:
                        open_start_price = new_open_start_price
                    elif l_dir == 'sell' and open_start_price > new_open_start_price:
                        open_start_price = new_open_start_price
                if new_open == False:
                    current_profit = check_with_direction(close, previous_close, open_price, open_start_price, l_dir, open_greedy)
                    issuing_close = False
                    if current_profit > open_cost: # yes, positive 
                        # do close
                        issuing_close = True
                    elif current_profit < -open_cost: # no, negative 
                        # do close
                        issuing_close = True
                        open_start_price = open_price # when seeing this price, should close, init only once
                    elif current_profit == 0: # partly no, but still positive consider open_start_price, do greedy process
                        # emit open again signal
                        open_greedy = True
                        greedy_action = ''
                        greedy_status = 'holding'
                        if l_dir == 'buy':
                            if close > previous_close:
                                greedy_action = 'close'
                                greedy_status = 'maybe closed'
                            elif close < previous_close:
                                greedy_action = 'open'
                        elif l_dir == 'sell':
                            if close < previous_close:
                                greedy_action = 'close'
                                greedy_status = 'maybe closed'
                            elif close > previous_close:
                                greedy_action = 'open'
                        print (trade_timestamp(), 'greedy signal %s at %s => %s (%s)' % (l_dir, previous_close, close, greedy_status))
                        if greedy_action != '': # update amount
                            if quarter_amount > thisweek_amount_pending:
                                thisweek_amount = math.ceil(quarter_amount * abs(previous_close - close) / previous_close * 10)
                                l_thisweek_amount = math.ceil(quarter_amount / amount_ratio)
                                if thisweek_amount < l_thisweek_amount:
                                    thisweek_amount = l_thisweek_amount
                            else:
                                thisweek_amount = math.ceil(quarter_amount / amount_ratio / amount_ratio)
                            thisweek_amount_pending += thisweek_amount
                        if greedy_action == 'close': # yes, close action pending
                            issue_thisweek_order_now_conditional(symbol, l_dir, 0, greedy_action)
                            issue_thisweek_order_now_conditional(symbol, reverse_follow_dir, 0, greedy_action, False)
                            # open following order
                            issue_thisweek_order_now(symbol, l_dir, thisweek_amount, 'open')
                            thisweek_amount_pending = 0
                        elif greedy_action == 'open': # yes, open action pending
                            issue_thisweek_order_now(symbol, l_dir, thisweek_amount, greedy_action)
                            # first close current order
                            issue_thisweek_order_now_conditional(symbol, reverse_follow_dir, 0, 'close')
                            # secondly open new order
                            issue_thisweek_order_now(symbol, reverse_follow_dir, thisweek_amount, greedy_action)
                        previous_close = close
                    else:
                        previous_close = close
                        return
                    if issuing_close == True:
                        globals()['signal_close_order_with_%s' % l_dir](l_index, trade_file, close)
                        t_bond = query_bond(symbol, 'quarter', l_dir)
                        if t_bond > 0:
                            last_bond = t_bond
                        issue_quarter_order_now_conditional(symbol, l_dir, 0, 'close', False)
                        # and open again, just like new_open == True
                        new_open = True
                        if open_greedy == True:
                            close_greedy = True
                            open_greedy = False
                        old_balance = last_balance
                        last_balance = query_balance(symbol)
                        delta_balance = (last_balance - old_balance) * 100 / old_balance if old_balance != 0 else 0
                        amount = quarter_amount
                        quarter_amount = last_balance / last_bond / amount_ratio if last_bond > 0 else 1
                        if quarter_amount < 1:
                            quarter_amount = 1
                        print ('update quarter_amount from %s=>%s(ratio=%f%s), bond=%f balance=%f->%f,%f%%' %
                               (amount, quarter_amount, amount_ratio, '*' if amount_ratio != default_amount_ratio else '',
                                last_bond,
                                old_balance, last_balance, delta_balance))
                if close_greedy == True:
                    print (trade_timestamp(), 'greedy signal %s at %s => %s (%s%s)' % (l_dir, previous_close, close,
                                                                                       'forced ' if forced_close == True else '',  'closed'))
                    issue_thisweek_order_now_conditional(symbol, l_dir, 0, 'close', False)
                    issue_thisweek_order_now_conditional(symbol, reverse_follow_dir, 0, 'close', False)
                    thisweek_amount_pending = 0
                    close_greedy = False
                if new_open == True:
                    if close > previous_close:
                        l_dir = 'buy'
                    elif close < previous_close:
                        l_dir = 'sell'
                    else:
                        previous_close = close
                        return
                    if forced_close == True: # should check open_start_price again
                        if l_dir == 'buy' and open_start_price > open_price:
                            open_start_price = open_price
                        elif l_dir == 'sell' and open_start_price < open_price:
                            open_start_price = open_price
                    trade_file = ''
                    open_greedy = False
                    close_greedy = False
                    open_price = 0.0
                    open_cost = 0.0
                    
                    if l_dir == '': # no updating
                        previous_close = close
                        return
                    
                    # do open
                    trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, l_dir)
                    # print (trade_file)
                    globals()['signal_open_order_with_%s' % l_dir](l_index, trade_file, close)
                    issue_quarter_order_now(symbol, l_dir, quarter_amount, 'open')
                    
                    (open_price, open_cost) = real_open_price_and_cost(symbol, 'quarter', l_dir) if options.emulate else (close, 0.001)
                    
                    if open_start_price == 0:
                        open_start_price = prices[ID_OPEN] # when seeing this price, should close, init only once
                    
                    previous_close = close

direction = 0
def try_to_trade_simple(subpath):
    global trade_file, old_close_mean
    global old_open_price
    global close_mean, close_upper, close_lower
    global old_close, bins, direction
    global l_trade_file
    bins = int(options.bins)
    #print (subpath)
    event_path=subpath
    l_index = os.path.basename(event_path)
    # print (l_index, event_path)
    if True: # type 256, new file event
        close = read_close(event_path)
        if trade_file == '':
            print ('%9.3f' % close, 0, direction)
        elif trade_file.endswith('.sell') == True: # sell order
            print ('%8.3f' % -close, '%9.3f' % old_open_price, direction)
        elif trade_file.endswith('.buy') == True: # buy order
            print ('%9.3f' % close, '%8.3f' % -old_open_price, direction)
        if close == 0: # in case read failed
            return
        if True:
                fresh_trade = False
                symbol=symbols_mapping[figure_out_symbol_info(event_path)]
                # print (symbol)
                now_close_mean = int(close * float(options.cmp_scale))
                if old_close_mean == 0:
                    old_close_mean = now_close_mean
                    direction = 0
                    l_trade_file = ''
                elif now_close_mean < old_close_mean:
                    if direction >= 0:
                        direction = -1
                    else:
                        direction = direction - 1
                elif now_close_mean > old_close_mean:
                    if direction <= 0:
                        direction = 1
                    else:
                        direction = direction + 1
                else: # now_close_mean == old_close_mean, see as reverse direction
                    if direction < 0:
                        direction = 1
                    elif direction > 0:
                        direction = - 1
                    else:
                        pass
                if direction < 0:
                    l_dir = 'sell'
                elif direction > 0:
                    l_dir = 'buy'
                else:
                    l_dir = ''
                    fresh_trade = True # let it go
                    pass
                # if two times, abs(direction) > bins==1
                if abs(direction) > bins :
                    if trade_file == '':
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, l_dir)
                        # print (trade_file)
                        globals()['signal_open_order_with_%s' % l_dir](l_index, trade_file, close)
                        old_open_price = close
                    elif trade_file.endswith(l_dir) == True:
                        pass # same direction
                    else:
                        globals()['signal_close_order_with_%s' % l_dir](l_index, trade_file, close)
                        time.sleep(30)
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, l_dir)
                        # print (trade_file)
                        globals()['signal_open_order_with_%s' % l_dir](l_index, trade_file, close)
                        old_open_price = close                        
                    l_trade_file = ''
                    fresh_trade = True
                    direction = direction / abs(direction) # clean
                if fresh_trade == True: # ok, fresh trade
                    pass
                elif trade_file == '':  # no open trade
                    pass
                elif l_trade_file != '': # do greedy processing
                    # write close to close_greedy signal for possible rate
                    global policy_notify
                    with open(policy_notify, 'w') as f:
                        f.write('%s' % close)
                        f.close()
                    print (trade_timestamp(), 'greedy cleanup %s with %f' % (os.path.basename(l_trade_file), close))
                    l_trade_file = ''
                elif options.policy == 'simple_greedy':
                    if l_dir == 'sell':
                        l_dir = 'buy'  # reversed
                    elif l_dir == 'buy':
                        l_dir = 'sell'
                    l_trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, l_dir)
                    # print (l_trade_file)
                    globals()['signal_open_order_with_%s' % l_dir](l_index, l_trade_file, close)
                    pass
                old_close_mean = now_close_mean
                old_close = close

# inotify specified dir to plot living price
# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def try_to_trade_boll(subpath):
    global trade_file, old_close_mean
    global old_open_price
    global close_mean, close_upper, close_lower
    global old_close, bins
    #print (subpath)
    event_path=subpath
    l_index = os.path.basename(event_path)
    # print (l_index, event_path)
    if True: # type 256, new file event
        boll = read_boll(event_path)
        close = read_close(event_path)
        print ('['+' '.join('%9.3f' % k for k in boll)+']', end=' ', flush=False)
        if trade_file == '':
            print ('%9.3f' % close, 0)
        elif trade_file.endswith('.sell') == True: # sell order
            print ('%8.3f' % -close, '%9.3f' % old_open_price)
        elif trade_file.endswith('.buy') == True: # buy order
            print ('%9.3f' % close, '%8.3f' % -old_open_price)
        if boll == 0 or close == 0: # in case read failed
            return
        if math.isnan(boll[0]) == False:
                close_mean[l_index]=boll[0]
                close_upper[l_index]=boll[1]
                close_lower[l_index]=boll[2]
                fresh_trade = False
                symbol=symbols_mapping[figure_out_symbol_info(event_path)]
                # print (symbol)
                now_close_mean = int(boll[0] * float(options.cmp_scale))
                if old_close_mean == 0:
                    old_close_mean = now_close_mean
                if now_close_mean < old_close_mean: # open sell order
                    if trade_file == '' and check_close_to_mean(boll, close) and check_open_order_gate(symbol, 'sell', close):
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'sell')
                        # print (trade_file)
                        signal_open_order_with_sell(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                        bins = int(options.bins)
                elif now_close_mean > old_close_mean: # open buy order
                    if trade_file == '' and check_close_to_mean(boll, close) and check_open_order_gate(symbol, 'buy', close):
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'buy')
                        # print (trade_file)
                        signal_open_order_with_buy(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                        bins = int(options.bins)
                if fresh_trade == True: # ok, fresh trade
                    pass
                elif trade_file == '':  # no open trade
                    bins = 0
                    pass
                # close is touch upper
                elif old_close_mean < now_close_mean and trade_file.endswith('.sell') == True :
                    # check if return bigger than fee
                    if check_close_sell_fee_threshold(old_open_price, close, amount) == True:
                        signal_close_order_with_buy(l_index, trade_file, close)
                        trade_file = ''  # make trade_file empty to indicate close
                        old_open_close = 0
                        bins = -1
                        # fast open now
                        time.sleep(5)
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'buy')
                        # print (trade_file)
                        signal_open_order_with_buy(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                        bins = int(options.bins)
                # close is touch lower
                elif old_close_mean > now_close_mean and trade_file.endswith('.buy') == True :
                    # check if return bigger than fee
                    if check_close_sell_fee_threshold(old_open_price, close, amount) == True:
                        signal_close_order_with_sell(l_index, trade_file, close)
                        trade_file = ''  # make trade_file empty to indicate close
                        old_open_close = 0
                        bins = -1
                        # fast open now
                        time.sleep(5)
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'sell')
                        # print (trade_file)
                        signal_open_order_with_sell(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                        bins = int(options.bins)
                elif options.policy == 'boll_greedy':
                    l_dir = ''
                    if trade_file.endswith('.sell') == True: # sell direction
                        if close > old_close:
                            l_dir = 'sell'
                            bins = bins - 1
                        else:
                            bins = int(options.bins) # reset as first open order
                        pass
                    else : # open direction
                        if close < old_close:
                            l_dir = 'buy'
                            bins = bins - 1
                        else:
                            bins = int(options.bins) # reset as first open order
                        pass
                    if l_dir != '': # yes, new order
                        l_trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, l_dir)
                        # print (l_trade_file)
                        globals()['signal_open_order_with_%s' % l_dir](l_index, l_trade_file, close)
                        time.sleep(5) # wait for signal processed
                        pass
                    if bins < 0: # write close to boll_greedy signal for possible rate
                        global policy_notify
                        with open(policy_notify, 'w') as f:
                            f.write('%s' % close)
                            f.close()
                        time.sleep(60) # wait 1m for trade is finished, but no guarentee
                        pass
                if close_lower.count() > 2 * latest_to_read:
                    close_lower = close_lower[-latest_to_read:]
                    close_mean = close_mean[-latest_to_read:]
                    close_upper = close_upper[-latest_to_read:]
                    print ('Reduce data size to %d', close_lower.count())
                old_close_mean = now_close_mean
                old_close = close

def read_ema(filename):
    ema = 0
    try:
        with open(filename, 'r') as f:
            line = f.readline().rstrip('\n')
            ema = [float(x) for x in line.split(',')]
            f.close()
    except Exception as ex:
        print ('read_ema: %s\n' % filename)
    return ema

total_revenue = 0
previous_close_price = 0
total_orders = 0
old_total_revenue = 0

# emas[0] is old, emas[1] is new. The save to closes[2]
def ema_greedy_policy(direction, emas, closes):
    if direction == 'sell':
        # only use first period of ema
        if (emas[0] < emas[1]) and abs(emas[0] - emas[1]) > 1 and (closes[0] < closes[1]) and abs(closes[0] - closes[1]) > 1: # double revert
            return 'close'
        elif (closes[0] < closes[1]) and abs(closes[0] - closes[1]) > 1: # close revert
            return 'open'
        else:
            return 'keep'
    else: # 'buy'
        if (emas[0] > emas[1]) and abs(emas[0] - emas[1]) > 1 and (closes[0] > closes[1]) and abs(closes[0] - closes[1]) > 1 : # double revert
            return 'close'
        elif (closes[0] > closes[1]) and abs(closes[0] - closes[1]) > 1 : # close revert
            return 'open'
        else:
            return 'keep'

# emas[0] is old, emas[1] is new. The save to closes[2]        
def close_ema_policy(direction, emas, closes):
    if direction == 'sell':
        # only use first period of ema
        if (emas[0] < emas[1]) and abs(emas[0] - emas[1]) > 1 and (closes[0] < closes[1]) and abs(closes[0] - closes[1]) > 1: # double revert
            return 'close'
        elif (closes[0] < closes[1]) and abs(closes[0] - closes[1]) > 1: # close revert
            return 'open'
        else:
            return 'keep'
    else: # 'buy'
        if (emas[0] > emas[1]) and abs(emas[0] - emas[1]) > 1 and (closes[0] > closes[1]) and abs(closes[0] - closes[1]) > 1 : # double revert
            return 'close'
        elif (closes[0] > closes[1]) and abs(closes[0] - closes[1]) > 1 : # close revert
            return 'open'
        else:
            return 'keep'
    
amount = 1
old_ema_0 = 0
direction = ''
old_close = 0
average_open_price = 0
old_delta = 0
delta = 0
def try_to_trade_close_ema(subpath):
    global trade_file, old_close_mean
    global total_revenue, previous_close_price, total_orders
    global old_open_price, old_ema_0, old_close
    global trade_notify
    global direction
    global average_open_price, order_num
    global old_total_revenue
    global delta, old_delta
    #print (subpath)
    event_path=subpath
    l_index = os.path.basename(event_path)
    # print (l_index, event_path)
    if True: # type 256, new file event
        ema = read_ema(event_path)
        ema_0 = ema[int(options.which_ema)]
        close = read_close(event_path)
        if options.emulate:
            if direction == 'sell' or direction == '-':
                delta = (average_open_price - close) * order_num
            elif direction == 'buy' or direction == '+':
                delta = (close - average_open_price) * order_num
            else:
                delta = 0
            if delta != 0:
                print ('%9.3f %9.3f %9.3f #%9.3f=>%9.3f' % (ema_0, close, average_open_price, old_delta, delta))
        if ema == 0 or close == 0: # in case read failed
            return
        if math.isnan(ema_0) == False:
                fresh_trade = False
                symbol=symbols_mapping[figure_out_symbol_info(event_path)]
                # print (symbol)
                if old_ema_0 == 0:
                    old_ema_0 = ema_0
                if old_close == 0:
                    old_close = close
                if direction == '' and close < old_close : # open sell order
                    if trade_file == '' and check_open_order_gate(symbol, 'sell', close):
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'sell')
                        #print (trade_file)
                        # print (previous_close_price, close)
                        signal_open_order_with_sell(l_index, trade_file, close)
                        fresh_trade = True
                        direction = '-' # should switch to 'sell'
                        average_open_price = close
                        order_num = 1
                        total_orders += 1
                        print ('<%9.3f %9.3f' % (ema_0, close))
                elif direction == '' and close > old_close: # open buy order
                    if trade_file == '' and check_open_order_gate(symbol, 'buy', close):
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'buy')
                        # print (trade_file)
                        #print (previous_close_price, close)
                        signal_open_order_with_buy(l_index, trade_file, close)
                        fresh_trade = True
                        direction = '+' # should switch to 'buy'
                        average_open_price = close
                        order_num = 1
                        total_orders += 1
                        print ('<%9.3f %9.3f' % (ema_0, close))
                if fresh_trade == True: # ok, fresh trade
                    pass
                elif trade_file == '':  # no open trade
                    pass
                elif direction == '+': # close or ema_0 is increasing
                    if close > old_close : # just use close
                        direction = 'buy'
                    elif close <= ema_0 or old_delta > delta: # force it closed
                        signal_close_order_with_sell(l_index, trade_file, close)
                        delta = (close - average_open_price) * order_num
                        average_open_price = 0
                        old_total_revenue = total_revenue
                        total_revenue += delta
                        trade_file = ''
                        direction = ''
                        print ('%9.3f %9.3f> return %f' % (ema_0, close, delta))
                        delta = 0
                        old_delta = 0
                    else: # abnormal case
                        print ('stay unchanged, neight to close nor to buy, %9.3f~%9.3f %9.3f' % (close, old_close, ema_0))
                elif direction == 'buy' :
                    if old_delta !=0 and old_delta > delta : # return is decreasing
                        signal_close_order_with_sell(l_index, trade_file, close)
                        delta = (close - average_open_price) * order_num
                        average_open_price = 0
                        total_revenue += delta
                        trade_file = ''
                        direction = ''
                        print ('%9.3f %9.3f> return %f' % (ema_0, close, delta))                        
                    elif close <= ema_0 :
                        direction = '+' # may trigger close
                        # more greedy
                        if order_num < int(options.order_num):
                            signal_open_order_with_buy(l_index, trade_file, close)
                            average_open_price = (average_open_price * order_num + close) / (order_num+1)
                            order_num += 1
                            total_orders += 1
                elif direction == '-': # close or ema_0 is decreasing
                    if close < old_close : # just use close
                        direction = 'sell'
                    elif close >= ema_0 or old_delta > delta: # force it closed
                        signal_close_order_with_buy(l_index, trade_file, close)
                        delta = (average_open_price - close) * order_num
                        average_open_price = 0
                        old_total_revenue = total_revenue
                        total_revenue += delta
                        trade_file = ''
                        direction = ''
                        print ('%9.3f %9.3f> return %f' % (ema_0, close, delta))
                        delta = 0
                        old_delta = 0
                    else: # abnormal case
                        print ('stay unchanged, neight to close nor to sell, %9.3f~%9.3f %9.3f' % (close, old_close, ema_0))
                elif direction == 'sell' :
                    if old_delta != 0 and old_delta > delta: # return is decreasing
                        signal_close_order_with_buy(l_index, trade_file, close)
                        delta = (average_open_price - close) * order_num
                        average_open_price = 0
                        total_revenue += delta
                        trade_file = ''
                        direction = ''
                        print ('%9.3f %9.3f> return %f' % (ema_0, close, delta))                        
                    elif close >= ema_0 :
                        direction = '-' # may trigger close
                        # more greedy
                        if order_num < int(options.order_num):
                            signal_open_order_with_sell(l_index, trade_file, close)
                            average_open_price = (average_open_price * order_num + close) / (order_num+1)
                            order_num += 1
                            total_orders += 1
                old_ema_0 = ema_0
                old_close = close
                old_delta = delta
        # used when do emulation
        if options.emulate:
            with open('%s.goon' % trade_notify, 'w') as f:
                f.write('goon')
                f.close()
    
def try_to_trade_old(subpath):
    global trade_file, old_close_mean
    global total_revenue, previous_close_price, total_orders
    global old_open_price, old_ema_0, old_close
    global trade_notify
    global direction
    global average_close_price, order_num
    global limit_direction, limit_amount, limit_price, limit_symbol
    #print (subpath)
    event_path=subpath
    l_index = os.path.basename(event_path)
    # print (l_index, event_path)
    if True: # type 256, new file event
        ema = read_ema(event_path)
        ema_0 = ema[int(options.which_ema)]
        close = read_close(event_path)
        if options.emulate:
            if direction == 'sell':
                delta = old_open_price - close
            elif direction == 'buy':
                delta = close - old_open_price
            else:
                delta = 0
            print (ema_0, close, old_open_price, '#%9.3f' % delta)
        if ema == 0 or close == 0: # in case read failed
            return
        if math.isnan(ema_0) == False:
                fresh_trade = False
                symbol=symbols_mapping[figure_out_symbol_info(event_path)]
                # print (symbol)
                if old_ema_0 == 0:
                    old_ema_0 = ema_0
                if ema_0 < old_ema_0 and close < old_close : # open sell order
                    if trade_file == '' and check_limit_direction('sell') and check_open_order_gate(symbol, 'sell', close):
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'sell')
                        #print (trade_file)
                        # print (previous_close_price, close)
                        signal_open_order_with_sell(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                        direction = 'sell'
                        average_close_price = close
                        order_num = 1
                        print ('<%9.3f %9.3f\n' % (ema_0, close))
                elif ema_0 > old_ema_0 and close > old_close: # open buy order
                    if trade_file == '' and check_limit_direction('buy') and check_open_order_gate(symbol, 'buy', close):
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'buy')
                        # print (trade_file)
                        #print (previous_close_price, close)
                        signal_open_order_with_buy(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                        direction = 'buy'
                        average_close_price = close
                        order_num = 1
                        print ('<%9.3f %9.3f\n' % (ema_0, close))
                if fresh_trade == True: # ok, fresh trade
                    pass
                elif trade_file == '':  # no open trade
                    pass
                # close is touch upper
                elif (ema_0 > old_ema_0 or close > old_close) and trade_file.endswith('.sell') == True :
                    # check if return bigger than fee
                    if options.policy == 'ema_greedy':
                        act = ema_greedy_policy('sell', [old_ema_0, ema_0],
                                                [old_close, close])
                        if act == 'open' and order_num < 2:
                            signal_open_order_with_sell(l_index, trade_file, close)
                            average_close_price = (average_close_price + close)/2.0
                            old_open_price = (old_open_price + close)/2.0
                            order_num += 1
                            print (' %9.3f %9.3f\n' % (ema_0, close))
                            pass
                        # igore close signal
                        elif False and act == 'close' and abs(average_close_price - close) > 1:
                            signal_close_order_with_buy(l_index, trade_file, close)
                            print ('return %f\n' % ((average_close_price - close) * order_num))
                            total_revenue += (average_close_price - close) * order_num
                            trade_file = ''
                            print ('%9.3f %9.3f>\n' % (ema_0, close))
                            # open trade again
                            try_to_trade_old(subpath)
                            pass
                        elif act == 'keep':
                            pass
                    if check_close_sell_fee_threshold(old_open_price, close, amount) == True:
                        signal_close_order_with_buy(l_index, trade_file, close)
                        if old_open_price < close:
                            previous_close_price = -close # negative means ever sold
                        else:
                            previous_close_price = 0
                        print ('return = ', old_open_price - close)
                        total_revenue += old_open_price - close
                        total_orders += 1
                        trade_file = ''  # make trade_file empty to indicate close
                        direction = ''
                # close is touch lower
                elif (ema_0 < old_ema_0 or close < old_close) and trade_file.endswith('.buy') == True :
                    # check if return bigger than fee
                    if options.policy == 'ema_greedy':
                        act = ema_greedy_policy('buy', [old_ema_0, ema_0],
                                                [old_close, close])
                        if act == 'open' and order_num < 5:
                            signal_open_order_with_buy(l_index, trade_file, close)
                            average_close_price = (average_close_price + close)/2.0
                            old_open_price = (old_open_price + close)/2.00
                            order_num += 1
                            print (' %9.3f %9.3f\n' % (ema_0, close))
                            pass
                        elif False and act == 'close' and abs(close - average_close_price) > 1:
                            signal_close_order_with_sell(l_index, trade_file, close)
                            print ('return %f\n' % ((close - average_close_price) * order_num))
                            total_revenue += (close - average_close_price) * order_num
                            trade_file = ''
                            print ('%9.3f %9.3f>\n' % (ema_0, close))
                            # open trade again
                            try_to_trade_old(subpath)
                            pass
                        elif act == 'keep':
                            pass
                    if check_close_sell_fee_threshold(old_open_price, close, amount) == True:
                        signal_close_order_with_sell(l_index, trade_file, close)
                        if old_open_price > close:
                            previous_close_price = close # positive means ever bought
                        else:
                            previous_close_price = 0
                        print ('return = ', close - old_open_price)
                        total_revenue += close - old_open_price
                        total_orders += 1
                        trade_file = ''  # make trade_file empty to indicate close
                        direction = ''
                old_ema_0 = ema_0
                old_close = close
        # used when do emulation
        if options.emulate:
            with open('%s.goon' % trade_notify, 'w') as f:
                f.write('goon')
                f.close()

def try_to_trade_ewma(subpath):
    if options.policy == 'close_ema':
        try_to_trade_close_ema(subpath)
    else:
        try_to_trade_old(subpath)
                
# generate file list
def with_listdir(l_dir):
    return os.listdir(l_dir)

# v2, fast than listdir
def with_scandir(l_dir):
    files = list()
    with os.scandir(l_dir) as it:
        for entry in it:
            if entry.name.endswith('.boll') == True:
                files.append(entry.name)
    return files


# process saved prices in specified dir
def plot_saved_price(l_dir):
    global old_close_mean
    try:
        files = with_scandir(l_dir)
        files.sort()
        to_read = len(files)
        if to_read > latest_to_read:
            to_read = latest_to_read
        print ('Total %d files, read latest %d' % (len(files), to_read))
        for fname in files[-to_read:]:
            fpath = os.path.join(l_dir, fname)
            boll = read_boll(fpath)
            try:
                    # ignore nan data
                    if math.isnan(boll[0]) == False:
                            close_mean[fname]=boll[0]
                            close_upper[fname]=boll[1]
                            close_lower[fname]=boll[2]
                            # save old close_mean
                            old_close_mean = boll[0]
            except Exception as ex:
                    print (fpath)
        files = None
        #print (close_mean)
    except Exception as ex:
        print (traceback.format_exc())

# v2, fast than listdir
def with_scandir_ewma(l_dir):
    files = list()
    with os.scandir(l_dir) as it:
        for entry in it:
            if entry.name.endswith('.ewma') == True:
                files.append(entry.name)
    return files

def with_scandir_tit2tat(l_dir):
    files = list()
    with os.scandir(l_dir) as it:
        for entry in it:
            if entry.name.endswith('.t2t') == True:
                files.append(entry.name)
    return files

# try to emulate signal notification
def emul_signal_notify(l_dir, l_signal):
    global old_close_mean, signal_notify, trade_notify
    global total_revenue, total_orders
    try:
        files = globals()['with_scandir_%s' % l_signal](l_dir)
        files.sort()
        total_files = len(files)
        to_read = int (random.random() * total_files)
        start_at = int (random.random() * (total_files - to_read))
        print ('Total %d files, read latest %d from %d' % (total_files, to_read, start_at))
        for fname in files[start_at:start_at+to_read]:
            fpath = os.path.join(l_dir, fname)
            # print (fpath)
            wait_signal_notify(fpath, l_signal, '')
        files = None
        if total_orders > 0:
            msg = 'Total revenue %.2f average %.2f(%d) with %d data from %d' % (total_revenue, total_revenue / total_orders, total_orders, to_read, start_at)
            with open("%s_new_result.txt" % l_dir, 'a') as f:
                f.write('%s\n' % msg)
                f.close()
                print (msg)
        #print (close_mean)
    except Exception as ex:
        print (traceback.format_exc())

# ['Path', 'is', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min\n']
# ['Watching', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min\n']
# ['Change', '54052560', 'in', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1535123280000,', 'flags', '70912Change', '54052563', 'in', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1535123280000.lock,', 'flags', '66304', '-', 'matched', 'directory,', 'notifying\n']

fence_count = 0

def wait_signal_notify(notify, signal, shutdown):
    global fee_threshold, fee_file, amount_file
    global fence_count
    global amount
    global trade_file
    shutdown_on_close = False
    while True:
        command = ['fswatch', '-1', notify, shutdown]
        try:
            # check if should read fee from file
            if os.path.isfile(fee_file) and os.path.getsize(fee_file) > 0:
                with open(fee_file) as f:
                    t_fee_threshold = float(f.readline())
                    f.close()
                    if t_fee_threshold != fee_threshold: # update if diff
                        fee_threshold = t_fee_threshold
                        print ('fee_threshold updated to %f' % fee_threshold)
            if os.path.isfile(amount_file) and os.path.getsize(amount_file) > 0:
                with open(amount_file) as f:
                    t_amount = int(f.readline())
                    f.close()
                    if t_amount != amount: # update amount
                        print ('amount updated from %d to %d' % (amount, t_amount))
                        amount = t_amount
        except Exception as ex:
            fee_threshold = default_fee_threshold
            print ('fee_threshold reset to %f' % fee_threshold)
        print ('', end='', flush=True)
        try:
            if options.emulate:
                globals()['try_to_trade_%s' % signal](notify)
                globals()['save_status_%s' % signal]()
                break
            if not options.one_shot and not options.do_self_trigger:
                result = subprocess.run(command, stdout=PIPE, encoding=default_encoding) # wait file modified
                # if received shutdown notify, close all order
                if shutdown != '' and shutdown in result.stdout:
                    shutdown_on_close = True
                    print ('shutdown triggered, shutdown when closed')
                    with open(shutdown, 'w') as f:
                        f.close()
            if shutdown_on_close and trade_file == '':
                print (trade_timestamp(), 'shutdown now')
                break
            with open(notify, 'r') as f:
                subpath = f.readline().rstrip('\n')
                f.close()
                #print (subpath)
                globals()['try_to_trade_%s' % signal](subpath)
                globals()['save_status_%s' % signal]()
            fence_count = 0
            if shutdown_on_close and trade_file == '':
                print (trade_timestamp(), 'shutdown now')
                break
            if options.one_shot or options.do_self_trigger:
                break
        except FileNotFoundError as fnfe:
            print (fnfe)
            break
        except Exception as ex:
            fence_count += 1
            print (ex)
            print (traceback.format_exc())
            if fence_count > 20: # exceptions 20 continiously
                break
            continue

# wait on ema_notify for signal
def wait_ewma_notify(notify, shutdown):
    global fee_threshold, fee_file, amount_file
    global fence_count
    global amount
    global trade_file
    shutdown_on_close = False
    while True:
        command = ['fswatch', '-1', notify, shutdown]
        try:
            # check if should read fee from file
            if os.path.isfile(fee_file) and os.path.getsize(fee_file) > 0:
                with open(fee_file) as f:
                    t_fee_threshold = float(f.readline())
                    f.close()
                    if t_fee_threshold != fee_threshold: # update if diff
                        fee_threshold = t_fee_threshold
                        print ('fee_threshold updated to %f' % fee_threshold)
            if os.path.isfile(amount_file) and os.path.getsize(amount_file) > 0:
                with open(amount_file) as f:
                    t_amount = int(f.readline())
                    f.close()
                    if t_amount != amount: # update amount
                        print ('amount updated from %d to %d' % (amount, t_amount))
                        amount = t_amount
        except Exception as ex:
            fee_threshold = default_fee_threshold
            print ('fee_threshold reset to %f' % fee_threshold)
        print ('', end='', flush=True)
        try:
            if options.emulate:
                globals()['try_to_trade_%s' % signal](notify)
                break
            
            result = subprocess.run(command, stdout=PIPE, encoding=default_encoding) # wait file modified
            if shutdown != '' and os.path.isfile(shutdown) and os.path.getsize(shutdown) > 0:
                shutdown_on_close = True
                print (trade_timestamp(), 'shutdown triggered, shutdown when closed')
                with open(shutdown, 'w') as f:
                    f.close()
            if shutdown_on_close and trade_file == '':
                print (trade_timestamp(), 'shutdown now')
                break
            with open(notify, 'r') as f:
                subpath = f.readline().rstrip('\n')
                f.close()
                # print (subpath)
                globals()['try_to_trade_%s' % signal](subpath)
            fence_count = 0
            if shutdown_on_close and trade_file == '':
                print (trade_timestamp(), 'shutdown now')
                break
        except FileNotFoundError as fnfe:
            print (fnfe)
            break
        except Exception as ex:
            fence_count += 1
            print (ex)
            print (traceback.format_exc())
            if fence_count > 20:
                break
            continue

def read_int_var(filename, var_name):
    l_var = globals()[var_name]
    if os.path.isfile(filename) and os.path.getsize(filename)>0:
        # check if should read from file
        with open(filename) as f:
            old_var = l_var
            try:
                l_var = float(f.readline())
                if old_var != l_var:
                    print ('%s updated to %f' % (var_name, l_var))
                else:
                    print ('%s unchanged, unlink %s' % (var_name, filename))
                    os.unlink(filename)
            except Exception as ex:
                l_var = globals()['default_%s' % var_name]
                print ('%s reset to default %f' % (var_name, l_var))
        f.close()
        globals()[var_name] = l_var
        return True
    return False

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--signal_notify", dest="signal_notify",
                  help="specify signal notifier")
parser.add_option("", "--startup_notify", dest="startup_notify",
                  help="specify startup notifier")
parser.add_option("", "--shutdown_notify", dest="shutdown_notify",
                  help="specify shutdown notifier")
parser.add_option("", "--pick_old_order", dest='pick_old_order',
                  action="store_true", default=False,
                  help="do not pick old order")
parser.add_option('', '--emulate', dest='emulate',
                  help="try to emulate trade notify")
parser.add_option('', '--skip_gate_check', dest='skip_gate_check',
                  action="store_false", default=True,
                  help="Should skip checking gate when open trade")
parser.add_option('', '--cmp_scale', dest='cmp_scale', default='1',
                  help='Should multple it before do compare')
parser.add_option('', '--policy', dest='policy',
                  help="use specified trade policy, ema_greedy/close_ema/boll_greedy/simple_greedy")
parser.add_option('', '--which_ema', dest='which_ema', default=0, 
                  help='using with one of ema')
parser.add_option('', '--order_num', dest='order_num',
                  help='how much orders')
parser.add_option('', '--fee_amount', dest='fee_amount',
                  help='take amount int account with fee')
parser.add_option('', '--signal', dest='signals', default=['tit2tat'],
                  action='append',
                  help='use wich signal to generate trade notify and also as prefix, boll, simple, tit2tat')
parser.add_option('', '--latest', dest='latest_to_read', default='1000',
                  help='only keep that much old values')
parser.add_option('', '--dir', dest='dirs', default=[],
                  action='append',
                  help='target dir should processing')
parser.add_option('', '--bins', dest='bins', default=0,
                  help='wait how many reverse, 0=once, 1=twice')
parser.add_option('', '--nolog', dest='nolog', default=0,
                  help='Do not log to file')
parser.add_option('', '--ratio', dest='amount_ratio', default=9,
                  help='default trade ratio of total amount')
parser.add_option('', '--open_start_price', dest='open_start_price',
                  help='init open_start_proce')
parser.add_option('', '--previous_close', dest='previous_close',
                  help='init previous_close')
parser.add_option('', '--restore_status', dest='restore_status',
                  help='restore status from status_file')
parser.add_option('', '--one_shot', dest='one_shot',
                  action='store_true', default=False,
                  help='just run once, save status and quit')
parser.add_option('', '--self_trigger', dest='do_self_trigger',
                  action='store_true', default=False,
                  help='read price by myself and do following trade')

(options, args) = parser.parse_args()
print (type(options), options, args)

latest_to_read = int(options.latest_to_read)

pick_old_order = options.pick_old_order

l_signal = options.signals[0]
l_prefix = '%s_' % l_signal
l_dir = options.dirs[0]

if not os.path.isdir(l_dir):
    print ('%s is not valid direction' % l_dir)
    sys.exit(1)

amount_file = '%s.%samount' % (l_dir, l_prefix)

default_amount_ratio = float(options.amount_ratio) # means use 1/50 of total amount on one trade, if auto_amount
amount_ratio = default_amount_ratio
ratio_file = '%s.%sratio' % (l_dir, l_prefix)
print ('ratio will read from %s if exist, default is %d' % (ratio_file, amount_ratio), flush=True)

trade_notify = '%s.%strade_notify' % (l_dir, l_prefix) # file used to notify trade
logfile='%s.log' % trade_notify
logging.basicConfig(filename=logfile, 
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG)
#logging.info('trade_notify: %s' % trade_notify)
if options.nolog == 0:
    saved_stdout = sys.stdout
    sys.stdout = open(logfile, 'a')
    sys.stderr = sys.stdout
print (dt.now())
print ('trade_notify: %s' % trade_notify)

status_file = '%s.%strade_status' % (l_dir, l_prefix) # file used to save status
print ('status_file: %s' % status_file)
trade_status = dict()

print ('using amount file: %s' % amount_file)

if options.signal_notify != None:
    signal_notify = options.signal_notify
else:
    signal_notify = '%s.%snotify' % (l_dir, l_prefix)
#logging.info ('signal_notify: %s' % signal_notify)
print ('signal_notify: %s' % signal_notify)

# should emit signal into policy_notify
if options.policy != None:
    policy_notify = '%s.%s_notify' % (l_dir, options.policy)
else:
    policy_notify = ''
print ('policy_notify: %s' % policy_notify)

fee_file = '%s.%sfee' % (l_dir, l_prefix)
#logging.info ('fee will read from %s if exist, default is %f' % (fee_file, fee_threshold))
print ('fee will read from %s if exist, default is %f' % (fee_file, fee_threshold))

pid_file = '%s.%strade_notify.pid' % (l_dir, l_prefix)
# os.setsid() # privilge
#print (os.getpgrp(), os.getpgid(os.getpid()))
with open(pid_file, 'w') as f:
    f.write('%d' % os.getpgrp())
    f.close()
print ('sid is %d, pgrp is %d, saved to file %s' % (os.getsid(os.getpid()), os.getpgrp(), pid_file))

if options.open_start_price != None:
    open_start_price = float(options.open_start_price)
if options.previous_close != None:
    previous_close = float(options.previous_close)

if pick_old_order == True:
    try_to_pick_old_order()
    if trade_file != '': # yes, old pending order exists
        print ('### pick old order: %s, open price %f\n' % (trade_file, old_open_price))

if options.startup_notify != None:
    startup_notify = options.startup_notify
    print ('startup_notify: %s' % startup_notify)
if options.shutdown_notify != None:
    shutdown_notify = options.shutdown_notify
    print ('shutdown_notify: %s' % shutdown_notify)
        
if options.emulate:
    emul_signal_notify(l_dir, l_signal)
    os.sys.exit(0)

if options.restore_status != None and \
   os.path.isfile(status_file) and \
   os.path.getsize(status_file) > 0:
    globals()['load_status_%s' % l_signal]()
    print ('trade status restored:\n', globals()['trade_status'])

periods_mapping_ms = { '1day': 24 * 60 * 60,
                       '12hour':12 * 60 * 60,
                       '6hour': 6 * 60 * 60,
                       '4hour': 4 * 60 * 60,
                       '2hour': 2 * 60 * 60,
                       '1hour': 1 * 60 * 60,
                       '30min': 30 * 60,
                       '5min': 5 * 60,
                       '1min': 60}

# logic copied from signal_notity.py
def prepare_for_self_trigger(notify, signal, l_dir):
    symbol=symbols_mapping[figure_out_symbol_info(notify)]
    contract=figure_out_contract_info(notify)
    period=figure_out_period_info(notify)
    try:
        reply=eval('%s' % (okcoinFuture.future_kline(symbol, period, contract, '1')))[0]
        price_filename = os.path.join(l_dir, '%s.%s' % (reply[0], signal))
        if os.path.isfile(price_filename) and os.path.getsize(price_filename) > 0:
            print (trade_timestamp(), '%s is already exist' % (price_filename))
            return price_filename
        print ('save price to %s' % price_filename) 
        with open(price_filename, 'w') as f:
            f.write('%s, %s, %s, %s, %s, %s' %
                    (reply[1], reply[2], reply[3], reply[4], reply[5], reply[6]))
            f.close()
        with open(notify, 'w') as f:
            f.write(price_filename)
            f.close()
            print ('save signal to %s' % notify)
        return price_filename
    except Exception as Ex:
        print (trade_timestamp(), traceback.format_exc())
        return None

def calculate_timeout_for_self_trigger(notify):
    period_ms = periods_mapping_ms[figure_out_period_info(notify)]
    moduls =int(datetime.datetime.now().strftime('%s')) % period_ms
    timeout = (period_ms - moduls) - 15
    if timeout > 0:
        return timeout
    else:
        return -15 # wait at least this long time of seconds

while True:
    if startup_notify != '':
        print (trade_timestamp(), 'Waiting for startup signal', flush=True)
        command = ['fswatch', '-1', startup_notify]
        result = subprocess.run(command, stdout=PIPE) # wait file modified
        if result.returncode < 0: # means run failed
            os.sys.exit(result.returncode)
        print ('%s received startup signal from %s' % (trade_timestamp(), startup_notify))
        limit_direction = ''
        limit_price = 0
        limit_symbol = ''
        limit_amount = 0
        read_int_var(ratio_file, 'amount_ratio')
        with open(startup_notify, 'r') as f:
            # f is a formated map type,just eval it
            line=f.readline()
            print ('order_info: %s', line)
            order_info = eval(line)
            f.close()
            dirs = ['', 'buy', 'sell', '', ''] # 1:buy, 2:sell
            if order_info['result'] == True:
                limit_direction = dirs[order_info['orders'][0]['type']]
                limit_price = order_info['orders'][0]['price']
                limit_symbol = order_info['orders'][0]['symbol']
                limit_amount = order_info['orders'][0]['amount']
        with open(startup_notify, 'w') as f:
            # try to clean startup notify
            f.close()
    print (trade_timestamp(), 'Waiting for process new coming file\n', flush=True)
    #issue kickup signal
    with open('%s.ok' % trade_notify, 'w') as f:
        f.close()

    if options.do_self_trigger:
        timeout = calculate_timeout_for_self_trigger(signal_notify)

        if timeout > 0: # wait for triggering
            print (trade_timestamp(),
                   'wait for next period about %dh:%dm:%ds later' %
                   (timeout / 60 / 60,
                    (timeout % 3600) / 60,
                    timeout - int(timeout / 60) * 60))
            time.sleep(timeout)
        else:
            print (trade_timestamp(), 'trigger safely')
            time.sleep(abs(timeout))
        prepare_for_self_trigger(signal_notify, l_signal, l_dir)

    wait_signal_notify(signal_notify, l_signal, shutdown_notify)

    if options.one_shot:
        break

    if shutdown_notify != '':
        print (trade_timestamp(), 'shutdown signal processed')
    if startup_notify == '':
        break;

# >>> datetime.date.today().strftime('%s')
# '1534003200'
