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
                  help='use wich signal to generate trade notify and also as prefix, [boll, ewma, boll_cutting, simple, tit2tat]')
parser.add_option('', '--latest', dest='latest_to_read', default='1000',
                  help='only keep that much old values')
parser.add_option('', '--dir', dest='dirs', default=[],
                  action='append',
                  help='target dir should processing')
parser.add_option('', '--boll_window', dest='boll_window_size', default='120',
                  help='config boll window size')
parser.add_option('', '--boll_std', dest='boll_std', default='2',
                  help='config boll std')
parser.add_option('', '--outdir', dest='outdir', default='',
                  help='save result to outdir')
parser.add_option('', '--cutting_window', dest='cutting_window', 
                  help='always cut window to that much, only use with boll_cutting')


(options, args) = parser.parse_args()
print (type(options), options, args)

if len(args) != 0 : # unknows options, quit
    print ('Unknown arguments: ', args)
    os.sys.exit(0)

latest_to_read = int(options.latest_to_read)
default_skip_suffixes=['.open', '.close', '.buy', '.sell', '.log']
v_outdir=options.outdir

# only processing on signal a time
v_signal = options.signals[0]
l_prefix = '%s_' % v_signal
v_dir = options.dirs[0]

close_prices = pandas.Series()

# parameters for bollinger band
default_window_size=int(options.boll_window_size)
default_num_of_std=int(options.boll_std)

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
    print (l_delta, end=' ')
    with open(filename, 'w') as f:
        f.write('%9.3f, %9.3f, %9.3f\n' % (mean, upper, lower))
        f.close()
    l_delta = dt.now() - l_start
    print (l_delta, flush=True)

# cut if necessary
def boll_cutting(stock_price, window_size, num_of_std):
    rolling_mean = stock_price.rolling(window=window_size).mean()
    rolling_std  = stock_price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean[-1], upper_band[-1], lower_band[-1]
    
def save_boll_cutting_to_file(stock_price, filename, window_size=default_window_size, num_of_std=default_num_of_std):
    l_start = dt.now()
    mean, upper, lower = boll(stock_price, window_size, num_of_std)
    l_delta = dt.now() - l_start
    l_start = dt.now()
    print (l_delta, end=' ')
    with open(filename, 'w') as f:
        f.write('%9.3f, %9.3f, %9.3f\n' % (mean, upper, lower))
        f.close()
    l_delta = dt.now() - l_start
    print (l_delta, flush=True)

# do post process 
def boll_cutting_post(stock_price, window_size, num_of_std):
    pass

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
    print (l_delta, end=' ')
    with open(filename, 'w') as f:
        f.write('%9.3f, %9.3f, %9.3f, %9.3f\n' % (w1, w2, w3, w4))
        f.close()
    l_delta = datetime.datetime.now() - l_start                
    print (l_delta, flush=True)

#just save close to filename    
def save_simple_to_file(stock_price, filename):
    with open(filename, 'w') as f:
        f.write('%9.3f\n' % float(stock_price[-1]))
        f.close()

old_event_path = ''
def save_tit2tat_to_file(stock_price, filename):
    global old_event_path
    with open(old_event_path, 'r') as f:
        with open(filename, 'w') as wf:
            wf.write('%s' % f.readline())
            wf.close()
        f.close()

def save_and_notify_signal(stock_price, filename, signal, notify_file=''):
    globals()['save_%s_to_file' % signal](stock_price, filename)
    if notify_file == '':
        return
    # make signal
    with open(notify_file, 'w') as f:
        f.write(filename)
        f.close()

def generate_signal_filename(event_path, v_signal, outdir=''):
    #print (event_path, v_signal, outdir)
    dirfix = '' if outdir == '' else '-'+outdir
    f_outdir=os.path.dirname(event_path)+dirfix
    filename = '%s.%s' % (os.path.join(f_outdir, os.path.basename(event_path)), v_signal)
    if os.path.isdir(f_outdir) == False:
        os.mkdir(f_outdir)
    #print (filename)
    print (os.path.basename(os.path.dirname(old_event_path)), old_l_index, l_index, close_prices.count(), '/%s:%s' % (outdir, v_signal), end=' ', flush=True)
    return filename
            
# #import the pandas library and aliasing as pd
# import pandas as pd
# import numpy as np
# data = np.array(['a','b','c','d'])
# s = pd.Series(data,index=[100,101,102,103])
# print s

