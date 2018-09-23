import os
import sys
import pandas
import numpy
import pprint
import traceback
import threading 

import pipes

import datetime
from datetime import datetime as dt
import tempfile

import subprocess
from subprocess import PIPE, run

# print (os.environ)
# print (sys.modules.keys())  # too much infor
print (sys.argv)

close_prices = pandas.Series()
close_mean = pandas.Series()
close_upper = pandas.Series()
close_lower = pandas.Series()

# parameters for bollinger band
window_size=20 
num_of_std=2

def Bolinger_Bands(stock_price, window_size, num_of_std):
    rolling_mean = stock_price.rolling(window=window_size).mean()
    rolling_std  = stock_price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

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
def callback_file_new(subpath):
    global l_index, old_l_index, event_path, old_event_path
    global close_mean, close_upper, close_lower
    global close_prices
    if subpath.endswith(('.boll', '.open', '.close')) == True:
        return
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
            filename = '%s.boll' % (old_event_path)
            print (os.path.basename(os.path.dirname(old_event_path)), old_l_index, l_index, close_prices.count(), end=' ', flush=True)
            l_start = datetime.datetime.now()
            close_mean, close_upper, close_lower = Bolinger_Bands(close_prices, window_size, num_of_std)
            l_delta = datetime.datetime.now() - l_start
            l_start = datetime.datetime.now()
            print (l_delta, end=' ', flush=True)
            with open(filename, 'w') as f:
                f.write('%0.7f, %0.7f, %0.7f\n' % (close_mean[old_l_index], close_upper[old_l_index], close_lower[old_l_index]))
            l_delta = datetime.datetime.now() - l_start                
            print (l_delta)
            # make signal
            global boll_notify
            with open(boll_notify, 'w') as f:
                f.write(filename)
        except Exception as ex:
            print (filename)
            print (traceback.format_exc())
            old_l_index = l_index
            old_event_path = event_path
            return # re do
        # write .boll successed, update info
        old_l_index = l_index
        old_event_path = event_path
        if close_prices.count() > 10 * latest_to_read:
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
def with_scandir(l_dir):
    files = list()
    with os.scandir(l_dir) as it:
        for entry in it:
            files.append(entry.name)
    return files

latest_to_read = 1000

# switch default to with-old-files, disabled with explicit without-old-files
if len(sys.argv) > 2 and sys.argv[2] == 'without-old-files': # disabled it now
    print ('Skip processing old files\n')
    pass
else: # if len(sys.argv) >= 2 and sys.argv[2]=='with-old-files': # process old files in dir
    print ('Processing old files, begin at %s' % (dt.now()))
    # with os.scandir(sys.argv[1]) as it:
    #     for entry in it:
    #         if not entry.name.startswith('.') and entry.is_file():
    #             while open(entry.path, 'r') as f:
    #                 close=eval(f.readline())[3]
    #                 close_prices[entry.name]=close
    try :
        l_dir = sys.argv[1].rstrip('/')
        read_saved = 0  # read boll data from saved file
        files=with_scandir(l_dir)
        files.sort()
        print ('Total %d files, read latest %d' % (len(files), latest_to_read))
        for fname in files[-latest_to_read:]:
            fpath = os.path.join(l_dir, fname)
            # print (fpath)
            if fpath.endswith(('.boll', '.open', '.close', '.buy', '.sell', '.log')) == False: # not bolinger band data
                with open(fpath, 'r') as f:
                    close=eval(f.readline())[3]
                    close_prices[fname]=close
            else:
                continue # 
            # first check .boll is exist
            fpathboll='%s.boll' % (fpath)
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
                    close_mean[fname]=boll[0]
                    close_upper[fname]=boll[1]
                    close_lower[fname]=boll[2]
            else:
                close_mean, close_upper, close_lower = Bolinger_Bands(close_prices, window_size, num_of_std)
                # print (close_mean[fname])
                with open('%s.boll' % (fpath), 'w') as fb: # write bull result to file with suffix of '.boll'
                    fb.write('%0.7f, %0.7f, %0.7f\n' % (close_mean[fname], close_upper[fname], close_lower[fname]))
        print ('Processed total %d(%d saved) old files\n' % (len(files), read_saved))
    except Exception as ex:
        #print ('exception occured: %s' % (ex))
        print (traceback.format_exc())
        exit ()
    print ('Stop at %s' % (dt.now()))

print ('Waiting for process new coming file\n')

price_notify = '%s.price_notify' % l_dir
print ('price_notify: %s' % price_notify)

boll_notify = '%s.boll_notify' % l_dir  # file used to notify boll finish signal
print ('boll_notify: %s' % boll_notify, flush=True)

pid_file = '%s.boll_notify.pid' % l_dir
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
                if os.path.isfile(subpath) == True:
                    #print (subpath)
                    callback_file_new(subpath)
                    break
                # for old version watch_poll_price.py
                elif os.path.isfile(os.path.join(l_dir, subpath)) == True:
                    print (subpath)
                    callback_file_new(os.path.join(l_dir, subpath))
                    break
    except Exception as ex:
        print (ex)
        continue

