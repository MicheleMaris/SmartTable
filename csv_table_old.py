__DESCRIPTION__="""self structure to read and handle a generic csv file 
2014 Aug 04 : Added support for column description """
"""
readcol.py by Adam Ginsburg (keflavich@gmail.com)

readcol is meant to emulate IDL's readcol.pro, but is more capable and
flexible.  It is not a particularly "pythonic" program since it is not modular.
For a modular ascii table reader, http://cxc.harvard.edu/contrib/asciitable/ is
probably better.  This single-function code is probably more intuitive to an
end-user, though.
"""
import string,re,sys
import numpy
try:
    from scipy.stats import mode
    hasmode = True
except ImportError:
    #print "scipy could not be imported.  Your table must have full rows."
    hasmode = False
except ValueError:
    #print "error"
    hasmode = False

def readcol(filename,skipline=0,skipafter=0,names=False,fsep=None,twod=True,
        fixedformat=None,asdict=False,comment='#',verbose=True,nullval=None,
        asStruct=False):
    """
    The default return is a two dimensional float array.  If you want a list of
    columns output instead of a 2D array, pass 'twod=False'.  In this case,
    each column's data type will be automatically detected.
    
    Example usage:
    CASE 1) a table has the format:
     X    Y    Z
    0.0  2.4  8.2
    1.0  3.4  5.6
    0.7  3.2  2.1
    ...
    names,(x,y,z)=readcol("myfile.tbl",names=True,twod=False)
    or
    x,y,z=readcol("myfile.tbl",skipline=1,twod=False)
    or 
    names,xx = readcol("myfile.tbl",names=True)
    or
    xxdict = readcol("myfile.tbl",asdict=True)
    or
    xxstruct = readcol("myfile.tbl",asStruct=True)

    CASE 2) no title is contained into the table, then there is
    no need to skipline:
    x,y,z=readcol("myfile.tbl")
    
    CASE 3) there is a names column and then more descriptive text:
     X      Y     Z
    (deg) (deg) (km/s) 
    0.0    2.4   8.2
    1.0    3.4.  5.6
    ...
    then use:
    names,x,y,z=readcol("myfile.tbl",names=True,skipline=1,twod=False)
    or
    x,y,z=readcol("myfile.tbl",skipline=2,twod=False)

    INPUTS:
        fsep - field separator, e.g. for comma separated value (csv) files
        skipline - number of lines to ignore at the start of the file
        names - read / don't read in the first line as a list of column names
                can specify an integer line number too, though it will be 
                the line number after skipping lines
        twod - two dimensional or one dimensional output
        nullval - if specified, all instances of this value will be replaced
           with a floating NaN
        asdict - zips names with data to create a dict with column headings 
            tied to column data.  If asdict=True, names will be set to True
        asStruct - same as asdict, but returns a structure instead of a dictionary
            (i.e. you call struct.key instead of struct['key'])
        fixedformat - if you have a fixed format file, this is a python list of 
            column lengths.  e.g. the first table above would be [3,5,5].  Note
            that if you specify the wrong fixed format, you will get junk; if your
            format total is greater than the line length, the last entries will all
            be blank but readcol will not report an error.

    If you get this error: "scipy could not be imported.  Your table must have
    full rows." it means readcol cannot automatically guess which columns
    contain data.  If you have scipy and columns of varying length, readcol will
    read in all of the rows with length=mode(row lengths).
    """
    f=open(filename,'r').readlines()
    
    null=[f.pop(0) for i in range(skipline)]

    if names or asdict or asStruct:
        # can specify name line 
        if type(names) == type(1):
            nameline = f.pop(names)
        else:
            nameline = f.pop(0)
        if nameline[0]==comment:
            nameline = nameline[1:]
        nms=nameline.split(fsep)

    null=[f.pop(0) for i in range(skipafter)]

    commentfilter = make_commentfilter(comment)
    
    if fixedformat:
        myreadff = lambda(x): readff(x,fixedformat)
        splitarr = map(myreadff,f)
        splitarr = filter(commentfilter,splitarr)
    else:
        fstrip = map(string.strip,f)
        fseps = [ fsep for i in range(len(f)) ]
        splitarr = map(string.split,fstrip,fseps)
        for i in xrange(splitarr.count([''])):
            splitarr.remove([''])

        splitarr = filter(commentfilter,splitarr)

        # check to make sure each line has the same number of columns to avoid 
        # "ValueError: setting an array element with a sequence."
        nperline = map(len,splitarr)
        if hasmode:
            ncols,nrows = mode(nperline)
            if nrows != len(splitarr):
                if verbose:
                    print "Removing %i rows that don't match most common length.  \
                     \n%i rows read into array." % (len(splitarr) - nrows,nrows)
                for i in xrange(len(splitarr)-1,-1,-1):  # need to go backwards
                    if nperline[i] != ncols:
                        splitarr.pop(i)

    try:
        x = numpy.asarray( splitarr , dtype='float')
    except ValueError:
        if verbose: 
            print "WARNING: reading as string array because %s array failed" % 'float'
        try:
            x = numpy.asarray( splitarr , dtype='S')
        except ValueError:
            if hasmode:
                raise Exception( "ValueError when converting data to array." + \
                        "  You have scipy.mode on your system, so this is " + \
                        "probably not an issue of differing row lengths." )
            else:
                raise Exception( "Conversion to array error.  You probably " + \
                        "have different row lengths and scipy.mode was not " + \
                        "imported." )

    if nullval is not None:
        x[x==nullval] = numpy.nan
        x = get_autotype(x)

    if asdict or asStruct:
        mydict = dict(zip(nms,x.T))
        for k,v in mydict.iteritems():
            mydict[k] = get_autotype(v)
        if asdict:
            return mydict
        elif asStruct:
            return Struct(mydict)
    elif names and twod:
        return nms,x
    elif names:
        # if not returning a twod array, try to return each vector as the spec. type
        return nms,[ get_autotype(x.T[i]) for i in xrange(x.shape[1]) ]
    else:
        if twod:
            return x
        else:
            return [ get_autotype(x.T[i]) for i in xrange(x.shape[1]) ]

