def hereDoc2table(csv,fsep=',',comment='#',has_header=True,asDict=True,asStruct=False,header=False,list_fields=False) :
   "converts an here document into a dictionary table"
   import numpy as np
   class _struct : 
      def __init__(self) : 
         pass
   def _column2array(x) :
      try :
         return np.array(x,dtype='int')
      except :
         try:
            return np.array(x,dtype='float')
         except :
            return np.array(x)
   Comment = []
   a=[]
   for line in csv.split('\n') :
      l=line.strip()
      if l != '' and l[0] != comment : 
         a.append(l)
      else :
         Comment.append(l)
   if has_header :
      head = a[0].split(',')
      if header :
         return head
      a=a[1:]
   for i in range(len(a)) : a[i] = a[i].split(',')
   a = np.array(a).transpose()
   if not has_header or not (asDict or asStruct):
      for i in range(len(a)) :
         a[i]=_column2array(a[i])
      return a
   if asDict :
      tb={}
      for i in range(len(head)) :
         if list_fields : print i,head[i]
         tb[head[i]]=_column2array(a[i])
      return tb
   tb=_struct()
   for i in range(len(head)) :
      if list_fields : print i,head[i]
      tb.__dict__[head[i]]=_column2array(a[i])
   return tb
