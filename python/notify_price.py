import pipes
import sys
import os
import subprocess
from subprocess import PIPE, run

import datetime
d = datetime.datetime(2010, 7, 4, 12, 15, 58)
print ('{:%Y-%m-%d %H:%M:%S}'.format(d))

command = ['notifywait', sys.argv[1]]
result = subprocess.Popen(command, stdout=PIPE, start_new_session=True)
print (result.communicate())
while True:
    print (result.communicate())
    
t = pipes.Template()
t.prepend('notifyloop %s false' % os.path.join(sys.argv[1], 'wait') , '.-')
f = t.open('notify_price', 'r')
while True:
    data = f.readline().split(' ')
    print (data)
    if data[0] == 'Change':
        print (data[3].rstrip(','))

# ['Change', '51930350', 'in', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1535035140000,', 'flags', '69888', '-', 'matched', 'directory,', 'notifying\n']
# ['Running', 'false\n']
# ['Path', 'is', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min\n']
# ['Watching', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min\n']
# ['Change', '51930368', 'in', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1535035080000.boll,', 'flags', '69888', '-', 'matched', 'directory,', 'notifying\n']
# ['Running', 'false\n']
# ['Path', 'is', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min\n']
# ['Watching', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min\n']
# ['Change', '51930428', 'in', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1535035140000,', 'flags', '70912', '-', 'matched', 'directory,', 'notifying\n']
# ['Running', 'false\n']
# ['Path', 'is', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min\n']
# ['Watching', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min\n']
# ['Change', '51930488', 'in', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1535035140000,', 'flags', '70912', '-', 'matched', 'directory,', 'notifying\n']
# ['Change', '51935648', 'in', '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1535035260000,', 'flags', '70656', '-', 'matched', 'directory,', 'notifying\n']

# from filelock import FileLock
# with FileLock("myfile.txt"):
#   # work with the file as it is now locked
#   print("Lock acquired.")
