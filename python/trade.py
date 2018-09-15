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


from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture

import subprocess
from subprocess import PIPE, run

import filelock

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

def figure_best_price_buy(symbol, contract_type='quarter', depth='10'):
    data=okcoinFuture.future_depth(symbol, contract_type, depth)
    # print (data['asks'])
    return data['asks'][0][0] * (1 + 0.001) # the biggest ask

def figure_best_price_sell(symbol, contract_type='quarter', depth='10'):
    data=okcoinFuture.future_depth(symbol, contract_type, depth)
    # print (data['bids'])
    return data['bids'][int(depth) - 1][0] * (1 - 0.001) # the smallest bid

def check_match_price_and_lever_rate(price, lever_rate):
    if price == '':
        match_price = '1'
    else:
        match_price = '0'
    if lever_rate != '10':
        lever_rate = '20'
    return match_price, lever_rate

def open_quarter_sell_rate(symbol, amount, price='', lever_rate='20'):
    match_price, lever_rate = check_match_price_and_lever_rate(price, lever_rate)
    return okcoinFuture.future_trade(symbol, 'quarter', price, amount, '2',
                                     match_price,
                                     lever_rate)

def close_quarter_sell_rate(symbol, amount, price='', lever_rate='20'):
    # should auto figure best close price
    price = figure_best_price_buy(symbol)
    match_price, lever_rate = check_match_price_and_lever_rate(price, lever_rate)
    return okcoinFuture.future_trade(symbol, 'quarter', price, amount, '4',
                                     match_price,
                                     lever_rate)

def open_quarter_buy_rate(symbol, amount, price='', lever_rate='20'):
    match_price, lever_rate = check_match_price_and_lever_rate(price, lever_rate)
    return okcoinFuture.future_trade(symbol, 'quarter', price, amount, '1',
                                     match_price,
                                     lever_rate)

def close_quarter_buy_rate(symbol, amount, price='', lever_rate='20'):
    # should auto figure best close price
    price = figure_best_price_sell(symbol)
    match_price, lever_rate = check_match_price_and_lever_rate(price, lever_rate)
    # print (match_price, lever_rate)
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
#print (okcoinFuture.future_userinfo_4fix())

#print (u'期货逐仓持仓信息')
#print (okcoinFuture.future_position_4fix('ltc_usd','this_week',1))

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
amount = 1

order_infos = {'usd_btc':'btc_usd',
               'usd_ltc':'ltc_usd',
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

#print (quarter_orderinfo('bch_usd', '1460633310147580'))
#print (quarter_orderinfo('bch_usd', '1426230836341760'))
#os.sys.exit()

# inotify specified dir to catch trade signals
# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def do_trade_new(subpath):
    global amount, trade_file
    #print (subpath)
    # only process file event of .boll.log
    symbol = figure_out_symbol_info(subpath)
    # get '.open' or '.close' action suffix
    pathext = os.path.splitext(subpath)
    action = pathext[1][1:]
    subsubpath = pathext[0]
    #print (pathext, subsubpath, action)
    # get '.buy' or '.sell' suffix
    direction = os.path.splitext(subsubpath)[1][1:]
    # print (direction, action)
    print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
           (order_infos[symbol], order_infos[direction][action]))
    msg = 'failed' # means failed
    try:
        result = order_infos[direction][action](order_infos[symbol], amount)
        print (result)
        normal_str = '"result":'
        if result.index(normal_str) == 1: # means successed
            msg = 'successed'
            order_id_msg = '"order_id":'
            order_id = result[result.index(order_id_msg) + len(order_id_msg):-1]
            print (order_id)
            print (quarter_orderinfo(symbol, order_id))
    except Exception as ex:
        print (ex)
    return msg

trade_notify = ''
# wait on trade_notify for signal
def wait_trade_notify(notify):
    global amount
    while True:
        print ('', end='', flush=True)
        command = ['fswatch', '-1', notify]
        try:
            # check if should read amount from file
            with open(amount_file) as f:
                old_amount = amount
                amount = int(f.readline())
                if old_amount != amount:
                    print ('amount updated to %d' % amount)
        except Exception as ex:
            amount = default_amount
            print ('amount reset to default %d' % amount)
        try:
            result = subprocess.run(command, stdout=PIPE) # wait file modified
            rawdata = result.stdout.decode().split('\n')
            # print (rawdata)
            for data in rawdata:
                if len(data) > 7 and data == notify:
                    # print (data)
                    subpath = data
                    with open(subpath, 'r') as f:
                        subpath = f.readline().rstrip('\n')
                        queue_trade_order(subpath)
                    break
            if os.path.isfile(trade_queue) == True:
                orders = list()
                # first get file lock, saved and cleared
                # print (trade_queue)
                with filelock.FileLock(trade_queue_lock, timeout=20) as flock:
                    # print ('locked')
                    with open(trade_queue, 'r') as f:
                        for subpath in iter(f.readline, ''):
                            orders.append(subpath)
                    with open(trade_queue, 'w') as f:
                        pass
                # print ('unlocked with %d orders' % len(orders))
                #wait for 10s
                time.sleep(10)
                for subpath in orders:
                    try:
                        # print ('order: %s' % subpath)
                        result = do_trade_new(subpath)
                        time.sleep(5)
                        if result.index('successed'):
                            continue
                    except Exception as ex:
                        orders.append(subpath)
                        print ('append %s to do it again' % subpath)
        except Exception as ex:
            print (ex)
            continue
        print ('', end='', flush=True)

print (sys.argv)
#print (globals()[sys.argv[1]](sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))
l_dir = sys.argv[1].rstrip('/')
#print (l_dir, os.path.basename(l_dir))

trade_queue = os.path.join(os.path.dirname(l_dir), 'trade_queue')
trade_queue_lock = '%s.lock' % trade_queue
print ('trade_queue: is %s' % trade_queue)

trade_notify = '%s.trade_notify' % l_dir
print ('trade_notify is %s' % trade_notify)

amount_file = '%s.amount' % l_dir
print ('amount will read from %s if exist, default is %d' % (amount_file, amount), flush=True)

trade_notify = os.path.realpath(trade_notify)
wait_trade_notify(trade_notify)


# 调用  websocket 中的 okcoin_websocket.py 来获取实时价格，写入到对应的目录中
# 调用 rest 中的 process_price_fsevents.py 来监控价格数据，生成 bolinger band 数据写入相同目录下的 .boll文件
# 调用 rest 中的 watch_poll_price.py 来监控boll数据，并根据趋势生成交易信号，分别写入 .sell 或者  .buy 文件
# 最后调用 Client.py 根据信号来执行交易
