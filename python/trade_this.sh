#!/bin/bash

set -ex

target_coin=$1
target_coin_log=$1.log
target_coin_amount=$1.amount

test -d ${target_coin} || (echo "Invalid coin $1" && false)

(python3 boll_notify.py ${target_coin} with-old-files | tee -a ${target_coin_log} )&

(python3 trade_notify.py ${target_coin} | tee -a ${target_coin_log} )&

echo '2' > ${target_coin_amount}

(python3 trade.py ${target_coin} | tee -a ${target_coin_log} )&

