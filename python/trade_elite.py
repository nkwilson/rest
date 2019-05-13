#!/usr/bin/python3
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

import sys
import getopt
import traceback

import pandas
import numpy
import datetime
from datetime import datetime as dt

import os
import os.path as path
import time
import random
import math
import threading


from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture

import subprocess
from subprocess import PIPE, run

import filelock

import json

print (sys.argv)
#print (globals()[sys.argv[1]](sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))

from optparse import OptionParser
parser = OptionParser()
parser.add_option('', '--signal', dest='signal', default='boll',
                  help='use wich signal to generate trade notify and also as prefix')
parser.add_option('', '--policy', dest='policy', default='boll_greedy',
                  help='should receive policy notify, key is [boll_greedy]')
parser.add_option('', '--amount', dest='amount', default=1,
                  help='default trade amount')
parser.add_option('', '--rate', dest='rate', default=0,
                  help='default positive revenue rate')
parser.add_option('', '--ratio', dest='amount_ratio', default=9,
                  help='default trade ratio of total amount')

(options, args) = parser.parse_args()
print (type(options), options, args)

l_dir = args[0].rstrip('/')
#print (l_dir, os.path.basename(l_dir))

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

def figure_best_price_buy(symbol, contract_type='quarter', depth='10'):
    data=okcoinFuture.future_depth(symbol, contract_type, depth)
    # print (data['asks'])
    #return data['asks'][0][0] * (1 + 0.001) # the biggest ask, 0.003/0.005 may trigger 20018/too big price error
    return data['asks'][4][0]

def figure_best_price_sell(symbol, contract_type='quarter', depth='10'):
    data=okcoinFuture.future_depth(symbol, contract_type, depth)
    # print (data['bids'])
    #return data['bids'][int(depth) - 1][0] * (1 - 0.001) # the smallest bid
    return data['bids'][4][0]

def check_match_price_and_lever_rate(price, lever_rate):
    if price == '':
        match_price = '1'
    else:
        match_price = '0'
    if lever_rate != '10':
        lever_rate = '20'
    return match_price, lever_rate

def open_quarter_sell_rate(symbol, amount, price='', lever_rate='10'):
    match_price, lever_rate = check_match_price_and_lever_rate(price, lever_rate)
    return okcoinFuture.future_trade(symbol, 'quarter', price, amount, '2',
                                     match_price,
                                     lever_rate)

def close_quarter_sell_rate(symbol, amount, price='', lever_rate='10'):
    match_price, lever_rate = check_match_price_and_lever_rate(price, lever_rate)
    return okcoinFuture.future_trade(symbol, 'quarter', price, amount, '4',
                                     match_price,
                                     lever_rate)

def open_quarter_buy_rate(symbol, amount, price='', lever_rate='10'):
    match_price, lever_rate = check_match_price_and_lever_rate(price, lever_rate)
    return okcoinFuture.future_trade(symbol, 'quarter', price, amount, '1',
                                     match_price,
                                     lever_rate)

def close_quarter_buy_rate(symbol, amount, price='', lever_rate='10'):
    match_price, lever_rate = check_match_price_and_lever_rate(price, lever_rate)
    return okcoinFuture.future_trade(symbol, 'quarter', price, amount, '3',
                                     match_price,
                                     lever_rate)

#print (u'期货批量下单')
#print (okcoinFuture.future_batchTrade('ltc_usd','this_week','[{price:0.1,amount:1,type:1,match_price:0},{price:0.1,amount:3,type:1,match_price:0}]','20'))

#print (u'期货取消订单')
#print (okcoinFuture.future_cancel('ltc_usd','this_week','47231499'))

#print (u'期货获取订单信息')
#print (okcoinFuture.future_orderinfo('ltc_usd','this_week','47231812','0','1','2'))

def quarter_orderinfo(symbol, order_id):
    return okcoinFuture.future_orderinfo(symbol,'quarter',order_id,'0','1','2')

#print (u'期货逐仓账户信息')
#print (json.loads(okcoinFuture.future_userinfo_4fix()))

#print (u'期货逐仓持仓信息')
#print (json.loads(okcoinFuture.future_position_4fix('ltc_usd','quarter', '1')))

last_bond = 0 # means uninitialized
last_balance = 0

def quarter_auto_bond(symbol):
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, 'quarter', '1'))
    # print (holding)
    if holding['result'] != True:
        return 0 # 0 means failed
    if len(holding['holding']) == 0:
        return 0
    for data in holding['holding']:
        if data['symbol'] == symbol:
            if data['buy_amount'] > 0:
                bond=data['buy_bond']/data['buy_amount']
            elif data['sell_amount'] > 0:
                bond=data['sell_bond']/data['sell_amount']
            return bond
    return 0
    
