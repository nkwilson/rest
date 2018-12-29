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
    return data['asks'][0][0] * (1 + 0.005) # the biggest ask

def figure_best_price_sell(symbol, contract_type='quarter', depth='10'):
    data=okcoinFuture.future_depth(symbol, contract_type, depth)
    # print (data['bids'])
    return data['bids'][int(depth) - 1][0] * (1 - 0.005) # the smallest bid

def check_match_price_and_lever_rate(price, lever_rate):
    if price == '':
        match_price = '1'
    else:
        match_price = '0'
    if lever_rate != '10':
        lever_rate = '20'
    return match_price, lever_rate

def open_quarter_sell_rate(symbol, amount, price='', lever_rate='20'):
    price = figure_best_price_sell(symbol)
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
    price = figure_best_price_buy(symbol)
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
#print (json.loads(okcoinFuture.future_userinfo_4fix()))

#print (u'期货逐仓持仓信息')
#print (json.loads(okcoinFuture.future_position_4fix('ltc_usd','quarter', '1')))

last_bond = 0 # means uninitialized
last_balance = 0

def quarter_auto_bond(symbol):
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, 'quarter', '1'))
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
auto_amount = 0 # if non-zero, auto figure out amount; enabled if amount_file no exists

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

order_dict = dict()
#{ 'subpath':'price', ..}
# if rate touched, close specified orders in order_dict
def cleanup_boll_greedy_order(close='', rate=''):
    topop = list()
    for key in order_dict.keys():
        subsubpath = order_dict[key]
        direction = os.path.splitext(subsubpath)[1][1:]
        if direction == 'sell':
            plus = (float(key) - float(close))/float(key)
        else:
            plus = (float(close) - float(key))/float(key)
        if close == '' or plus > float(rate):
            print ('cleanup %s at %s with %s' % (subsubpath, key, close))
            do_trade_new('%s.close' % subsubpath)
            list.append(key)
            # every 5s for each order
            time.sleep(5)
    for key in topop:
        order_dict.pop(key, None)
    pass

# when open, reset order_dict
def setup_boll_greedy_order(subpath, close):
    key = '%s' % close
    if order_dict.get(key) == None:
        order_dict[key] = subpath
    else:
        key = '%s' % (close + 0.00001) # plus mini value
        order_dict[key] = subpath
    print ('setup %s at %s' % (subpath, key))
    pass

# inotify specified dir to catch trade signals
# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def do_trade_new(subpath):
    global amount, last_balance, last_bond
    global startup_notify, shutdown_notify
    #print (subpath)
    # only process file event of .boll.log
    raw_symbol = figure_out_symbol_info(subpath)
    # get '.open' or '.close' action suffix
    pathext = os.path.splitext(subpath)
    action = pathext[1][1:]
    subsubpath = pathext[0]
    #print (pathext, subsubpath, action)
    # get '.buy' or '.sell' suffix
    direction = os.path.splitext(subsubpath)[1][1:]
    # print (direction, action)
    symbol = order_infos[raw_symbol]
    print (trade_timestamp(), symbol, order_infos[direction][action])
    msg = 'failed' # means failed
    try:
        l_amount = amount
        if action == 'close': # if close, read order_id info from subsubpath
            order_id = ''
            raw_order_info = ''
            id_amounts = 0
            try: # in case read amount failed
                with open(subsubpath, 'r') as f:
                    order_ids = f.readline().split(',')[1:]
                    f.close()
                for this_id in order_ids:
                    raw_order_info = quarter_orderinfo(symbol, this_id)
                    order_info = json.loads(raw_order_info)
                    if order_info['result'] == False:
                        continue
                    this_order = order_info['orders'][0]
                    if this_order['type'] < 3: # 1: buy, 2:sell
                        this_amount = int(this_order['amount'])
                        print ('order %s has %d' % (this_id, this_amount))
                        id_amounts += this_amount
                    else:
                        # unexpected type, skip and return
                        return msg
            except Exception as ex:
                print (order_id, raw_order_info)
                print (ex)
                print (traceback.format_exc())
                pass
            finally:
                if id_amounts != 0:
                    l_amount = id_amounts
                    print ('amount may accumulated to %d' % l_amount)
        raw_result = order_infos[direction][action](symbol, l_amount)
        result = json.loads(raw_result)
        msg = 'failed,go'
        print (result)
        order_id = str(result['order_id']) # no exceptions, means successed
        msg = 'successed,go'
        #print (order_id)
        order_info = json.loads(quarter_orderinfo(symbol, order_id))
        print (order_info)
        if action == 'open': # figure bond info
           # generate startup notify
           with open(startup_notify, 'w') as f:
              f.write('%s' % order_info)
              f.close()
              print ('%s startup signal generated' % trade_timestamp())
           # append amount info to subsubpath
           with open(subsubpath, 'a') as f:
              f.write(',%s' % order_id)
              f.close()
           # order ok
           # first argument is stripped subpath, second is price in order_info
           if order_info['orders'][0]['price_avg'] == 0:
               globals()['setup_%s_order' % options.policy](subsubpath, order_info['orders'][0]['price'])
           else:
               globals()['setup_%s_order' % options.policy](subsubpath, order_info['orders'][0]['price_avg'])
        elif action == 'close': # figure balance info
            # close all unconditionally
            globals()['cleanup_%s_order' % options.policy]()
            # generate shutdown notify
            with open(shutdown_notify, 'w') as f:
                f.write('%s' % order_info)
                f.close()
                print ('%s shutdown signal generated' % trade_timestamp())
            # only update when no holdings, check with bond
            balance = 0
            if quarter_auto_bond(symbol) == 0:
                balance = quarter_auto_balance(symbol)
            if balance > 0 and last_bond > 0: # successed
                print ('balance is updated from %f to %f\n' % (last_balance, balance))
                last_balance = balance
    except Exception as ex:
        print (ex)
        print (traceback.format_exc())
    return msg

