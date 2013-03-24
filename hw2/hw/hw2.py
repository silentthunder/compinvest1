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
    # calculations for sp5002008
    ls_symbols_2008 = dataobj.get_symbols_from_list('sp5002008')
    ls_symbols_2008.append('SPY')    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data_2008 = dataobj.get_data(ldt_timestamps, ls_symbols_2008, ls_keys)
    d_data_2008 = dict(zip(ls_keys, ldf_data_2008))
    remove_NAN_from_price_data(d_data_2008, ls_keys)
    df_events_2008 = find_events_price_drops_below(ls_symbols_2008, d_data_2008, 5.0)
    print "Creating Study for 2008"
    ep.eventprofiler(df_events_2008, d_data_2008, i_lookback=20, i_lookforward=20,
                s_filename='output/MyEventStudysp5002008threshold5.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
    
    # calculations for sp5002008
    ls_symbols_2012 = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols_2012.append('SPY')    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data_2012 = dataobj.get_data(ldt_timestamps, ls_symbols_2012, ls_keys)
    d_data_2012 = dict(zip(ls_keys, ldf_data_2012))
    #remove_NAN_from_price_data(d_data_2012, ls_keys)
    df_events_2012 = find_events_price_drops_below(ls_symbols_2012, d_data_2012, 5.0)
    print "Creating Study for 2012"
    ep.eventprofiler(df_events_2012, d_data_2012, i_lookback=20, i_lookforward=20,
                s_filename='output/MyEventStudysp5002012threshold5.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
    
    # calculations for Q2: period 2008-2009, sp5002008, threshold 6.0
    ls_symbols_2008 = dataobj.get_symbols_from_list('sp5002008')
    ls_symbols_2008.append('SPY')    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data_2008 = dataobj.get_data(ldt_timestamps, ls_symbols_2008, ls_keys)
    d_data_2008 = dict(zip(ls_keys, ldf_data_2008))
    remove_NAN_from_price_data(d_data_2008, ls_keys)
    df_events_2008 = find_events_price_drops_below(ls_symbols_2008, d_data_2008, 6.0)
    print "Creating Study for Q2"
    ep.eventprofiler(df_events_2008, d_data_2008, i_lookback=20, i_lookforward=20,
                s_filename='output/MyEventStudyQ2sp5002008threshold6.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
    
    # calculations for Q3: period 2008-2009, sp5002012, threshold 8.0
    ls_symbols_2012 = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols_2012.append('SPY')    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data_2012 = dataobj.get_data(ldt_timestamps, ls_symbols_2012, ls_keys)
    d_data_2012 = dict(zip(ls_keys, ldf_data_2012))
    #remove_NAN_from_price_data(d_data_2012, ls_keys)
    df_events_2012 = find_events_price_drops_below(ls_symbols_2012, d_data_2012, 8.0)
    print "Creating Study for Q3"
    ep.eventprofiler(df_events_2012, d_data_2012, i_lookback=20, i_lookforward=20,
                s_filename='output/MyEventStudyQ3sp5002012threshold8.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
    
     # calculations for Q3 attempt 3: period 2008-2009, sp5002012, threshold 10.0
    ls_symbols_2012 = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols_2012.append('SPY')    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data_2012 = dataobj.get_data(ldt_timestamps, ls_symbols_2012, ls_keys)
    d_data_2012 = dict(zip(ls_keys, ldf_data_2012))
    #remove_NAN_from_price_data(d_data_2012, ls_keys)
    df_events_2012 = find_events_price_drops_below(ls_symbols_2012, d_data_2012, 10.0)
    print "Creating Study for Q3"
    ep.eventprofiler(df_events_2012, d_data_2012, i_lookback=20, i_lookforward=20,
                s_filename='output/MyEventStudyQ3sp5002012threshold10.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
    