def quarter_auto_balance(symbol):
    coin = symbol[0:symbol.index('_')]
    result=json.loads(okcoinFuture.future_userinfo_4fix())
    if result['result'] != True:
        return 0
    balance=result['info'][coin]['balance']
    return balance

#print (quarter_auto_bond('ltc_usd'), quarter_auto_balance('ltc_usd'))
#os.sys.exit(0)

def figure_out_symbol_info(path):
    start_pattern = 'ok_sub_future'
    end_pattern = '_kline_'
    start = path.index(start_pattern) + len(start_pattern)
    end = path.index(end_pattern)
    # print (path[start:end])
    return path[start:end]

trade_file = ''  # signal storing file
amount_file = '' # if exist, read from file
default_amount = 1 # default amount, if auto then figure it out 
amount = default_amount
auto_amount = 0 # if non-zero, auto figure out amount; enabled if amount_file no exists

rate_file = '' # if exist, read rate from file
default_rate = float(options.rate) # default rate
rate = default_rate

ratio_file = '' # if exist read ratio from file
default_amount_ratio = float(options.amount_ratio) # means use 1/50 of total amount on one trade, if auto_amount
amount_ratio = default_amount_ratio


order_infos = {'usd_btc':'btc_usd',
               'usd_ltc':'ltc_usd',
               'usd_eth':'eth_usd',
               'usd_eos':'eos_usd',                              
               'usd_bch':'bch_usd',
               'sell':{'open':open_quarter_sell_rate,
                       'close':close_quarter_sell_rate},
               'buy':{'open':open_quarter_buy_rate,
                      'close':close_quarter_buy_rate}}

# use global trade queue file to sync trade process
trade_queue = ''
trade_queue_lock = ''

def queue_trade_order(subpath):
    with filelock.FileLock(trade_queue_lock, timeout=20) as flock:
        with open(trade_queue, 'a') as f:
            f.write(subpath)

def trade_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#print (quarter_orderinfo('bch_usd', '1460633310147580'))
#print (quarter_orderinfo('bch_usd', '1426230836341760'))
#os.sys.exit()

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
            except Exception as ex:
                l_var = globals()['default_%s' % var_name]
                print ('%s reset to default %f' % (var_name, l_var))
        f.close()
        globals()[var_name] = l_var
        return True
    return False

def wrapper():
        print ('', end='', flush=True)
        if read_int_var(amount_file, 'amount') == False:
            auto_amount = 1
            print ('switched to auto amount policy\n')
        read_int_var(rate_file, 'rate')
        read_int_var(ratio_file, 'amount_ratio')

        result = do_trade_new(subpath)
        time.sleep(1)
        if result.index('go'):
            redo = 0 # if go, reset it 
        print ('', end='', flush=True)


l_signal = options.signal
l_prefix = '%s_' % l_signal

amount_file = '%s.%samount' % (l_dir, l_prefix)
print ('amount will read from %s if exist, default is %d' % (amount_file, amount), flush=True)

rate_file = '%s.%srate' % (l_dir, l_prefix)
print ('rate will read from %s if exist, default is %f' % (rate_file, rate), flush=True)

ratio_file = '%s.%sratio' % (l_dir, l_prefix)
print ('ratio will read from %s if exist, default is %d' % (ratio_file, amount_ratio), flush=True)


# 调用  websocket 中的 okcoin_websocket.py 来获取实时价格，写入到对应的目录中
# 调用 rest 中的 process_price_fsevents.py 来监控价格数据，生成 bolinger band 数据写入相同目录下的 .boll文件
# 调用 rest 中的 watch_poll_price.py 来监控boll数据，并根据趋势生成交易信号，分别写入 .sell 或者  .buy 文件
# 最后调用 Client.py 根据信号来执行交易

# 首先，用 boll 1hour 触发入场交易

def issue_order_now(symbol, direction, amount, action):
    print (symbol, direction, amount, action)
    raw_result = order_infos[direction][action](symbol, amount)
    result = json.loads(raw_result)
    #print (result)
    if result['result'] == False:
        return False
    order_id = str(result['order_id']) # no exceptions, means successed
    #print (order_id)
    order_info = json.loads(quarter_orderinfo(symbol, order_id))
    #print (order_info)
    return True

print ('Usage: symbol direction amount action\n')
print (sys.argv)
print (issue_order_now(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
