#!/usr/bin/python3
# -*- coding: utf-8 -*-
# encoding: utf-8

import os
import sys
import subprocess
from subprocess import PIPE, run

print (sys.argv)
# skip sys.argv[0] 
command = [sys.executable] + sys.argv[1:]
print (command, os.getsid(os.getpid()))

while True:
    result = subprocess.run(command, start_new_session=True)
    if result.returncode == -30: # SIGUSR1 means restart 
        pass
    else:
        print (result)
        break
