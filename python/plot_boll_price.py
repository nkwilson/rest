# -*- coding: utf-8 -*-

import sys
import getopt
import traceback

import pandas
import numpy
import pp
import datetime
import tushare

import os
import os.path as path
import time
import random
import math

import matplotlib

import matplotlib.pyplot as pyplot

def new_weekly_policy (stock, data, total_money=100000, deal_count=8, first_buy='', max_tt_share=0.4, do_tt=1):
        # global next_buy, selling_good_deals, next_half_buy, next_steady_buy
        # global global_tendency, lodgers, total_op_count, total_cost
        # global deal_cost, total_money, do_half_buy, do_steady_buy
        # global show_detail, show_signal, show_summary, show_verbose

        lodgers=None

        if deal_count == 0: # fast return
                return

        only_lastest_weeks = 5000 # lastest 50 weeks
        selling_good_deals=-1
        with_profit=0.068  # golden rate
        force_selling_good_deals=-1 # if total_cost is reach, then sell profit more than 10%
        do_sold_slowly = 1
        selling_slowly = -1
        forced_with_profit=0.68
        next_buy=-1
        next_half_buy=-1  # buy half cost when globa_tendency=1 and close_s=1
        next_steady_buy=-1 # buy one cost
        global_tendency=0
        # deal_cost=37000 # calculated from input total_money
        # deal_count=8  # at most this many deals # input argument with default value

        tt_cash = total_money * max_tt_share
        cash = total_money - tt_cash
        
        deal_cost = cash / deal_count
        # total_money=deal_count * deal_cost # all of my money
        total_cost=0 # total cost of holding until now, must be less than total_money

        total_tt_money = tt_cash

        tt_deal_cost = tt_cash / deal_count
        total_tt_cost = 0
        next_tt_buy=-1
        current_tt_profit=0
        sold_tt_value=0
        virt_tt_profit=0
        current_profit=0
        do_half_buy=0
        do_steady_buy=1
        show_detail=0
        show_signal=1
        show_summary=0
        total_op_count=0
        show_verbose=0
        profit_invested=1  # using profit to buy more stocks
        profit_multi=3 # must left that much as cash
        virt_profit=0 # all profit since time 0
        virt_total=0 # current holding shares value plut virtal profit
        sold_value=0 # saved all sold shares until now

        count = data['signal'].count()
        # if no volume, return now
        if count < 1 or data['Volume'][count-1] == 0:
                return

        # if non-empty, buy at no early that it else use the start date
        first_buy_at = data.index[0] if len(first_buy) == 0 else first_buy #pandas.datetime.strptime(first_buy, '%Y-%m-%d')

        # record sold count recently
        sold_count=0
        sold_tt_count=0
        for i in range(count):
            if show_verbose > 0 :
                print '### round %d' % i
                print data.iloc[i][['Open', 'Volume']]
            if data['Volume'][i] == 0:
                continue
            if not isinstance(lodgers, type(None)) and do_tt : # means have tt pending
                to_sold_deals=lodgers.select(lambda x: True if lodgers.loc[x]['tt-profit'] == 0 and lodgers.loc[x]['tt-price'] < data['Open'][i] else False)
                if not isinstance(to_sold_deals, type(None)):
                        if show_verbose > 0:
                                if to_sold_deals['tt-price'].count() == 0:
                                        print "Nothing to tt"
                                else:
                                        print to_sold_deals[['price','tt-count','cost']]
                        for j in range(to_sold_deals['tt-price'].count()):
                                l_count=to_sold_deals['tt-count'][j]
                                sold_tt_count+=l_count
                                l_index=to_sold_deals.index[j]
                                sold_tt_value += data['Open'][i] * l_count
                                l_profit = (data['Open'][i]-to_sold_deals['price'][j])*l_count
                                lodgers.loc[l_index]['tt-price']=data['Open'][i] # updated to sold price
                                lodgers.loc[l_index]['sell-date']=data.index[i]
                                lodgers.loc[l_index]['tt-profit']= l_profit
                                lodgers.loc[l_index]['tt-profit-rate']=l_profit/lodgers.loc[l_index]['cost']
                                total_tt_cost-=lodgers.loc[l_index]['cost']
                                current_tt_profit += l_profit
                                virt_tt_profit += l_profit

                                if show_verbose > 0:
                                        print total_tt_money, current_tt_profit
                        tt_cash += sold_tt_value    
                        if show_verbose > 0 :
                                print lodgers
            if selling_good_deals == 0 and force_selling_good_deals == 0 and next_buy==0 and next_half_buy==0 and next_steady_buy == 0 and next_tt_buy==0:
                print "*** Empty round %d" % i
                continue
            if (selling_good_deals > 0 or force_selling_good_deals > 0) and not isinstance(lodgers, type(None)):
                # find those holding deals, sell-price is empty
               deals=lodgers.select(lambda x: True if lodgers.loc[x]['sell-price'] == 0 else False)
               if selling_good_deals > 0:
                       to_sold_deals=deals.select(lambda x: True if deals.loc[x]['price']*(1+with_profit) < data['Open'][i] else False)
               else:
                       to_sold_deals=deals.select(lambda x: True if deals.loc[x]['price']*(1+forced_with_profit) < data['Open'][i] else False)

               if isinstance(to_sold_deals, type(None)):
                   continue;

               if show_verbose > 0:
                if to_sold_deals['price'].count() == 0:
                  print "Nothing to sold"
                else:
                  print to_sold_deals[['price','count','cost']]

               selling_slowly=False
               for j in reversed(range(to_sold_deals['price'].count())):
                   #           print data.index[i]
                   lodgers.loc[to_sold_deals.index[j]]['sell-date']=data.index[i]
                   lodgers.loc[to_sold_deals.index[j]]['sell-price']=data['Open'][i]
                   sold_value += data['Open'][i] * to_sold_deals['count'][j]
                   sold_count += to_sold_deals['count'][j]
                   l_profit = (data['Open'][i]-to_sold_deals['price'][j])*to_sold_deals['count'][j]
                   lodgers.loc[to_sold_deals.index[j]]['profit']= l_profit
                   lodgers.loc[to_sold_deals.index[j]]['profit-rate']=lodgers.loc[to_sold_deals.index[j]]['profit']/lodgers.loc[to_sold_deals.index[j]]['cost']
                   total_cost -= lodgers.loc[to_sold_deals.index[j]]['cost']
                   current_profit += lodgers.loc[to_sold_deals.index[j]]['profit']

                   virt_profit += l_profit

                   # only update when first buy. 
                   # lodgers.loc[to_sold_deals.index[j]]['virt-total']=virt_total
                   # lodgers.loc[to_sold_deals.index[j]]['virt-profit']=virt_profit

                   # ok, just do sold slowly
                   if do_sold_slowly :
                        selling_slowly=True
                        break
               cash += sold_value    
               # if with big profit, increase total_money
               if (cash + tt_cash - total_money) > profit_multi * deal_cost and profit_invested == 1:
                        total_money = cash + tt_cash
                        deal_cost = cash / deal_count
                        current_profit-= deal_cost
               if show_verbose > 0:
                     print total_money, current_profit
               if show_verbose > 0 :
                print lodgers[['price','count','cost','sell-date','sell-price']]

            if not selling_slowly:
                selling_good_deals=-1
                force_selling_good_deals=-1

            if first_buy_at < data.index[i] :
                    new_row_data=pandas.DataFrame(index=data.index[i:i+1],
                                                  columns=['price',
                                                       'count',
                                                       'tt-count',                                                
                                                       'total-count',
                                                       'cost',
                                                       'total-cost',
                                                       'virt-total',
                                                       'virt-profit',
                                                        'cash',
                                                        'tt-cash',
                                                       'sell-date',
                                                       'sell-price',
                                                       'profit',
                                                       'profit-rate',
                                                       'pending-rate',
                                                           'tt-price',
                                                           'tt-profit',
                                                           'tt-profit-rate'
                                                ])
                    new_row_data['virt-total'][0]=0
                    new_row_data['virt-profit'][0]=0
                    new_row_data['pending-rate'][0]=0
                    new_row_data['count'][0]=0
                    new_row_data['tt-count'][0]=0
                    new_row_data['total-count'][0]=0
                    new_row_data['total-cost'][0]=0
                    new_row_data['cost'][0]=0
                    new_row_data['price'][0]=data['Open'][i]
                    if sold_count > 0 or sold_tt_count > 0: # stop buy
                        new_row_data['count'][0]-=sold_count
                        new_row_data['tt-count'][0]-=sold_tt_count
                        new_row_data['cost'][0]-=sold_value+sold_tt_value
                    elif (next_buy > 0 or next_half_buy > 0 or next_steady_buy > 0):
                        count=int(min(deal_cost, cash) / data['Open'][i]/100.0) * 100
                        if next_half_buy > 0 and count >= 200:
                            count=count / 2
                        new_row_data['count'][0]=count
                        new_row_data['cost'][0]=count * data['Open'][i]
                        #        new_row_data['signal'][0]=0
                        #        new_row_data['close_s'][0]=0
                        new_row_data['sell-date'][0]=0
                        new_row_data['sell-price'][0]=0
                        new_row_data['profit'][0]=0
                        new_row_data['profit-rate'][0]=0
                        new_row_data['pending-rate'][0]=0
                        total_cost += new_row_data['cost'][0]
                        cash -= new_row_data['cost'][0]
                        # exclude current cost from sold_value
                        if sold_value > 0:
                                sold_value -= new_row_data['cost'][0]
                    elif next_tt_buy > 0: # do tt buying
                        new_row_data['tt-price'][0]=data['Open'][i]                            
                        new_row_data['tt-profit'][0]=0
                        count=int(tt_deal_cost/data['Open'][i]/100.0)*100
                        new_row_data['tt-count'][0]=count
                        new_row_data['cost'][0]=count * data['Open'][i]
                        total_tt_cost+=count * data['Open'][i]
                        tt_cash -= new_row_data['cost'][0]
                    sold_count=0
                    sold_value=0
                    sold_tt_count=0
                    sold_tt_value=0
                    new_row_data['cash'][0]=cash
                    new_row_data['tt-cash'][0]=tt_cash
                    if isinstance(lodgers, type(None)):
                            lodgers=new_row_data
                    else:
                            lodgers=lodgers.append(new_row_data)
            next_buy=-1
            next_half_buy=-1
            next_steady_buy=-1
            next_tt_buy=-1
            if show_verbose > 0 :
                print 'signal %d close_s %d EMA_s %d global %d' % (data['signal'][i], data['close_s'][i], data['EMA_s'][i], global_tendency)
            if data['signal'][i] < 0:
                selling_good_deals=1
            elif data['signal'][i] > 0 and cash > 100 * data['Adj Close'][i]:
                next_buy=1
            else :
                if global_tendency < 1:
                        selling_good_deals=1
                if cash > 100 * data['Adj Close'][i]:
                        if data['close_s'][i] == 0:
                                next_buy=1
                        elif do_half_buy > 0:
                                next_half_buy=1
                        elif do_steady_buy > 0:
                                next_steady_buy=1
                elif selling_good_deals < 1:
                        force_selling_good_deals=1

            global_tendency = data['EMA_s'][i]
            if show_verbose > 0:
                print 'selling %d force_selling %d next_buy %d next_half_buy %d global %d' % (selling_good_deals,
                                                                                              force_selling_good_deals,
                                                                                              next_buy, next_half_buy, global_tendency)
            if do_tt and tt_cash > tt_deal_cost:
                next_tt_buy = data['Close'][i] < data['Open'][i]
            if not isinstance(lodgers, type(None)):
                    l_index=lodgers['total-count'].count()-1
                    if l_index==0: # only one item
                            lodgers.iloc[l_index]['total-count']=lodgers.iloc[l_index]['count']+lodgers.iloc[l_index]['tt-count']
                            lodgers.iloc[l_index]['total-cost']=lodgers.iloc[l_index]['cost']
                            lodgers.iloc[l_index]['virt-total']=lodgers.iloc[l_index]['cost']
                            continue
                    lodgers.iloc[l_index]['total-count']=lodgers.iloc[l_index-1]['total-count']+lodgers.iloc[l_index]['count']+lodgers.iloc[l_index]['tt-count']
                    lodgers.iloc[l_index]['total-cost']=lodgers.iloc[l_index-1]['total-cost']+lodgers.iloc[l_index]['cost']
                    lodgers.iloc[l_index]['virt-total']=lodgers.iloc[l_index]['total-count']*data['Adj Close'][i]

        # generate signal for next operation, buy and/or sell?
        if show_signal > 0 and not isinstance(lodgers, type(None)):
            last=data['Open'].count()-1
            price=data.iloc[last]['Open']
            sellings=lodgers.select(lambda x: True if (lodgers.loc[x]['sell-date'] == data.index[last] and lodgers.loc[x]['sell-price'] > 0)
                                                   else False)['count']
            #    print sellings
            if (sellings.count() > 0):
                    total_op_count -= sellings.sum()

            # sellings=lodgers.select(lambda x: True if (lodgers.loc[x]['price'] < price and lodgers.loc[x]['sell-price'] == 0)
            #                                        else False)['count']
            # if (sellings.count() > 0):
            #         total_op_count -= sellings.sum()

        if (next_buy > 0 or next_half_buy > 0 or next_steady_buy > 0) and show_signal > 0:
            last=data['Open'].count()-1
            count=int(min(deal_cost, cash) / data.iloc[last]['Open']/100.0) * 100
            if next_half_buy > 0 and count >= 200:
                count=count / 2
            if count > 0 and total_op_count == 0:
                print ' buy +%d, at %f' % (count, data.iloc[last]['Adj Close'])

        if (total_op_count != 0):
                print 'sell %d, at %f' % (total_op_count, data.iloc[last]['Adj Close'])

        if show_summary > 0 and not isinstance(lodgers, type(None)):
            last=data['Open'].count()-1
            price=data.iloc[last]['Open']
            holdings=lodgers.select(lambda x: True if lodgers.loc[x]['sell-price']==0 else False)
            total_profit=lodgers.select(lambda x: True if lodgers.loc[x]['profit']>0 else False)['profit'].sum()
            total_profit2=lodgers.select(lambda x: True if lodgers.loc[x]['profit']>0 else False)['profit']/lodgers.select(lambda x: True if lodgers.loc[x]['profit']>0 else False)['cost']
            total_flows=lodgers.select(lambda x: True if lodgers.loc[x]['profit']>0 else False)['cost'].sum()
            if total_flows > 0:
                    print '### flows %d profit %d rate %.3f rate2 %.3f holding %d(=%d) pending %d left %d' % (total_flows, total_profit, total_profit/total_flows, total_profit2.sum() / total_profit2.count(),
                                                                                                              holdings['count'].sum(),
                                                                                                              holdings['cost'].sum(),
                                                                                                              holdings['count'].sum() * price - holdings['cost'].sum(),
                                                                                                              total_money-total_cost+current_profit)

        if isinstance(lodgers, type(None)):
                return
        
        # calculate pending-rate now
        for i in range(lodgers['price'].count()):
                if lodgers.iloc[i]['sell-price'] > 0:
                        continue
                if lodgers.iloc[i]['tt-price'] > 0 and lodgers.iloc[i]['tt-profit'] > 0:
                        continue
                if lodgers.iloc[i]['count'] > 0:
                        lodgers.iloc[i]['pending-rate'] = '%0.2f' % ((data.iloc[data['Open'].count()-1]['Adj Close']-lodgers.iloc[i]['price'])/lodgers.iloc[i]['price'])

        lodgers.to_csv('%s-lodgers.csv' % stock)

        if show_detail > 0:
            print lodgers

