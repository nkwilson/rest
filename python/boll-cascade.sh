set -e

COIN=${1:-btc}
TOTAL=${2:-10} # 3:3:3:3 ratio
KEY1=${3:-1hour}
KEY2=${4:-30min}
KEY3=${5:-5min}
KEY4=${6:-1min}
SYMBOL1=../../websocket/python/ok_sub_futureusd_${COIN}_kline_quarter_${KEY1}
SYMBOL2=../../websocket/python/ok_sub_futureusd_${COIN}_kline_quarter_${KEY2}
SYMBOL3=../../websocket/python/ok_sub_futureusd_${COIN}_kline_quarter_${KEY3}
SYMBOL4=../../websocket/python/ok_sub_futureusd_${COIN}_kline_quarter_${KEY4}
RATE1=3
RATE2=3
RATE3=3
RATE4=3
DIVID=12
echo "start trade on symbol"
echo "  ${SYMBOL1}"
echo "  ${SYMBOL2}"
echo "  ${SYMBOL3}"
echo "  ${SYMBOL4}"

TIMES=1

case ${COIN} in
     btc)
	 echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 echo '0.001' > ${SYMBOL1}.boll_fee
	 SCALE1=1
	 
	 echo $(expr "${RATE2}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL2}.boll_amount
	 echo '0.001' > ${SYMBOL2}.boll_fee
	 SCALE2=1
	 
	 echo $(expr "${RATE3}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL3}.boll_amount	 
	 echo '0.001' > ${SYMBOL3}.boll_fee
	 SCALE3=1

	 echo $(expr "${RATE4}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL4}.boll_amount	 
	 echo '0.001' > ${SYMBOL4}.boll_fee
	 SCALE4=1
	 ;;
     eth)
	 echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 echo '0.001' > ${SYMBOL1}.boll_fee
	 SCALE1=100
	 
	 echo $(expr "${RATE2}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL2}.boll_amount
	 echo '0.001' > ${SYMBOL2}.boll_fee
	 SCALE2=100
	 
	 echo $(expr "${RATE3}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL3}.boll_amount
	 echo '0.001' > ${SYMBOL3}.boll_fee
	 SCALE3=100
	 
	 echo $(expr "${RATE4}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL4}.boll_amount
	 echo '0.001' > ${SYMBOL4}.boll_fee
	 SCALE4=100
	 ;;
     ltc)
	 echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 echo '0.001' > ${SYMBOL1}.boll_fee
	 SCALE1=100
	 
	 echo $(expr "${RATE2}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL2}.boll_amount
	 echo '0.001' > ${SYMBOL2}.boll_fee
	 SCALE2=100
	 
	 echo $(expr "${RATE3}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL3}.boll_amount	 
	 echo '0.001' > ${SYMBOL3}.boll_fee
	 SCALE3=100

	 echo $(expr "${RATE4}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL4}.boll_amount	 
	 echo '0.001' > ${SYMBOL4}.boll_fee
	 SCALE4=100
	 ;;
     eos)
	 echo $(expr "${RATE1}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL1}.boll_amount
	 echo '0.001' > ${SYMBOL1}.boll_fee
	 SCALE1=1000
	 
	 echo $(expr "${RATE2}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL2}.boll_amount
	 echo '0.001' > ${SYMBOL2}.boll_fee
	 SCALE2=1000
	 
	 echo $(expr "${RATE3}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL3}.boll_amount
	 echo '0.001' > ${SYMBOL3}.boll_fee
	 SCALE3=1000
	 
	 echo $(expr "${RATE4}" '*' "${TOTAL}" '/' "${DIVID}" '*' $"${TIMES}") > ${SYMBOL4}.boll_amount
	 echo '0.001' > ${SYMBOL4}.boll_fee
	 SCALE4=1000
	 ;;
     *)
	 echo 'unknow coin, quit'
	 exit 
esac
	 
python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL1} &
sleep 2
python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL1} --cmp_scale=${SCALE1} &
sleep 2
python3 monitor_me.py trade.py --signal=boll ${SYMBOL1} &
sleep 2

python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL2} &
sleep 2
python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL2} --cmp_scale=${SCALE2} &
sleep 2
python3 monitor_me.py trade.py --signal=boll ${SYMBOL2} &
sleep 2

python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL3} &
sleep 2
python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL3} --cmp_scale=${SCALE3} &
sleep 2
python3 monitor_me.py trade.py --signal=boll ${SYMBOL3} &
sleep 2

python3 monitor_me.py signal_notify.py --signal=boll --dir=${SYMBOL4} &
sleep 2
python3 monitor_me.py trade_notify.py --signal=boll --dir=${SYMBOL4} --cmp_scale=${SCALE4} &
sleep 2
python3 monitor_me.py trade.py --signal=boll ${SYMBOL4} &
sleep 2
