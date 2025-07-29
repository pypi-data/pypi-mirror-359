from .nexel import Nexel
class Glaze:
    _type=''
    max_depth=0
    curr_depth=0
    keys=0
    is_missing=False
    isayushlist=False
    unique_values=set()
    seen_values=[]
    def if_is_nested(self,data,curr):
        x=0
        z=set()
        z2=set()
        curr=curr
        for y,i in enumerate(data):
            z.add(type(i).__name__)
            if type(i).__name__ not in ['float','str','int']:
                z2.add(y)
                
                if curr>self.max_depth:
                    self.max_depth=curr
            else:
                self.keys+=1
        for c,t in enumerate(z):
            temp=0
            self._type+=f' of {t}'
            if t not in ['str', 'int']:
                if temp==0:
                    for i in z2:
                        self.if_is_nested(data[i],curr+1)
                        temp+=1


            if c<len(z)-1:
                self._type+=' and'


    def __init__(self,data):
        self.data=data
        if type(self.data).__name__=='dict':
            raise TypeError("Unsupported Type Dictionary.Please give data in list and tuple format")
        if type(self.data).__name__=='str':
            self._type='string'
            self.keys+=1
        if type(self.data).__name__=='int':
            self._type='integer'
            self.keys+=1
        if type(self.data).__name__ in ('list','set','tuple'):
            self._type=f'{type(self.data).__name__}'
            for y, i in enumerate(data):
                curr_depth = 1
                if type(i).__name__ not in ['str', 'int','float']:

                    if curr_depth > self.max_depth:
                        self.max_depth = self.curr_depth
                        self.if_is_nested(data,curr_depth+1)
                else:
                    self.keys += 1

            

    def organize_data(self,preserveNesting=True,preserveDuplication=True):
        if not self.max_depth==0:
            if preserveNesting and preserveDuplication:
                self.data=Nexel(self.data)
                self.isayushlist=True
            if not (preserveNesting and preserveDuplication):
                self.get_unique_values_flatten(self.data)
                if len(self.unique_values)==1:
                    self.data=list(self.unique_values)[0]
                else:
                    self.data=tuple(self.unique_values)
            if preserveNesting and not preserveDuplication:
                if self.max_depth==1:
                    self.data = tuple(self.remove_duplication_preserve_nesting(list(self.data)))
                else:
                    self.data=Nexel(self.remove_duplication_preserve_nesting(list(self.data)))
                    self.isayushlist = True
            if preserveNesting==False and preserveDuplication==True:
                data=self.remove_duplication_preserve_nesting(list(self.data))
                del(data)
                self.data=tuple(self.seen_values)
                if len(self.data)==1:
                    self.data=list(self.data)[0]
        return self.data
    @property
    def size(self):
        return self.keys
    def get_unique_values_flatten(self,data):
        for i in data:
            if type(i).__name__ not in ('str','int'):
                self.get_unique_values_flatten(i)
            else:
                self.unique_values.add(i)

    def remove_duplication_preserve_nesting(self,data:list):
        if type(data).__name__ !='list':
            raise TypeError("Only lists can be removed from duplication while preserving nesting")

        for j,i in enumerate(data):
            if type(i).__name__ not in ('str','int'):
                data.pop(j)
                data.insert(j,self.remove_duplication_preserve_nesting(i))
            if i not in self.seen_values:
                self.seen_values.append(i)
            else:
                self.seen_values.append(i)
                data.pop(j)
        return data






    def __repr__(self):
        return self._type


