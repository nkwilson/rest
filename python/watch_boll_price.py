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

old_close_mean = 0
window_size = 20
trade_file = ''

# plot and save to file
def do_plot_with_window_size(l_index, filename, close):
    if os.path.isfile(filename) == True: # already ordered
        return
    line = '%s sell at %f\n' % (l_index, close)
    with open(filename, 'w') as f:
        print (line.rstrip('\n'))            
        f.write(line)

# close sell order now
def close_order_with_buy(l_index, filename, close):
    if os.path.isfile(filename) == False: # no order opened
        return
    line = '%s buy at %f, closed\n' % (l_index, close)
    with open(filename, 'a') as f:
        print (line.rstrip('\n'))            
        f.write(line)

def generate_trade_filename(dir, l_index):
        fname = '%s-trade-%s.log' % (os.path.basename(dir), l_index)
        #print (trade_file)
        return os.path.join(os.path.dirname(dir), fname)

# format: mean, upper, lower
def read_boll(filename):
        with open(filename, 'r') as f:
                line = f.readline().rstrip('\n')
                try: 
                        boll = [float(x) for x in line.split(',')]
                        return boll
                except Exception as ex:
                        print (filename)
        pass

#  '6179.63', '6183.09', '6178.98', '6180.34', '3148.0', '50.936313653924'
# format: open, high, low, close, volume, total-value
def read_close(filename):
    filename = os.path.splitext(filename)[0]
    # print (filename)
    if os.path.isfile(filename) == False: # in case not exist
        return 0
    with open(filename, 'r') as f:
        close = eval(f.readline())[3]
    # print (close)
    return float(close)

# inotify specified dir to plot living price
# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def plot_living_price(subpath):
    global window_size, trade_file, old_close_mean
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
        if math.isnan(boll[0]) == False:
                close_mean[l_index]=boll[0]
                close_upper[l_index]=boll[1]
                close_lower[l_index]=boll[2]
                if boll[0] < old_close_mean: # open sell order
                    if trade_file == '':
                        trade_file = generate_trade_filename(os.path.dirname(event_path), l_index)
                        # print (trade_file)
                        do_plot_with_window_size(l_index, trade_file, close)
                old_close_mean = boll[0] # update unconditiionally
                if close > ((boll[0]+boll[1]) / 2) : # close is touch half of upper
                    close_order_with_buy(l_index, trade_file, close)
                    trade_file = ''  # make trade_file empty to indicate close

# process saved prices in specified dir        
def plot_saved_price(l_dir):
    try:
        files = os.listdir(l_dir)
        files.sort()
        print ('Total %d files to plot\n' % (len(files)))
        for fname in files:
            if fname.endswith('.boll') == False:
                continue
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
        l_dir = sys.argv[1].rstrip('/')
        #print (l_dir, os.path.basename(l_dir))
        plot_saved_price(l_dir)
        
        stream = Stream(plot_living_price, l_dir, file_events=True)
        print ('Waiting for process new coming file\n')
        
        observer = Observer()
        observer.start()
        
        observer.schedule(stream)


# >>> datetime.date.today().strftime('%s')
# '1534003200'
        
