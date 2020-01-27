# -*- coding: utf-8 -*-

import sys
import getopt
import traceback

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
#print (json.loads(okcoinFuture.future_userinfo_4fix())) # not work for 全仓模式

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
    # print ('symbol is %s' % (path[start:end]))
    return path[start:end]

def figure_out_contract_info(path):
    path = os.path.splitext(path)[0]
    start_pattern = 'kline_'
    end_pattern = '_'
    start = path.index(start_pattern) + len(start_pattern)
    end = path.rindex(end_pattern)
    # print ('contract is %s' % (path[start:end]))
    return path[start:end]

def figure_out_period_info(path):
    path = os.path.splitext(path)[0]
    start_pattern = '_'
    start = path.rindex(start_pattern) + len(start_pattern)
    # print ('period is %s' % (path[start:]))
    return path[start:]


# {'result': True, 'holding': [{'buy_price_avg': 176.08158274, 'symbol': 'eth_usd', 'lever_rate': 10, 'buy_available': 0, 'contract_id': 201906280020041, 'sell_risk_rate': '99.36', 'buy_amount': 0, 'buy_risk_rate': '1,000,000.00', 'profit_real': -1.847e-05, 'contract_type': 'quarter', 'sell_flatprice': '178.453', 'buy_bond': 0, 'sell_profit_lossratio': '-0.66', 'buy_flatprice': '0.000', 'buy_profit_lossratio': '0.00', 'sell_amount': 1, 'sell_bond': 0.00615942, 'sell_price_cost': 162.388, 'buy_price_cost': 176.08158274, 'create_date': 1552656509000, 'sell_price_avg': 162.388, 'sell_available': 1}]}
# if current order is permit to issue
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

#print (okcoinFuture.future_position('ltc_usd','quarter'))  # works
#print (okcoinFuture.future_position('ltc_usd','this_week'))  # works
#print (check_holdings_profit('ltc_usd', 'this_week', 'buy'))
#print (check_holdings_profit('ltc_usd', 'this_week', 'sell'))
#sys.exit(1)

order_infos = {'usd_btc':'btc_usd',
               'usd_ltc':'ltc_usd',
               'usd_eth':'eth_usd',
               'usd_eos':'eos_usd',                              
               'usd_bch':'bch_usd',
               'usd_xrp':'xrp_usd',
               'sell':{'open':open_order_sell_rate,
                       'close':close_order_sell_rate},
               'buy':{'open':open_order_buy_rate,
                      'close':close_order_buy_rate}}

# {'result': True, 'orders': [{'symbol': 'eth_usd', 'lever_rate': 10, 'amount': 1, 'fee': -1.131e-05, 'contract_name': 'ETH0517', 'unit_amount': 10, 'type': 3, 'price_avg': 265.304, 'deal_amount': 1, 'price': 265.304, 'create_date': 1557968404000, 'order_id': 2833278863744000, 'status': 2}]}
reissuing_order = 0
wait_for_completion = 1 # default is no wait
def issue_order_now(symbol, contract, direction, amount, action):
    global reissuing_order, wait_for_completion
    # print (symbol, direction, amount, action)
    raw_result = order_infos[direction][action](symbol, contract, amount)
    result = json.loads(raw_result)
    # print (result)
    if result['result'] == False:
        reissuing_order += 1
        if amount < 2:
            return (False, 0)
        return issue_order_now(symbol, contract, direction, amount / 2, action)
    order_id = str(result['order_id']) # no exceptions, means successed
    #print (order_id)
    if wait_for_completion > 0: # only valid if positive
        time.sleep(wait_for_completion)
    raw_order_info = query_orderinfo(symbol, contract, order_id)
    if result['result'] == False: # something is wrong
        reissuing_order += 1
    else:
        order_info = json.loads(raw_order_info)
        #print (order_info)
        new_amount = 0
        try: # in case amount too much 
            # update amount_ratio from current order's lever_rate field
            globals()['amount_ratio'] = float(order_info['orders'][0]['lever_rate'])
            deal_amount = order_info['orders'][0]['deal_amount']
            if order_info['orders'][0]['amount'] != deal_amount:
                if deal_amount > 0 and wait_for_completion == 0: # it's ok
                    # no update for last_fee
                    return (True, order_info['orders'][0]['price'])
                else: # should wait 
                    amount -= int(deal_amount)
                    reissuing_order += 1
            else:
                globals()['last_fee'] = abs(float(order_info['orders'][0]['fee']))/float(order_info['orders'][0]['amount'])
                return (True, order_info['orders'][0]['price'])
        except Exception as ex:
            if amount < 2: # no balance now
                return (False, 0)
            reissuing_order += 1
            amount = amount / 2
    if reissuing_order > 60: # more than 60 , quit
        reissuing_order = 0
        return (False, 0)
    print ('try to cancel pending order and reissue', ' amount = %d' % amount)
    cancel_order(symbol, contract, order_id)
    return issue_order_now(symbol, contract, direction, amount, action)

# orders need to close, sorted by price
orders_holding ={'sell':{'reverse':False, 'holding':list()},
                 'buy':{'reverse':True, 'holding':list()}}