ppservers = ()
jobs = []

job_server = pp.Server(ppservers=ppservers)

def one_stock(stock, start, end):
        print stock,start, end
        data = local_func1(stock, start, end)
        #data = pandas.read_csv('%sw-all-data.csv' % stock, index_col=0).sort_index()

#        plot_data=data[['EMA', 'signal']][-60:]
#        plot_data['EMA']=plot_data['EMA']/max(plot_data['EMA']) * 10
        plot_data=data[['price', 'signal']]#[-60:]
        plot_data['price']=plot_data['price']/max(plot_data['price']) * 10

	count=plot_data['price'].count()
        up_data=[ 1 if a > 0 else 0 for a in plot_data['signal'] ] * plot_data['price']
        down_data=[ 1 if a < 0 else 0 for a in plot_data['signal'] ] * plot_data['price']

        _style = 'bar'
        
        # plot as point
        if cmp(_style, 'point') == 0 :
	        pyplot.plot(range(count), plot_data['price'], '.')
                pyplot.plot(range(count), up_data, '^')
                pyplot.plot(range(count), down_data, 'v')
                pyplot.plot(range(count), plot_data['signal'])
        elif cmp(_style, 'bar') == 0 :
		pyplot.bar(range(count),plot_data['price'], label='code = %s (%d/%d)' % (stock, 1, 1))
		pyplot.bar(range(count),up_data, label='buy')
		pyplot.bar(range(count),down_data, label='sell')
                #pyplot.bar(range(count),plot_data['signal'])
                pyplot.legend(loc='upper left')

	pyplot.title(stock)
	pyplot.savefig('%s.png' % stock)
	pyplot.close()

        new_weekly_policy(stock, data, total_money=stocks[0][4], deal_count=stocks[0][5], first_buy=stocks[0][6])

