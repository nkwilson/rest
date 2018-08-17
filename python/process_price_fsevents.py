import os
import sys
import pandas
import numpy
import pprint
import traceback
from fsevents import Observer

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

def callback_dir(subpath, mask):
    print (subpath, mask)

l_index = ''
old_l_index = ''
event_path = ''
old_event_path = ''

# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def callback_file(subpath):
    global l_index, old_l_index, event_path, old_event_path
    #print (subpath, str(subpath), type(subpath))
    tup=eval(str(subpath))
    #print (type(tup), tup[0])
    # ignore file event of %.boll
    if tup[2].endswith('.boll') == True:
        return
    old_l_index = l_index
    old_event_path = event_path
    event_type=tup[0]
    event_path=tup[2]
    l_index = os.path.basename(event_path)
    # print (event_type, event_path)
    if (event_type == 2):
        with open(event_path, 'r') as f:
            close=eval(f.readline())[3]
        # print (close)
        try:
            # Parameters:	
            # to_append : Series or list/tuple of Series
            # ignore_index : boolean, default False
            # If True, do not use the index labels.
            # New in version 0.19.0.
            # verify_integrity : boolean, default False
            # If True, raise Exception on creating index with duplicates
            
            # Series.append(to_append, ignore_index=False, verify_integrity=False)[source]
            # Concatenate two or more Series.
            close_prices[l_index]=close
            # print (l_index, close)
            return
        except Exception as ex:
            print (traceback.format_exc())
            # not exist
            # if close_prices.count() > 0:
            #     print (Bolinger_Bands(close_prices, window_size, num_of_std))
                
            # close_prices.append(pandas.Series([close], [l_index]), verify_integrity=True)
            # print (l_index, close)
            return
    elif (event_type != 256):
        print (event_type)
        return
    else: # type 256, new file event
        print (old_l_index, old_event_path, ',')
        print (l_index, event_path, ',', close_prices.count())
        close_mean, close_upper, close_lower = Bolinger_Bands(close_prices, window_size, num_of_std)
        with open('%s.boll' % (old_event_path), 'w') as fb: # write bull result to file with suffix of '.boll'
            fb.write('%0.40f, %0.40f, %0.40f\n' % (close_mean[old_l_index], close_upper[old_l_index], close_lower[old_l_index]))
            
if len(sys.argv) >= 2 and sys.argv[2]=='with-old-files': # process old files in dir
    # with os.scandir(sys.argv[1]) as it:
    #     for entry in it:
    #         if not entry.name.startswith('.') and entry.is_file():
    #             while open(entry.path, 'r') as f:
    #                 close=eval(f.readline())[3]
    #                 close_prices[entry.name]=close
    try :
        read_saved = 0  # read boll data from saved file
        files=os.listdir(sys.argv[1])
        files.sort()
        print ('Total %d old files' % (len(files)))
        for fname in files:
            fpath = os.path.join(sys.argv[1], fname)
            # print (fpath)
            if fpath.endswith('.boll') == False: # not bolinger band data
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
                    fb.write('%0.40f, %0.40f, %0.40f\n' % (close_mean[fname], close_upper[fname], close_lower[fname]))
        print ('Processed total %d(%d saved) old files\n' % (len(files), read_saved))
    except Exception as ex:
        #print ('exception occured: %s' % (ex))
        print (traceback.format_exc())
        exit ()

from fsevents import Stream
stream = Stream(callback_file, sys.argv[1], file_events=True)
print ('Waiting for process new coming file\n')

observer = Observer()
observer.start()

observer.schedule(stream)


