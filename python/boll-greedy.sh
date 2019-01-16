set -e

WINDOW=20 # default is 20 
KEY1=30min

while getopts "c:k:f:s:a:w:r:b:RKh" var; do
    case $var in
	'c') # coin
	    COIN=$OPTARG
	    ;;
	'k') # key
	    KEY1=$OPTARG
	    ;;
	'f') # fee_rate1
	    FEE_RATE1=$OPTARG
	    ;;
	's') # cmp_scale
	    SCALE1=$OPTARG
	    ;;
	'r') # ratio
	    RATIO=$OPTARG
	    ;;
	'R') # restart
	    DO_RESTART=1
	    ;;
	'b') # din=close
	    BINS=$OPTARG
	    ;;
	'K') # force restart
	    DO_RESTART=1
	    DO_FORCE_RESTART=1
	    ;;
	'a') # amount
	    AMOUNT=$OPTARG
	    ;;
	'w') # boll window
	    WINDOW=$OPTARG
	    ;;
	'h') # help
	    echo 'Usage: '
	    echo '-c: coin'
	    echo '-k: key, such as 30min'
	    echo '-f: fee rate'
	    echo '-a: amount'
	    echo '-s: cmp_scale'
	    echo '-r: ratio'
	    echo '-b: bins'
	    echo '-R: use stop notify to restart all'
	    echo '-K: force restart all if no order holded'
	    echo unknown argument
	    ;;
    esac
done

SYMBOL1=../../websocket/python/ok_sub_futureusd_${COIN}_kline_quarter_${KEY1}
pushd ${SYMBOL1} || exit
popd

echo "start trade on symbol"
echo "  ${SYMBOL1}"

rm -f ${SYMBOL1}.boll_fee
test -n "${FEE_RATE1}" && echo "${FEE_RATE1}" > ${SYMBOL1}.boll_fee

rm -f ${SYMBOL1}.boll_amount
test -n "${AMOUNT}" && echo "${AMOUNT}" > ${SYMBOL1}.boll_amount

test ${WINDOW} -eq $(expr "${WINDOW}" + "0") || exit 

case ${KEY1} in
    30min)
	RATIO=${RATIO:-50}
	;;
    12hour)
	RATIO=${RATIO:-25}
	;;
    *)
	RATIO=${RATIO:-50}
	echo unknown key ${KEY1}, using ratio ${RATIO}
	;;
esac

BINS=${BINS:-1}

case ${COIN} in
     btc)
	 SCALE1=${SCALE1:-1}
	 ;;
     bch)
	 SCALE1=${SCALE1:-10}
	 ;;
     eth)
	 SCALE1=${SCALE1:-100}
	 ;;
     ltc)
	 SCALE1=${SCALE1:-100}
	 ;;
     eos)
	 SCALE1=${SCALE1:-1000}
	 ;;
     *)
	 echo 'unknow coin, quit'
	 exit 
esac

if test -n "${DO_RESTART}"; then
    echo -n restart requested
    if test -z "${DO_FORCE_RESTART}"; then
	echo ' gracefully'
	# should stop trade
	touch ${SYMBOL1}.boll_trade.stop_notify
	date
	fswatch -1 ${SYMBOL1}.boll_trade.stop_notify
    else
	echo ' forced'
	kill $(cat ${SYMBOL1}.boll_trade.pid)
    fi
    date
    kill $(cat ${SYMBOL1}.boll_notify.pid)
    kill $(cat ${SYMBOL1}.boll_trade_notify.pid)
    # kill $(cat ${SYMBOL1}.boll_trade.pid)
fi

rm -f ${SYMBOL1}.boll_notify.ok go
jobs -x python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL1} --boll_window=${WINDOW} > /dev/null &
while ! test -f ${SYMBOL1}.boll_notify.ok ; do
    sleep 1
done

rm -f ${SYMBOL1}.boll_trade_notify.ok go
jobs -x python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL1} --cmp_scale=${SCALE1} --bins=${BINS} &
while ! test -f ${SYMBOL1}.boll_trade_notify.ok ; do
    sleep 1
done

rm -f ${SYMBOL1}.boll_trade.ok go
jobs -x python3 monitor_me.py trade.py --signal=boll --ratio=${RATIO} ${SYMBOL1} &
while ! test -f ${SYMBOL1}.boll_trade.ok ; do
    sleep 1
done    



