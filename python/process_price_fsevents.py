import os
import sys
import pandas
import numpy
import pprint
from fsevents import Observer

# print (os.environ)
# print (sys.modules.keys())  # too much infor
print (sys.argv)

observer = Observer()
observer.start()

close_prices = pandas.Series()

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

# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def callback_file(subpath):
    #print (subpath, str(subpath), type(subpath))
    tup=eval(str(subpath))
    #print (type(tup), tup[0])
    event_type=tup[0]
    event_path=tup[2]
    if (event_type == 2):
        with open(event_path, 'r') as f:
            close=eval(f.readline())[3]
        # print (close)
        # print (close_prices)
        l_index = os.path.basename(event_path)
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
            print (ex)
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
        print (type(close_prices), close_prices.count())
        if close_prices.count() >= window_size :
            pprint.pprint (Bolinger_Bands(close_prices, window_size, num_of_std))
        pass
    
    # print (event_type, event_path)

if len(sys.argv) >= 2 and sys.argv[2]=='with-old-files': # process old files in dir
    # with os.scandir(sys.argv[1]) as it:
    #     for entry in it:
    #         if not entry.name.startswith('.') and entry.is_file():
    #             while open(entry.path, 'r') as f:
    #                 close=eval(f.readline())[3]
    #                 close_prices[entry.name]=close
    files=os.listdir(sys.argv[1])
    files.sort()
    print ('Total %d old files' % (len(files)))
    for fname in files:
        with open(os.path.join(sys.argv[1], fname), 'r') as f:
            close=eval(f.readline())[3]
            close_prices[fname]=close

from fsevents import Stream
stream = Stream(callback_file, sys.argv[1], file_events=True)
observer.schedule(stream)


