#!/bin/bash

set -ex

target_coin=$1
target_coin_amount=$1.amount

amount=${2:-15}

test -d ${target_coin} || (echo "Invalid coin $1" && false)
expr "$2" + "0" || (echo  "Invalid amount $2" && false)

if ! test -d ${target_coin} then
	pushd $(dirname ${target_coin})
	python3 price_notify.py > /dev/null 2>&1 &
	popd
fi	

echo "${amount}" > ${target_coin_amount}
(python3 trade.py ${target_coin} >> ${target_coin}.trade.log) 2>&1 &
sleep 1
(python3 trade_notify.py ${target_coin} >> ${target_coin}.trade_notify.log ) 2>&1 &
sleep 1
(python3 boll_notify.py ${target_coin} with-old-files >> ${target_coin}.boll_notify.log ) 2>&1 &

