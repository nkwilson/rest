#!/usr/bin/python3
# -*- coding: utf-8 -*-
# encoding: utf-8

import os
import sys
import subprocess
from subprocess import PIPE, run
import signal

print (sys.argv)
# skip sys.argv[0] 
command = [sys.executable] + sys.argv[1:]
sid = os.getsid(os.getpid())
print (command, sid)
sys.stdout = open('%s.log' % sid, 'a')

while True:
    sys.stdout.flush()
    result = subprocess.run(command, start_new_session=True)
    if result.returncode == -signal.SIGUSR1: # SIGUSR1 means restart
        pass
    else:
        print (result)
        break
sys.stdout.flush()
