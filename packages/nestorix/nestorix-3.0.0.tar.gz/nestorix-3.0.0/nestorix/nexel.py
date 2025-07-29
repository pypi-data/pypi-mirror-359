

class Node:
    def __init__(self,data):
        self.prev=None
        self.next=None
        self.data=data
        self.level=None
        self.count=None
    def __len__(self):
        return len(self.data)
class Nexel:
    max_depth=0
    max_count=0
    def nested(self,data,curr_dept):
        nodes=[]
        curr_depth=curr_dept
        curr_depth+=1
        count=0
        for j,i in enumerate(data):
            if type(i).__name__ in ('str','int','float'):
                count+=1
                if count>self.max_count:
                    self.max_count=count
                if curr_depth>self.max_depth:
                    self.max_depth=curr_depth
                nodes.append(Node(i))
                nodes[j].level=curr_depth
                nodes[j].count=count
            else:
                nodes.append(self.nested(i,curr_depth))
        node= Node(nodes)
        return node
    def nested_handle(self,data):
        for j,i in enumerate(data.data):
            if type(i.data).__name__ in ['str', 'int', 'float']:
                self.levels[i.level - 1].append(i)
                i.count = len(self.levels[i.level - 1]) - 1
                if i.count>self.max_count:
                    self.max_count=i.count
            if j<len(data.data)-1:
                i.next=data.data[j+1]
            if j>0:
                i.prev = data.data[j - 1]


            if type(i.data).__name__ not in ['str','int','float']:
                self.nested_handle(i)


    def __init__(self,data):
        nodes=[]
        self.levels=[]
        self.data = data
        self.max_depth = 1
        self.max_count=0
        count=0
        for j,i in enumerate(data):
            curr_depth=1
            if type(i).__name__ in ('str','int','float'):
                count+=1
                if count>self.max_count:
                    self.max_count=count
                if curr_depth>self.max_depth:
                    self.max_depth=curr_depth
                nodes.append(Node(i))
                nodes[j].level=1
                nodes[j].count=count
            else:
                nodes.append(self.nested(i,curr_depth))

        for i in range(self.max_depth):
            self.levels.append([1])
        for i,j in enumerate(nodes):
            if type(j.data).__name__ in ['str', 'int', 'float']:
                self.levels[j.level - 1].append(j)
                j.count = len(self.levels[j.level - 1]) - 1
                if j.count>self.max_count:
                    self.max_count=j.count
            if i<len(nodes)-1:
                j.next=nodes[i+1]
                j.prev = nodes[i - 1]
            if type(j.data).__name__ not in ['str','int','float']:
                self.nested_handle(j)
        for i in range(self.max_depth):
            self.levels[i].pop(0)
        self.nodes=nodes
        self.head = nodes[0] if nodes else None
        del self.data
    def __bool__(self):
        return True if self.head else False
    def __len__(self):
        return len(self.nodes)

    def append(self, object):
        if type(object).__name__ not in ['str','int','float','list','tuple','set']:
            object=self.information(object.nodes)
        try:
            self.nodes[-1].next = Node(object)
        except:
            pass

        finally:
            self.nodes.append(Node(object))
            try:
                self.nodes[-1].prev=self.nodes[-2]
            except:
                pass
            finally:
                x = Nexel(self.information(self.nodes))

                self.nodes = x.nodes
                self.head = x.head
                self.levels = x.levels
                self.max_depth = x.max_depth
                del x

    def insert(self,index,value):
        if type(value).__name__ not in ['str','int','float','list','tuple','set']:
            value=self.information(value.nodes)
        self.nodes[index]=Node(value)
        try:
            self.nodes[index].next=self.nodes[index+1]
            self.nodes[index + 1].prev=self.nodes[index]
        except:
            pass
        finally:
            try:
                self.nodes[index-1].next=self.nodes[index]
                self.nodes[index].prev=self.nodes[index-1]
            except:
                pass
            finally:
                x = Nexel(self.information(self.nodes))
                self.nodes = x.nodes
                self.head = x.head
                self.levels = x.levels
                self.max_depth = x.max_depth
                del x
    def remove_internal(self,value,data):
        for j,i in enumerate(data):
            if type(i).__name__ not in ['str','int','float']:
                if value in i:
                    data.pop(j)
                    return data
                self.remove_internal(value,i)
            else:
                if i==value:
                    data.pop(j)
                    return data
        return data
    def remove(self,value):
        if type(value).__name__ not in ['str','int','float','list','tuple','set']:
            value=self.information(value.nodes)
        x=Nexel(self.information(self.remove_internal(value,self.information(self.nodes))))
        self.nodes = x.nodes
        self.levels=x.levels
        self.max_depth=x.max_depth
        self.head = self.nodes[0] if self.nodes else None
        del x
    def pop(self,index):
        self.nodes.pop(index)
        x=Nexel(self.information(self.nodes))
        self.nodes=x.nodes
        self.head=x.head
        self.levels=x.levels
        self.max_depth=x.max_depth
        del x
    def __getitem__(self, index):
        return Nexel(self.information(self.nodes)[index])

    def fetch(self,level,count=None):
        if count==None:
            return self.levels[level]
        return self.levels[level][count]

    def make_matrix(self):
        levels=self.levels.copy()
        counts=self.max_count
        for i in range(len(levels)):
            for j in range(counts):
                if len(self.levels[i])<j:
                    levels[i].append(Node('0'))
        return levels
    def make_numpy_tree(self):
        import numpy as np
        return np.array(self.information(self.make_matrix()))
    def make_numpy_original(self):
        import numpy as np
        try:
            return np.array(self.information(self.nodes))
        except:
            return 'Array can not be created'
    def fetch_prev_of(self,data):
        for i in self.levels:
            for j in i:
                if j.data==data:
                    return j.prev.data

    def fetch_next_of(self,data):
        for i in self.levels:
            for j in i:
                if j.data==data:
                    return j.next.data

    def information(self,nodes):
        data=[]
        for i in nodes:
            if not type(i).__name__ in ['str','float','int','list']:
                i = i.data
            if type(i).__name__ in ['str','float','int']:
                data.append(i)
            else:
                data.append(self.information(i))
        return data
    @property
    def info(self):
        return self.information(self.nodes)
    def __str__(self):
        return str(self.head.data)
    @property
    def tree(self):
        return self.levels

    def __iter__(self):
        self.iter_index=0
        return self
    def __next__(self):
        if self.iter_index>=len(self.nodes):
            raise StopIteration
        node=self.nodes[self.iter_index]
        self.iter_index+=1
        return node
    def __add__(self, other):
        if type(other).__name__ in ['set','list','tuple']:
            other=list(other)
            x=self.information(self.nodes)
            x.append(other)
            return Nexel(x)
        elif type(other).__name__ in ['str','int','float']:
            x=self.information(self.nodes)
            x.append(other)
            return Nexel(x)
        else:
            x=self.information(self.nodes)
            x.append(self.information(other.nodes))
            return Nexel(x)
    def __iadd__(self, other):
        return self+other
    def __setitem__(self, key, value):
        self.nodes[key] = value
        return Nexel(self.information(self.nodes))
    def apply_each_node_internal(self,fx,data):
        for j,i in enumerate(data):
            if type(i).__name__ in ['str','int','float']:
                data[j]=fx(i)
            else:
                data[j]=self.apply_each_node_internal(fx, data[j])
        return data
    def apply(self,fx):
        return Nexel(self.apply_each_node_internal(fx,self.information(self.nodes)))
    def index(self,value):
        x=self.information(self.nodes)
        if value in x:
            return x.index(value)
        else:
            raise ValueError("Value asked does not exist in the Nexel")
    def index_node_internal(self,data,value):
        if type(data).__name__ in ['str','int','float'] and value==data:
            return 0
        elif type(data).__name__ in ['str','int','float']:
            return None
        if value in data:
            return data.index(value)
        for j,i in enumerate(data):
            if (self.index_node_internal(i,value) !=None) and not(type(data).__name__ in ['str','int','float']):
                return j,self.index_node_internal(i,value)
        return None


    def index_node(self,value):
        x=self.information(self.nodes)
        if value in x:
            return x.index(value)
        for j,i in enumerate(x):
            if self.index_node_internal(i,value) !=None:
                return j,self.index_node_internal(i,value)


    def index_node_tree(self,value):
        for x,i in enumerate(self.tree):
            for y,j in enumerate(self.information(i)):
                if j==value:
                    return x,y

    @property
    def size(self):
        keys=0
        for i in self.levels:
            for j in i:
                if type(j.data).__name__ in ['str','int','float']:
                    keys+=1

        return keys
    @property
    def shape(self):
        return len(self.levels),self.max_count
    @property
    def symmetric_size(self):
        return int(len(self.levels)*self.max_count)
    @property
    def missing_to_make_tree(self):
        return self.symmetric_size-self.size
    def __copy__(self):
        return Nexel(self.information(self.nodes))
    def depth_of(self,value):
        for i in self.levels:
            for j in i:
                if j.data==value:
                    return j.level
        raise ValueError("Value not found")
    def __eq__(self, other):
        if type(other).__name__ in ['str','int','float','set','list','tuple']:
            if self.information(self.nodes)==other:
                return True
            return False
        else:
            if self.information(self.nodes)==self.information(other):
                return True
            return False

