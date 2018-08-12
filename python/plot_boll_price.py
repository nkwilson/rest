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

import matplotlib

import matplotlib.pyplot as pyplot

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

window_size = 20
png_file = ''

# plot and save to file
def do_plot_with_window_size(window_size, filename):
        if close_mean.count() < window_size:
                window_size = close_mean.count()

        # plot in line for boll bands
        matplotlib.pyplot.plot(range(window_size), close_mean[- window_size:])
        matplotlib.pyplot.plot(range(window_size), close_upper[ - window_size:])
        matplotlib.pyplot.plot(range(window_size), close_lower[- window_size :])
        matplotlib.pyplot.draw()
        
        matplotlib.pyplot.savefig(filename)
        print (matplotlib.pyplot.gcf())
        print (matplotlib.pyplot.figure('fig').canvas.is_saving())
        print (close_mean.count())

def generate_png_filename(dir):
        png_file = '%s.png' % os.path.basename(dir)
        #print (png_file)
        return png_file

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


# inotify specified dir to plot living price
# if new file, subpath = (256, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
# if old file modified, subpath = (2, None, '/Users/zhangyuehui/workspace/okcoin/websocket/python/ok_sub_futureusd_btc_kline_quarter_1min/1533455340000')
def plot_living_price(subpath):
    global window_size, png_file
    #print (subpath, str(subpath), type(subpath))
    tup=eval(str(subpath))
    #print (type(tup), tup[0])
    # only process file event of %.boll
    if tup[2].endswith('.boll') == False:
        return
    event_type=tup[0]
    event_path=tup[2]
    l_index = os.path.basename(event_path)
    print (event_type, event_path)
    if (event_type == 2):
        pass
    elif (event_type != 256):
        pass
    else: # type 256, new file event
        boll = read_boll(event_path)
        print (boll)
        if math.isnan(boll[0]) == False:
                close_mean[l_index]=boll[0]
                close_upper[l_index]=boll[1]
                close_lower[l_index]=boll[2]
        do_plot_with_window_size(window_size, png_file)
        pass

# process saved prices in specified dir        
def plot_saved_price(dest_dir):
    try:
        l_dir=dest_dir.rstrip('/')
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
            except Exception as ex:
                    print (fpath)
                    
        #print (close_mean)
        # only plot when finished processing
        png_file = generate_png_filename(l_dir)
        do_plot_with_window_size(window_size, png_file)
    except Exception as ex:
        print (traceback.format_exc())

if __name__ == "__main__":
        #matplotlib.pyplot.ioff()
        matplotlib.pyplot.figure('fig')
        
        l_dir = sys.argv[1]
        plot_saved_price(l_dir)
        
        stream = Stream(plot_living_price, l_dir, file_events=True)
        print ('Waiting for process new coming file\n')
        
        observer = Observer()
        observer.start()
        
        observer.schedule(stream)
