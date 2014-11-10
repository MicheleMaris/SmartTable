__DESCRIPTION__="""Library to help to convert a table written as a dictionary into a fits table
and back
"""
def Description(Dict,names=None,unit_value='') :
   "Try to compile a description from the dictionary"
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
   fmtT={'bool':'L','int16':'I','int32':'J','int64':'K','string':'A','float32':'E','float64':'D','complex128':'M'}
   count=0
   for ttype in lstn :
      if type(Dict[ttype]) == type({}) :
         print "%s is a dictionary, skipped"
      else :
         try :
            fmt = fmtT[Dict[ttype].dtype.name]
         except :
            if np.array(Dict[ttype]).dtype.name[0:3]=='str':
               fmt='A'
            else :
               print "Format %s not found"%np.array(Dict[ttype]).dtype.name
               fmt=''
         if fmt!='' :
            size=''
            if fmt == 'A':
               #dt = np.array(Dict[ttype][0]).dtype
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

def DescriptionV2(Dict,names=None,unit_value='',verbose=False) :
   "Try to compile a description from the dictionary"
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

def Table(Dict,description=None,table_name='') :
   "Convert a dictionary (and optionally a description) into a fits table"
   import pyfits
   import numpy as np
   if description == None :
      _description=Description(Dict)
   else :
      if type(description) != type({}) :
         _description=Description(Dict,names=description)
      else :
         _description = description
   c=[]
   for k in range(len(_description['name'])) :
      name = _description['name'][k]
      c.append(pyfits.Column(array=Dict[name],name=name,format=_description['format'][k],unit=_description['unit'][k]))
   if len(c) > 0 :
      coldefs=pyfits.ColDefs(c)
      tbhdu=pyfits.new_table(coldefs)
      if type(table_name) == type('') :
         if len(table_name.strip()) > 0 :
            tbhdu.name=table_name.strip()
      return tbhdu
   return None

#def Header2Dict(FitsHeader) : 
   #"convert an header into a dictionary"
   #d = {}
   #for k in str(FitsHeader).split("\n") :
      #if k[0:7].lower() != 'comment' :
         #n,bc=k.split('=')
         #n=n.strip().lower()
         #d[n]=bc.split('//')[0].strip()
   #return d
      
def Dict(FitsTable) :
   "convert a fits table into a dictionary"
   import pyfits
   import numpy as np
   import copy
   d = {}
   for ii in range(len(FitsTable.get_coldefs())) :
      k=FitsTable.get_coldefs()[ii].name
      d[k]=copy.deepcopy(FitsTable.data.field(ii))
   return d

def KeyDict(FitsTable) :
   "convert the keywords of a fits table into a dictionary"
   import pyfits
   import numpy as np
   import copy
   d = {}
   for k in FitsTable.header.keys() :
      d[k]=copy.deepcopy(FitsTable.header[k])
   return d

class TableInfos :
   """ A table Infos is a way to convert a set of long keywords containing scalars into a fits table
      this is used to overcome problems with fits keywords
   """
   def __init__(self,info='info',text='text',comment='comment') :
      """keywords: 
      info=name of the info colum, 
      text=name of the text column
      comment=name of the comment column
      """
      self.info=[]
      self.text=[]
      self.comment=[]
      self._names={'info':info,'text':text,'comment':comment}
      self._columns=[]
      self._n=[1,1,1]
      for k in ['info','text','comment'] :
         self._columns.append(self._names[k])
   def keys(self) :
      return self._columns
   def toTabDict(self) :
      """ converts to a table dictionary """
      import numpy
      l={}
      l[self._names['info']]=numpy.array(self.info)
      l[self._names['text']]=numpy.array(self.text)
      l[self._names['comment']]=numpy.array(self.comment)
      return l
   def todict(self) :
      """ converts to a dictionary of keywords"""
      l={}
      for k in range(len(self)) :
         l[self.info[k]] = self.text[k]
      return l
   def __len__(self) :
      return len(self.info)
   def __str__(self) :
      fmt=''
      for k in self._n :
         fmt += '%'+str(k)+'s '
      l = []
      l.append(fmt % (self._names['info'],self._names['text'],self._names['comment']))
      for k in range(len(self)) :
         l.append(fmt % (self.info[k],self.text[k],self.comment[k]))
      return "\n".join(l)
   def __call__(self,*arg) :
      import numpy as np
      if len(arg) < 1 :
         return
      try :
         idx=np.where(self.info==arg[0])[0]
         if len(arg[0]) > self._n[0] :
            self._n[0] = len(arg[0])
      except :
         idx = []
      if len(idx) == 0 :
         self.info.append(arg[0])
         if len(arg[0]) > self._n[0] :
            self._n[0] = len(arg[0])
         try :
            self.text.append(arg[1])
            if len(arg[1]) > self._n[1] :
               self._n[1] = len(arg[1])
         except :
            self.text.append('')
         try :
            self.comment.append(arg[2])
            if len(arg[2]) > self._n[2] :
               self._n[2] = len(arg[2])
         except :
            self.comment.append('')
      else :
         self.info[idx] = arg[0]
         if len(arg[0]) > self._n[0] :
            self._n[0] = len(arg[0])
         try :
            self.text[idx] = arg[1]
            if len(arg[1]) > self._n[1] :
               self._n[1] = len(arg[1])
         except :
            self.text[idx] = ''
         try :
            self.comment[idx] = arg[2]
            if len(arg[2]) > self._n[2] :
               self._n[2] = len(arg[2])
         except :
            self.comment[idx] = ''
   def tofits(self,*arg) :
      """convert to a fits hdu"""
      import pyfits
      import numpy as np
      c=[]
      a=str(self._n[0])+'A'
      c.append(pyfits.Column(array=np.array(self.info),name=self._names['info'],format=a))
      a=str(self._n[1])+'A'
      c.append(pyfits.Column(array=np.array(self.text),name=self._names['text'],format=a))
      a=str(self._n[2])+'A'
      c.append(pyfits.Column(array=np.array(self.comment),name=self._names['comment'],format=a))
      coldefs=pyfits.ColDefs(c)
      tbhdu=pyfits.new_table(coldefs)
      try :
         tn=arg[0].strip()
      except :
         tn=''
      tbhdu.name=tn
      return tbhdu


if __name__=="__main__" :
   from numpy import array
   example={'column':[1,2,3],'x':[3.4,6.5,2.1],'y':[True,False,True],'h':['p1','g',''],'r':[long(10),long(-20),long(100)]}
   
   for k in example.keys() : example[k]=array(example[k])
   
   fitsTable = Table(example,['column','x','y','h','r'])
   
   