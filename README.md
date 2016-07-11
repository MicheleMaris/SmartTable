This is a collection of tools to handle tables organized in columns of homogeneous elements.

Needed libraries: 
  numpy
  matplotlib
  pickle
  pyfits

Usage:

# read data from a csv table
from SmartTable import csv_table()
SM=csv_table('filename.csv')

#print number of elements
print len(SM)

#print list of column names
print SM.keys()

# write data to a pickle file
SM.pickle('pickle_table.pkl')

# read data from a pickle file
SM1=csv_table()
SM1.load('pickle_table.pkl')

************ README TO BE COMPLETED ************