def process_one_stock(s, name, total_money, deal_count, first_buy, csv_file='', start=0, stocks_count=0):
        print '%s processing...' % s

        data=pandas.read_csv(csv_file, index_col=0).sort_index()

        plot_data=data[['price', 'signal']]#[-60:]
        plot_data['price']=plot_data['price']/max(plot_data['price']) * 10
        #figure=plot_data.plot(kind='bar',figsize=(12,6),title='%s' % s[0]).figure
        #figure.savefig('%s-%s.png' % (s, _stocks.ix[s].name), bbox_inches='tight')
        #figure=None
	count=plot_data['price'].count()
        up_data=[ 1 if a > 0 else 0 for a in plot_data['signal'] ] * plot_data['price']
        down_data=[ 1 if a < 0 else 0 for a in plot_data['signal'] ] * plot_data['price']

	matplotlib.pyplot.ioff()
	matplotlib.pyplot.figure(figsize=(18,6))
        
        tt = u'code = %s %s (%d/%d)' % (s, name.decode('utf-8'), start, stocks_count)
	matplotlib.pyplot.bar(range(count),plot_data['price'], label=tt)
	matplotlib.pyplot.bar(range(count),up_data, label='buy')
	matplotlib.pyplot.bar(range(count),down_data, label='sell')
        #pyplot.bar(range(count),plot_data['signal'])
        matplotlib.pyplot.legend(loc='upper left')
        
	matplotlib.pyplot.title(s)
	matplotlib.pyplot.savefig('%s-%s.png' % (s,name))
	matplotlib.pyplot.clf() # clear current figure
        matplotlib.pyplot.close()
        
        new_weekly_policy(s, data, total_money, deal_count, first_buy)
        
