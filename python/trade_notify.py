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

close_mean = pandas.Series()
close_upper = pandas.Series()
close_lower = pandas.Series()

old_open_price = 0
old_close_mean = 0
window_size = 20
trade_file = ''
default_fee_threshold = 0.012# baesed on one order's fee
fee_threshold = default_fee_threshold
levage_rate = 20

# if fee is bigger than lost, then delay it to next signal
def check_close_sell_fee_threshold(open_price, current_price):
    return abs((current_price - open_price) / open_price) > fee_threshold

def check_close_sell_half_fee_threshold(open_price, current_price):
    return abs((current_price - open_price) / open_price) > (fee_threshold / 2.0)

symbols_mapping = { 'usd_btc': 'btc_usd',
                    'usd_ltc': 'ltc_usd',
                    'usd_bch': 'bch_usd'}

reverse_dirs = { 'buy': {'reverse_dir':'sell', 'gate': lambda order_price, current_price:
                         (order_price > current_price) and check_close_sell_half_fee_threshold(order_price, current_price)},
                         
                 'sell': {'reverse_dir':'buy', 'gate': lambda order_price, current_price:
                        (order_price < current_price) and check_close_sell_half_fee_threshold(current_price, order_price)}}

def figure_out_symbol_info(path):
    start_pattern = 'ok_sub_future'
    end_pattern = '_kline_'
    start = path.index(start_pattern) + len(start_pattern)
    end = path.index(end_pattern)
    # print (path[start:end])
    return path[start:end]

# if current order is permit to issue
def check_open_order_gate(symbol, direction, current_price):
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
                return dirs['gate'](data['%s_price_avg' % dirs['reverse_dir']], current_price)
    return False

def trade_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# open sell order now
def signal_open_order_with_sell(l_index, filename, close):
    if not options.emulate and os.path.isfile(filename) == True: # already ordered
        return
    line = '%s sell at %0.7f' % (l_index, close)
    with open(filename, 'w') as f:
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
    line = '%s buy at %0.7f closed' % (l_index, close)
    with open(filename, 'a') as f:
        f.write(line)
        f.close()
    print (trade_timestamp(), line.rstrip('\n'), flush=True)
    global trade_notify
    with open(trade_notify, 'w') as f:
        f.write('%s.close' % filename)
        f.close()


# open buy order now
def signal_open_order_with_buy(l_index, filename, close):
    if not options.emulate and os.path.isfile(filename) == True: # already ordered
        return
    line = '%s buy at %0.7f' % (l_index, close)
    with open(filename, 'w') as f:
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
    line = '%s sell at %0.7f closed' % (l_index, close)
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

latest_to_read = 15000
new_trade_file = True

pick_old_order = True # try to pick old order
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

