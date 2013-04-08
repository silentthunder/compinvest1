#hw 3 part 1 & 2
import sys



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
    
    #scan trades for symbols and dates - built a list of symbols and a date range
    
    #Read in data (use adjusted close)
    
    #scan trades to update cash
    
    #scan trades to create ownership array & value
    
    #scan cash and value to create total fund value
    
if __name__ == "__main__":
   main(sys.argv[1:])