def all_stocks(choice='all'):
        stocks_count = 0
	_stocks=tushare.get_stock_basics()

        selected = False;
        deselected = False;
        existed = False;
        
        print 'choice = %s' % choice
        
        if cmp(choice, 'selected') == 0:
                selected = True;
        elif cmp(choice, 'deselected') == 0:
                deselected = True;
 
        for s in _stocks.index:
               if _stocks.ix[s].profit <= 0:
                       continue
               
               existed = path.exists('selected/%s-%s.png' % (s,_stocks.ix[s].name))
               if selected == True and existed == False: 
                       continue
               if deselected == True and existed == True:
                       continue
               
               stocks_count+=1

	       csv_file='%sw-all-data.csv' % s
	       if path.exists(csv_file):
                       continue
               
               jobs.append(job_server.submit(local_func1, (s, stocks[0][2], stocks[0][3]), (), ("StockSignal", "pandas", )))

        l_ppservers = ()
        l_jobs = []

        l_job_server = pp.Server(ppservers=l_ppservers)
                
        start = 0

        for s in _stocks.index:
                if _stocks.ix[s].profit <= 0:
                        continue

                existed = path.exists('selected/%s-%s.png' % (s,_stocks.ix[s].name))
                if selected == True and existed == False: 
                        continue
                if deselected == True and existed == True:
                        continue
 
                start += 1
                # name is not the real name
                name= _stocks.ix[s].name

		csv_file='%sw-all-data.csv' % s
                stop = 5
		while not path.exists(csv_file) and stop > 0:
                        # wait random seceonds
                        secs=random.random() * 10
			print 'waiting %ds for %s (#%d) ' % (secs, csv_file, stop)
			time.sleep(secs)
                        stop -= 1

                l_jobs.append(l_job_server.submit(process_one_stock,
                                                  args=(s, name, stocks[0][4], stocks[0][5], stocks[0][6], csv_file, start, stocks_count),
                                                  modules=("StockSignal", "pandas", "matplotlib.pyplot", "new_weekly_policy")))
                #process_one_stock(s, name, stocks[0][4], stocks[0][5], stocks[0][6], csv_file, start, stocks_count)

        l_job_server.wait()
        print ''
        l_job_server.print_stats()

                
