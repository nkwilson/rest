set -e

while getopts "c:k:f:s:a:Rh" var; do
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
	'h') # help
	    echo 'Usage: '
	    echo '-c: coin'
	    echo '-k: key, such as 30min'
	    echo '-f: fee rate'
	    echo '-a: amount'
	    echo '-s: cmp_scale'
	    echo '-R: restart all'
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

case ${COIN} in
     btc)
	 SCALE1=${SCALE1:-1}
	 ;;
     bch)
	 SCALE1=${SCALE1:-1}
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
jobs -x python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL1} > /dev/null &
test -f ${SYMBOL1}.boll_notify.ok || fswatch -1 ${SYMBOL1}.boll_notify.ok

rm -f ${SYMBOL1}.boll_trade_notify.ok
jobs -x python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL1} --cmp_scale=${SCALE1} &
test -f ${SYMBOL1}.boll_trade_notify.ok || fswatch -1 ${SYMBOL1}.boll_trade_notify.ok

rm -f ${SYMBOL1}.boll_trade.ok
jobs -x python3 monitor_me.py trade.py --signal=boll ${SYMBOL1} &
test -f ${SYMBOL1}.boll_trade.ok || fswatch -1 ${SYMBOL1}.boll_trade.ok