# inotify specified dir to plot living price
# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def plot_living_price_new(subpath):
    global window_size, trade_file, old_close_mean
    global old_open_price
    global close_mean, close_upper, close_lower
    #print (subpath)
    event_path=subpath
    l_index = os.path.basename(event_path)
    # print (l_index, event_path)
    if True: # type 256, new file event
        boll = read_boll(event_path)
        close = read_close(event_path)
        print (boll, close, old_open_price)
        if boll == 0 or close == 0: # in case read failed
            return
        if math.isnan(boll[0]) == False:
                close_mean[l_index]=boll[0]
                close_upper[l_index]=boll[1]
                close_lower[l_index]=boll[2]
                fresh_trade = False
                symbol=symbols_mapping[figure_out_symbol_info(event_path)]
                # print (symbol)
                if boll[0] < old_close_mean: # open sell order
                    if trade_file == '' and check_open_order_gate(symbol, 'sell', close):
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'sell')
                        # print (trade_file)
                        signal_open_order_with_sell(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                elif boll[0] > old_close_mean: # open buy order
                    if trade_file == '' and check_open_order_gate(symbol, 'buy', close):
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'buy')
                        # print (trade_file)
                        signal_open_order_with_buy(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                old_close_mean = boll[0] # update unconditiionally
                if fresh_trade == True: # ok, fresh trade
                    pass
                elif trade_file == '':  # no open trade
                    pass
                # close is touch upper
                elif close > boll[1] and trade_file.endswith('.sell') == True :
                    # check if return bigger than fee
                    if check_close_sell_fee_threshold(old_open_price, close) == True:
                        signal_close_order_with_buy(l_index, trade_file, close)
                        trade_file = ''  # make trade_file empty to indicate close
                # close is touch lower
                elif close < boll[2] and trade_file.endswith('.buy') == True :
                    # check if return bigger than fee
                    if check_close_sell_fee_threshold(old_open_price, close) == True:
                        signal_close_order_with_sell(l_index, trade_file, close)
                        trade_file = ''  # make trade_file empty to indicate close
                elif close_lower.count() > 10 * latest_to_read:
                    close_lower = close_lower[-latest_to_read:]
                    close_mean = close_mean[-latest_to_read:]
                    close_upper = close_upper[-latest_to_read:]
                    print ('Reduce data size to %d', close_lower.count())

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

def try_to_trade(subpath):
    global window_size, trade_file, old_close_mean
    global total_revenue, previous_close_price
    global old_open_price
    global close_mean, close_upper, close_lower
    global trade_notify
    #print (subpath)
    event_path=subpath
    l_index = os.path.basename(event_path)
    # print (l_index, event_path)
    if True: # type 256, new file event
        ema = read_ema(event_path)
        close = read_close(event_path)
        if not options.emulate:
            print (ema, close, old_open_price, '^' if ema[0] > ema[1] else 'v')
        if ema == 0 or close == 0: # in case read failed
            return
        if math.isnan(ema[0]) == False:
                fresh_trade = False
                symbol=symbols_mapping[figure_out_symbol_info(event_path)]
                # print (symbol)
                if ema[0] < ema[1] : # open sell order
                    if trade_file == '' and check_open_order_gate(symbol, 'sell', close):
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'sell')
                        #print (trade_file)
                        print (previous_close_price, close)
                        signal_open_order_with_sell(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                elif ema[0] > ema[1] : # open buy order
                    if trade_file == '' and check_open_order_gate(symbol, 'buy', close):
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'buy')
                        # print (trade_file)
                        print (previous_close_price, close)
                        signal_open_order_with_buy(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                if fresh_trade == True: # ok, fresh trade
                    pass
                elif trade_file == '':  # no open trade
                    pass
                # close is touch upper
                elif (ema[0] > ema[1]) and trade_file.endswith('.sell') == True :
                    # check if return bigger than fee
                    if check_close_sell_fee_threshold(old_open_price, close) == True:
                        signal_close_order_with_buy(l_index, trade_file, close)
                        if old_open_price < close:
                            previous_close_price = -close # negative means ever sold
                        else:
                            previous_close_price = 0
                        print ('return = ', old_open_price - close)
                        total_revenue += old_open_price - close
                        trade_file = ''  # make trade_file empty to indicate close
                # close is touch lower
                elif (ema[0] < ema[1]) and trade_file.endswith('.buy') == True :
                    # check if return bigger than fee
                    if check_close_sell_fee_threshold(old_open_price, close) == True:
                        signal_close_order_with_sell(l_index, trade_file, close)
                        if old_open_price > close:
                            previous_close_price = close # positive means ever bought
                        else:
                            previous_close_price = 0
                        print ('return = ', close - old_open_price)
                        total_revenue += close - old_open_price
                        trade_file = ''  # make trade_file empty to indicate close
                elif close_lower.count() > 10 * latest_to_read:
                    close_lower = close_lower[-latest_to_read:]
                    close_mean = close_mean[-latest_to_read:]
                    close_upper = close_upper[-latest_to_read:]
                    print ('Reduce data size to %d', close_lower.count())
        # used when do emulation
        with open('%s.goon' % trade_notify, 'w') as f:
            f.write('goon')
            f.close()

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
def emul_signal_notify(l_dir):
    global old_close_mean, signal_notify, trade_notify
    global total_revenue
    try:
        files = with_scandir_ewma(l_dir)
        files.sort()
        to_read = len(files)
        if to_read > latest_to_read:
            to_read = latest_to_read
        print ('Total %d files, read latest %d' % (len(files), to_read))
        for fname in files[-to_read:]:
            fpath = os.path.join(l_dir, fname)
            # print (fpath)
            wait_ema_notify(fpath)
        files = None
        print ('Total revenue ', total_revenue)
        #print (close_mean)
    except Exception as ex:
        print (traceback.format_exc())

# ['Path', 'is', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min\n']
# ['Watching', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min\n']
# ['Change', '54052560', 'in', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1535123280000,', 'flags', '70912Change', '54052563', 'in', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1535123280000.lock,', 'flags', '66304', '-', 'matched', 'directory,', 'notifying\n']

# wait on boll_notify for signal
def wait_boll_notify(notify):
    global fee_threshold, fee_file
    while True:
        command = ['fswatch', '-1', notify]
        try:
            # check if should read fee from file
            if os.path.isfile(fee_file) and os.path.getsize(fee_file) > 0:
                with open(fee_file) as f:
                    t_fee_threshold = float(f.readline())
                    f.close()
                    if t_fee_threshold != fee_threshold: # update if diff
                        fee_threshold = t_fee_threshold
                        print ('fee_threshold updated to %f' % fee_threshold)
        except Exception as ex:
            fee_threshold = default_fee_threshold
            print ('fee_threshold reset to %f' % fee_threshold)
        print ('', end='', flush=True)
        try:
            result = subprocess.run(command, stdout=PIPE) # wait file modified
            with open(notify, 'r') as f:
                subpath = f.readline().rstrip('\n')
                f.close()
                #print (subpath)
                plot_living_price_new(subpath)
        except FileNotFoundError as fnfe:
            print (fnfe)
            break
        except Exception as ex:
            print (ex)
            print (traceback.format_exc())
            continue

# wait on ema_notify for signal
def wait_ema_notify(notify):
    global fee_threshold, fee_file
    while True:
        command = ['fswatch', '-1', notify]
        try:
            # check if should read fee from file
            if os.path.isfile(fee_file) and os.path.getsize(fee_file) > 0:
                with open(fee_file) as f:
                    t_fee_threshold = float(f.readline())
                    f.close()
                    if t_fee_threshold != fee_threshold: # update if diff
                        fee_threshold = t_fee_threshold
                        print ('fee_threshold updated to %f' % fee_threshold)
        except Exception as ex:
            fee_threshold = default_fee_threshold
            print ('fee_threshold reset to %f' % fee_threshold)
        print ('', end='', flush=True)
        try:
            if options.emulate:
                try_to_trade(notify)
                break
            
            result = subprocess.run(command, stdout=PIPE) # wait file modified
            with open(notify, 'r') as f:
                subpath = f.readline().rstrip('\n')
                f.close()
                # print (subpath)
                try_to_trade(subpath)
        except FileNotFoundError as fnfe:
            print (fnfe)
            break
        except Exception as ex:
            print (ex)
            print (traceback.format_exc())
            continue

def wait_signal_notify(notify):
    if l_signal == 'boll':
        wait_boll_notify(notify)
    elif l_signal == 'ema':
        wait_ema_notify(notify)
    
from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--signal_notify", dest="signal_notify",
                  help="specify signal notifier")