def __main():
#        stocks = stocks3
        
        for s in stocks:
                if s[5] == 0:  # deal_cost is zero, continue
                        continue
                jobs.append(job_server.submit(local_func1, (s[0], s[2], s[3]), (), ("StockSignal", "pandas", )))

        job_server.wait()
        print ''
        job_server.print_stats()
	
	pyplot.ioff()
        #use pp for following computing is not so good
	start=0
	stocks_count = len(stocks)
	pyplot.figure(figsize=(22,6*stocks_count))
        for s in stocks:
                if s[5] == 0: # deal_cost is zero, continue
                        continue
                data=pandas.read_csv('%sw-all-data.csv' % s[0], index_col=0).sort_index()

                print s[1],s[0]
#                plot_data=data[['EMA', 'signal']][-60:]
#                plot_data['EMA']=plot_data['EMA']/max(plot_data['EMA']) * 10
                plot_data=data[['price', 'signal', 'EMA']]#[-60:]
                plot_data['price']=plot_data['price']/max(plot_data['price']) * 10
                plot_data['EMA']=plot_data['EMA']/max(plot_data['EMA']) * 10
                #figure=plot_data.plot(kind='bar',figsize=(12,6),title='%s' % s[0]).figure
                #figure.savefig('%s-%s.png' % (s[0], s[1]), bbox_inches='tight')
                #figure=None
		start+=1
		pyplot.subplot(stocks_count, 1, start)
		count=plot_data['price'].count()
                up_data=[ 1 if a > 0 else 0 for a in plot_data['signal'] ] * plot_data['price']
                down_data=[ 1 if a < 0 else 0 for a in plot_data['signal'] ] * plot_data['price']

                _style = 'bar'

                # plot as point
                if cmp(_style, 'point') == 0 :
	                pyplot.plot(range(count), plot_data['price'], '.')
                        pyplot.plot(range(count), up_data, '^')
                        pyplot.plot(range(count), down_data, 'v')
                        pyplot.plot(range(count), plot_data['signal'])
                elif cmp(_style, 'bar') == 0 :
                        tt = u'code = %s %s (%d/%d)' % (s[0], s[1].decode('utf-8'), start, stocks_count)
		        pyplot.bar(range(count),plot_data['price'], label=tt)
		        pyplot.bar(range(count),up_data, label='buy')
		        pyplot.bar(range(count),down_data, label='sell')
                        #pyplot.bar(range(count),plot_data['signal'])
                        pyplot.plot(range(count),plot_data['EMA'], label='EMA')
                        pyplot.legend(loc='upper left')

		pyplot.title(s[0])

                if s[4] > 0:
                        new_weekly_policy(s[0], data, total_money=s[4], deal_count=s[5], first_buy=s[6])
                else:
                        new_weekly_policy(s[0], data, deal_count=s[5], first_buy=s[6])
	pyplot.subplots_adjust(left=0.05, top=0.99, bottom=0.01, right=0.95, hspace=0.1, wspace=0.1) 
	pyplot.savefig('stocks.png')
	pyplot.close()

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

