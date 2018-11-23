import os
import sys
import pandas
#import numpy
#import pprint
import traceback
#import threading 

#import pipes

import datetime
from datetime import datetime as dt
#import tempfile

import subprocess
from subprocess import PIPE, run

# print (os.environ)
# print (sys.modules.keys())  # too much infor
print (sys.argv)

from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--signal_notify", dest="signal_notify",
                  help="specify signal notifier")
parser.add_option("", "--without_old_files", dest='without_old_files',
                  action="store_true", default=False,
                  help="do not processing stock files")
parser.add_option('', '--signal', dest='signals', default=[],
                  action='append',
                  help='use wich signal to generate trade notify and also as prefix')
parser.add_option('', '--latest', dest='latest_to_read', default='1000',
                  help='only keep that much old values')
parser.add_option('', '--dir', dest='dirs', default=[],
                  action='append',
                  help='target dir should processing')

(options, args) = parser.parse_args()
print (type(options), options, args)

if len(args) != 0 : # unknows options, quit
    print ('Unknown arguments: ', args)
    os.sys.exit(0)

latest_to_read = int(options.latest_to_read)
default_skip_suffixes=['.open', '.close', '.buy', '.sell', '.log']

# only processing on signal a time
l_signal = options.signals[0]
l_prefix = '%s_' % l_signal
l_dir = options.dirs[0]

close_prices = pandas.Series()

# parameters for bollinger band
default_window_size=60
default_num_of_std=2

def Bolinger_Bands(stock_price, window_size, num_of_std):
    rolling_mean = stock_price.rolling(window=window_size).mean()
    rolling_std  = stock_price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

def boll(stock_price, window_size, num_of_std):
    rolling_mean = stock_price.rolling(window=window_size).mean()
    rolling_std  = stock_price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean[-1], upper_band[-1], lower_band[-1]
    
def save_boll_to_file(stock_price, filename, window_size=default_window_size, num_of_std=default_num_of_std):
    l_start = dt.now()
    mean, upper, lower = boll(stock_price, window_size, num_of_std)
    l_delta = dt.now() - l_start
    l_start = dt.now()
    print (l_delta, end=' ', flush=True)
    with open(filename, 'w') as f:
        f.write('%0.3f, %0.3f, %0.3f\n' % (mean, upper, lower))
        f.close()
    l_delta = dt.now() - l_start
    print (l_delta)

# refer to: http://pandas.pydata.org/pandas-docs/stable/computation.html#exponentially-weighted-windows
def ewma(stock_price, w1=3, w2=10, w3=20, w4=60):
    #print (w1, w2, w3, w4)
#    l_w1 = stock_price.rolling(window=w1).mean().get_values()
#    l_w2 = stock_price.rolling(window=w2).mean().get_values()
#    l_w3 = stock_price.rolling(window=w3).mean().get_values()
#    l_w4 = stock_price.rolling(window=w4).mean().get_values()
    l_w1 = stock_price.ewm(span=w1, min_periods=w1).mean().get_values()
    l_w2 = stock_price.ewm(span=w2, min_periods=w2).mean().get_values()
    l_w3 = stock_price.ewm(span=w3, min_periods=w3).mean().get_values()
    l_w4 = stock_price.ewm(span=w4, min_periods=w4).mean().get_values()
    # print (l_w1[-1], l_w2[-1], l_w3[-1], l_w4[-1])
    return l_w1[-1], l_w2[-1], l_w3[-1], l_w4[-1]

def save_ewma_to_file(stock_price, filename, w1=3, w2=10, w3=20, w4=60):
    l_start = datetime.datetime.now()
    w1, w2, w3, w4 = ewma(stock_price, w1, w3, w3, w4)
    l_delta = datetime.datetime.now() - l_start
    l_start = datetime.datetime.now()
    print (l_delta, end=' ', flush=True)
    with open(filename, 'w') as f:
        f.write('%0.3f, %0.3f, %0.3f, %0.3f\n' % (w1, w2, w3, w4))
        f.close()
    l_delta = datetime.datetime.now() - l_start                
    print (l_delta)

def save_and_notify_signal(stock_price, filename, signal, notify_file):
    globals()['save_%s_to_file' % signal](stock_price, filename)
    # make signal
    with open(notify_file, 'w') as f:
        f.write(filename)
        f.close()

