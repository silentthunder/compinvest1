'''
Created on 24 Mar 2013

@author: stw
'''
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

# condition C1 - entry point - when a price of a stock makes higher high and lower lows 
#within two consecutive periods and open price in the next(third) period is lower than previous close
def find_entry_points(ls_symbols, d_data):
    df_actual_close = d_data['actual_close']
    
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_actual_close)
    df_events = df_events * np.NaN

    # Time stamps for the event range
    ldt_timestamps = df_actual_close.index

    for s_sym in ls_symbols:
        for t in range(2, len(ldt_timestamps)):
            current_open = d_data['open'][s_sym].ix[ldt_timestamps[t]]
            prev_close = d_data['actual_close'][s_sym].ix[ldt_timestamps[t-1]]
            prev_high = d_data['high'][s_sym].ix[ldt_timestamps[t-1]]
            prev_low = d_data['low'][s_sym].ix[ldt_timestamps[t-1]]
            prev_prev_high = d_data['high'][s_sym].ix[ldt_timestamps[t-2]]
            prev_prev_low = d_data['low'][s_sym].ix[ldt_timestamps[t-2]]
            
            #print current_open, ', ', prev_close, ', ', prev_high, ', ', prev_low, ', ',prev_prev_high, ', ',prev_prev_low

            #price makes higher highs and lower lows
            if prev_prev_high < prev_high and prev_prev_low > prev_low and current_open < prev_close:
                df_events[s_sym].ix[ldt_timestamps[t]] = 1
    return df_events

#input
#- buy signals
#output
#- buy and sell orders according to the rules
# sell at FIRST PROFITABLE OPEN after a buy signal
# stop\loss high Px(t) - low Px(t) ) / 2.0 for a buy signal fired at t+1
def generate_buy_and_sell_orders(df_events, d_data, n_amount):
    print 'Generating trades'
    ldt_timestamps = df_events.index
    #print 'days:',ldt_timestamps
    ls_trades = []    #date,symbol,orderType,quantity,price_type,stoploss(yes/no)
    ls_symbols = df_events.columns
    #print 'symbols: ',ls_symbols
    t = 0
    n_days = len(ldt_timestamps)
    for t in range (2, n_days):
        for symbol in ls_symbols:
            #buy order for a buy signal
            if (df_events[symbol].ix[ldt_timestamps[t]] == 1):                
                d_price_at_buy = d_data['open'][symbol].ix[ldt_timestamps[t]]
                buyOrder = (ldt_timestamps[t], symbol, 'Buy', n_amount, 'open','-')
                ls_trades.append(buyOrder)
                #search forward for sell signal or stop loss
                tf = t+1
                b_stop = False
                while (b_stop == False and tf < n_days):
                    #check next profitable close
                    if (d_data['open'][symbol].ix[ldt_timestamps[tf]] > d_price_at_buy ):
                        #take profit - sell at profitable open
                        sellOrder =  (ldt_timestamps[tf], symbol, 'Sell', n_amount, 'open','no')
                        ls_trades.append(sellOrder)
                        b_stop = True
                    #check stop loss
                    else:
                        d_halfrange_2nd_outside_day = (d_data['high'][symbol].ix[ldt_timestamps[t-1]] -d_data['low'][symbol].ix[ldt_timestamps[t-1]])/2
                        for o_type in ['open','low','actual_close']:
                            if (d_data[o_type][symbol].ix[ldt_timestamps[tf]] < (d_price_at_buy - d_halfrange_2nd_outside_day)):
                                sellOrder =  (ldt_timestamps[tf], symbol, 'Sell', n_amount, o_type, 'yes')
                                ls_trades.append(sellOrder)
                                b_stop = True    
                                break                    
                    tf = tf + 1                    
    #print 'Trades:',ls_trades
    return ls_trades
def count_trades(ls_trades):
    n_profitable = 0
    n_loss = 0
    for trade in ls_trades:
        s_stoploss = trade[5]
        if s_stoploss == 'yes':
            n_loss = n_loss+1
        elif s_stoploss == 'no':
            n_profitable = n_profitable + 1
    return (n_profitable, n_loss)

#Input     
#date,symbol,orderType,quantity,price_type,stoploss(yes/no)
def serialize_trades(s_output_file, ls_trades):
    print 'Serializing trades to the file: ',s_output_file
    fout = open(s_output_file, 'w')
    i = 0
    nTrades = len(ls_trades)
    for trade in ls_trades:
        dt_date = trade[0]
        symbol = trade[1]
        order_type = trade[2]
        amount = trade[3]
        price_type = trade[4]
        stop_loss = trade[5]
        #day,month,day,symbol,orderType,quantity
        line ='%d,%d,%d,%s,%s,%d,%s,%s' % (dt_date.year,dt_date.month,dt_date.day,symbol,order_type, amount, price_type, stop_loss) 
        #print line
        fout.write(line)
        i += 1
        if i < nTrades:
            fout.write('\n')
        
def count_total_number_of_events(df_events):
    ldt_timestamps = df_events.index
    ls_symbols = df_events.columns
    n_days = len(ldt_timestamps)
    count = 0
    for i in range(n_days):
        for symbol in ls_symbols:
            if (df_events[symbol].ix[ldt_timestamps[i]] == 1):
                count = count + 1
    return count

def remove_NAN_from_price_data(d_data_2008, ls_keys):
    for s_key in ls_keys:
        d_data_2008[s_key] = d_data_2008[s_key].fillna(method = 'ffill')
        d_data_2008[s_key] = d_data_2008[s_key].fillna(method = 'bfill')
        d_data_2008[s_key] = d_data_2008[s_key].fillna(1.0)

if __name__ == '__main__':
    print 'Main'
    year_start = 2008
    year_end = 2009
    dt_start = dt.datetime(year_start, 1, 1)
    dt_end = dt.datetime(year_end, 12, 31)
    outputFileName = "output/outsideDaySystem"+`year_start`+"-"+`year_end`+".csv"
    print "Output filename: ",outputFileName
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    
    ls_symbols_2012 = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols_2012.append('SPY')
    #ls_symbols_2012 = ['AAPL','SPY']     
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data_2012 = dataobj.get_data(ldt_timestamps, ls_symbols_2012, ls_keys)
    d_data_2012 = dict(zip(ls_keys, ldf_data_2012))
    remove_NAN_from_price_data(d_data_2012, ls_keys)
    df_events_2012 = find_entry_points(ls_symbols_2012, d_data_2012)
    #print "Creating Study"
    #print 'event generated: ', count_total_number_of_events(df_events_2012)
#     ep.eventprofiler(df_events_2012, d_data_2012, i_lookback=20, i_lookforward=20,
#                  s_filename='output/MyEventStudyOutsideDaySystem2008-2009.pdf', b_market_neutral=True, b_errorbars=True,
#                  s_market_sym='SPY')
    ls_trades = generate_buy_and_sell_orders(df_events_2012, d_data_2012, 5)
    print 'number of trades generated: ', len(ls_trades)
    (n_profitable_trades,n_loss_trades) = count_trades(ls_trades)
    print 'profitable: ',n_profitable_trades,'loss: ',n_loss_trades
    serialize_trades(outputFileName, ls_trades)
    
    
    