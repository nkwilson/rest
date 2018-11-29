set -e

COIN=${1:-btc}
TOTAL=${2:-7} # 1:2:4 ratio
KEY1=${3:-12hour}
KEY2=${4:-1hour}
KEY3=${5:-5min}
SYMBOL1=../../websocket/python/ok_sub_futureusd_${COIN}_kline_quarter_${KEY1}
SYMBOL2=../../websocket/python/ok_sub_futureusd_${COIN}_kline_quarter_${KEY2}
SYMBOL3=../../websocket/python/ok_sub_futureusd_${COIN}_kline_quarter_${KEY3}
RATE1=1
RATE2=2
RATE3=4
DIVID=7
echo "start trade on symbol"
echo "  ${SYMBOL1}"
echo "  ${SYMBOL2}"
echo "  ${SYMBOL3}"

TIMES=1

case ${COIN} in
     btc)
	 echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 echo '0.012' > ${SYMBOL1}.boll_fee
	 
	 echo $(expr "${RATE2}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL2}.boll_amount
	 echo '0.012' > ${SYMBOL2}.boll_fee

	 echo $(expr "${RATE3}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL3}.boll_amount	 
	 echo '0.012' > ${SYMBOL3}.boll_fee
	 ;;
     eth)
	 echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 echo '0.012' > ${SYMBOL1}.boll_fee

	 echo $(expr "${RATE2}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL2}.boll_amount
	 echo '0.012' > ${SYMBOL2}.boll_fee

	 echo $(expr "${RATE3}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL3}.boll_amount
	 echo '0.012' > ${SYMBOL3}.boll_fee
	 ;;
     ltc)
	 echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 echo '0.012' > ${SYMBOL1}.boll_fee

	 echo $(expr "${RATE2}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL2}.boll_amount
	 echo '0.012' > ${SYMBOL2}.boll_fee

	 echo $(expr "${RATE3}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL3}.boll_amount	 
	 echo '0.012' > ${SYMBOL3}.boll_fee
	 ;;
esac
	 
python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL1} &
sleep 2
python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL1} &
sleep 2
python3 monitor_me.py trade.py --signal=boll ${SYMBOL1} &
sleep 2

python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL2} &
sleep 2
python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL2} --startup_notify=${SYMBOL1}.boll_trade.startup --shutdown_notify=${SYMBOL1}.boll_trade.shutdown &
sleep 2
python3 monitor_me.py trade.py --signal=boll ${SYMBOL2} &
sleep 2

python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL3} &
sleep 2
python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL3} --startup_notify=${SYMBOL2}.boll_trade.startup --shutdown_notify=${SYMBOL2}.boll_trade.shutdown &
sleep 2
python3 monitor_me.py trade.py --signal=boll ${SYMBOL3} &
sleep 2