# #import the pandas library and aliasing as pd
# import pandas as pd
# import numpy as np
# data = np.array(['a','b','c','d'])
# s = pd.Series(data,index=[100,101,102,103])
# print s

l_index = ''
old_l_index = ''
event_path = ''
old_event_path = ''

# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def callback_file_new(subpath, signal_notify):
    global l_index, old_l_index, event_path, old_event_path
    global close_prices
    event_path=subpath
    l_index = os.path.basename(event_path)
    if old_l_index == '':
        old_l_index = l_index
        old_event_path = event_path
    # For the very first time , old_event_path is empty
    if os.path.isfile(old_event_path) == False:
        return
    # if same, price updated
    if old_l_index == l_index:
        try:
            with open(old_event_path, 'r') as f:
                close=eval(f.readline())[3]
                # print (close)
                print ('.', end='', flush=True)
            # Parameters:	
            # to_append : Series or list/tuple of Series
            # ignore_index : boolean, default False
            # If True, do not use the index labels.
            # New in version 0.19.0.
            # verify_integrity : boolean, default False
            # If True, raise Exception on creating index with duplicates
            
            # Series.append(to_append, ignore_index=False, verify_integrity=False)[source]
            # Concatenate two or more Series.
            close_prices[old_l_index]=close
            # print (old_l_index, close)
        except Exception as ex:
            print (traceback.format_exc())
            # not exist
            # if close_prices.count() > 0:
            #     print (Bolinger_Bands(close_prices, window_size, num_of_std))
                
            # close_prices.append(pandas.Series([close], [l_index]), verify_integrity=True)
            # print (l_index, close)
    # if different, new file event
    # case 1:
    # ok_sub_futureusd_btc_kline_quarter_1min 1535198340000 1535198400000 418
    # ok_sub_futureusd_btc_kline_quarter_1min 1535198400000 1535198340000 418
    elif l_index > old_l_index: # if os.path.isfile(old_event_path) and os.path.getsize(old_event_path) > 0 :
        try:
            print ('')
            filename = '%s.%s' % (old_event_path, l_signal)
            print (os.path.basename(os.path.dirname(old_event_path)), old_l_index, l_index, close_prices.count(), end=' ', flush=True)
            save_and_notify_signal(close_prices, filename, l_signal, signal_notify)
        except Exception as ex:
            print (filename)
            print (traceback.format_exc())
            old_l_index = l_index
            old_event_path = event_path
            return # re do
        old_l_index = l_index
        old_event_path = event_path
        if close_prices.count() > 2 * latest_to_read:
            close_prices = close_prices[-latest_to_read:]
            print ('Reduce data size to %d', close_lower.count())
    else: # Yes, things has happened: old_l_index  > l_index
        old_l_index = ''
        old_event_path = ''
        print ('*', end=' ', flush=True)

# generate file list
def with_listdir(l_dir):
    return os.listdir(l_dir)

# v2, fast than listdir
def with_scandir_withskip(l_dir, skips):
    files = list()
    #print (skips)
    with os.scandir(l_dir) as it:
        for entry in it:
            if skips != '' and entry.name.endswith(skips) == True:
                continue
            files.append(entry.name)
    return files

def with_scandir_suffix(l_dir, suffix):
    files = list()
    #print (skips)
    with os.scandir(l_dir) as it:
        for entry in it:
            if suffix != '' and entry.name.endswith(suffix) == True:
                files.append(entry.name)
    return files
    
def with_scandir(l_dir):
    return with_scandir_withskip(l_dir, skips='')

def with_scandir_suffix(l_dir, suffix):
    files = list()
    #print (skips)
    with os.scandir(l_dir) as it:
        for entry in it:
            if suffix != '' and entry.name.endswith(suffix) == True:
                files.append(entry.name)
    return files

def with_scandir_nosuffix(l_dir):
    files = list()
    with os.scandir(l_dir) as it:
        for entry in it:
            # drop any '.*' suffix            
            if os.path.splitext(entry)[1] == '':
                files.append(entry.name)
        it.close()
    return files
    
