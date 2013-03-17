#hw 1 part 1

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

def simulate(dt_start, dt_end, ls_symbols, allocations):
    print 'Simulate'
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

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
    
     # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]
    
    # portfolio valu
    na_portf_norm_price = na_normalized_price * allocations
    
    
    

def main():
    print 'Main'
    ls_symbols = ["AAPL", "GLD", "GOOG", "$SPX", "XOM"]
    dt_start = dt.datetime(2006, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    allocations = [0.1, 0.1, 0.5, 0.3]
    simulate()
    
if __name__ == '__main__':
    main()