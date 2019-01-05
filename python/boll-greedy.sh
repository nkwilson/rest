set -e

DO_RESTART=${RESTART:-0}

COIN=${1:-btc}
TOTAL=${2:-50} # 3:3:3:3 ratio
KEY1=${3:-30min}
SYMBOL1=../../websocket/python/ok_sub_futureusd_${COIN}_kline_quarter_${KEY1}
RATE1=1
DIVID=50
FEE_RATE1=0.001
echo "start trade on symbol"
echo "  ${SYMBOL1}"

TIMES=1

case ${COIN} in
     btc|dry)
	 #echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 #echo "${FEE_RATE1}" > ${SYMBOL1}.boll_fee
	 SCALE1=1
	 ;;
     bch)
	 #echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 #echo "${FEE_RATE1}" > ${SYMBOL1}.boll_fee
	 SCALE1=1
	 ;;
     eth)
	 #echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 #echo "${FEE_RATE1}" > ${SYMBOL1}.boll_fee
	 SCALE1=100
	 ;;
     ltc)
	 #echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 #echo "${FEE_RATE1}" > ${SYMBOL1}.boll_fee
	 SCALE1=100
	 ;;
     eos)
	 #echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 #echo "${FEE_RATE1}" > ${SYMBOL1}.boll_fee
	 SCALE1=1000
	 ;;
     *)
	 echo 'unknow coin, quit'
	 exit 
esac

case ${DO_RESTART} in
    0)
	true
	;;
    *)
	# should stop trade
	touch ${SYMBOL1}.boll_trade.stop_notify
	fswatch -1 ${SYMBOL1}.boll_trade.stop_notify
	kill $(cat ${SYMBOL1}.boll_notify.pid)
	kill $(cat ${SYMBOL1}.boll_trade_notify.pid)
	# kill $(cat ${SYMBOL1}.boll_trade.pid)
	;;
esac

# quit if dry
test "${COIN}" = "dry" && exit

jobs -x python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL1} > /dev/null &
fswatch -1 ${SYMBOL1}.boll_notify.ok
jobs -x python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL1} --cmp_scale=${SCALE1} &
fswatch -1 ${SYMBOL1}.boll_trade_notify.ok
jobs -x python3 monitor_me.py trade.py --signal=boll ${SYMBOL1} &
fswatch -1 ${SYMBOL1}.boll_trade.ok
