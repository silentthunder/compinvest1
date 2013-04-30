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

def find_events_price_drops_below(ls_symbols, d_data_2008, n_treshold):
    df_actual_close = d_data_2008['actual_close']
    
    print 'Finding events in which stockprice(actual close) drops below:'
    print n_treshold
    
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_actual_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_actual_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_actual_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_actual_close[s_sym].ix[ldt_timestamps[i - 1]]

            # Event is found if actual close of the stock price drops below given threshold
            if f_symprice_yest >= n_treshold and f_symprice_today < n_treshold:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events
def generate_buy_and_sell_orders(df_events, n_amount, n_days_to_sell):
    print 'Generating trades'
    ldt_timestamps = df_events.index
    #print 'days:',ldt_timestamps
    ls_trades = []    #date,symbol,orderType,quantity
    ls_symbols = df_events.columns
    #print 'symbols: ',ls_symbols
    i = 0
    n_days = len(ldt_timestamps)
    while (i < n_days):
        for symbol in ls_symbols:
            if (df_events[symbol].ix[ldt_timestamps[i]] == 1):
                buyOrder = (ldt_timestamps[i], symbol, 'Buy', n_amount)
                idx = i+n_days_to_sell
                if (idx >= n_days):
                    idx = n_days-1
                sellOrder =  (ldt_timestamps[idx], symbol, 'Sell', n_amount)
                ls_trades.append(buyOrder)
                ls_trades.append(sellOrder)
        i = i+1
    #print 'Trades:',ls_trades
    return ls_trades

def serialize_trades(s_output_file, ls_trades):
    print 'Serializing trades to the file: ',s_output_file
    fout = open(s_output_file, 'w')
    i = 0
    for trade in ls_trades:
        dt_date = trade[0]
        symbol = trade[1]
        order_type = trade[2]
        amount = trade[3]
        #day,month,day,symbol,orderType,quantity
        line ='%d,%d,%d,%s,%s,%d' % (dt_date.year,dt_date.month,dt_date.day,symbol,order_type, amount) 
        print line
        fout.write(line)
        i += 1
        if i < len(ls_trades):
            fout.write('\n')
        
def remove_NAN_from_price_data(d_data_2008, ls_keys):
    for s_key in ls_keys:
        d_data_2008[s_key] = d_data_2008[s_key].fillna(method = 'ffill')
        d_data_2008[s_key] = d_data_2008[s_key].fillna(method = 'bfill')
        d_data_2008[s_key] = d_data_2008[s_key].fillna(1.0)

if __name__ == '__main__':
    print 'Main'
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    
     # HW4 period 2008-2009, sp5002012, threshold 5.0
    ls_symbols_2012 = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols_2012.append('SPY')    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data_2012 = dataobj.get_data(ldt_timestamps, ls_symbols_2012, ls_keys)
    d_data_2012 = dict(zip(ls_keys, ldf_data_2012))
    #remove_NAN_from_price_data(d_data_2012, ls_keys)
    df_events_2012 = find_events_price_drops_below(ls_symbols_2012, d_data_2012, 6.0)
    #print "Creating Study for HW4"
    #ep.eventprofiler(df_events_2012, d_data_2012, i_lookback=20, i_lookforward=20,
    #            s_filename='output/MyEventStudyHW4sp5002012threshold5.pdf', b_market_neutral=True, b_errorbars=True,
    #            s_market_sym='SPY')
    ls_trades = generate_buy_and_sell_orders(df_events_2012, 100, 5)
    print 'number of trades generated: ', len(ls_trades)
    serialize_trades('output/orders_hw4_q2.csv', ls_trades)
    
    
    