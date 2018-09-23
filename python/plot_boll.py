#!/usr/bin/python3
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

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
import threading

import json

import matplotlib

import matplotlib.pyplot as pyplot

# v2, fast than listdir
def with_scandir(l_dir):
    files = list()
    with os.scandir(l_dir) as it:
        for entry in it:
            if entry.name.endswith('.boll') == True:
                files.append(entry.name)
    return files

# format: mean, upper, lower
def read_boll(filename):
    boll = 0
    try: 
        with open(filename, 'r') as f:
            line = f.readline().rstrip('\n')
            boll = [float(x) for x in line.split(',')]
    except Exception as ex:
        print ('read_boll: %s\n' % filename)
    return boll

# process saved prices in specified dir        
def plot_boll(l_dir, latest):
    files = with_scandir(l_dir)
    files.sort()
    data = list()
    for fname in files[-int(latest):-1]:
        boll = read_boll(os.path.join(l_dir,fname))
        if boll == 0:
            continue
        #print (boll)
        data.append(boll)
    pdata=pandas.DataFrame(data, columns=['boll', 'upper', 'lower'])
    matplotlib.pyplot.plot(pdata)
    matplotlib.pyplot.show()
    # return data

print ('Usage: l_dir count\n')
print (sys.argv)
print (plot_boll(sys.argv[1], sys.argv[2]))

