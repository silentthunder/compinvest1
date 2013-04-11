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
    print 'Number of arguments:', len(argv), 'arguments.'
    print 'Argument List:', str(argv)
    valuesFilename = argv[0]
    benchmarkSym = argv[1]
    print 'Values\' file name:',valuesFilename
    print 'Benchmark:',benchmarkSym
    
    #read values file
    na_values = np.loadtxt(valuesFilename, dtype={'names': ('Year','Month','Day', 'Value'),
                                                  'formats': ('i4', 'i4','i4', 'f4')}, delimiter=',')
    
    ls_dates = []
    ls_values= [] 
    for record in na_values:
        aDate = dt.datetime(record[0], record[1], record[2])
        ls_dates.append(aDate)
        ls_values.append(record[3])
    dt_start = ls_dates[0]
    dt_end = ls_dates[len(ls_dates)-1]
    
    # daily returns
    na_returns = np.array(ls_values)
    tsu.returnize0(na_returns)
    
    na_vol = np.std(na_returns)
    na_sharp = np.sqrt(252)*np.mean(na_returns)/na_vol
    print 'Sharp ratio: ',na_sharp
    
if __name__ == "__main__":
   main(sys.argv[1:])