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

from fsevents import Observer
from fsevents import Stream


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
fee_threshold = 0.0001 / 0.0009 # baesed on one order's fee 
levage_rate = 10

# if fee is bigger than lost, then delay it to next signal
def check_close_sell_fee_threshold(open_price, current_price):
    return abs((current_price - open_price) / open_price) > (fee_threshold / levage_rate)

# plot and save to file
def do_plot_with_window_size(l_index, filename, close):
    if os.path.isfile(filename) == True: # already ordered
        return
    line = '%s sell at %f\n' % (l_index, close)
    with open(filename, 'w') as f:
        print (line.rstrip('\n'))            
        f.write(line)

# open sell order now
def signal_open_order_with_sell(l_index, filename, close):
    if os.path.isfile(filename) == True: # already ordered
        return
    line = '%s sell at %0.4f\n' % (l_index, close)
    with open(filename, 'w') as f:
        print (line.rstrip('\n'))            
        f.write(line)

# close sell order now
def signal_close_order_with_buy(l_index, filename, close):
    if os.path.isfile(filename) == False: # no order opened
        return
    line = '%s buy at %0.4f closed\n' % (l_index, close)
    with open(filename, 'a') as f:
        print (line.rstrip('\n'))            
        f.write(line)

# open buy order now
def signal_open_order_with_buy(l_index, filename, close):
    if os.path.isfile(filename) == True: # already ordered
        return
    line = '%s buy at %0.4f\n' % (l_index, close)
    with open(filename, 'w') as f:
        print (line.rstrip('\n'))            
        f.write(line)

# close buy order now
def signal_close_order_with_sell(l_index, filename, close):
    if os.path.isfile(filename) == False: # no order opened
        return
    line = '%s sell at %0.4f closed\n' % (l_index, close)
    with open(filename, 'a') as f:
        print (line.rstrip('\n'))            
        f.write(line)

def generate_trade_filename(dir, l_index, order_type):
        fname = '%s-trade-%s.%s' % (os.path.basename(dir), l_index, order_type)
        #print (trade_file)
        return os.path.join(os.path.dirname(dir), fname)

# format: mean, upper, lower
def read_boll(filename):
    boll = 0
    with open(filename, 'r') as f:
        try: 
            line = f.readline().rstrip('\n')
            boll = [float(x) for x in line.split(',')]
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
    with open(filename, 'r') as f:
        try: 
            line = eval(f.readline().rstrip('\n'))  # can't just copy from boll 
            close = float(line[3])
            # close = eval(f.readline())[3]
        except Exception as ex:
            print ('read_close: %s' % filename)
    # print (close)
    return close

# inotify specified dir to plot living price
# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def plot_living_price(subpath):
    global window_size, trade_file, old_close_mean
    global old_open_price
    #print (subpath, str(subpath), type(subpath))
    tup=eval(str(subpath))
    #print (type(tup), tup[0])
    # only process file event of %.boll
    if tup[2].endswith('.boll') == False:
        return
    event_type=tup[0]
    event_path=tup[2]
    l_index = os.path.basename(event_path)
    # print (event_type, event_path)
    if (event_type == 2):
        pass
    elif (event_type != 256):
        print (event_type)
        pass
    else: # type 256, new file event
        boll = read_boll(event_path)
        close = read_close(event_path)
        print (boll)
        if boll == 0 or close == 0: # in case read failed
            return
        if math.isnan(boll[0]) == False:
                close_mean[l_index]=boll[0]
                close_upper[l_index]=boll[1]
                close_lower[l_index]=boll[2]
                fresh_trade = False
                if boll[0] < old_close_mean: # open sell order
                    if trade_file == '':
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index, 'sell')
                        # print (trade_file)
                        signal_open_order_with_sell(l_index, trade_file, close)
                        fresh_trade = True
                        old_open_price = close
                elif boll[0] > old_close_mean: # open buy order
                    if trade_file == '':
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
                elif close > ((boll[0]+boll[1]) / 2) and trade_file.endswith('.sell') == True : # close is touch half of upper
                    # check if return bigger than fee
                    if check_close_sell_fee_threshold(old_open_price, close) == True:
                        signal_close_order_with_buy(l_index, trade_file, close)
                        trade_file = ''  # make trade_file empty to indicate close
                elif close < ((boll[0]+boll[2]) / 2) and trade_file.endswith('.buy') == True : # close is touch half of lower
                    # check if return bigger than fee
                    if check_close_sell_fee_threshold(old_open_price, close) == True:
                        signal_close_order_with_sell(l_index, trade_file, close)
                        trade_file = ''  # make trade_file empty to indicate close

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

latest_to_read = 300

# process saved prices in specified dir        
def plot_saved_price(l_dir):
    global old_close_mean
    try:
        files = with_scandir(l_dir)
        files.sort()
        print ('Total %d files, read latest %d' % (len(files), latest_to_read))
        for fname in files[-latest_to_read:]:
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
                    
        #print (close_mean)
    except Exception as ex:
        print (traceback.format_exc())

if __name__ == "__main__":
        print ('Begin at %s' % (dt.now()))
        l_dir = sys.argv[1].rstrip('/')
        #print (l_dir, os.path.basename(l_dir))
        plot_saved_price(l_dir)
        print ('Stop at %s' % (dt.now()))

        stream = Stream(plot_living_price, l_dir, file_events=True)
        print ('Waiting for process new coming file\n')
        
        observer = Observer()
        observer.start()
        
        observer.schedule(stream)


# >>> datetime.date.today().strftime('%s')
# '1534003200'
        
