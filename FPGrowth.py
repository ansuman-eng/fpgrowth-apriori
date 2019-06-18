#!/usr/bin/env python
# coding: utf-8

# In[255]:


import pandas as pd
import numpy as np
from copy import deepcopy
import sys
sys.setrecursionlimit(10000)  # default is 1000 in my installation


# In[260]:


######################STARTING DATA PREPROCESSING############################
print("Loading and Preprocessing Groceries dataset")
with open('groceries.csv') as f:
    lis = [line.split(',')for line in f]
    for transaction in lis:
        len_trans = len(transaction)
        transaction[len_trans-1] = transaction[len_trans-1].split('\n')[0]
    lis = np.array(lis)
    print("Total number of transactions in the Groceries dataset: ",lis.shape[0])
    print("")


# In[261]:


minsup_percent = input("Please enter minsup as a % of size of transaction list ")
minsup = int(float(minsup_percent)/100.0 * len(lis))


# In[262]:


print("Minsup as a number is ",minsup)
print("")


# In[263]:


conf = float(input("Please enter conf as a % "))
print("")


# In[264]:


max_length=-1
for transaction in lis:
    if(len(transaction)>max_length):
        max_length=len(transaction)
print("Max length of any transaction is : ", max_length)
print("")


# In[265]:


distinct_items = set()


# In[266]:


print("Counting support for one item sets")
print("")
support_count = {}
for transaction in lis:
    for item in transaction:
        if item not in distinct_items:
            distinct_items.add(item)
            support_count[item] = 1
        else:
            support_count[item]+=1


# In[267]:


item_support_pairs=[]
for key,val in support_count.items():
    item_support_pairs.append((val,key))
item_support_pairs.sort()


# In[268]:


item_support_pairs = item_support_pairs[::-1]


# In[269]:


print("Encoding and reverse encoding items acc. to frequency")
print("")
encode = {}
reverse_encode = {}
for i in range(len(item_support_pairs)):
    encode[item_support_pairs[i][1]] = i
    reverse_encode[i] = item_support_pairs[i][1]


# In[270]:


print("Total number of distinct items ",len(distinct_items))
print("")


# In[271]:


processed_lis=[]
for trans_index in range(len(lis)):
    trans_temp=[]
    for item_index in range(len(lis[trans_index])):
        trans_temp.append(encode[lis[trans_index][item_index]])
    trans_temp.sort()
    processed_lis.append(trans_temp)


# In[272]:


#PRINT TRANSACTIONS AS ENCODED
print("A sample of encoded transactions")
for transaction in processed_lis[:10]:
    print(transaction)
print("")
print("")


# In[273]:


#Tree node definition
class Node:
    def __init__(self,code):
        self.code = code
        self.count = 0
        self.children = []
        self.next_code = None
        self.parent = None


# In[274]:


#Tree definition
class FPTree:
    def __init__(self):
        self.existing_items=[]
        self.root = Node(-1)
        self.last_active_node={}
        self.first_active_node={}
        
    #Insert a transaction into tree   
    def insert(self,transaction):
        temp = self.root
        parent = None
        for item in transaction:
            found_item = 0
            for idx in range(len(temp.children)):
                if(temp.children[idx].code == item):
                    found_item=1
                    break
            if(found_item==1):
                temp.children[idx].count+=1
                temp = temp.children[idx]
                
            else:
                child_node = Node(item)
                child_node.count = 1
                child_node.parent = temp
                temp.children.append(child_node)
                temp = child_node
                if(item in self.existing_items):
                    self.last_active_node[item].next_code = child_node
                    self.last_active_node[item] = child_node
                else:
                    self.existing_items.append(item)
                    self.first_active_node[item] = child_node
                    self.last_active_node[item] = child_node
                    
    #Level order traversal for debugging purposes
    def level_traversal(self):
        level=0
        queue=[]
        queue.append(self.root)
        while(len(queue)>0):
            l = len(queue)
            print('Level :', level)
            while(l!=0):
                node = queue.pop(0)
                for c in node.children:
                    queue.append(c)
                print('Item code:', node.code)
                print('Item count:', node.count)
                l-=1
            print("###########################")
            level+=1
            


# In[275]:


print("Inserting all transactions into tree")
print("")
Tree = FPTree()
for transaction in processed_lis:
    Tree.insert(transaction)


# In[276]:


#Tree.level_traversal()


# In[277]:


def make_prefix_path(Tree,code):
    #Copying input tree with specific nodes for prefix tree
    left_anchor = Tree.first_active_node[code]
    right_anchor = Tree.last_active_node[code]  
    Tree1 = FPTree()
    old_to_new={}
    old_to_new[Tree.root]=Tree1.root
    count_code=0
    temp = left_anchor
    while(temp!=None):
        temp1=temp
        while(temp1!=None):
            #print((temp1.code,temp1.count))

            if(temp1 not in old_to_new.keys()):
                #print("NOT FOUND SO ADDING", temp1.code,temp1.count)
                old_to_new[temp1]= Node(temp1.code)
                old_to_new[temp1].count = temp1.count
            for c in temp1.children:
                if(c in old_to_new.keys() and (old_to_new[c] not in old_to_new[temp1].children)):
                    #print("ADDING",c.code,c.count,"TO THE CHILDREN OF",old_to_new[temp1].code,old_to_new[temp1].count)
                    old_to_new[temp1].children.append(old_to_new[c])
                    old_to_new[c].parent = old_to_new[temp1]                
            temp1=temp1.parent
        #print("New path")
        count_code+=temp.count
        temp=temp.next_code

    ###################################################
    ###################################################
    
    #Restoring the linked list of target item
    Tree1.first_active_node[code] = old_to_new[Tree.first_active_node[code]]
    Tree1.last_active_node[code]= old_to_new[Tree.last_active_node[code]]

    temp = Tree.first_active_node[code]
    while(temp!=Tree.last_active_node[code]):
        old_to_new[temp].next_code = old_to_new[temp.next_code]
        temp=temp.next_code
    left_anchor = Tree1.first_active_node[code]
    right_anchor = Tree1.last_active_node[code]  
    
    temp=left_anchor
    while(temp!=None):
        #print(temp.code,temp.count)
        temp=temp.next_code
    ###################################################
    #print("NODE POINTER DICTIONARY")
    #print(Tree1.first_active_node)
    #print(Tree1.last_active_node)
    
    ###################################################
    #Debugging code
    left_anchor = Tree1.first_active_node[code]
    right_anchor = Tree1.first_active_node[code]    
    #print("DEBUGGING")
    temp = left_anchor
    count_code=0
    while(temp!=None):
        temp1=temp
        while(temp1!=Tree1.root):
            #print((temp1.code,temp1.count))
            temp1=temp1.parent
        #print("New path")
        count_code+=temp.count
        temp=temp.next_code
    #print(count_code)
    
    ###################################################
    
    #print("REMOVING CORRUPTED POINTERS")    
    #REMOVING CORRUPTED POINTERS
    for key in Tree1.first_active_node.keys():
        if(key!=code):
            Tree1.first_active_node[key]=None

    for key in Tree1.last_active_node.keys():
        if(key!=code):
            Tree1.last_active_node[key]=None
    #print(Tree1.first_active_node)        
    #print(Tree1.last_active_node)
    
    ###################################################
    #UPDATING NEXT_CODE POINTERS FOR OTHER ITEMS
    level=0
    queue=[]
    queue.append(Tree1.root)
    while(len(queue)>0):
        l = len(queue)
        while(l!=0):
            node = queue.pop(0)
            for c in node.children:
                queue.append(c)
            if(node.code!=code):
                if(node.code not in Tree1.first_active_node.keys() or Tree1.first_active_node[node.code]==None):
                    Tree1.first_active_node[node.code]=node
                    Tree1.last_active_node[node.code]=node
                else:
                    Tree1.last_active_node[node.code].next_code=node
                    Tree1.last_active_node[node.code]=node
            l-=1
        #print("###########################")
        level+=1

            
    return (Tree1,count_code)


# In[278]:


def prefix_to_cond(Tree1, code):
    
    left_anchor = Tree1.first_active_node[code]
    right_anchor = Tree1.first_active_node[code]  
    
   # print("MAKING NODES ZERO")
    temp = left_anchor
    count_code = 0
    while(temp!=None):
        temp1=temp
        while(temp1!=Tree1.root):
            if(temp1!=temp):
                temp1.count=0
            temp1=temp1.parent
        count_code+=temp.count
        temp=temp.next_code
    #print(count_code)
    
    #####################################################
    
    #print("MAKE COUNTS PROPER BY PROPOAGATING UPWARDS")
    temp = left_anchor
    count_code = 0
    while(temp!=None):
        temp1=temp
        c=temp.count
        while(temp1!=Tree1.root):
            if(temp1!=temp):
                temp1.count+=c
            temp1=temp1.parent
        count_code+=temp.count
        temp=temp.next_code
    #print(count_code)
    
    ######################################################
    
   # print("ANALYSING THE LESS FREQUENT NODES")
    #REMOVE LESS FREQUENT
    count_conditional={}
    for key in Tree1.first_active_node.keys():
        left = Tree1.first_active_node[key]
        count_key=0
        while(left!=None):
            count_key+=left.count
            left=left.next_code
        #print(count_key)
        count_conditional[key]=count_key    
    #print(count_conditional)
    to_be_removed=[]
    for key in count_conditional.keys():
        if(count_conditional[key]<minsup):
            to_be_removed.append(key)
    #print("To be removed", to_be_removed)
    
    ######################################################
    
    #print("ACTUALLY REMOVING THE LESS FREQUENT ONES")
    
    temp = left_anchor
    count_code = 0
    while(temp!=None):
        temp1=temp
        while(temp1!=Tree1.root):      
            if(temp1.code in to_be_removed and temp1.code!=code):            
                for c in temp1.children:
                    c.parent=temp1.parent

                p=temp1.parent

                p.children.remove(temp1)
                for c in temp1.children:
                    p.children.append(c)

            temp1=temp1.parent

        count_code+=temp.count
        temp=temp.next_code
    #print(count_code)
    
    ######################################################
        
    #print("REMOVING CODE NODES")
    #REMOVING CODE NODES
    temp = left_anchor
    count_code=0
    while(temp!=None):
        temp.parent.children.remove(temp)
        temp=temp.next_code
    
    return Tree1


