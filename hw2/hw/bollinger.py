# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import copy

import hw2 as hw2

def bollinger_value(dt_start, dt_end,ls_symbols, n_days_lookback):
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    return bollinger_value_int(d_data, n_days_lookback)
    
def bollinger_value_int(d_data, n_days_lookback):    
    # Getting the numpy ndarray of close prices.
    df_price = d_data['close'].copy()
    ls_symbols = df_price.columns
    ldt_timestamps = df_price.index
    #
    n_data_size = len(ldt_timestamps)
    n_symbols = len(ls_symbols)

    df_sma = pd.DataFrame(np.zeros((n_data_size, n_symbols)), columns=ls_symbols, index=ldt_timestamps)
    df_stddev_price = pd.DataFrame(np.zeros((n_data_size, n_symbols)), columns=ls_symbols, index=ldt_timestamps)
    df_lower_band = pd.DataFrame(np.zeros((n_data_size, n_symbols)), columns=ls_symbols, index=ldt_timestamps)
    df_upper_band = pd.DataFrame(np.zeros((n_data_size, n_symbols)), columns=ls_symbols, index=ldt_timestamps)
    df_bollinger_val = pd.DataFrame(np.zeros((n_data_size, n_symbols)), columns=ls_symbols, index=ldt_timestamps)
    
    df_sma =  pd.rolling_mean(df_price, n_days_lookback)
    df_stddev_price = pd.rolling_std(df_price, n_days_lookback)
    df_upper_band = df_sma + df_stddev_price
    df_lower_band = df_sma - df_stddev_price
    df_bollinger_val = (df_price - df_sma) / (df_stddev_price)
    
    return (df_price, df_sma, df_upper_band, df_lower_band, df_bollinger_val)

def find_events(df_bollinger_val, n_bval_sym_daily_drop_threshold, s_sym_mkt_index, n_bval_mktindex_above):
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_bollinger_val)
    df_events = df_events * np.NAN
    ls_symbols = df_bollinger_val.columns
    ldt_timestamps = df_bollinger_val.index
    #TODO split df_bollinger into two structures: 1 dataframe of bollinger values for stocks 
    #and a list of bollinger values for market index
    
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            #if s_sym == s_sym_mkt_index:
                #skip checking the event for mkt_index
                #continue
            # Calculating the bolinger values
            n_bolinger_val_sym_today = df_bollinger_val[s_sym].ix[ldt_timestamps[i]]
            n_bolinger_val_sym_yest = df_bollinger_val[s_sym].ix[ldt_timestamps[i-1]]
            n_bolinger_val_mkt_today_mkt = df_bollinger_val[s_sym_mkt_index].ix[ldt_timestamps[i]]
            
            # Event is found if bollinger value for a stock drops below given threshold (n_bval_sym_daily_drop_threshold)
            # AND bollinger value for market index is above given value(n_bval_mktindex_above)
            if n_bolinger_val_sym_yest >= n_bval_sym_daily_drop_threshold \
            and n_bolinger_val_sym_today < n_bval_sym_daily_drop_threshold \
            and n_bolinger_val_mkt_today_mkt >= n_bval_mktindex_above:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
    return df_events
    
def main():
    print 'Bollinger indicator exercise'
    #parameters
#     dt_start = dt.datetime(2010, 1, 1)
#     dt_end = dt.datetime(2010, 12, 31)
#     ls_symbols = ['GOOG','AAPL','MSFT']
#     n_days_lookback = 20
#     (df_price, df_sma, df_upper_band, df_lower_band, df_bollinger_val) = bollinger_value(dt_start, dt_end, ls_symbols, n_days_lookback)
    
#     print 'Q1:',df_bollinger_val['AAPL'].ix[dt.datetime(2010, 5, 21,16,0)]
#     print 'Q2:',df_bollinger_val['MSFT'].ix[dt.datetime(2010, 5, 12,16,0)]
#     plt.clf()
#     
#     plt.plot(df_price.index, df_price['GOOG'].values)
#     plt.plot(df_sma.index, df_sma['GOOG'].values)
#     plt.plot(df_upper_band.index, df_upper_band['GOOG'].values)
#     plt.plot(df_lower_band.index, df_lower_band['GOOG'].values)
#     plt.axhline(y=0, color='r')
#     plt.legend(['price', 'SMA','upper band', 'lower band'])
#     plt.ylabel('SMA')
#     plt.xlabel('Date')
#     plt.savefig('test.pdf', format='pdf')
    
    # HW6
    #Event:
    #Bollinger value for the equity today <= -2.0
    #Bollinger value for the equity yesterday >= -2.0
    #Bollinger value for SPY today >= 1.0
    #Start date: 1 Jan 2008
    #End date: 31 Dec 2009
    #20 day lookback for Bollinger bands
    #Symbol list: SP502012
    #Adjusted close.
    n_bval_sym_daily_drop_threshold = -2.0
    n_bval_mktindex_above = 1.0
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    s_sym_mkt_idx = 'SPY'
    ls_symbols.append(s_sym_mkt_idx)
    n_days_lookback = 20
    
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    (df_price, df_sma, df_upper_band, df_lower_band, df_bollinger_val) = bollinger_value_int(d_data, n_days_lookback)     
    df_events = find_events(df_bollinger_val, n_bval_sym_daily_drop_threshold, s_sym_mkt_idx, n_bval_mktindex_above)
    print "Creating Study for HW6 test"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='output/MyEventStudyHW6test.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym=s_sym_mkt_idx)
    
    # HW6 Q1
    # Bollinger value of equity today < -2.0 
    # Bollinger value of equity yesterday >= -2.0
    # Bollinger value of SPY today >= 1.5
    # 
    # * Test this event using the Event Profiler over the period from 1st Jan, 2008 to 31st Dec 2009. 
    # * Using the symbol list - SP5002012 
    # * Using adjusted_close to create Bollinger bands 
    # * 20 day lookback Bollinger bands 
    n_bval_sym_daily_drop_threshold = -2.0
    n_bval_mktindex_above = 1.5
    df_events = find_events(df_bollinger_val, n_bval_sym_daily_drop_threshold, s_sym_mkt_idx, n_bval_mktindex_above)
    print "Creating Study for HW6 Q1"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='output/MyEventStudyHW6Q1.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym=s_sym_mkt_idx)
   
    
if __name__ == '__main__':
    main()