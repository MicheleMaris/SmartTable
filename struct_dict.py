class struct_dict : 
   "a subclass to manage a structure"
   def __init__(self,*arg,**keys) : 
      import numpy as np
      if len(arg)==0 : return
      names=arg[0]
      if names==None : return 
      try :
	 default_value=keys['default_value']
      except :
	 default_value=None
      if type(names)==type({})  : self.from_dict(names)
      if type(names)==type('')  : self.__dict__[names]=default_value
      try :
         if type(default_value) == type([]) or type(default_value) == type(np.array([])):
            count = 0
            for k in names : 
               self.__dict__[k]=default_value[count]
               count+=1
         else :
            for k in names : self.__dict__[k]=default_value
      except :
         self.__dict__[k]=None
   def argsearch(self,*arg,**karg) :
      import numpy as np
      arg=np.ones(len(self))
      for k in karg.keys() :
         arg*=self.__dict__[k]==karg[k]
      return np.where(arg)[0]
   def select(self,*arg,**karg) :
      import numpy as np
      arg=np.ones(len(self.__dict__[self.keys()[0]]))
      for k in karg.keys() :
         arg*=self.__dict__[k]==karg[k]
      idx = np.where(arg)[0]
      if len(idx) == 0 : return 
      out=_struct(None)
      for k in self.keys() :
         out.__dict__[k]=self.__dict__[k][idx]
      return out
   def keys(self) : return self.__dict__.keys()
   def __setitem__(self,*arg) :
      if len(arg) == 0 : return
      if len(arg) == 1 :
	 self.__dict__[arg[0]]=None
      elif len(arg) == 2 :
	 self.__dict__[arg[0]]=arg[1]
      else :
	 self.__dict__[arg[0]]=arg[1:]
   def __getitem__(self,key) :
      return self.__dict__[key]
   def __len__(self) : return len(self.__dict__.keys())
   def todict(self) : return self.__dict__
   def from_dict(self,dtc) : self.__dict__=dtc
   def copy(self) : 
      import copy
      return copy.deepcopy(self)
