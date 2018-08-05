import sys
from fsevents import Observer

print (sys.argv)

observer = Observer()
observer.start()

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
    if (event_type == 256):
        print (event_type, event_path)
              

from fsevents import Stream
stream = Stream(callback_file, sys.argv[1], file_events=True)
observer.schedule(stream)