#pandas.read_csv('510300w-all-data.csv', index_col=0)[['EMA', 'signal']][-60:].plot(kind='bar',figsize=(20,12),title='ETF300').figure.show()
#figure.savefig('a.svg', format='svg', bbox_inches='tight')

def main(argv):
    print argv

    matplotlib.rcParams['font.sans-serif'] = ['AR PL KaitiM GB'] # SimHei is common Chinese font on macOS. ttc is not ok.
#fonts-arphic-gkai00mp/xenial 2.11-15 all
#  "AR PL KaitiM GB" Chinese TrueType font by Arphic Technology

# after install new font, must delete this file: /root/.cache/matplotlib/fontList.cache  to let matplotlib update font cache

    if len(argv) == 1:
        __main()
        return

    # 1 args: all_stocks | selected
    if len(argv) == 2:
            globals()[argv[1]]()
    # 2 args: one_stock ######, last year
    elif len(argv) == 3:
            end = pandas.datetime.now();
            start=end-datetime.timedelta(365)

            globals()[argv[1]](argv[2],start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    # 3 args: one_stock ######, start, until now
    elif len(argv) == 4:
            globals()[argv[1]](argv[2], argv[3], pandas.datetime.now().strftime('%Y-%m-%d'))
    elif len(argv) == 5:
    # 4 args: one_stock ######, start, end
            globals()[argv[1]](argv[2], argv[3], argv[4])
    else:
            print "Usage: program [one_stock [stock [start [end]]]]"

close_mean = pandas.Series()
close_upper = pandas.Series()
close_lower = pandas.Series()

window_size = 20

# plot and save to file
def do_plot_with_window_size(window_size, filename):
        if close_mean.count() < window_size:
                window_size = close_mean.count()

        matplotlib.pyplot.ioff()  
        matplotlib.pyplot.figure()

        # plot in line for boll bands
        matplotlib.pyplot.plot(range(window_size), close_mean[- window_size:])
        matplotlib.pyplot.plot(range(window_size), close_upper[ - window_size:])
        matplotlib.pyplot.plot(range(window_size), close_lower[- window_size :])

        matplotlib.pyplot.savefig(filename)
        matplotlib.pyplot.close()

def generate_png_filename(dir):
        png_file = '%s.png' % os.path.basename(dir)
        #print (png_file)
        return png_file

# inotify specified dir to plot living price
def plot_living_price(argv):
        pass

# process saved prices in specified dir        
def plot_saved_price(dest_dir):
    try:
        l_dir=dest_dir.rstrip('/')
        files = os.listdir(l_dir)
        files.sort()
        print ('Total %d files to plot\n' % (len(files)))
        for fname in files:
            if fname.endswith('.boll') == False:
                continue
            fpath = os.path.join(l_dir, fname)
            with open(fpath, 'r') as f:
                line = f.readline().rstrip('\n')
                try: 
                        boll = [float(x) for x in line.split(',')]
                except Exception as ex:
                        print fpath
                        continue
                # ignore nan data
                if math.isnan(boll[0]) == False:
                    close_mean[fname]=boll[0]
                    close_upper[fname]=boll[1]
                    close_lower[fname]=boll[2]
        #print (close_mean)
        # only plot when finished processing
        png_file = generate_png_filename(l_dir)
        do_plot_with_window_size(window_size, png_file)
    except Exception as ex:
        print (traceback.format_exc())

if __name__ == "__main__":
        l_dir = sys.argv[1]
        plot_saved_price(l_dir)
        sys.exit(plot_living_price(l_dir))
