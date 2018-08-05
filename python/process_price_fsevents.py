import sys
#import pandas
#import numpy
from fsevents import Observer

print (sys.argv)

observer = Observer()
observer.start()

# close_prices = pandas.Series()

# parameters for bollinger band
window_size=20 
num_std=2

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
    if (event_type != 256):
        return
    # if (event_type == 2):
        # with open(event_path, 'r') as f:
        #     close=eval(f.readline())[3]
        # print (close, close_prices)
        # try:
        #     # Parameters:	
        #     # to_append : Series or list/tuple of Series
        #     # ignore_index : boolean, default False
        #     # If True, do not use the index labels.
        #     # New in version 0.19.0.
        #     # verify_integrity : boolean, default False
        #     # If True, raise Exception on creating index with duplicates
            
        #     # Series.append(to_append, ignore_index=False, verify_integrity=False)[source]
        #     # Concatenate two or more Series.
        #     close_prices[os.path.basename(event_path)]=close
        #     return
        # except Exception as ex:
        #     # not exist
        #     close_prices.append(pandas.Series([close], [os.path.basename(event_path)]), verify_integrity=True)
        #     return
    # elif (event_type != 256):
    #     return
    print (event_type, event_path)
    # close_prices.append(pandas.Series([close], [os.path.basename(event_path)]), verify_integrity=True)    

from fsevents import Stream
stream = Stream(callback_file, sys.argv[1], file_events=True)
observer.schedule(stream)