def get_autotype(arr):
    """
    Attempts to return a numpy array converted to the most sensible dtype
    Value errors will be caught and simply return the original array
    Tries to make dtype int, then float, then no change
    """
    try:
        narr = arr.astype('float')
        if (narr < sys.maxint).all() and (narr % 1).sum() == 0:
            return narr.astype('int')
        else:
            return narr
    except ValueError:
        return arr

class Struct(object):
    """
    Simple struct intended to take a dictionary of column names -> columns
    and turn it into a struct by removing special characters
    """
    def __init__(self,namedict):
        R = re.compile('\W')  # find and remove all non-alphanumeric characters
        for k in namedict.keys():
            v = namedict.pop(k) 
            if k[0].isdigit():
                k = 'n'+k
            namedict[R.sub('',k)] = v  
        self.__dict__ = namedict

def readff(s,format):
    """
    Fixed-format reader
    Pass in a single line string (s) and a format list, 
    which needs to be a python list of string lengths 
    """

    F = numpy.array([0]+format).cumsum()
    bothF = zip(F[:-1],F[1:])
    strarr = [s[l:u] for l,u in bothF]

    return strarr

def make_commentfilter(comment):
    if comment is not None:
        def commentfilter(a):
            try: return comment.find(a[0][0])
            except: return -1
        return commentfilter
    else: # always return false 
        return lambda(x): -1

 