# only for close
def issue_order_now_conditional(symbol, contract, direction, amount, action, must_positive=True):
    (loss, t_amount) = check_holdings_profit(symbol, contract, direction)
    if t_amount == 0:
        return 0 # no operation
    holding=orders_holding[direction]['holding']
    l_reverse=orders_holding[direction]['reverse']
    # print (holding)
    if len(holding) > 1:
        orders_holding[direction]['holding'] = [tuple(x) for x in holding]
        holding=orders_holding[direction]['holding']        
        holding.sort(reverse=l_reverse)
    if must_positive == False:
        if amount == 0:
            holding.clear()
            amount = t_amount
        else:
            amount = min(t_amount, amount) # get little one
            total_amount = 0
            while len(holding) > 0:
                (price, l_amount) = holding.pop()
                total_amount += l_amount
                if amount > 0 and total_amount > amount:
                    holding.append((price, total_amount - amount))
                    break
        (ret, price) = issue_order_now(symbol, contract, direction, amount, action)
        print ('loss ratio=%f%%, %s, closed %d' % (loss, 'yeap' if loss > 0 else 'tough', amount))
        return amount if ret == True else 0
    total_amount = 0
    addon = ''
    saved_amount = amount
    amount = min(t_amount, amount) # get little on
    while len(holding) > 0:
        (price, l_amount)=holding.pop()
        if globals()['positive_greedy_tiny_profit'](price, direction) == True:
            # print ('(%s, %s) selected' % (price, l_amount))
            total_amount += l_amount
            if amount > 0 and total_amount > amount:
                holding.append((price, total_amount - amount))
                total_amount = amount
                break
        else: # not positive
            holding.append((price, l_amount)) # put it back
            break
    if total_amount > 0 : # yes, has positive holdings
        (ret, price) = issue_order_now(symbol, contract, direction, total_amount, action)
        addon = ' (%d required, %d closed, %d left)' % (saved_amount, total_amount, (t_amount - total_amount))
    print ('loss ratio=%f%%, keep holding%s' % (loss, addon))
    return total_amount

global options
def issue_quarter_order_now(symbol, direction, amount, action):
    print ('EMUL ' if options.noaction else '',
           'issue quarter order: ',
           action, symbol, direction, amount)
    if options.noaction:
        return 0
    (ret, price) = issue_order_now(symbol, globals()['contract'], direction, amount, action)
    if ret == True and action == 'open':
        orders_holding[direction]['holding'].append((price, amount))
    return amount if ret == True else 0

def issue_quarter_order_now_conditional(symbol, direction, amount, action, must_positive=True):
    print ('EMUL ' if options.noaction else '',
           'issue quarter order conditional: ',
           action, symbol, direction, amount)
    if options.noaction:
        return 0
    return issue_order_now_conditional(symbol, globals()['contract'], direction, amount, action, must_positive)

# apikey = 'e2625f5d-6227-4cfd-9206-ffec43965dab'
# secretkey = "27BD16FD606625BCD4EE6DCA5A8459CE"
# okcoinRESTURL = 'www.okex.com'
    
# #现货API
# okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)

# #期货API
# okcoinFuture = OKCoinFuture(okcoinRESTURL,apikey,secretkey)


old_open_price = 0
old_close_mean = 0
trade_file = ''
default_fee_threshold = 0.0001# baesed on one order's fee
fee_threshold = default_fee_threshold
levage_rate = 20

symbols_mapping = { 'usd_btc': 'btc_usd',
                    'usd_ltc': 'ltc_usd',
                    'usd_eth': 'eth_usd',
                    'usd_eos': 'eos_usd',                     
                    'usd_xrp': 'xrp_usd',
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
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, globals()['contract'], '1'))
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

# previou is calcuated ema with period , re
def get_ema(previous, new_data, period):
    return (previous * (period - 1) + 2 * new_data) / (period + 1)