# In[279]:


#RETURN WHICH NODES ARE ACTUALLY IN THE TREE
def find_nodes(Tree):
    distinct={}
    level=0
    queue=[]
    queue.append(Tree.root)
    while(len(queue)>0):
        l = len(queue)
        #print('Level :', level)
        while(l!=0):
            node = queue.pop(0)
            for c in node.children:
                queue.append(c)
                
            if(node.code not in distinct):
                distinct[node.code]=node.count
            else:
                distinct[node.code]+=node.count
            
            l-=1
        #print("###########################")
        level+=1
    return distinct


# In[280]:


frequent_itemsets=[]
#THE RECURSIVE FP GROWTH ALGORITHM
def recurse(Tree, suffix):
    #FIRST FIND WHICH NODES ARE ACTUALLY IN THE TREE
    #print(suffix)
    nodes = find_nodes(Tree)
    #print(nodes)        
    
    if(len(nodes.keys())==1):
        return
    for code in nodes.keys():
        if(nodes[code]>=minsup and code!=-1):
            #print(suffix+[code])
            frequent_itemsets.append((suffix+[code],nodes[code]))
            #print("MAKING PREFIX PATH FOR",suffix+[code])
            prefix_Tree, count_code = make_prefix_path(Tree,code)
            cond_Tree = prefix_to_cond(prefix_Tree,code)
            recurse(cond_Tree,suffix+[code])
        else:
            pass
            #No need to recurse further


# In[281]:


print("Running the FP Growth Algorithm")
print("")
recurse(Tree,[])


# In[282]:


print("Number of frequent itemsets is : ",len(frequent_itemsets))
print("")


# In[283]:


item_to_freq={}
for f in frequent_itemsets:
    #print(tuple(f[0]),f[1])
    #print("[", end=" ")
    for item in f[0]:
        print(reverse_encode[item],",", end=" ")
    #print("]", end=" ")
    print("(",f[1],")")
    item_to_freq[tuple(f[0])]=f[1]
#print(len(frequent_itemsets))


# In[284]:


####CLOSED FREQUENT ITEMSETS
closed_frequent=[]
for pair in frequent_itemsets:
    itemset=pair[0]
    supsets_with_equal_f=0
    #CHECK ITEMSET's FREQUENCY
    itemset_frequency=pair[1]
    
    for supset in frequent_itemsets:
        if(len(supset[0])>len(itemset)):
            all_items_in=1
            for item in itemset:
                if(item not in supset[0]):
                    all_items_in=0
                    break
             
            #IT IS A SUPERSET
            if(all_items_in==1):
                superset_frequency=supset[1]
                if(superset_frequency==itemset_frequency):
                    supsets_with_equal_f+=1
                    
    if(supsets_with_equal_f==0):
        closed_frequent.append(pair)
                
#print(len(closed_frequent))
print("CLOSED FREQUENT ITEMSETS")  
for f in closed_frequent:
    #print(tuple(f[0]),f[1])
    #print("[", end=" ")
    for item in f[0]:
        print(reverse_encode[item],",", end=" ")
    #print("]", end=" ")
    print("(",f[1],")")
    item_to_freq[tuple(f[0])]=f[1]


# In[285]:


####MAXIMAL FREQUENT ITEMSETS
maximal_frequent=[]
for pair in frequent_itemsets:
    itemset=pair[0]
    #print(itemset, end=" ")
    supset_true=0
    
    for supset in frequent_itemsets:
        if(len(supset[0])>len(itemset)):
            all_items_in=1
            for item in itemset:
                if(item not in supset[0]):
                    all_items_in=0
                    break
            if(all_items_in==1):
                supset_true=1
                break

    if(supset_true==0):
        maximal_frequent.append(pair)
        #print("Maximal")
        
print(len(maximal_frequent))
print("MAXIMAL FREQUENT ITEMSETS")  
for f in maximal_frequent:
    #print(tuple(f[0]),f[1])
    #print("[", end=" ")
    for item in f[0]:
        print(reverse_encode[item],",", end=" ")
    #print("]", end=" ")
    print("(",f[1],")")
    item_to_freq[tuple(f[0])]=f[1]


