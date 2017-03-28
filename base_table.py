
__DESCRIPTION__ = """Base for Table object."""

__VERSION__="3.0 : 2016 Feb 24; 3.1 : 2016 Dec 26"

def DescriptionV2(Dict,names=None,unit_value='',verbose=False) :
   """Try to compile a description from the dictionary
    This is a private method
   """
   import pyfits
   import numpy as np
   from collections import OrderedDict
   try :
      names[0]
      lstn=names
   except :
      lstn=Dict.keys() 
   description = OrderedDict()
   description['name']=[]
   description['format']=[]
   description['comment']=[]
   description['unit']=[]
   count=0
   for ttype in lstn :
      dtn=None
      name=None
      try :
         dtn = Dict[ttype].dtype.name
      except :
         if verbose :
            print "%s is a dictionary, or something which can not be convered, skipped"%ttype
         dtn=None
      if dtn != None :
         dtn=dtn.lower().strip()
         if dtn=='bool' :
            fmt = 'L'
         elif dtn=='int16' :
            fmt='I'
         elif dtn=='int32' :
            fmt='J'
         elif dtn=='int64' :
            fmt='K'
         elif dtn=='float32' :
            fmt='E'
         elif dtn=='float64' :
            fmt='D'
         elif dtn=='complex128' :
            fmt='M'
         elif dtn[0:6]=='string' :
            fmt='A'
         else :
            if verbose :
               print "Format %s not found"%dtn
            fmt=None
         if fmt!=None :
            size=''
            if fmt == 'A':
               ll=1
               for k in Dict[ttype] :
                  if ll < len(k) :
                     ll = len(k)
               size='%d'%ll
            else :
               shape = Dict[ttype].shape
               if len(shape) > 1 :
                  size='%d'%shape[1]
            fmt=size+fmt
            description['name'].append(ttype)
            description['format'].append(fmt)
            description['unit'].append(unit_value)
            description['comment'].append('')
            count+=1
   description['number']=count
   return description

