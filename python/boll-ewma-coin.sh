set -e

COIN=${1:-btc}
KEY=${2:-5min}
SYMBOL=../../websocket/python/ok_sub_futureusd_${COIN}_kline_quarter_${KEY}
echo "start trade on symbol ${SYMBOL}"

TIMES=1

case ${COIN} in
     btc)
	 echo $(expr '1' '*' "${TIMES}") > ${SYMBOL}.boll_amount
	 echo '0.012' > ${SYMBOL}.boll_fee
	 
	 echo $(expr '1' '*' "${TIMES}") > ${SYMBOL}.ewma_amount
	 echo '0.012' > ${SYMBOL}.ewma_fee
	 ;;
     eth)
	 echo $(expr '10' '*' "${TIMES}") > ${SYMBOL}.boll_amount
	 echo '0.012' > ${SYMBOL}.boll_fee

	 echo $(expr '10' '*' "${TIMES}") > ${SYMBOL}.ewma_amount
	 echo '0.012' > ${SYMBOL}.ewma_fee
	 ;;
     ltc)
	 echo $(expr '40' '*' "${TIMES}") > ${SYMBOL}.boll_amount
	 echo '0.012' > ${SYMBOL}.boll_fee

	 echo $(expr '40' '*' "${TIMES}") > ${SYMBOL}.ewma_amount
	 echo '0.012' > ${SYMBOL}.ewma_fee
	 ;;
esac
	 
python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL} &
python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL} &
python3 monitor_me.py trade.py --signal=boll ${SYMBOL} &

python3 monitor_me.py signal_notify.py --signal=ewma --dir=${SYMBOL} &
python3 monitor_me.py trade_notify.py --signal=ewma --dir=${SYMBOL} --startup_notify=${SYMBOL}.boll_trade.startup --shutdown_notify=${SYMBOL}.boll_trade.shutdown &
python3 monitor_me.py trade.py --signal=ewma ${SYMBOL} &