class csv_table :
   def __init__(self,*arg,**karg) : 
      """Creates a Table from a CSV file
      
         Signatures :
      
         csv_table() an empty object is created with just metadata
                     the same for csv_table('') or csv_table(None)
            
         csv_table(csvname) with csvname a string
               the parameter is handles as the filename of a csv table, 
               the corrisponding file is readed
            
         csv_table(csvdict) with csvdict a dictionary or an OrderedDict, 
               the parameter is handled as a dictionary including a table
               and ingestes as it is
            
         csv_table(csvpickle,pickle=True) csvpickle a string
               the parameter is handled as pickle file through the
               csv_table.load() procedure
         
         csv_table(csvhdu,hdu=True) csvhdu a fits hdu
               the parameter is handled as an HDU through the
               csv_table.get_from_hdu() procedure
         
         Keywords: 
            fsep=',' (default) the character used to separate columns
            tablename=None (default) name of the table
            description=None (default) the description of the table
            newmetadata=None (default) list of metadata names to be added to the table
                        BEWARE: 
                           metadata names are private members and begins with '__' 
                           and possibly ends the same manner
                        Example '__keys__'"
            pickle=False (default) takes data from a pickle
            hdu=False (default) takes data from an hdu
            signpost = False (default) if True a completelly empty object is created
                    the object so created has just a name and a type
                    it can be used for nothing but tests of the type:
                        if foo.__class__ == csv_table(signpost=True).__class__ : 
                           print 'foo is a csv_table'
       """
      import copy
      from collections import OrderedDict
      #
      # creates completely empty object (usually used as signpost object)
      if karg.has_key('signpost') :
         if karg['signpost'] : 
            return
      #
      # creates metadata
      self.__fsep__=',' if not karg.has_key('fsep') else karg['fsep']
      self.__tablename__=None if not karg.has_key('tablename') else karg['tablename']
      self.__description__=None if not karg.has_key('description') else karg['description']
      self.__metadata_list__=None if not karg.has_key('newmetadata') else karg['newmetadata']
      self.__columns_description__=None 
      self.__csvname__=None
      self.__picklefilename__=None
      self.__info__=OrderedDict()
      self.__keys__=None
      self.__fitsfilename__=None
      #
      # arguments are not passed?
      if len(arg) != 1 : return
      #
      # the argument is a dictionary
      if type(arg[0]) == type({}) or type(arg[0]) == type(OrderedDict()) :
         self.__keys__=arg[0].keys()
         for k in arg[0].keys() : self.__dict__[k]=copy.deepcopy(arg[0][k])
         self.register_existing_columns_to_column_description()
         return
      #
      # the argument is a not empty string or it is not None
      if arg[0] == None or arg[0].strip()=='' : return
      #
      # handle name as a pickle file
      if karg.has_key('pickle') :
         if karg['pickle'] : 
            self.load(arg[0].strip())
            return
      #
      # handle the parameter as an hdu
      if karg.has_key('hdu') :
         if karg['hdu'] : 
            self.get_from_hdu(arg[0])
            return
      #
      # handle the name as a csv file
      try :
         a=readcol(arg[0].strip(),fsep=self.__fsep__,asStruct=True).__dict__
      except :
         print "File not found or unreadable"
         return 
      self.__keys__=a.keys()
      for k in a.keys() : self.__dict__[k]=a[k]
      self.register_existing_columns_to_column_description()
   def list_metadata(self,asArray=True) :
      import numpy as np
      l=['__csvname__','__fsep__','__keys__','__picklefilename__','__description__','__info__','__metadata_list__','__columns_description__','__fitsfilename__','__tablename__']
      try :
         for k in self.__metadata_list__ :
            l.append(k)
      except :
         pass
      return np.array(l) if asArray else l
   def keys(self,noMeta=True,justMeta=False,asArray=False) : 
      import numpy as np
      l=self.list_metadata()
      if justMeta : 
         return np.array(l) if asArray else l
      a=[]
      for k in self.__dict__.keys() :
         if (k==l).sum() == 0 or not noMeta :
            a.append(k)
      return np.array(a) if asArray else a
   def __len__(self) : 
      import numpy as np
      k=self.keys()
      if len(k)==0 : return 0
      if np.isscalar(self.__dict__[k[0]]) : return 1
      return len(self.__dict__[k[0]])
   def copy(self,justCols=False,justMeta=False) :
      import copy
      if justMeta :
         a=csv_table(self,None)
         for k in self.list_metadata():
            try :
               a.__dict__[k]=copy.deepcopy(self.__dict__[k])
            except :
               a.__dict__[k]=None
         return a
      return copy.deepcopy(self)
   def __getitem__(self,arg) :
      return self.__dict__[arg]
   def __setitem__(self,*arg) :
      "this does not affect columns description"
      if len(arg) == 2 :
         self.__dict__[arg[0]]=arg[1]
      if len(arg) == 3 :
         self.__dict__[arg[0]][arg[1]]=arg[2]
   def newcolumn(self,name,value,description='- to be described -',unit='-tbd-',shape='-tbd-') :
      "creates a new column and adds the corresponding description"
      self[name]=value
      self.register_column_description(name,description,unit=unit,shape=shape) 
   def pickle(self,picklefilename) :
      import pickle 
      pickle.dump(self.__dict__,open(picklefilename,'w'))
   def load(self,picklefilename) :
      import pickle 
      self.__dict__=pickle.load(open(picklefilename,'r'))
      self.__picklefilename__=picklefilename
      # old pickle files can not contain column descriptions, creates a dummy one
      if not self.__dict__.has_key('__columns_description__') :
         self.__columns_description__=None
         self.register_existing_columns_to_column_description()
      if not self.__dict__.has_key('__fitsfilename__') :
         self.__fitsfilename__=None
      if not self.__dict__.has_key('__tablename__') :
         self.__tablename__=None
   def register_column_description(self,name,description,unit='-tbd-',shape='-tbd-') :
      "register a column description, overwrite any old entry with the same name"
      from collections import OrderedDict
      if self.empty_column_description() : 
         self.__columns_description__ = OrderedDict()
      self.__columns_description__[name]=(name,description,unit,shape)
   def unpack_column_description(self,name) :
      "returns unpacked entry of column description"
      if self.empty_column_description() : return None
      return self.__columns_description__[name]
   def update_column_description(self,name,description=None,unit=None,shape=None,force=False) :
      """update a column description
         fields not included in the call are left as they are
         usually if the description does not exists, no update is done, but if "force=True" a new entry is created
      """
      from collections import OrderedDict
      if self.empty_column_description() : return
      try :
         #(name,description,unit,shape)
         _name,_description,_unit,_shape = self.unpack_column_description(name)
         if description != None : _description=description
         if unit != None : _unit=unit
         if shape != None : _shape=shape
         self.register_column_description(name,_description,unit=_unit,shape=_shape)
      except :
         if force :
            _description=description if description != None else '-tbd-'
            _unit=unit if unit != None else '-tbd-'
            _shape=shape if shape != None else '-tbd-'
            self.register_column_description(name,_description,unit=_unit,shape=_shape)
   def empty_column_description(self) :
      "True if column description is None"
      return self.__columns_description__ == None
   def has_name_column_description(self,name) :
      """True if column description has key "name"""
      if self.empty_column_description() : return False
      return self.__columns_description__.has_key(name)
   def register_existing_columns_to_column_description(self,overwrite=False) :
      """register all the fields not already registered 
         all the parameters but the name are filled with '-tbd-'
         overwrite = False (default) prevents from resetting already registered keywords
      """
      for k in self.keys() :
         if not self.has_name_column_description(k) or overwrite :
            self.register_column_description(k,'-tbd-')
   def help_column(self,name) :
      "returns the column description for a given column"
      try :
         dd=self.__columns_description__[name]
         return "%s : %s : %s : %s"%(dd[0],dd[2],str(dd[3]),dd[1])
      except :
         return "column %s is not registered"%name
   def banner(self,onscreen=True) :
      "generates a banner with the column description"
      line=[]
      line.append('*****************************')
      line.append('Table  : '+(self.__tablename__ if self.__tablename__ != None else ''))
      line.append('CSV    : '+(self.__csvname__ if self.__csvname__ != None else ''))
      line.append('Pickle : '+(self.__picklefilename__ if self.__picklefilename__ != None else ''))
      line.append('Pickle : '+(self.__fitsfilename__ if self.__fitsfilename__ != None else ''))
      line.append('*****************************')
      for k in self.__columns_description__.keys() :
         if self.help_column(k) != None :
            line.append(self.help_column(k))
      line.append('*****************************')
      line='\n'.join(line)
      if onscreen : 
         print line
         return
      return line
   def tablename(self) :
      "def returns the table name"
      try :
         return self.__tablename__ if self.__tablename__!=None else ''
      except :
         return ''
   def argslice(self,idx) :
      import numpy as np
      import copy
      a=self.copy(justMeta=True)
      for k in self.keys() :
         try :
            a.__dict__[k]=self.__dict__[k][idx]
         except :
            a.__dict__[k]=copy.deepcopy(self.__dict__[k])
      if len(idx) == 1 :
         u=np.array([1]).shape
         for k in self.keys() :
            a.__dict__[k].shape=u
      return a
   def flag(self,*arg,**karg) :
      import numpy as np
      flag=np.ones(len(self))
      for k in karg.keys() :
         flag*=(self.__dict__[k]==karg[k])
      return flag
   def argselect(self,*arg,**karg) :
      import numpy as np
      flag=np.ones(len(self))
      for k in karg.keys() :
         flag*=(self.__dict__[k]==karg[k])
      idx=np.where(flag)[0]
      return idx
   def select(self,*arg,**karg) :
      import numpy as np
      flag=np.ones(len(self))
      for k in karg.keys() :
         flag*=(self.__dict__[k]==karg[k])
      idx=np.where(flag)[0]
      return self.argslice(idx)
   def fields2arrays(self) :
      "forces all the fields to be arrays"
      import numpy as np
      if len(self) == 1 :
         u=np.array([1]).shape
         for k in self.keys() :
            self.__dict__[k]=np.array([self.__dict__[k]])
            self.__dict__[k].shape=u
      else :
         for k in self.keys() :
            self.__dict__[k]=np.array(self.__dict__[k])
   def dict(self) :
      "returns the table as a dictionary"
      out={}
      for k in self.keys() :
         out[k]=self.__dict__[k]
      return out
   def to_fits_hdu(self) :
      "returns the table as a fits HDU" 
      from dict2fits import Table
      T=Table(self.dict())
      try :
         T.update('csv',self.__csvname__ if self.__csvname__ != None else '')
      except :
         T.update('csv','')
      try :
         T.update('pkl',self.__picklefilename__ if self.__picklefilename__ != None else '')
      except :
         T.update('pkl','')
      try :
         T.update('fits',self.__fitsfilename__ if self.__fitsfilename__ != None else '')
      except :
         T.update('fits','')
      if self.__columns_description__ != None :
         if len(self.__columns_description__.keys()) > 0 :
            T.add_comment('')
            T.add_comment('***************************')
            T.add_comment('Description of columns')
            for k in self.__columns_description__.keys() :
               T.add_comment(self.help_column(k))
            T.add_comment('***************************')
            T.add_comment('')
      return T
   def get_from_hdu(self,hdu) :
      "gets data from an hdu formatted as a fits table"
      for it in range(1,hdu.header['TFIELDS']+1) :
         n=hdu.header['TTYPE%d'%it]
         u=hdu.header['TUNIT%d'%it]
         f=hdu.header['TFORM%d'%it]
         d=''
         try :
            d=hdu.header['TDSCR%d'%it]
            if d == None : d = ''
         except :
            d=''
         self.newcolumn(n.capitalize(),hdu.data.field(n),unit=u,shape=f,description=d)