trade_notify = ''
# wait on trade_notify for signal
def wait_trade_notify(notify, policy_notify='', rate='0.01'):
    global amount, auto_amount
    while True:
        print ('', end='', flush=True)
        command = ['fswatch', '-1', notify, policy_notify]
        if os.path.isfile(amount_file) and os.path.getsize(amount_file)>0:
            auto_amount = 0
            # check if should read amount from file
            with open(amount_file) as f:
                old_amount = amount
                try:
                    amount = int(f.readline())
                    if old_amount != amount:
                        print ('amount updated to %d' % amount)
                except Exception as ex:
                    amount = default_amount
                    print ('amount reset to default %d' % amount)
        else: # no amount file means auto
            if auto_amount != 1:
                print ('switched to auto amount policy\n')
            auto_amount = 1
        try:
            result = subprocess.run(command, stdout=PIPE) # wait file modified
            rawdata = result.stdout.decode().split('\n')
            # should sort rawdata by notify date
            # print (rawdata)
            for data in rawdata:
                if len(data) > 7:
                    if data == notify:
                        # print (data)
                        subpath = data
                        with open(subpath, 'r') as f:
                            subpath = f.readline().rstrip('\n')
                            queue_trade_order(subpath)
                            f.close()
                        break
                    elif data == policy_notify:
                        # print (data)
                        subpath = data
                        # read close from policy_notify
                        with open(subpath, 'r') as f:
                            close = f.readline().rstrip('\n')           
                            globals()['cleanup_%s_order' % options.policy](close, rate)
                            f.close()
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
                #time.sleep(1)
                last_subpath = ''
                redo = 0
                for subpath in orders:
                    last_subpath = subpath
                    try:
                        # print ('order: %s' % subpath)
                        result = do_trade_new(subpath)
                        time.sleep(1)
                        if result.index('go'):
                            continue
                    except Exception as ex:
                        if redo > 3:
                            print ('more than %d redo, quit' % redo)
                            break
                        orders.append(subpath)
                        print ('append %s to do it again' % subpath)
                        redo +=1 
                if os.path.isfile(stop_notify) and last_subpath.endswith('.close'):
                    print ('stop signaled by %s, quit now' % stop_notify)
                    os.unlink(stop_notify)
                    print ('%s unlinked' % stop_notify)
                    break
        except Exception as ex:
            print (ex)
            print (traceback.format_exc())
            continue
        print ('', end='', flush=True)

print (sys.argv)
#print (globals()[sys.argv[1]](sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))

from optparse import OptionParser
parser = OptionParser()
parser.add_option('', '--signal', dest='signal', default='boll',
                  help='use wich signal to generate trade notify and also as prefix')
parser.add_option('', '--policy', dest='policy', default='boll_greedy',
                  help='should receive policy notify, key is [boll_greedy]')

(options, args) = parser.parse_args()
print (type(options), options, args)

l_dir = args[0].rstrip('/')
#print (l_dir, os.path.basename(l_dir))

l_signal = options.signal
l_prefix = '%s_' % l_signal

logfile='%s.%strade.log' % (l_dir, l_prefix)
saved_stdout = sys.stdout
sys.stdout = open(logfile, 'a')
print (dt.now())

trade_queue = os.path.join(os.path.dirname(l_dir), '%strade_queue' % (l_prefix))
trade_queue_lock = '%s.lock' % trade_queue
print ('trade_queue: is %s' % trade_queue)

trade_notify = '%s.%strade_notify' % (l_dir, l_prefix)
print ('trade_notify is %s' % trade_notify)

if options.policy != '':
    policy_notify = '%s.%s_notify' % (l_dir, options.policy)
else:
    policy_notify = ''
print ('policy_notify is %s' % policy_notify)

amount_file = '%s.%samount' % (l_dir, l_prefix)
print ('amount will read from %s if exist, default is %d' % (amount_file, amount), flush=True)

stop_notify = '%s.%strade.stop_notify' % (l_dir, l_prefix) # file indicate trade should stop
print ('stop_notify: %s' % stop_notify)

startup_notify = '%s.%strade.startup' % (l_dir, l_prefix)
shutdown_notify = '%s.%strade.shutdown' % (l_dir, l_prefix)
print ('startup_notify: %s' % startup_notify)
print ('shutdown_notify: %s' % shutdown_notify)

pid_file = '%s.%strade.pid' % (l_dir, l_prefix)
# os.setsid() # privilge
#print (os.getpgrp(), os.getpgid(os.getpid()))
with open(pid_file, 'w') as f:
    f.write('%d' % os.getpgrp())
print ('sid is %d, pgrp is %d, saved to file %s' % (os.getsid(os.getpid()), os.getpgrp(), pid_file))

trade_notify = os.path.realpath(trade_notify)
policy_notify= os.path.realpath(policy_notify)
wait_trade_notify(trade_notify, policy_notify)

# 调用  websocket 中的 okcoin_websocket.py 来获取实时价格，写入到对应的目录中
# 调用 rest 中的 process_price_fsevents.py 来监控价格数据，生成 bolinger band 数据写入相同目录下的 .boll文件
# 调用 rest 中的 watch_poll_price.py 来监控boll数据，并根据趋势生成交易信号，分别写入 .sell 或者  .buy 文件
# 最后调用 Client.py 根据信号来执行交易

# 首先，用 boll 1hour 触发入场交易