open_price = 0
previous_close = 0
open_start_price = 0
last_bond = 0 # means uninitialized
last_balance = 0
last_decision_logic=''

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
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, globals()['contract'], '1'))
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
    global last_decision_logic
    if l_dir == 'buy':
        last_decision_logic = 'buy, '
        if close > previous_close:
            last_decision_logic += 'increasing, '
            if open_greedy == False and close > open_price:
                last_decision_logic += 'greedy no, close > open_price = True'
                return (close - open_price)
            else:
                last_decision_logic += 'greedy yes or else '
                if (close > open_price):
                    last_decision_logic += 'close - open_price = %.4f, close - previous_close = %.4f' % (close - open_price, close - previous_close)
                    if (close - open_price) > (close - previous_close):
                        return (close - open_price)
                if close < open_start_price:
                    last_decision_logic += 'close - open_start_price = %.4f ' % (close - open_start_price)
                    return (close - open_start_price)
                last_decision_logic += ' open greedy now'
                return 0.0
        elif close < previous_close:
            last_decision_logic += 'decreasing, '
            if open_greedy == False:
                last_decision_logic += 'greedy no, '
                if close > open_start_price: # positive profit
                    last_decision_logic += 'close > open_start_price = True'
                    return 0.0
                else:
                    last_decision_logic += 'close > open_start_price = False, %0.4f' % ( close - open_start_price)
                    return (close - open_start_price)
            else:
                last_decision_logic += 'greedy yes, '
                if close > open_start_price: # positive profit
                    last_decision_logic += 'close > open_start_price = True'
                    return 0.0
                else:
                    last_decision_logic += 'close > open_start_price = False, %0.4f' % ( close - open_start_price)
                    if previous_close < open_start_price:
                        return (close - open_start_price)
                last_decision_logic += ' open greedy now'
                return 0.0
    elif l_dir == 'sell':
        last_decision_logic = 'sell, '
        if close < previous_close:
            last_decision_logic += 'decreasing, '
            if open_greedy == False and close < open_price:
                last_decision_logic += 'greedy no, close < open_price = True'
                return -(close - open_price)
            else:
                last_decision_logic += 'greedy yes or else '
                if close < open_price: # already positive profit
                    last_decision_logic += 'close - open_price = %.4f, close - previous_close = %.4f' % (close - open_price, close - previous_close)
                    if (close - open_price) < (close - previous_close):
                        return -(close - open_price)
                if close > open_start_price:
                    last_decision_logic += 'close - open_start_price = %.4f ' % (close - open_start_price)
                    return -(close - open_start_price)
                last_decision_logic += ' open greedy now'
                return 0.0
        elif close > previous_close:
            last_decision_logic += 'increasing, '
            if open_greedy == False:
                last_decision_logic += 'greedy no, '
                if close < open_start_price: # positive profit
                    last_decision_logic += 'close < open_start_price = True'
                    return 0.0
                else:
                    last_decision_logic += 'close < open_start_price = False, %0.4f' % ( close - open_start_price)
                    return -(close - open_start_price)
            else:
                last_decision_logic += 'greedy yes, '
                if close < open_start_price: # positive profit
                    last_decision_logic += 'close < open_start_price = True'
                    return 0.0
                else:
                    last_decision_logic += 'close < open_start_price = False, %0.4f' % ( close - open_start_price)
                    if previous_close > open_start_price:
                        return -(close - open_start_price)
                last_decision_logic += ' open greedy now'
                return 0.0
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
            real= float(data['profit_real'])
            return (avg, avg*real)
    return 0

def try_loadsave_with_names(status, names, load):
    if not load:
        globals()[status].clear()        
    for name in globals()[names]:
        if load: # from status to individual names
            if name in globals()[status].keys(): # in case name not exist
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
                 'next_open_start_price',
                 'open_price',
                 'open_cost',
                 'open_greedy',
                 'quarter_amount',
                 'thisweek_amount_pending',
                 'quarter_amount_multiplier',
                 'greedy_count',
                 'greedy_count_max',
                 'greedy_whole_balance',
                 'greedy_same_amount',
                 'last_balance',
                 'last_bond',
                 'update_quarter_amount_forward',
                 'update_quarter_amount_backward',
                 'profit_cost_multiplier',
                 'greedy_cost_multiplier',
                 'last_fee',
                 'amount_ratio',
                 'amount_ratio_plus',
                 'amount_real',
                 'orders_holding',
                 'ema_1',
                 'ema_1_up',
                 'ema_1_lo',
                 'ema_period_1',
                 'ema_2',
                 'ema_2_up',
                 'ema_2_lo',
                 'ema_period_2',
                 'on_guard',
                 'guard_timeout', 
                 'forward_greedy',
                 'backward_greedy',
                 'enable_guard',
                 'wait_for_completion'];

def save_status_tit2tat(subpath=''):
    loadsave_status('tit2tat', load=False)
    with open(globals()['status_file'], 'r') as r:
        with open('%s.trade_status' % (subpath), 'w') as w:
            w.write(r.read()) # read whole file and write all
            w.close()
        r.close()

def load_status_tit2tat(subpath=''):
    loadsave_status('tit2tat', load=True)

def get_greedy_tiny_delta(price):
    # print ('greedy delta', globals()['previous_close'], price)
    return 10 * (globals()['previous_close'] - price) # 'previous_close is update to current price'

def get_greedy_delta(price):
    # print ('greedy delta', globals()['previous_close'], price)
    return globals()['previous_close'] - price # 'previous_close is update to current price'

def get_normal_delta(price):
    # print ('normal delta', price, globals()['open_price'])
    return price - globals()['open_price']

def get_quit_delta(price):
    # print ('quit delta', price, globals()['open_start_price'])
    return price - globals()['open_start_price']

profit_policy = { 'greedy-tiny': {'multiplier':'greedy_cost_multiplier',
                                  'get_delta':get_greedy_tiny_delta},
                  'greedy': {'multiplier':'greedy_cost_multiplier',
                             'get_delta':get_greedy_delta},
                  'normal': {'multiplier':'profit_cost_multiplier',
                             'get_delta':get_normal_delta},
                  'quit': {'multiplier':'greedy_cost_multiplier',
                           'get_delta':get_quit_delta},
                  'trans': {'buy': 1, 'sell': -1}}

def positive_profit_with(price, direction, typeof):
    cost = globals()[profit_policy[typeof]['multiplier']] * globals()['open_cost']
    delta = profit_policy[typeof]['get_delta'](price)
    trans = profit_policy['trans'][direction]
    # print (delta * trans, cost, delta * trans > cost)
    return delta * trans > cost

def positive_greedy_profit(price, direction):
    return positive_profit_with(price, direction, 'greedy')

def positive_greedy_tiny_profit(price, direction):
    return positive_profit_with(price, direction, 'greedy-tiny')

def positive_normal_profit(price, direction):
    return positive_profit_with(price, direction, 'normal')

def positive_quit_profit(price, direction):
    return positive_profit_with(price, direction, 'quit')