# In[286]:


'''
Say conf value is 20%
Which means freq(11,6,1)/freq(LHS) has to be greater than 20%
Which means freq(LHS) is less than or equal to 5*freq(11,6,1)
'''
'''
We write a recursive function to find out candidate LHSs'''

#Threshold is the max support that a LHS may have
#itemset is considered LHS. If satisfied we will recurse with its subsets
#selected_LHS will contain all subsets which can be on LHS at the end
def LHS(itemset,threshold,selected_LHS):
    #print(itemset)
    #print(item_to_freq[itemset])
    #print(len(itemset))
    if(item_to_freq[itemset]>threshold):
        #print("Won't consider any further subsets")
        return
    #Reaches here means the itemset in consideration can be LHS
    if(itemset not in selected_LHS):
        selected_LHS.append(itemset)
        #print("Added the itemset into considered LHS")
        if(len(itemset)==1):
            #print("Returning back")
            return
        else:            
            for item in list(itemset):
                itemlist = list(itemset)
                itemlist.remove(item)
                #print(tuple(itemlist))
                #print("GOING INTO", tuple(itemlist))
                LHS(tuple(itemlist),threshold,selected_LHS)
   
    return


# In[287]:


allrules=set()
count=0
for f in frequent_itemsets:
    if(len(f[0])==1):
        #Can'tformrules
        continue
    itemset = tuple(f[0])
    threshold = (100.0/conf)*item_to_freq[itemset]
    #print(threshold)
    selected_LHS=[]
    LHS(itemset,threshold,selected_LHS)
    #DONT WANT ENTIRE ITEMSET ON THE LHS
    selected_LHS.remove(itemset)
    
    #print("Itemset is", itemset)
    #print("The LHS can be", selected_LHS)
    
    
    #print("Rules are")
    if(len(selected_LHS)==0):
        #print("Can't form rules")
        #CAN'T FORM RULES
        continue
    
    for lhs in selected_LHS:
        rhs=list()
        for item in itemset:
            if(item not in lhs):
                rhs.append(item)
        rhs=tuple(rhs)
        
        for item in lhs:
            print(reverse_encode[item],",", end=" ")
        print("(",item_to_freq[lhs],")",end=" ")
        
        print("----->",end=" ")
        
        for item in rhs:
            print(reverse_encode[item],",", end=" ")
        print("(",item_to_freq[rhs],")",end=" ")
        print("- conf ",item_to_freq[itemset]/item_to_freq[lhs])
        if(item_to_freq[itemset]/item_to_freq[lhs]<0.3):
            count+=1
        allrules.add((itemset,lhs,rhs))
    
print(count)
    

    


# In[288]:


nonredundant=set()
for f in closed_frequent:
    if(len(f[0])==1):
        #Can'tformrules
        continue
    itemset = tuple(f[0])
    threshold = (100.0/conf)*item_to_freq[itemset]
    #print(threshold)
    selected_LHS=[]
    LHS(itemset,threshold,selected_LHS)
    #DONT WANT ENTIRE ITEMSET ON THE LHS
    selected_LHS.remove(itemset)
    
    #print("Itemset is", itemset)
    #print("The LHS can be", selected_LHS)
    
    
    #print("Rules are")
    if(len(selected_LHS)==0):
        #print("Can't form rules")
        #CAN'T FORM RULES
        continue
    
    for lhs in selected_LHS:
        rhs=list()
        for item in itemset:
            if(item not in lhs):
                rhs.append(item)
        rhs=tuple(rhs)
        
        for item in lhs:
            print(reverse_encode[item],",", end=" ")
        print("(",item_to_freq[lhs],")",end=" ")
        
        print("----->",end=" ")
        
        for item in rhs:
            print(reverse_encode[item],",", end=" ")
        print("(",item_to_freq[rhs],")",end=" ")
        print("- conf ",item_to_freq[itemset]/item_to_freq[lhs])
        nonredundant.add((itemset,lhs,rhs))
       
        
        


# In[289]:


print(len(nonredundant))
print(len(allrules))
print(len(allrules-nonredundant))


# In[290]:


redundant = allrules - nonredundant
for rule in redundant:
    lhs=rule[1]
    rhs=rule[2]
    itemset=rule[0]

    for item in lhs:
        
        print(reverse_encode[item],",", end=" ")
    print("(",item_to_freq[lhs],")",end=" ")

    print("----->",end=" ")
        
    for item in rhs:
        print(reverse_encode[item],",", end=" ")
        
    print("(",item_to_freq[rhs],")",end=" ")
    print("- conf ",item_to_freq[itemset]/item_to_freq[lhs])
    


# In[ ]:




