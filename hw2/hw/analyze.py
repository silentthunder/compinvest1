#hw 3 part 2
import sys
import numpy as np
import datetime as dt
import pandas as pd

#QSTK imports
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu

def main(argv):
    valuesFilename = argv[0]
    benchmarkSym = argv[1]
    
    #read values file
    na_values = np.loadtxt(valuesFilename, dtype={'names': ('Year','Month','Day', 'Value'),
                                                  'formats': ('i4', 'i4','i4', 'f4')}, delimiter=',')
    dt_timeofday = dt.timedelta(hours=16)
    ls_dates = []
    ls_values= [] 
    for record in na_values:
        aDate = dt.datetime(record[0], record[1], record[2]) + dt_timeofday
        ls_dates.append(aDate)
        ls_values.append(record[3])
    dt_start = ls_dates[0]
    dt_end = ls_dates[len(ls_dates)-1]
    
    #retrieve data for benchmark
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ls_dates, [benchmarkSym], ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    df_close = d_data['close'].copy()
    na_values_bench = df_close[benchmarkSym].values
    print na_values_bench
    
    # daily returns
    na_returns = np.array(ls_values)
    tsu.returnize0(na_returns)
    na_returns_bench = na_values_bench.copy()
    tsu.returnize0(na_returns_bench)
    
    na_vol = np.std(na_returns)
    na_vol_bench = np.std(na_returns_bench)
    na_avg_return = np.mean(na_returns)
    na_avg_return_bench = np.mean(na_returns_bench)
    
    na_sharp = np.sqrt(252)*na_avg_return/na_vol
    na_sharp_bench = np.sqrt(252)*na_avg_return_bench/na_vol_bench
    na_total_return = ls_values[len(ls_values)-1] / ls_values[0]
    na_total_return_bench = na_values_bench[len(na_values_bench)-1] / na_values_bench[0]
    
    print 'The final value of the portfolio using the sample file is -- ', na_values[len(na_values)-1]
    print 'Details of the Performance of the portfolio :'

    print 'Data Range : ',dt_start, 'to ',dt_end

    print 'Sharpe Ratio of Fund : ', na_sharp
    print 'Sharpe Ratio of ',benchmarkSym, ' : ',na_sharp_bench

    print 'Total Return of Fund :  ',na_total_return
    print 'Total Return of ',benchmarkSym, ' : ',na_total_return_bench

    print 'Standard Deviation of Fund : ', na_vol
    print 'Standard Deviation of $SPX : ', na_vol_bench

    print 'Average Daily Return of Fund : ',na_avg_return
    print 'Average Daily Return of ',benchmarkSym, ' : ', na_avg_return_bench
    
if __name__ == "__main__":
   main(sys.argv[1:])