def get_multiple_profit4(close, previoud_close, open_price, open_start_price, l_dir, open_greedy):
    current_profit = check_with_direction(close, previous_close, open_price, open_start_price, l_dir, open_greedy)
    if l_dir == 'buy':
        current_profit1 = close - open_start_price
        current_profit2 = close - open_price
        current_profit3 = close - previous_close
    else:
        current_profit1 = open_start_price - close
        current_profit2 = open_price - close
        current_profit3 = previous_close - close
    return (current_profit, current_profit1, current_profit2, current_profit3)

next_open_start_price = 0
last_fee = 0
open_cost = 0
quarter_amount = 1
thisweek_amount_pending = 0
quarter_amount_multiplier = 2 # 2 times is up threshold
greedy_count_max = 2 # limit this times pending greedy
greedy_count = 0 # current pending greedy
greedy_whole_balance = False # greedy will cover whole balance
greedy_same_amount = False # greedy use the same as quarter_amount
close_greedy = False
open_greedy = False
amount_ratio_plus = 0.05 # percent of total amount
profit_cost_multiplier = 0.2 # times of profit with open_cost
greedy_cost_multiplier = 0.1 # times of greedy with open_cost
amount_real = 0 # supercede on amount_ratio, as percent of amount
ema_period_1 = 2 # signal period
ema_period_2 = 20 # tendency period
ema_1 = 0
ema_2 = 0
ema_1_up = 0 # up means high price
ema_1_lo = 0 # lo means low price
ema_2_up = 0
ema_2_lo = 0
on_guard = False  # if set, do price guard
forward_greedy = True # following tendency
backward_greedy = False # following reverse tendency
guard_timeout = 180 #  3minutes
enable_guard = False # default is disabled
update_quarter_amount_forward = True # update it if balance increase
update_quarter_amount_backward = False # update it if balance decrease

