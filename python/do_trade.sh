#!/bin/bash

set -ex

target_coin=$1
target_coin_amount=$1.amount

amount=${2:-15}

test -d ${target_coin} || (echo "Invalid coin $1" && false)
expr "$2" + "0" || (echo  "Invalid amount $2" && false)

if ps U $(whoami) | grep -q 'python3 price_notify.py';  then
    true
else
    pushd $(dirname ${target_coin})
    python3 monitor_me.py price_notify.py > /dev/null 2>&1 &
    popd
fi	

echo "${amount}" > ${target_coin_amount}
(python3 monitor_me.py trade.py ${target_coin} &
sleep 5
(python3 monitor_me.py trade_notify.py ${target_coin} &
sleep 5
(python3 monitor_me.py boll_notify.py ${target_coin} &
sleep 5
 
