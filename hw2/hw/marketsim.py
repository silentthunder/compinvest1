#hw 3 part 1
import sys
import numpy as np
import datetime as dt
import pandas as pd

#QSTK imports
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
from _sortedlist import sortedset

def main(argv):
    print 'Number of arguments:', len(argv), 'arguments.'
    print 'Argument List:', str(argv)
    startingCash = int(argv[0])
    ordersFilename = argv[1]
    valuesFilename = argv[2]
    print 'Starting cash:',str(startingCash)
    print 'Orders\' file name:',ordersFilename
    print 'Values\' file name:',valuesFilename
    
    #read CSV into "trades" array
    na_trades = np.loadtxt(ordersFilename, dtype={'names': ('Year','Month','Day', 'Symbol', 'txType', 'nShares'),
                                                  'formats': ('i4', 'i4','i4', 'S5', 'S5','i4')}, delimiter=',')
    #print(na_trades)
    na_trades_norm = []
    #print 'empty norm trades array', na_trades_norm
    
    #scan trades for symbols and dates - built a list of symbols and a date range
    ls_symbols = []
    ls_dates = []
    dt_timeofday = dt.timedelta(hours=16)
    
    for record in na_trades:
        ls_symbols.append(record[3])        
        aDate = dt.datetime(record[0], record[1], record[2]) + dt_timeofday
        ls_dates.append(aDate)
        na_trades_norm.append((aDate,record[3], record[4], record[5]));

    #print 'norm trades ',na_trades_norm
    na_trades_norm = sorted(na_trades_norm,key=lambda trade: trade[0])
    #print 'norm trades sorted ',na_trades_norm
    set_symbols = set(ls_symbols)
    ls_dates_sorted = sorted(ls_dates)
    dt_start = ls_dates_sorted[0]
    dt_end = ls_dates_sorted[len(ls_dates)-1]
    
    print 'start date:',dt_start
    print 'end_date:', dt_end
    
    #Read in data (use adjusted close)
    c_dataobj = da.DataAccess('Yahoo')
   
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    #print 'timestamps=', ldt_timestamps
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, set_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    df_actual_close = d_data['close'].copy()

    #scan trades to update cash
    ls_cash = []
    currentCash = startingCash
    i = 0
    numberOftrades = len(na_trades_norm)
    for dt_date in ldt_timestamps:
        # if there are trades for dt_date
        while  dt_date == na_trades_norm[i][0]:
            symbol = na_trades_norm[i][1]
            txType = na_trades_norm[i][2]
            nShares = na_trades_norm[i][3]
            price = df_actual_close[symbol].ix[dt_date]
            if (txType == 'Buy'):
                currentCash -= (nShares*price)
            else:
                currentCash += (nShares*price)
            i = i+1
            if (i == numberOftrades):
                break
        ls_cash.append(currentCash)
    print ls_cash
        
    #print 'ls_cash ', ls_cash
    #scan trades to create ownership array & value
    #print 'all symbols:',set_symbols
    set_columns = set_symbols.copy()
    set_columns.add('Value')
    #index array must be sorted otherwise algorithm in the for loop won't work correctly
    df_ownership = pd.DataFrame(np.zeros((len(ldt_timestamps), len(set_columns))), columns=set_columns, index=ldt_timestamps)
    #print df_ownership
    d_current_positions = dict(zip(set_symbols, np.zeros((len(set_symbols)))))
    print d_current_positions
    i = 0
    for dt_date in ldt_timestamps:
        # if there are trades for dt_date
        while (dt_date == na_trades_norm[i][0]):
            symbol = na_trades_norm[i][1]
            txType = na_trades_norm[i][2]
            nShares = na_trades_norm[i][3]
            if (txType == 'Sell'):
                nShares = -nShares
            d_current_positions[symbol] += nShares
            i = i+1
            if (i == numberOftrades):
                break
        assetsValue = 0
        #TODO add vector to the current row in data frame
        for symbol in d_current_positions.keys():
            nSharesOfSymbol = d_current_positions[symbol]
            print 'shares of symbol',symbol,'=',nSharesOfSymbol
            df_ownership.ix[dt_date].ix[symbol] = nSharesOfSymbol
            if nSharesOfSymbol != 0:
                stockPrice = df_actual_close[symbol].ix[dt_date]
                assetsValue += stockPrice * nSharesOfSymbol
        df_ownership.ix[dt_date].ix['Value'] = assetsValue
    
    #scan cash and value to create total fund value
    np_total_fund_value = np.array(ls_cash) + np.array(df_ownership['Value'])
    print np_total_fund_value
    
    #generate result file
    fout = open(valuesFilename, 'w')
    i = 0
    print df_ownership.index
    for dt_date in df_ownership.index:
        line ='%d, %d, %d, %f\n' % (dt_date.year,dt_date.month,dt_date.day,np_total_fund_value[i]) 
        print line
        fout.write(line)
        i += 1
        
    #fout.write('')
    fout.close()
    
if __name__ == "__main__":
   main(sys.argv[1:])