# if guard true, then check and do quick turn 
def try_to_trade_tit2tat(subpath, guard=False):
    global trade_file, old_close_mean
    global old_open_price
    global old_close, bins, direction
    global l_trade_file
    global previous_close
    global open_greedy, close_greedy 
    global open_price, open_start_price
    global open_cost
    global quarter_amount, thisweek_amount_pending
    global last_bond, last_balance
    global next_open_start_price
    global last_decision_logic
    global ema_1, ema_1_up, ema_1_lo
    global ema_2, ema_2_up, ema_2_lo
    global on_guard
    global enable_guard
    global forward_greedy, backward_greedy
    global update_quarter_amount_forward, update_quarter_amount_backward
    global greedy_count, greedy_count_max
    
    greedy_status = ''    
    #print (subpath)
    event_path=subpath
    l_index = os.path.basename(event_path)
    # print (l_index, event_path)
    if True: # type 256, new file event
        prices = read_4prices(event_path)
        close = prices[ID_CLOSE]
        guard_signal = 0
        if trade_file.endswith('.sell') == True: # sell order
            l_dir = 'sell'
            reverse_follow_dir = 'buy'
            if on_guard and guard: # guard price turn
                guard_signal = close - ema_1
        elif trade_file.endswith('.buy') == True: # buy order
            l_dir = 'buy'
            reverse_follow_dir = 'sell'
            if on_guard and guard: # guard price turn
                guard_signal = ema_1 - close
        if guard_signal > 0: # seen signal
            symbol=symbols_mapping[figure_out_symbol_info(event_path)]
            on_guard = False # silent now, until next period
            globals()['signal_close_order_with_%s' % l_dir](l_index, trade_file, close)
            issue_quarter_order_now(symbol, l_dir, 0, 'close')
            # restart it now
            # do open
            l_dir = reverse_follow_dir
            trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, l_dir)
            # print (trade_file)
            globals()['signal_open_order_with_%s' % l_dir](l_index, trade_file, close)
            issue_quarter_order_now(symbol, l_dir, quarter_amount, 'open')

            (open_price, no_use) = real_open_price_and_cost(symbol, globals()['contract'], l_dir) if not options.emulate else (close, 0.001)
            t_bond = query_bond(symbol, globals()['contract'], l_dir)
            if t_bond > 0:
                last_bond = t_bond
                t_open_cost = open_price * last_fee / last_bond  # just see cost
                open_cost = max(open_cost, t_open_cost)
            if open_start_price == 0:
                open_start_price = prices[ID_OPEN] # when seeing this price, should close, init only once
            previous_close = close
            return
        if guard: # nothing happend, continue
            return
        new_ema_1 = get_ema(ema_1, close, ema_period_1)
        new_ema_2 = get_ema(ema_2, close, ema_period_2)
        new_ema_1_up = get_ema(ema_1_up, prices[ID_HIGH], ema_period_1)
        new_ema_1_lo = get_ema(ema_1_lo, prices[ID_LOW], ema_period_1)
        new_ema_2_up = get_ema(ema_2_up, prices[ID_HIGH], ema_period_2)
        new_ema_2_lo = get_ema(ema_2_lo, prices[ID_LOW], ema_period_2)        
        delta_ema_1 = new_ema_1 - ema_1
        reverse_follow_dir = ''
        price_delta = 0
        print ('') # add an empty line
        if trade_file == '':
            print ('%9.4f' % close, '-',
                   'ema_%d:%9.4f' % (ema_period_1, new_ema_1), 'ema_%d:%9.4f' % (ema_period_2, new_ema_2))
        elif l_dir == 'sell': # sell order
            ema_tendency = new_ema_2 - new_ema_1_lo # ema_2 should bigger than ema_1_lo
            reverse_follow_dir = 'buy'
            price_delta = (previous_close - close) / previous_close
            print ('%9.4f' % -close, '%9.4f' % open_price, l_dir, 'gate %9.4f' % open_start_price,
                   'ema_%d:%9.4f' % (ema_period_1, new_ema_1), 'ema_%d:%9.4f' % (ema_period_2, new_ema_2),
                   'ema_%d signal:%9.4f' % (ema_period_1, new_ema_1_lo),
                   'greedy : %f' % greedy_count
            )
        elif l_dir == 'buy': # buy order
            ema_tendency = new_ema_1_up - new_ema_2 # ema_1_up should bigger than ema_2
            reverse_follow_dir = 'sell'
            price_delta = (close - previous_close) / previous_close
            print ('%9.4f' % close, '%9.4f' % -open_price, l_dir, 'gate %9.4f' % open_start_price,
                   'ema_%d:%9.4f' % (ema_period_1, new_ema_1), 'ema_%d:%9.4f' % (ema_period_2, new_ema_2),
                   'ema_%d signal:%9.4f' % (ema_period_1, new_ema_1_up),
                   'greedy : %f' % greedy_count
            )                   
        ema_1 = new_ema_1 # saved now
        ema_1_up = new_ema_1_up
        ema_1_lo = new_ema_1_lo
        ema_2 = new_ema_2 # saved now
        ema_2_up = new_ema_2_up
        ema_2_lo = new_ema_2_lo
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
                        delta = open_price - prices[ID_LOW]
                        new_open_start_price = prices[ID_LOW]
                        if next_open_start_price < new_open_start_price and new_open_start_price < open_price:
                            next_open_start_price = new_open_start_price
                    else: # sell
                        delta = prices[ID_HIGH] - open_price
                        new_open_start_price = prices[ID_HIGH]
                        if next_open_start_price > new_open_start_price and new_open_start_price > open_price:
                            next_open_start_price = new_open_start_price
                    if next_open_start_price == 0:
                        next_open_start_price = new_open_start_price
                    if delta < 0.001: # zero means too small
                        t_amount = 1
                    else:
                        t_amount = open_price - delta * amount_ratio # calcuate by forced close probability
                    if not options.emulate: # if emualtion, figure it manually
                        (loss, t_amount) = check_holdings_profit(symbol, globals()['contract'], l_dir)
                    if t_amount <= 0:
                        # check if should take normal close action
                        (current_profit, current_profit1, current_profit2, current_profit3) = get_multiple_profit4(close, previous_close, open_price, open_start_price, l_dir, open_greedy)
                        if current_profit1 <= -greedy_cost_multiplier * open_cost: # no, negative 
                            forced_close = False
                        elif current_profit2 >= profit_cost_multiplier * open_cost: # yes, positive 
                            forced_close = False
                        else:
                            forced_close = True
                    else:
                        thisweek_amount_pending = math.ceil(t_amount - quarter_amount)
                if forced_close:
                    open_greedy = True
                    # suffered forced close
                    globals()['signal_close_order_with_%s' % l_dir](l_index, trade_file, close)
                    print (trade_timestamp(), 'detected forced close signal %s at %s => %s' % (l_dir, previous_close, close))
                    # action likes new_open equals true, but take original l_dir as it
                    mini_amount = max(1, math.ceil(quarter_amount / 8))
                    issue_quarter_order_now(symbol, l_dir, mini_amount, 'open')
                    # clear it
                    thisweek_amount_pending = 0
                    (open_price, no_use) = real_open_price_and_cost(symbol, globals()['contract'], l_dir) if not options.emulate else (close, 0.001)
                    if l_dir == 'buy' and open_start_price < new_open_start_price:
                        open_start_price = (open_start_price + new_open_start_price) / 2
                    elif l_dir == 'sell' and open_start_price > new_open_start_price:
                        open_start_price = (open_start_price + new_open_start_price) / 2
                new_l_dir = ''
                if close > previous_close and delta_ema_1 > 0:
                    new_l_dir = 'buy'
                elif close < previous_close and delta_ema_1 < 0:
                    new_l_dir = 'sell'                
                if new_open == False:
                    on_guard = enable_guard
                    if not forced_close:
                        (current_profit, current_profit1, current_profit2, current_profit3) = get_multiple_profit4(close, previous_close, open_price, open_start_price, l_dir, open_greedy)
                    else:
                        forced_close = False # let stop it here
                        current_profit1 = 0
                        current_profit2 = 0
                        current_profit3 = 0
                    issuing_close = False
                    if current_profit1 <= -greedy_cost_multiplier * open_cost: # no, negative
                        # take ema into account
                        if ema_tendency <= 0: # do close
                            issuing_close = True
                            open_start_price = open_price # when seeing this price, should close, init only once
                        # keep previous_close un-touched here
                    elif current_profit2 >= profit_cost_multiplier * open_cost: # yes, positive 
                        # take ema into account
                        if ema_tendency <= 0: # do close
                            issuing_close = True # do close
                        # keep previous_close un-touched here
                    if ema_tendency <= 0: # take charge of issuing_close signal
                        issuing_close = True
                        open_start_price = open_price # when seeing this price, should close, init only once
                    else:
                        issuing_close = False
                    if on_guard:
                        if l_dir == 'buy' and delta_ema_1 < 0:
                            issuing_close = True
                            open_start_price = open_price # when seeing this price, should close, init only once
                        elif l_dir == 'sell' and delta_ema_1 > 0:
                            issuing_close = True
                            open_start_price = open_price # when seeing this price, should close, init only once
                    # if issuing_close is true, check the new direction first
                    if issuing_close == True and l_dir == new_l_dir: # the same direction, just treat it as a greedy
                        issuing_close = False
                    greedy_action = ''
                    greedy_status = 'no action'
                    update_quarter_amount = False
                    if issuing_close == False and (forward_greedy or backward_greedy): # partly no, but still positive consider open_start_price, do greedy process
                        # emit open again signal
                        if l_dir == 'buy':
                            if (close - previous_close) > greedy_cost_multiplier * open_cost:
                                greedy_action = 'close'
                                greedy_status = 'maybe closed'
                            elif (close - previous_close) < - greedy_cost_multiplier * open_cost:
                                greedy_action = 'open'
                                greedy_status = 'holding'
                        elif l_dir == 'sell':
                            if (close - previous_close) < - greedy_cost_multiplier * open_cost:
                                greedy_action = 'close'
                                greedy_status = 'maybe closed'
                            elif (close - previous_close) > greedy_cost_multiplier * open_cost:
                                greedy_action = 'open'
                                greedy_status = 'holding'
                        print (trade_timestamp(), 'greedy signal %s at %s => %s (%s) ' % (l_dir, previous_close, close, greedy_status))
                        if greedy_action != '': # update amount
                            open_greedy = True
                            previous_close = close
                            if globals()['amount_real'] > 0 or globals()['greedy_same_amount']:
                                thisweek_amount = quarter_amount
                            elif globals()['greedy_whole_balance']:
                                thisweek_amount = math.ceil((quarter_amount / ( 1 / amount_ratio + amount_ratio_plus) - quarter_amount) / greedy_count_max)
                            else:
                                thisweek_amount = math.floor((quarter_amount_multiplier - 1) * quarter_amount / greedy_count_max)
#  持续更新 pending
#  开始状态，直接买入quarter_amount , greedy_count = max, pending = 0
#  逆向发展，greedy_count >= 1, 增加持仓，greedy_count = greedy_count * (1- 1/max), pending += thisweek_amount ;  == 重复该过程
#  逆向发展，greedy_count < 1, 减少持仓， - (quarter_amount - 1), 更新 pending
#  无动作，更新 balance，quarter_amount
#  同向发展，pending==0, greedy_count += 1/ max ;  == 重复该过程
#  同向发展，pending > 0, 减少持仓pending， 根据减少的比例增加 greedy_count
#  同向发展，pending < 0, greedy_count = max
#  同向发展，pending < 0, greedy_count >= max，则直接增加持仓为 -pending
#  
                        if greedy_action == 'close': # yes, close action pending
                            if forward_greedy :
                                if globals()['greedy_same_amount']:
                                    issue_quarter_order_now_conditional(symbol, reverse_follow_dir, 0, 'close', False)
                                if thisweek_amount_pending > 0: 
                                    l_amount = issue_quarter_order_now_conditional(symbol, l_dir, thisweek_amount_pending, 'close') # as much as possible
                                    if thisweek_amount_pending >= l_amount: # is ok
                                        thisweek_amount_pending -= l_amount
                                    else:
                                        print ('greedy close request %d, return %d' % (thisweek_amount_pending, l_amount))
                                        thisweek_amount_pending = 0;
                                    if thisweek_amount_pending == 0: # fresh go
                                        greedy_count = greedy_count_max # increase it to threshold
                                    else:
                                        greedy_count += (l_amount / thisweek_amount)                                    
                                elif thisweek_amount_pending < 0 : # if less holdings, increase it
                                    if greedy_count < greedy_count_max:
                                        greedy_count = greedy_count_max
                                    else:
                                        l_amount = issue_quarter_order_now(symbol, l_dir, -thisweek_amount_pending, 'open') # as much as possible
                                        thisweek_amount_pending += l_amount
                                else:
                                    greedy_count = greedy_count + (1 / greedy_count_max)
                            if backward_greedy:
                                issue_quarter_order_now_conditional(symbol, reverse_follow_dir, 0, 'close', False)
                        elif greedy_action == 'open': # yes, open action pending
                            if greedy_count < 1.0: # must bigger than 1
                                issue_quarter_order_now(symbol, l_dir, thisweek_amount * greedy_count_max - 1, 'close') # forced, left 1 in case empty holding
                                thisweek_amount_pending -= thisweek_amount * greedy_count_max - 1
                            else:
                                greedy_count = greedy_count * (1.0 - 1.0 / greedy_count_max) # decreasing fast
                                if forward_greedy: # adjust open sequence according to l_dir
                                    if l_dir == 'buy': # first open sell, then open buy
                                        if globals()['greedy_same_amount']:
                                            issue_quarter_order_now(symbol, reverse_follow_dir, thisweek_amount * 0.90, 'open')
                                        issue_quarter_order_now(symbol, l_dir, thisweek_amount, 'open')
                                        pass
                                    else:
                                        issue_quarter_order_now(symbol, l_dir, thisweek_amount, 'open')
                                        if globals()['greedy_same_amount']:
                                            issue_quarter_order_now(symbol, reverse_follow_dir, thisweek_amount * 0.90, 'open')
                                        pass
                                    thisweek_amount_pending += thisweek_amount
                                if backward_greedy:
                                    issue_quarter_order_now_conditional(symbol, reverse_follow_dir, 0, 'close')
                                    # secondly open new order
                                    issue_quarter_order_now(symbol, reverse_follow_dir, max(1, thisweek_amount / 2), 'open')
                        if greedy_action == '' or greedy_count >= greedy_count_max : # update balance
                            update_quarter_amount = True
                    if issuing_close == True:
                        globals()['signal_close_order_with_%s' % l_dir](l_index, trade_file, close)
                        issue_quarter_order_now_conditional(symbol, l_dir, 0, 'close', False) # use zero to close all 
                        # and open again, just like new_open == True
                        new_open = True
                        if open_greedy == True :
                            close_greedy = backward_greedy # only if backward_greedy is true
                            open_greedy = False
                            thisweek_amount_pending = 0
                        update_quarter_amount = True
                        trade_file = '' # clear it
                    if update_quarter_amount == True:
                        old_balance = last_balance
                        last_balance = query_balance(symbol)
                        if last_balance == 0:
                            last_balance = old_balance # in case quary failed
                        delta_balance = (last_balance - old_balance) * 100 / old_balance if old_balance != 0 else 0
                        amount = quarter_amount
                        base_amount = last_balance / last_bond if last_bond > 0 else 1
                        if amount_real > 0: # if set, just use it
                            new_quarter_amount = math.ceil(base_amount * amount_real)
                        else:
                            new_quarter_amount = math.ceil(base_amount / amount_ratio + base_amount * amount_ratio_plus)
                        if new_quarter_amount < 1:
                            new_quarter_amount = quarter_amount # means no real update
                        if abs(close - next_open_start_price) > profit_cost_multiplier * open_cost: # only update if enough gap
                            open_start_price = (open_start_price + next_open_start_price) / 2 # if new order, update open_start_price from next_open_start_price
                        do_updating = 'no '
                        if update_quarter_amount_forward and delta_balance > 0 and quarter_amount < new_quarter_amount : # auto update
                            do_updating = 'do '
                            quarter_amount = new_quarter_amount
                        elif update_quarter_amount_backward and delta_balance < 0 and quarter_amount > new_quarter_amount  : # auto update
                            do_updating = 'do '
                            quarter_amount = new_quarter_amount
                        print (trade_timestamp(), '%supdate quarter_amount from %s=>%s, balance=%f=>%f,%f%%' %
                               (do_updating, 
                                amount, new_quarter_amount, 
                                old_balance, last_balance, delta_balance))
                if close_greedy == True:
                    print (trade_timestamp(), 'greedy signal %s at %s => %s %0.2f (%s%s)' % (l_dir, previous_close, close, price_delta,
                                                                                       'forced ' if forced_close == True else '',  'closed'))
                    if forward_greedy:
                        if globals()['greedy_same_amount']:
                            issue_quarter_order_now_conditional(symbol, reverse_follow_dir, 0, 'close', False)
                        issue_quarter_order_now_conditional(symbol, l_dir, thisweek_amount_pending, 'close', False)
                    if backward_greedy:    
                        issue_quarter_order_now_conditional(symbol, reverse_follow_dir, 0, 'close', False)
                    thisweek_amount_pending = 0
                    close_greedy = False
                if new_open == True:
                    if new_l_dir == '': 
                        previous_close = close
                        return
                    else:
                        l_dir = new_l_dir
                    trade_file = ''
                    open_greedy = False
                    close_greedy = False
                    open_price = 0.0
                    greedy_count = greedy_count_max
                    
                    if l_dir == '': # no updating
                        previous_close = close
                        return
                    
                    # do open
                    trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, l_dir)
                    # print (trade_file)
                    globals()['signal_open_order_with_%s' % l_dir](l_index, trade_file, close)
                    issue_quarter_order_now(symbol, l_dir, quarter_amount, 'open')
                    
                    (open_price, no_use) = real_open_price_and_cost(symbol, globals()['contract'], l_dir) if not options.emulate else (close, 0.001)
                    t_bond = query_bond(symbol, globals()['contract'], l_dir)
                    if t_bond > 0:
                        last_bond = t_bond
                        t_open_cost = open_price * last_fee / last_bond  # just see cost
                        open_cost = max(open_cost, t_open_cost)
                    if open_start_price == 0:
                        open_start_price = prices[ID_OPEN] # when seeing this price, should close, init only once
                    previous_close = close
    return greedy_status