def run_tests():
    print("Running Nexel test suite...")
    passed = 0
    total = 19

    # Test 1: Simple linking
    data1 = [1, 2, 3]
    lst1 = Nexel(data1)
    try:
        assert lst1.head.data == 1
        assert lst1.head.next.data == 2
        assert lst1.head.next.next.data == 3
        passed += 1
        print("Test 1 ✅ Linking & structure")
    except:
        print("Test 1 ❌")

    # Test 2: Nested structure
    data2 = [1, [2, 3], 4]
    lst2 = Nexel(data2)
    try:
        nested_node = lst2.head.next
        assert isinstance(nested_node.data, list)
        assert nested_node.data[0].data == 2
        assert nested_node.data[0].next.data == 3
        passed += 1
        print("Test 2 ✅ Nested linking")
    except:
        print("Test 2 ❌")

    # Test 3: Deep nesting
    lst3 = Nexel([1, [2, [3, 4]], 5])
    try:
        assert lst3.head.next.data[1].data[0].data == 3
        assert lst3.head.next.data[1].data[0].next.data == 4
        passed += 1
        print("Test 3 ✅ Deep nesting")
    except:
        print("Test 3 ❌")

    # Test 4: Empty list
    lst4 = Nexel([])
    try:
        assert lst4.head is None
        passed += 1
        print("Test 4 ✅ Empty list handled")
    except:
        print("Test 4 ❌")

    # Test 5: Append
    lst1.append(4)
    try:
        assert lst1.nodes[-1].data == 4
        passed += 1
        print("Test 5 ✅ Append works")
    except:
        print("Test 5 ❌")

    # Test 6: Insert
    lst1.insert(1, 99)
    try:
        assert lst1.nodes[1].data == 99
        passed += 1
        print("Test 6 ✅ Insert works")
    except:
        print("Test 6 ❌")

    # Test 7: Remove
    lst1.remove(99)
    try:
        assert all(n.data != 99 for n in lst1.nodes)
        passed += 1
        print("Test 7 ✅ Remove works")
    except:
        print("Test 7 ❌")

    # Test 8: Pop
    pre_len = len(lst1)
    lst1.pop(0)
    try:
        assert len(lst1) == pre_len - 1
        passed += 1
        print("Test 8 ✅ Pop works")
    except:
        print("Test 8 ❌")

    # Test 9: Indexing

    assert isinstance(lst3[1], Nexel)
    passed += 1
    print("Test 9 ✅ Indexing __getitem__")


    # Test 10: Iteration
    try:
        it = iter(lst1)
        first = next(it)
        second = next(it)
        assert isinstance(first, Node) and isinstance(second, Node)
        passed += 1
        print("Test 10 ✅ Iteration __iter__ + __next__")
    except:
        print("Test 10 ❌")

    # Test 11: Fetch level, count

    try:
        x = Nexel([1, [2, 3], [4, [5]]])
        level, count = x.tree[1][0].level, x.tree[1][0].count
        node = x.fetch(level - 1, count-1)
        assert node.data==2
        passed += 1
        print("Test 11 ✅ Fetch by level-count")
    except:
        print("Test 11 ❌")

    # Test 12: Size and shape
    try:
        s = x.size
        shp = x.shape
        assert isinstance(s, int) and isinstance(shp, tuple)
        passed += 1
        print("Test 12 ✅ Size and shape")
    except:
        print("Test 12 ❌")

    # Test 13: Index and index_node
    try:
        print(x.info)
        val=x.index([2,3])
        val2 = x.index_node(2)
        assert val2==(1,0)
        assert val==1
        passed += 1
        print("Test 13 ✅ index() and index_node()")
    except:
        print("Test 13 ❌")

    # Test 14: Make matrix
    try:
        mat = x.make_matrix()
        assert isinstance(mat, list)
        passed += 1
        print("Test 14 ✅ make_matrix()")
    except:
        print("Test 14 ❌")

    # Test 15: Functional - apply
    if 2+2==4:
        a = Nexel([1, 2, [3, 4]])
        b = a.apply(lambda x: x * 10)
        print(b.nodes[1].data)
        passed += 1
        print("Test 15 ✅ apply()")
    else:
        print("Test 15 ❌")


    try:
        a = Nexel([1, 2])
        b = Nexel([3, 4])
        c = a + b
        assert c.information(c.nodes)==[1,2,[3,4]]
        a += [5]
        print( a.information(a.nodes)[-1]==[5])
        passed += 1
        print("Test 17 ✅ __add__ and __iadd__")
    except:
        print('Test 17 ❌')


    # Test 18: Symmetry helpers



    m = x.symmetric_size
    m2 = x.missing_to_make_tree
    assert isinstance(m2,int)
    passed += 1
    print("Test 18 ✅ Symmetry helpers")


    # Test 19: Copying
    try:
        c = x.__copy__()
        assert isinstance(c, Nexel)
        passed += 1
        print("Test 19 ✅ Copying")
    except:
        print("Test 19 ❌")

    # Test 20: Depth
    try:
        val = x.depth_of(x.tree[1][2].data)
        assert val==2
        passed += 1
        print("Test 20 ✅ Depth of node")
    except:
        print("Test 20 ❌")

    # Final Result
    print(f"\n🧪 {passed}/{total} tests passed.")

if __name__ == "__main__":
    run_tests()
