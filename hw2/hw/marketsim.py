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
    
    
if __name__ == "__main__":
   main(sys.argv[1:])