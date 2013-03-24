#hw 1 part 1

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
#dfdsfds
# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from duplicity.globals import volsize
from numpy.ma.core import sqrt

def simulate(dt_start, dt_end, ls_symbols, na_allocations):
    print 'Simulate'
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo',cachestalltime=0)

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
    
    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]
    
    # portfolio value
    na_cum_daily_portf_value = np.dot(na_normalized_price, na_allocations)
    #print na_cum_daily_portf_value.size #should be 252
    n_trading_days =  na_cum_daily_portf_value.size
    
    # daily returns
    na_daily_rets = na_cum_daily_portf_value.copy()
    tsu.returnize0(na_daily_rets)
    
    #volatility
    na_vol = np.std(na_daily_rets)
    
    #sharp
    na_sharp = np.sqrt(252)*np.mean(na_daily_rets)/na_vol
    
    return (na_vol, na_daily_rets, na_sharp, na_cum_daily_portf_value[na_cum_daily_portf_value.size-1])

def main():
    print 'Main'
    ls_symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    na_allocations = np.array([0.0, 0.0, 0.0, 1.0])
    vol, daily_ret, sharpe, cum_ret = simulate(dt_start, dt_end, ls_symbols, na_allocations)
    print 'Sharpe ratio '
    print sharpe
    print 'Volatility'
    print vol
    print 'Avg daily ret'
    print np.average(daily_ret)
    print 'Cumulative return'
    print cum_ret
    
if __name__ == '__main__':
    main()