def processing_old_files(l_dir, latest_to_read, skip_suffixes, suffix):
    start = dt.now()
    print ('Processing old files, begin at %s' % (start))
    # with os.scandir(sys.argv[1]) as it:
    #     for entry in it:
    #         if not entry.name.startswith('.') and entry.is_file():
    #             while open(entry.path, 'r') as f:
    #                 close=eval(f.readline())[3]
    #                 close_prices[entry.name]=close
    try :
        read_saved = 0  # read boll data from saved file
        files=with_scandir_nosuffix(l_dir)
        files.sort()
        print ('Total %d files, read latest %d' % (len(files), latest_to_read))
        for fname in files[-latest_to_read:]:
            fpath = os.path.join(l_dir, fname)
            if os.path.getsize(fpath) == 0:
                continue
            # print (fpath)
            with open(fpath, 'r') as f:
                close=eval(f.readline())[3]
                close_prices[fname]=close
            # first check .ewma is exist
            fpathboll='%s.%s' % (fpath, suffix)
            # print (fpathboll)
            if os.path.isfile(fpathboll) and os.path.getsize(fpathboll) > 0 :
                with open(fpathboll, 'r') as fb:
                    read_saved+=1
                    l_line = fb.readline().rstrip('\n')
                    # print (l_line, type(l_line))
                    boll = l_line.split(',')
                    # print (boll)
                    boll = [float(x) for x in boll]
                    # print (boll)
            else:
                w1, w2, w3, w4 = ewma(close_prices)
                # print (w1, w2, w3, w4)
                with open(fpathboll, 'w') as fb: # write bull result to file with suffix of '.boll'
                    fb.write('%0.3f, %0.3f, %0.3f, %0.3f\n' % (w1, w2, w3, w4))
                    fb.close()
        print ('Processed total %d(%d saved) old files' % (len(files), read_saved))
    except Exception as ex:
        #print ('exception occured: %s' % (ex))
        print (traceback.format_exc())
        exit ()
    stop = dt.now()
    print ('Stop at %s, cost %s' % (stop, stop - start))

def waiting_for_notify(l_dir, prefix):
    print ('')
    print ('Waiting for process new coming file')

    signal_notify = '%s.%s_notify' % (l_dir, prefix)  # file used to notify boll finish signal

    logfile='%s.log' % signal_notify
    saved_stdout = sys.stdout
    sys.stdout = open(logfile, 'a')
    print (dt.now())
    print ('signal_notify: %s' % signal_notify, flush=True)

    price_notify = '%s.price_notify' % l_dir
    print ('price_notify: %s' % price_notify)

    pid_file = '%s.%s_notify.pid' % (l_dir, prefix)
    # os.setsid() # privilge
    #print (os.getpgrp(), os.getpgid(os.getpid()))
    with open(pid_file, 'w') as f:
        f.write('%d' % os.getpgrp())
        print ('sid is %d, pgrp is %d, saved to file %s' % (os.getsid(os.getpid()), os.getpgrp(), pid_file))

    while True:
        print ('', end='', flush=True)
        subpath = ''
        price_notify = os.path.realpath(price_notify)
        command = ['fswatch', '-1', price_notify]
        try:
            result = subprocess.run(command, stdout=PIPE) # wait file until rewrited
            rawdata = result.stdout.decode().split('\n')
            #print (rawdata)
            for data in rawdata:
                if len(data) > 7 and data == price_notify:
                    #print (data)
                    subpath = data
                    #print (subpath)
                    with open(subpath, 'r') as f:
                        subpath = f.readline().rstrip('\n')
                        #print (subpath)
                    if os.path.isfile(subpath) == True and os.path.getsize(subpath) > 0:
                        #print (subpath)
                        callback_file_new(subpath, signal_notify)
                        break
                    # for old version watch_poll_price.py
                    elif os.path.isfile(os.path.join(l_dir, subpath)) == True and os.path.getsize(os.path.join(l_dir, subpath)) > 0:
                        print (subpath)
                        callback_file_new(os.path.join(l_dir, subpath), signal_notify)
                        break
        except Exception as ex:
            print (ex)
            continue

print ('Skip processing old files\n') if options.without_old_files == True \
    else processing_old_files(l_dir, latest_to_read, tuple(default_skip_suffixes + ['.%s' % l_signal]), l_signal)

waiting_for_notify(l_dir, l_signal)
