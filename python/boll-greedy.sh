set -e

WINDOW=20 # default is 20 
KEY1=30min

while getopts "c:k:f:s:a:w:Rh" var; do
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
	'R') # restart
	    DO_RESTART=1
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
	    echo '-R: restart all'
	    echo '-w: boll window size'
	    exit
	    ;;
	?)
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
    echo restart requested
    # should stop trade
    touch ${SYMBOL1}.boll_trade.stop_notify
    date
    fswatch -1 ${SYMBOL1}.boll_trade.stop_notify
    date
    kill $(cat ${SYMBOL1}.boll_notify.pid)
    kill $(cat ${SYMBOL1}.boll_trade_notify.pid)
    # kill $(cat ${SYMBOL1}.boll_trade.pid)
fi

rm -f ${SYMBOL1}.boll_notify.ok
jobs -x python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL1} --boll_window=${WINDOW} > /dev/null &
sleep 1
test -f ${SYMBOL1}.boll_notify.ok || fswatch -1 ${SYMBOL1}.boll_notify.ok

rm -f ${SYMBOL1}.boll_trade_notify.ok
jobs -x python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL1} --cmp_scale=${SCALE1} &
sleep 1
test -f ${SYMBOL1}.boll_trade_notify.ok || fswatch -1 ${SYMBOL1}.boll_trade_notify.ok

rm -f ${SYMBOL1}.boll_trade.ok
jobs -x python3 monitor_me.py trade.py --signal=boll ${SYMBOL1} &
sleep 1
test -f ${SYMBOL1}.boll_trade.ok || fswatch -1 ${SYMBOL1}.boll_trade.ok
