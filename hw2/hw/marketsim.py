#hw 3 part 1 & 2
import sys
import numpy as np
import datetime as dt
import pandas as pd

#QSTK imports
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
from posixpath import samefile

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
    
    for record in na_trades:
        ls_symbols.append(record[3])        
        aDate = dt.datetime(record[0], record[1], record[2])
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
    dt_timeofday = dt.timedelta(hours=16)
    
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end+dt.timedelta(days=1), dt_timeofday)
    #print 'timestamps=', ldt_timestamps
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, set_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    df_actual_close = d_data['close'].copy()
    #print(df_actual_close)
    #print(df_actual_close.index)

    #scan trades to update cash
    ls_cash = []
    currentCash = startingCash
    for trade in na_trades_norm:
        dt_date = trade[0]
        symbol = trade[1]
        txType = trade[2]
        nShares = trade[3]
        price = df_actual_close[symbol].ix[dt_date+dt_timeofday]
        print 'Operation: ',txType,', stock: ', trade[1],', date: ', dt_date+dt_timeofday, ', price: ',  price,', amount: ',nShares
        if (txType == 'Buy'):
            currentCash -= (nShares*price)
        else:
            currentCash += (nShares*price)
        print currentCash
        ls_cash.append(currentCash)
        
    print 'ls_cash ', ls_cash
    
    #scan trades to create ownership array & value
    #print 'all symbols:',set_symbols
    df_ownership = pd.DataFrame(np.zeros((len(na_trades_norm), len(set_symbols))), columns=set_symbols)
    i = 0
    ls_value = []
    for trade in na_trades_norm:
        dt_date = trade[0]
        symbol = trade[1]
        txType = trade[2]
        nShares = trade[3]
        if (txType == 'Sell'):
            nShares = -nShares
        if i == 0: 
            df_ownership.ix[i].ix[symbol] = nShares
        else:
            for stockSymbol in set_symbols:
                #copy the previous state
                df_ownership.ix[i].ix[stockSymbol] = df_ownership.ix[i-1].ix[stockSymbol]
            df_ownership.ix[i].ix[symbol] += nShares
        
        assetsValueAfterTx = 0
        for stockSymbol in set_symbols:
            stockPrice = df_actual_close[stockSymbol].ix[dt_date+dt_timeofday]
            assetsValueAfterTx += stockPrice * df_ownership.ix[i].ix[stockSymbol] 
        
        #df_ownership.ix[i].ix['Value'] = assetsValueAfterTx
        ls_value.append(assetsValueAfterTx)
        i += 1
    print df_ownership
    
    #scan cash and value to create total fund value
    np_total_fund_value = np.array(ls_cash) + np.array(ls_value)
    print np_total_fund_value
    
    #generate result file
    fout = open(valuesFilename, 'w')
    print ls_dates_sorted
    i = 0
    for trade in na_trades_norm:
        dt_date = trade[0]
        
        line ='%d, %d, %d, %f\n' % (dt_date.year,dt_date.month,dt_date.day,np_total_fund_value[i]) 
        print line
        fout.write(line)
        i += 1
        
    #fout.write('')
    fout.close()
    
if __name__ == "__main__":
   main(sys.argv[1:])