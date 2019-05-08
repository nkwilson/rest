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

apikey = 'e2625f5d-6227-4cfd-9206-ffec43965dab'
secretkey = "27BD16FD606625BCD4EE6DCA5A8459CE"
okcoinRESTURL = 'www.okex.com'
    
#现货API
okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)

#期货API
okcoinFuture = OKCoinFuture(okcoinRESTURL,apikey,secretkey)


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
parser.add_option('', '--policy', dest='policy', default='simple_greedy', 
                  help="use specified trade policy, ema_greedy/close_ema/boll_greedy/simple_greedy")
parser.add_option('', '--which_ema', dest='which_ema', default=0, 
                  help='using with one of ema')
parser.add_option('', '--order_num', dest='order_num',
                  help='how much orders')
parser.add_option('', '--fee_amount', dest='fee_amount',
                  action='store_true', default=False,
                  help='take amount int account with fee')
parser.add_option('', '--signal', dest='signals', default=[],
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

(options, args) = parser.parse_args()
print (type(options), options, args)

latest_to_read = int(options.latest_to_read)

pick_old_order = options.pick_old_order

l_signal = options.signals[0]
l_prefix = '%s_' % l_signal
l_dir = options.dirs[0]

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
            line = eval(f.readline().rstrip('\n'))  # can't just copy from boll
            prices = float(line[0:3])
            f.close()
            # close = eval(f.readline())[3]
    except Exception as ex:
        print ('read_4prices: %s' % filename)
    # print (close)
    return prices

open_price = 0

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

def quarter_auto_bond(symbol, direction):
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, 'quarter', '1'))
    # print (holding)
    if holding['result'] != True:
        return 0.0 # 0 means failed
    if len(holding['holding']) == 0:
        return 0.0
    for data in holding['holding']:
        if data['symbol'] == symbol:
            if data['%s_amount' % direction] > 0:
                return data['%s_bond' % direction]/data['%s_amount' % direction]
    return 0.0
    
def quarter_auto_balance(symbol):
    coin = symbol[0:symbol.index('_')]
    result=json.loads(okcoinFuture.future_userinfo_4fix())
    if result['result'] != True:
        return 0.0
    balance=result['info'][coin]['balance']
    return float(balance)

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
                    return (close - open_price)
        elif close < previous_close:
            if open_greedy == False:
                if close > open_start_price: # positive profit
                    return 0
                else:
                    return (close - open_start_price)
            else:
                if close > open_start_price: # positive profit
                    return 0
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
                    return -(close - open_price)
        elif close > previous_close:
            if open_greedy == False:
                if close < open_start_price: # positive profit
                    return 0
                else:
                    return -(close - open_start_price)
            else:
                if close < open_start_price: # positive profit
                    return 0
                else:
                    return -(close - open_start_price)
    pass

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
def real_open_price_and_cost(symbol, direction, prices):
    if prices != None: # when do emulation
        return (prices[ID_CLOSE], 0.001)
    holding=json.loads(okcoinFuture.future_position_4fix(symbol, 'quarter', '1'))
    if holding['result'] != True:
        return 0
    if len(holding['holding']) == 0:
        return 0
    # print (holding['holding'])
    for data in holding['holding']:
        if data['symbol'] == symbol and data['%s_amount' % direction] != 0:
            last_bond = quarter_auto_bond(symbol, direction)
            avg = data['%s_price_avg' % direction]
            real= data['profit_real']
            return (float(avg), float(avg)*float(real))
    return 0

def try_to_trade_tit2tat(subpath):
    global trade_file, old_close_mean
    global old_open_price
    global close_mean, close_upper, close_lower
    global old_close, bins, direction
    global l_trade_file
    global previous_close
    global open_greedy
    global open_price, open_start_price
    global open_cost
    
    #print (subpath)
    event_path=subpath
    l_index = os.path.basename(event_path)
    # print (l_index, event_path)
    if True: # type 256, new file event
        prices = read_4prices(event_path)
        close = prices[ID_CLOSE]
        l_dir = ''
        if trade_file == '':
            print ('%9.3f' % close, '-')
        elif trade_file.endswith('.sell') == True: # sell order
            l_dir = 'sell'
            print ('%8.3f' % -close, '%9.3f' % open_price, l_dir)
        elif trade_file.endswith('.buy') == True: # buy order
            l_dir = 'buy'
            print ('%9.3f' % close, '%8.3f' % -open_price, l_dir)
        if close == 0: # in case read failed
            return
        if True:
            if True:
                if previous_close == 0:
                    previous_close = close
                    return
                
                symbol=symbols_mapping[figure_out_symbol_info(event_path)]
                
                new_open = True if trade_file == '' else False
                
                if new_open == False and check_forced_close(symbol, l_dir, prices if options.emulate else None):
                    # suffered forced close
                    globals()['signal_close_order_with_%s' % l_dir](l_index, trade_file, close)
                    new_open = True
                
                if new_open == False:
                    # delay here to update open price
                    if open_price == 0:
                        (open_price, open_cost) = real_open_price_and_cost(symbol, l_dir, prices if options.emulate else None)
                    
                    current_profit = check_with_direction(close, previous_close, open_price, open_start_price, l_dir, open_greedy)
                    
                    if current_profit > open_cost: # yes, positive 
                        # do close
                        globals()['signal_close_order_with_%s' % l_dir](l_index, trade_file, close)
                        # and open again, just like new_open == True
                        new_open = True
                        open_greedy = False
                    elif current_profit < -open_cost: # no, negative 
                        # do close
                        globals()['signal_close_order_with_%s' % l_dir](l_index, trade_file, close)
                        # and open again, just list new_open == True
                        new_open = True
                        open_greedy = False
                        open_start_price = open_price # when seeing this price, should close, init only once
                    elif current_profit == 0: # partly no, but still positive consider open_start_price, do greedy process
                        # emit open again signal
                        open_greedy = True
                        with open(policy_notify, 'w') as f:
                            f.write('%s %s %s' % (l_dir, close, previous_close))
                            f.close()
                        print (trade_timestamp(), 'greedy signal %s at %s => %s' % (l_dir, previous_close, close))
                        previous_close = close
                    else:
                        previous_close = close
                        return
                if new_open == True:
                    trade_file = ''
                    open_greedy = False
                    open_price = 0.0
                    open_cost = 0.0
                    
                    if close > previous_close:
                        l_dir = 'buy'
                    elif close < previous_close:
                        l_dir = 'sell'
                    else:
                        previous_close = close
                        return
                    
                    # do open
                    trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, l_dir)
                    # print (trade_file)
                    globals()['signal_open_order_with_%s' % l_dir](l_index, trade_file, close)
                    
                    if open_start_price == 0:
                        open_start_price = prices[ID_OPEN] # when seeing this price, should close, init only once
                    
                    previous_close = close
                    return

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
            wait_signal_notify(fpath, l_signal)
        files = None
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
                break

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

amount_file = '%s.%samount' % (l_dir, l_prefix)

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
    wait_signal_notify(signal_notify, l_signal, shutdown_notify)
    print (trade_timestamp(), 'shutdown signal processed')

    if startup_notify == '':
        break;

# >>> datetime.date.today().strftime('%s')
# '1534003200'