parser.add_option("", "--no_pick_old_order", dest='pick_old_order',
                  action="store_false", default=True,
                  help="do not pick old order")
parser.add_option('', '--signal', dest='signal', default='boll',
                  help='use wich signal to generate trade notify and also as prefix')
parser.add_option('', '--emulate', dest='emulate',
                  help="try to emulate trade notify")

(options, args) = parser.parse_args()
print (type(options), options, args)

pick_old_order = options.pick_old_order
l_dir = args[0].rstrip('/')

l_signal = options.signal
l_prefix = ''
if l_signal == 'boll': # old scheme
    print ('Begin at %s' % (dt.now()))
    #print (l_dir, os.path.basename(l_dir))
    plot_saved_price(l_dir)
    print ('Stop at %s' % (dt.now()))
    pass
else: # new scheme
    l_prefix = '%s_' % l_signal


if options.signal_notify :
    signal_notify = options.signal_notify
else:
    signal_notify = '%s.%s_notify' % (l_dir, l_signal)
print ('signal_notify: %s' % signal_notify)

trade_notify = '%s.%strade_notify' % (l_dir, l_prefix) # file used to notify trade
print ('trade_notify: %s' % trade_notify)

fee_file = '%s.%sfee' % (l_dir, l_prefix)
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

if options.emulate:
    emul_signal_notify(l_dir)
    os.sys.exit(0)

print ('Waiting for process new coming file\n', flush=True)
wait_signal_notify(signal_notify)

# >>> datetime.date.today().strftime('%s')
# '1534003200'