direction = 0

total_revenue = 0
previous_close_price = 0
total_orders = 0
old_total_revenue = 0
    
amount = 1
old_ema_0 = 0
direction = ''
old_close = 0
average_open_price = 0
old_delta = 0
delta = 0
                
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
                            # save old close_mean
                            old_close_mean = boll[0]
            except Exception as ex:
                    print (fpath)
        files = None
        #print (close_mean)
    except Exception as ex:
        print (traceback.format_exc())

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

def wait_signal_notify(notify, signal, shutdown, guard):
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
                globals()['try_to_trade_%s' % signal](notify, guard)
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
                status = globals()['try_to_trade_%s' % signal](subpath, guard)
                if status != 'no action':
                    globals()['save_status_%s' % signal](subpath)
                    # print (globals()['trade_status'])
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
                  action="store_true", default=False,
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
parser.add_option('', '--nolog', dest='nolog', 
                  action='store_true', default=False,
                  help='Do not log to file')
parser.add_option('', '--ratio', dest='amount_ratio', default=9,
                  help='default trade ratio of total amount')
parser.add_option('', '--open_start_price', dest='open_start_price',
                  help='init open_start_price')
parser.add_option('', '--previous_close', dest='previous_close',
                  help='init previous_close')
parser.add_option('', '--restore_status', dest='restore_status',
                  action='store_false', default=True,
                  help='restore status from status_file')