l_index = ''
old_l_index = ''
event_path = ''

# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def callback_file_new(subpath, signal_notify, v_signal, v_outdir=''):
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
            filename = generate_signal_filename(old_event_path, v_signal, v_outdir)
            save_and_notify_signal(close_prices, filename, v_signal, signal_notify)
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
def with_listdir(v_dir):
    return os.listdir(v_dir)

# v2, fast than listdir
def with_scandir_withskip(v_dir, skips):
    files = list()
    #print (skips)
    with os.scandir(v_dir) as it:
        for entry in it:
            if skips != '' and entry.name.endswith(skips) == True:
                continue
            files.append(entry.name)
    return files

def with_scandir_suffix(v_dir, suffix):
    files = list()
    #print (skips)
    with os.scandir(v_dir) as it:
        for entry in it:
            if suffix != '' and entry.name.endswith(suffix) == True:
                files.append(entry.name)
    return files
    
def with_scandir(v_dir):
    return with_scandir_withskip(v_dir, skips='')

def with_scandir_suffix(v_dir, suffix):
    files = list()
    #print (skips)
    with os.scandir(v_dir) as it:
        for entry in it:
            if suffix != '' and entry.name.endswith(suffix) == True:
                files.append(entry.name)
    return files

def with_scandir_nosuffix(v_dir):
    files = list()
    with os.scandir(v_dir) as it:
        for entry in it:
            # drop any '.*' suffix            
            if os.path.splitext(entry)[1] == '':
                files.append(entry.name)
        it.close()
    return files
    
def processing_old_files(v_dir, latest_to_read, signal, outdir):
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
        files=with_scandir_nosuffix(v_dir)
        files.sort()
        print ('Total %d files, read latest %d' % (len(files), latest_to_read))
        for fname in files[-latest_to_read:]:
            fpath = os.path.join(v_dir, fname)
            if os.path.getsize(fpath) == 0:
                continue
            # print (fpath)
            with open(fpath, 'r') as f:
                close=eval(f.readline())[3]
                # print (close)
                close_prices[fname]=close
            fpathboll = generate_signal_filename(fpath, signal, outdir)
            save_and_notify_signal(close_prices, fpathboll, signal, fpath)
        print ('Processed total %d(%d saved) old files' % (len(files), read_saved))
    except Exception as ex:
        #print ('exception occured: %s' % (ex))
        print (traceback.format_exc())
        exit ()
    stop = dt.now()
    print ('Stop at %s, cost %s' % (stop, stop - start))

def waiting_for_notify(v_dir, v_signal, v_outdir):
    signal_notify = '%s.%s_notify' % (v_dir, v_signal)  # file used to notify boll finish signal

    logfile='%s.log' % signal_notify
    saved_stdout = sys.stdout
    sys.stdout = open(logfile, 'a')
    print (dt.now())
    print ('signal_notify: %s' % signal_notify, flush=True)

    price_notify = '%s.price_notify' % v_dir
    print ('price_notify: %s' % price_notify)

    pid_file = '%s.%s_notify.pid' % (v_dir, v_signal)
    # os.setsid() # privilge
    #print (os.getpgrp(), os.getpgid(os.getpid()))
    with open(pid_file, 'w') as f:
        f.write('%d' % os.getpgrp())
        print ('sid is %d, pgrp is %d, saved to file %s' % (os.getsid(os.getpid()), os.getpgrp(), pid_file))

    if v_signal == 'boll':
        print ('(window_size, std) is (%d, %d)' % (default_window_size, default_num_of_std))
    elif v_signal == 'simple':
        options.without_old_files = True

    print ('Skip processing old files') if options.without_old_files == True \
        else processing_old_files(v_dir, latest_to_read, v_signal, v_outdir)

    print ('')
    print ('Waiting for process new coming file')
    # issue kickup signal
    with open('%s.ok' % signal_notify, 'w') as f:
        f.close()
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
                        callback_file_new(subpath, signal_notify, v_signal, v_outdir)
                        break
                    # for old version watch_poll_price.py
                    elif os.path.isfile(os.path.join(v_dir, subpath)) == True and os.path.getsize(os.path.join(v_dir, subpath)) > 0:
                        print (subpath)
                        callback_file_new(os.path.join(v_dir, subpath), signal_notify, v_signal, v_outdir)
                        break
        except Exception as ex:
            print (ex)
            continue

waiting_for_notify(v_dir, v_signal, v_outdir)