class base_table :
   def __init__(self,*arg,**karg) : 
      """A base table is a table divided in columns of same length
      
         Signatures :
      
         base_table() an empty object is created with just metadata
                     the same for base_table('') or base_table(None)
            
         base_table(dict) with dict a dictionary or an OrderedDict, 
               the parameter is handled as a dictionary including a table
               and ingestes as it is
            
         base_table(pickle,pickle=True) pickle a string
               the parameter is handled as pickle file through the
               csv_table.load() procedure
         
         base_table(hdu,hdu=True) hdu a fits hdu
               the parameter is handled as an HDU through the
               base_table.get_from_hdu() procedure
         
         Keywords: 
            fsep=',' (default) the character used to separate columns in a csv file
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
                        if foo.__class__ == base_table(signpost=True).__class__ : 
                           print 'foo is a base_table'
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
      self._setup_metadata()
      self.__fsep__=',' if not karg.has_key('fsep') else karg['fsep']
      self.__tablename__=None if not karg.has_key('tablename') else karg['tablename']
      self.__description__=None if not karg.has_key('description') else karg['description']
      self.__metadata_list__=None if not karg.has_key('newmetadata') else karg['newmetadata']
      self.__verbose__=False if not karg.has_key('Verbose') else karg['Verbose']
      #self.__columns_description__=None 
      #self.__csvname__=None
      #self.__picklefilename__=None
      #self.__info__=OrderedDict()
      #self.__keys__=None
      #self.__fitsfilename__=None
      #
      # arguments are not passed?
      if len(arg) == 0 : 
         self.__status__='init:completed'
         return
      #
      # the argument is a dictionary
      if type(arg[0]) == type({}) or type(arg[0]) == type(OrderedDict()) :
         self.__keys__=arg[0].keys()
         for k in arg[0].keys() : self.__dict__[k]=copy.deepcopy(arg[0][k])
         self.register_existing_columns_to_column_description()
         self.__status__='init:completed'
         return
      #
      # handle the parameter as an hdu
      if karg.has_key('hdu') :
         if karg['hdu'] : 
            self.get_from_hdu(arg[0])
            self.__status__='init:completed'
            return
      #
      # the argument is a not empty string or it is not None
      if arg[0] == None or arg[0].strip()=='' : 
         self.__status__='init:completed'
         return
      #
      # handle name as a pickle file
      if karg.has_key('pickle') :
         if karg['pickle'] : 
            self.load(arg[0].strip())
            self.__status__='init:completed'
            return
   def isVerbose(self) :
      try :
         return self.__verbose__==True
      except :
         return False
   def version(self) :
      return __VERSION__
   def _setup_metadata(self) :
      from collections import OrderedDict
      for k in self.list_metadata() : 
         if k == '__info__' : 
            self.__dict__[k]=OrderedDict()
         else :
            self.__dict__[k]=None
   def list_metadata(self,asArray=True) :
      import numpy as np
      l=['__csvname__','__fsep__','__keys__','__picklefilename__','__description__','__info__','__metadata_list__','__columns_description__','__fitsfilename__','__tablename__','__status__','__verbose__']
      try :
         for k in self.__metadata_list__ :
            l.append(k)
      except :
         pass
      return np.array(l) if asArray else l
   def set_metadata(self,name,value) :
      mname='__%s__'%name
      if (self.list_metadata()==mname).sum() > 0 :
         self.__dict__[mname]=value
      else :
         raise NameError('Metadata %s not found'%name)
   def get_metadata(self,name) :
      mname='__%s__'%name
      if (self.list_metadata==mname).sum() > 0 :
         return self.__dict__[mname]
      else :
         raise NameError('Metadata %s not found'%name)
   def set_keys(self,List) :
     """sets the list of keys as wanted by the owner
        default is None
     """
     import copy
     if List == None : self.__keys__=None
     self.__keys__=list(List)
   def keys(self,noMeta=True,justMeta=False,asArray=False,fromColumnsDescription=False,forceInternal=False) : 
      import numpy as np
      l=self.list_metadata(asArray=False)
      if justMeta : 
         return np.array(l) if asArray else l
      if fromColumnsDescription : #or self.empty_column_description()  :
         l1=self.__columns_description__.keys()
         if noMeta : 
            return np.array(l1) if asArray else l1
         l1=np.concatenate([np.array(l),np.array(l1)])
         return np.array(l1) if asArray else list(l1)
      else :
         l1=None
	 if self.__dict__.has_key('__keys__') :
	    if self.__keys__.__class__==np.zeros(1).__class__ or self.__keys__.__class__==[].__class__ or self.__keys__.__class__==().__class__ :
               if len(self.__keys__)>0 :
                  l1=self.__keys__
         if l1 == None or forceInternal : l1=self.__dict__.keys()
         if not noMeta : 
            return np.array(l1) if asArray else l1
         for k in range(len(l1)) :
            if l1[k] in l :
               l1[k]=''
         l1=np.array(l1)
         idx=np.where(l1!='')[0]
         l1=l1[idx]
         return np.array(l1) if asArray else list(l1)
   def __len__(self) : 
      import numpy as np
      k=self.keys()
      if len(k)==0 : return 0
      if np.isscalar(self.__dict__[k[0]]) : return 1
      return len(self.__dict__[k[0]])
   def copy(self,justCols=False,justMeta=False) :
      import copy
      if justMeta :
         a=base_table()
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
   def clean_column_description(self) :
      "clean all the column descriptions"
      from collections import OrderedDict
      self.__columns_description__ = OrderedDict()
   def empty_column_description(self) :
      "True if column description is None"
      if self.__columns_description__ == None : return True
      if len(self.__columns_description__.keys()) == 0 : return True
      return False
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
      line.append('Fits   : '+(self.__fitsfilename__ if self.__fitsfilename__ != None else ''))
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
      for k in self.__dict__.keys() :
         try :
            a.__dict__[k]=self.__dict__[k][idx]
         except :
            a.__dict__[k]=copy.deepcopy(self.__dict__[k])
      if len(idx) == 1 :
         u=np.array([1]).shape
         for k in self.keys() :
            if 'numpy' in str(type(a.__dict__[k])) :
               a.__dict__[k].shape=u
      a.__class__=self.__class__
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
   def fields2arrays(self,operator='array') :
      """reduce fields in the table to numpy arrays
         keyword operator = type of operator to be used
                    if operator == 'array' (default) 
                       for k in self.keys() : self[k]=np.array(self[k])
                    if operator == 'concatenate' (default) 
                       for k in self.keys() : self[k]=np.concatenate(self[k])
      """
      import numpy as np
      if len(self) == 1 :
         u=np.array([1]).shape
         for k in self.keys() :
            self.__dict__[k]=np.array([self.__dict__[k]])
            self.__dict__[k].shape=u
      else :
         if operator == 'array' :
            for k in self.keys() :
               self.__dict__[k]=np.array(self.__dict__[k])
         elif operator == 'concatenate' :
            for k in self.keys() :
               self.__dict__[k]=np.concatenate(self.__dict__[k])
         else :
            raise Exception('Error: unknowm operator "'+operator+'" in reduce2array, valid values: "array", "concatenate".')
   def dict(self) :
      "returns the table as a dictionary (no metadata included)"
      out={}
      for k in self.keys() :
         out[k]=self.__dict__[k]
      return out
   def to_csv(self,fsep=None,fileName=None) :
      """returns a text formatted as csv
         putting fileName='foo.csv' the result is written in foo.csv
      """
      _fsep=self.__fsep__+' ' if fsep == None or fsep.strip() == '' else fsep
      body=[_fsep.join(self.keys(fromColumnsDescription=True))]
      for i in range(len(self)) :
         line = []
         for k in self.keys(fromColumnsDescription=True) :
            line.append(str(self[k][i]))
         body.append(_fsep.join(line))
      if fileName != None :
         if fileName.strip() !='' :
            o=open(fileName,'w')
            o.write(('\n'.join(body))+'\n')
            o.close()
            return
      return '\n'.join(body)
   def to_fits_hdu(self) :
      "returns the table as a fits HDU" 
      import pyfits
      import numpy as np
      dsc=DescriptionV2(self,names=self.keys())
      c=[]
      for k in range(len(self.keys())) :
         name=self.keys()[k]
         c.append(pyfits.Column(array=self[name],name=dsc['name'][k],format=dsc['format'][k]))
      #T=pyfits.new_table(pyfits.ColDefs(c))
      T=pyfits.BinTableHDU.from_columns(pyfits.ColDefs(c))
      try :
         T.header.update('csv',self.__csvname__ if self.__csvname__ != None else '')
      except :
         T.header.update('csv','')
      try :
         T.header.update('pkl',self.__picklefilename__ if self.__picklefilename__ != None else '')
      except :
         T.header.update('pkl','')
      try :
         T.header.update('fits',self.__fitsfilename__ if self.__fitsfilename__ != None else '')
      except :
         T.header.update('fits','')
      if self.__columns_description__ != None :
         if len(self.__columns_description__.keys()) > 0 :
            T.header.add_comment('')
            T.header.add_comment('***************************')
            T.header.add_comment('Description of columns')
            for k in self.__columns_description__.keys() :
               T.header.add_comment(self.help_column(k))
            T.header.add_comment('***************************')
            T.header.add_comment('')
      if self.__dict__.has_key('__info__') :
         for k in self.__info__.keys() :
            name=k if len(k) <=8 else 'HIERARCH '+k
            T.header.update(name,self.__info__[k])
      return T
   def get_from_hdu(self,hdu,capitalizeColumns=False,useTNAME=True) :
      "gets data from an hdu formatted as a fits table"
      for it in range(1,hdu.header['TFIELDS']+1) :
         if useTNAME :
            try :
               n=hdu.header['TNAME%d'%it]
            except :
               n=hdu.header['TTYPE%d'%it]
         else :
               n=hdu.header['TTYPE%d'%it]
         try :
            u=hdu.header['TUNIT%d'%it]
         except :
            if self. isVerbose() :
               print 'TUNIT%d not found, left blanck'%it
            u=''
         f=hdu.header['TFORM%d'%it]
         d=''
         try :
            d=hdu.header['TDSCR%d'%it]
            if d == None : d = ''
         except :
            d=''
         if useTNAME :
            try :
               aaa=hdu.header['TNAME%d'%it]
            except :
               aaa=n
         if capitalizeColumns : n=n.capitalize()
         self.newcolumn(n,hdu.data.field(n),unit=u,shape=f,description=d)
   def has_key(self,key) :
      "true if a column named key exists"
      k=self.keys(asArray=True)
      if len(k) == 0 : return False
      return (k == key).sum() > 0
   def plot(self,*arg,**karg) :
      """ plot one or two arguments
         bt.plot(*arg,**karg)
         returns handles for the plot, xlabel and ylabel
         keywords are directly passed to pyplot.plot
         Example :
            bt.plot('a')
            bt.plot('a',marker='+',linestyle='')
            bt.plot('a','b',marker='+',linestyle='')
         
      """
      from matplotlib import pyplot as plt
      if len(arg) == 0 : 
         raise NameError("Missing fields")
      if len(arg)>2 :
         raise NameError("Too much fields")
      if len(self) == 0 :
         raise NameError("No elements in the table")
      if len(arg)==1 :
         if not self.has_key(arg[0]) :
            raise NameError("Field %s not found"%arg[0])
         h1=plt.plot(self[arg[0]],**karg)
         h2=plt.xlabel('index')
         h3=plt.ylabel(arg[0])
         return h1,h2,h3
      if len(arg)==2 :
         if not self.has_key(arg[0]) :
            raise NameError("Field %s not found"%arg[0])
         if not self.has_key(arg[1]) :
            raise NameError("Field %s not found"%arg[1])
         h1=plt.plot(self[arg[0]],self[arg[1]],**karg)
         h2=plt.xlabel(arg[0])
         h3=plt.ylabel(arg[1])
         return h1,h2,h3
   def append(self,that) :
      """append a base table to the current table
      It is assumed both tables have the same fields
      Metainformations for the in_base_table are lost
      """
      import numpy as np
      # test that the input table that has the same keys of the current table
      for k in self.keys() :
         if (that.keys(asArray=True) == k).sum() == 0 :
            raise NameError("Error: Input table misses keyword '%s' in input table."%k)
            return
      # it is all ok, do concatenation
      for k in self.keys() :
         self[k]=np.concatenate([self[k],that[k]])
   def new_empty(self) :
      """returns an empty itself"""
      out=base_table()
      out.__class__=self.__class__
      return out
   def table2template(self,initialValue=[]) :
      """creates a template from existing table.
         A template is a table with same fields in the current table, but empty.
         initialValue=value of the field (default [])
      """
      out=self.new_empty()
      for k in self.keys() : out.newcolumn(k,initialValue)
      return out
   def subtable(self,*arg,**karg) :
      """returns a table with only the columns specified as arguments"""
      import copy
      if len(arg) == 0 : 
         raise NameError("No column names specified")
      #
      inclusive = karg['exclude']==False if karg.has_key('exclude') else True
      ll=[]
      if inclusive :
         for k in arg :
            if not self.has_key(k) : 
               raise NameError("Column %s does not exists"%k)
            ll.append(k)
      else :
         for k in self.keys() :
            if not k in arg :
               ll.append(k)
      #
      that = self.new_empty()
      for k in self.list_metadata():
         try :
            that.__dict__[k]=copy.deepcopy(self.__dict__[k])
         except :
            if self.isVerbose() :
               print "metadata '%s' does not exists, skipped"%k
      that.clean_column_description()
      for k in ll :
         that[k]=copy.deepcopy(self[k])
         if self.has_name_column_description(k) :
            _name,_description,_unit,_shape = self.unpack_column_description(k)
         else :
            _description='-tbd-'
            _unit='-tbd-'
            _shape='-tbd-'
         that.register_column_description(_name,_description,unit=_unit,shape=_shape)
      that.set_metadata('csvname','')
      that.set_metadata('fitsfilename','')
      that.set_metadata('picklefilename','')
      return that