parser.add_option('', '--one_shot', dest='one_shot',
                  action='store_true', default=False,
                  help='just run once, save status and quit')
parser.add_option('', '--self_trigger', dest='do_self_trigger',
                  action='store_false', default=True,
                  help='read price by myself and do following trade')
parser.add_option('', '--noaction', dest='noaction',
                  action='store_true', default=False,
                  help='dry run, no real buy/sell action')

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
# print ('ratio will read from %s if exist, default is %d' % (ratio_file, amount_ratio), flush=True)

trade_notify = '%s.%strade_notify' % (l_dir, l_prefix) # file used to notify trade
logfile='%s.log' % trade_notify
logging.basicConfig(filename=logfile, 
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG)
#logging.info('trade_notify: %s' % trade_notify)
if not options.nolog:
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
    f.write('%d' % os.getpid())
    f.close()
print ('sid %d pgrp %d pid %d saved to file %s' % (os.getsid(os.getpid()), os.getpgrp(), os.getpid(), pid_file))

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

if options.restore_status and \
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
                       '15min': 15 * 60,
                       '5min': 5 * 60,
                       '3min': 3 * 60,
                       '1min': 60}

# logic copied from signal_notify.py
def prepare_for_self_trigger(notify, signal, l_dir):
    symbol=symbols_mapping[figure_out_symbol_info(notify)]
    contract=figure_out_contract_info(notify)
    period=figure_out_period_info(notify)
    try:
        reply=eval('%s' % (okcoinFuture.future_kline(symbol, period, contract, '1')))[0]
        price_filename0 = os.path.join(l_dir, '%s' % (reply[0]))
        price_filename = os.path.join(l_dir, '%s.%s' % (reply[0], signal))
        if os.path.isfile(price_filename) and os.path.getsize(price_filename) > 0:
            # print (trade_timestamp(), '%s is already exist' % (price_filename))
            return price_filename
        # print ('save price to %s' % price_filename)
        with open(price_filename0, 'w') as f:
            f.write('%s, %s, %s, %s, %s, %s' %
                    (reply[1], reply[2], reply[3], reply[4], reply[5], reply[6]))
            f.close()
        with open(price_filename, 'w') as f:
            f.write('%s, %s, %s, %s, %s, %s' %
                    (reply[1], reply[2], reply[3], reply[4], reply[5], reply[6]))
            f.close()
        with open(notify, 'w') as f:
            f.write(price_filename)
            f.close()
            # print ('save signal to %s' % notify)
        return price_filename
    except Exception as Ex:
        print (trade_timestamp(), traceback.format_exc())
        return None

def calculate_timeout_for_self_trigger(notify):
    period_ms = periods_mapping_ms[figure_out_period_info(notify)]
    moduls =int(datetime.datetime.now().strftime('%s')) % period_ms
    delta = 30
    timeout = (period_ms - moduls) - delta
    if timeout > 0:
        return (timeout, delta)
    else:
        return (-1, delta) # wait at least this long time of seconds

contract = figure_out_contract_info(signal_notify)

first_prompt = True
guard_count = 0
while True:
    orig_startup_notify = startup_notify
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
    if first_prompt:
        print (trade_timestamp(), 'Waiting for process new coming file\n', flush=True)
        first_prompt = False
    #issue kickup signal
    with open('%s.ok' % trade_notify, 'w') as f:
        f.close()

    if options.do_self_trigger:
        (timeout, delta) = calculate_timeout_for_self_trigger(signal_notify)

        if timeout > 0: # wait for triggering
            if guard_count == 0:
                guard_count = timeout / guard_timeout
            if on_guard and guard_count > 0: # using guard_timeout
                guard_count -= 1
                time.sleep(guard_timeout)
            else:
                #print (trade_timestamp(),
                #       'wait for next period about %dh:%dm:%ds later' %
                #       (timeout / 60 / 60,
                #        (timeout % 3600) / 60,
                #        timeout - int(timeout / 60) * 60))
                time.sleep(timeout)
                on_guard = False
                guard_count = 0
        else:
            #print (trade_timestamp(), 'trigger safely')
            pass
        prepare_for_self_trigger(signal_notify, l_signal, l_dir)

    wait_signal_notify(signal_notify, l_signal, shutdown_notify, on_guard)

    if options.do_self_trigger:
        time.sleep(delta)

    if options.one_shot:
        break

    if shutdown_notify != '':
        print (trade_timestamp(), 'shutdown signal processed')
    # flush stdout and stderr
    sys.stdout.flush()
    sys.stderr.flush()
    if startup_notify == '' and orig_startup_notify != '':
        break;

# >>> datetime.date.today().strftime('%s')
# '1534003200'
