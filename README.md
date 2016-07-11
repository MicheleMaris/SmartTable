This is a collection of tools to handle CSV tables organized in columns of homogeneous elements.

Needed libraries: 
  numpy
  matplotlib
  pickle
  pyfits

A CSV table is a table where
 
data are written just in ASCII
each row is a record
fields are separed by "," 
the first row defines column names.

Each row begining with # is a comment and it is skipped

As an example

#Example Table
NAME,SURNAME,CODE
Jhon,Smith,101
Harrison,Smith,102
Liu,Smith,102
#end table

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

