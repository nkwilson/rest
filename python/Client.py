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

import os
import os.path as path
import time
import random
import math
import threading

from fsevents import Observer
from fsevents import Stream

from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture

import subprocess
from subprocess import PIPE, run

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
def future_trade_open_buy(symbol, contract_type, price, amount, match_price):
    okcoinFuture.future_trade(symbol, contract_type, price, amount,'1', match_price)

def future_trade_close_buy(symbol, contract_type, price, amount, match_price):
    okcoinFuture.future_trade(symbol, contract_type, price, amount,'3', match_price)

def future_trade_open_sell(symbol, contract_type, price, amount, match_price):
    okcoinFuture.future_trade(symbol, contract_type, price, amount,'2', match_price)

def future_trade_close_sell(symbol, contract_type, price, amount, match_price):
    okcoinFuture.future_trade(symbol, contract_type, price, amount,'4', match_price)

def btc_usd_open_quarter_sell_10x(amount):
    print (okcoinFuture.future_trade('btc_usd', 'quarter', '', amount, '2', '1', '10'))

def btc_usd_close_quarter_sell_10x(amount):
    print (okcoinFuture.future_trade('btc_usd', 'quarter', '', amount, '4', '1', '10'))

def btc_usd_open_quarter_buy_10x(amount):
    print (okcoinFuture.future_trade('btc_usd', 'quarter', '', amount, '1', '1', '10'))

def btc_usd_close_quarter_buy_10x(amount):
    print (okcoinFuture.future_trade('btc_usd', 'quarter', '', amount, '3', '1', '10'))

def open_quarter_sell_10x(symbol, amount):
    print (okcoinFuture.future_trade(symbol, 'quarter', '', amount, '2', '1', '10'))

def close_quarter_sell_10x(symbol, amount):
    print (okcoinFuture.future_trade(symbol, 'quarter', '', amount, '4', '1', '10'))

def open_quarter_buy_10x(symbol, amount):
    print (okcoinFuture.future_trade(symbol, 'quarter', '', amount, '1', '1', '10'))

def close_quarter_buy_10x(symbol, amount):
    print (okcoinFuture.future_trade(symbol, 'quarter', '', amount, '3', '1', '10'))
    
#print (u'期货批量下单')
#print (okcoinFuture.future_batchTrade('ltc_usd','this_week','[{price:0.1,amount:1,type:1,match_price:0},{price:0.1,amount:3,type:1,match_price:0}]','20'))

#print (u'期货取消订单')
#print (okcoinFuture.future_cancel('ltc_usd','this_week','47231499'))

#print (u'期货获取订单信息')
#print (okcoinFuture.future_orderinfo('ltc_usd','this_week','47231812','0','1','2'))

#print (u'期货逐仓账户信息')
#print (okcoinFuture.future_userinfo_4fix())

#print (u'期货逐仓持仓信息')
#print (okcoinFuture.future_position_4fix('ltc_usd','this_week',1))

# read price data from path, and do trade of period, with specified amount
def do_trade_with_boll(path, period, amount):
    pass

def figure_out_symbol_info(path):
    start_pattern = 'ok_sub_future'
    end_pattern = '_kline_'
    start = path.index(start_pattern) + len(start_pattern)
    end = path.index(end_pattern)
    # print (path[start:end])
    return path[start:end]

trade_file = ''  # signal storing file
amount = 20 # default amount

order_infos = {'usd_btc':'btc_usd',
               'usd_ltc':'ltc_usd',
               'usd_bch':'bch_usd',
               'sell':{'open':open_quarter_sell_10x, 'close':close_quarter_sell_10x},
               'buy':{'open':open_quarter_buy_10x, 'close':close_quarter_buy_10x}}

# inotify specified dir to catch trade signals
# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def do_trade(subpath):
    global amount, trade_file
    global price_lock
    price_lock.acquire()
    sell = False
    buy = False
    #print (subpath)
    tup=eval(str(subpath))
    #print (type(tup), tup[0])
    # only process file event of .boll.log
    symbol = figure_out_symbol_info(tup[2])
    if tup[2].endswith('.sell') == True:
        direction='sell'
        pass
    elif tup[2].endswith('.buy') == True:
        direction='buy'
        pass
    else:
        price_lock.release()
        return
    event_type=tup[0]
    event_path=tup[2]
    print (event_type, event_path)
    if (event_type == 2): # must have a balance signal now
        print (order_infos[symbol], order_infos[direction]['close'])
        order_infos[direction]['close'](order_infos[symbol], amount)
        if sell == True:
            btc_usd_close_quarter_sell_10x(amount)
        elif buy == True:
            btc_usd_close_quarter_buy_10x(amount)
        pass
    elif (event_type != 256):
        print (event_type)
        pass
    else: # type 256, new order signal
        print (order_infos[symbol], order_infos[direction]['open'])
        order_infos[direction]['open'](order_infos[symbol], amount)
        if sell == True:
            btc_usd_open_quarter_sell_10x(amount)
        elif buy == True:
            btc_usd_open_quarter_buy_10x(amount)
        pass
    price_lock.release()

def do_trade_new(subpath):
    global amount, trade_file
    global price_lock
    sell = False
    buy = False
    #print (subpath)
    # only process file event of .boll.log
    symbol = figure_out_symbol_info(subpath)
    # get '.open' or '.close' action suffix
    pathext = os.path.splitext(subpath)
    action = pathext[1]
    subsubpath = pathext[0]
    print (pathext, subsubpath, action)
    # get '.buy' or '.sell' suffix
    direction = os.path.splitext(subsubpath)[1]
    print (direction)
    return

    if (event_type == 2): # must have a balance signal now
        print (order_infos[symbol], order_infos[direction]['close'])
        order_infos[direction]['close'](order_infos[symbol], amount)
        if sell == True:
            btc_usd_close_quarter_sell_10x(amount)
        elif buy == True:
            btc_usd_close_quarter_buy_10x(amount)
        pass
    elif (event_type != 256):
        print (event_type)
        pass
    else: # type 256, new order signal
        print (order_infos[symbol], order_infos[direction]['open'])
        order_infos[direction]['open'](order_infos[symbol], amount)
        if sell == True:
            btc_usd_open_quarter_sell_10x(amount)
        elif buy == True:
            btc_usd_open_quarter_buy_10x(amount)
        pass
    
price_lock = threading.Lock()
print (sys.argv)
#print (globals()[sys.argv[1]](sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))
l_dir = sys.argv[1].rstrip('/')
#print (l_dir, os.path.basename(l_dir))

while True:
    command = ['notifywait', l_dir]
    result = subprocess.run(command, stdout=PIPE) # wait file exist 
    data = result.stdout.decode().split('\n')
    data = data[2].split(' ')
    #print (data)
    if data[0] == 'Change' :
        subpath = data[3].rstrip(',')
        # only consider %.buy or %.sell signal file
        if subpath.endswith(('.open', '.close')) == False:
            continue
        print (subpath)
        # do_trade_new(subpath)
    
# stream = Stream(do_trade, l_dir, file_events=True)
# print ('Waiting for sell signal\n')

# observer = Observer()
# observer.start()

# observer.schedule(stream)



# 调用  websocket 中的 okcoin_websocket.py 来获取实时价格，写入到对应的目录中
# 调用 rest 中的 process_price_fsevents.py 来监控价格数据，生成 bolinger band 数据写入相同目录下的 .boll文件
# 调用 rest 中的 watch_poll_price.py 来监控boll数据，并根据趋势生成交易信号，分别写入 .sell 或者  .buy 文件
# 最后调用 Client.py 根据信号来执行交易
