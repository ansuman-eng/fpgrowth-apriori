from __future__ import print_function
import numpy as np
import csv
import itertools
import sys


hash={}

#(not used)finds subsets of S of size m
def findsubsets(S,m):
	return set(itertools.combinations(S, m))

# def allSubsets(S):
# 	for i in range(len(S)):
# 		isets=findsubsets(S,i)
# 		for j in isets:
# 			if j in hash.keys():
# 				hash[j]+=1;
# 			else:
# 				hash[j]=1;

#(not used)checks if a is a subset of b
def checksubset(a,b):
	if len(a)==0 or len(b)==0:
		return False
	i=0
	j=0
	
	for i in range(len(a)):
		flag=False
		for j in range(len(b)):
			if a[i] == b[j]:
				flag=True
		if flag==False:
			return flag
	return True

# generates candidate k itemsets from frequent k-1 itemsets 
def apgenn(S):
	S1=np.array([[]])
	S=np.sort(S)
	c=1
	kk=0
	#loop for F(k-1)xF(k-1)
	for i in range(len(S)):
		for j in range(i+1,len(S)):
			if (np.array_equal(S[i][:len(S[i])-1],S[j][:len(S[j])-1])):
				temp=np.array([])
				temp=np.append(temp,S[i][:len(S[i])-1])
				temp=np.append(temp,S[i][len(S[i])-1])
				temp=np.append(temp,S[j][len(S[j])-1])
				# temp=np.reshape(temp,(len(temp),1))
				# temp=np.array([temp])
				# print temp
				if c==1:
					S1=np.array([temp])
					c+=1
					kk=np.shape(S1)[1]
				else:
					S1=np.append(S1,temp)
					S1=np.reshape(S1,(c,kk))
					c+=1
				# print "boom"
				# print S1
				# print np.shape(temp)
				# print np.shape(S1)
				#S1=np.reshape(S1,(len(S1),1))
	return S1

#(not used)same as apgen() but worse
def apgen(S):
	if np.array_equal(S,np.array([[]])):
		return S
	S1=np.array([[]])
	# S=np.sort(S,axis=0)
	# print S
	rows=0
	try:
		cols=len(S[0])+1
	except:
		return S
	cur=np.array([])
	for i in range(len(S)-1):
		# print S[i][:len(S[i])-1]
		# print S[i+1][:len(S[i+1])-1]
		if (np.array_equal(S[i][:len(S[i])-1],S[i+1][:len(S[i+1])-1])):
			cur=np.append(cur,[S[i][len(S[i])-1]])
			cur=np.append(cur,[S[i+1][len(S[i+1])-1]])
			cur=np.unique(cur)
			# print cur
		elif not np.array_equal(cur,np.array([])):
			curr=np.array(list(findsubsets(cur,2)))
			# curr=np.unique()
			# print curr
			for j in range(len(curr)):
				S1=np.append(S1,[S[i][:len(S[i])-1]])
				S1=np.append(S1,[curr[j]])
				rows+=1
				S1=np.reshape(S1,(rows,cols))
			cur=np.array([])
	if len(cur)>0:
		curr=np.array(list(findsubsets(cur,2)))
		# print curr
		for j in range(len(curr)):
			S1=np.append(S1,[S[i][:len(S[i])-1]])
			S1=np.append(S1,[curr[j]])
			rows+=1
			S1=np.reshape(S1,(rows,cols))

	return S1


f=open('groceries.csv')
reader = csv.reader(f)
ListOfItems=np.array(['adsadf'])
# print np.shape(np.array([[1],[2]]))
# print np.shape(np.array([1,2]))
# exit()
# print ListOfItems
Transactions=np.empty([9835,32])
DataSet=np.zeros((9835,169),dtype=int)
max=0
var=2

#reading the dataset
for row in f:
	row=row.strip()
	Ti=np.array(row.split(','))
	# print Ti
	# allSubsets(Ti)
	if len(Ti)>max:
		max=len(Ti)
	# print Ti
	
	for pp in Ti:
		# print np.array([[pp]])
		ListOfItems=np.append(ListOfItems,np.array([pp]),axis=0)
		# ListOfItems=np.reshape(ListOfItems,(var,1))
		var+=1
	
		# print ListOfItems
	# print ListOfItems


ListOfItems=ListOfItems[1:]
ListOfItems=np.unique(ListOfItems)
ListOfItems=np.reshape(ListOfItems,(169,1))
# print ListOfItems

#Encoding the Items
for i in range(len(ListOfItems)):
	hash[ListOfItems[i][0]]=i

dehash={}
for i in range(len(ListOfItems)):
	dehash[i]=ListOfItems[i][0]
# print hash
g=open('groceries.csv')
reader = csv.reader(g)
count=0
for row in g:
	row=row.strip()
	Ti=np.array(row.split(','))
	for j in Ti:
		# print hash[j]
		# print j
		DataSet[count][hash[j]]=1
		# if count>9835:
		# 	break
	count+=1
# for i in range(5):
# 	for j in range(169):
# 		print(DataSet[i][j]),
# 	print('.')
print ("Enter the required support in percentage")
supper=input()

support = int((supper/100.0)*9835)
# ListOfItems
ok=list(range(169))
# op=np.array(map(str,ok))
op=np.array(ok)
op=np.reshape(op,(169,1))

for i in range(len(op)):
	hash[op[i][0]]=i

FreqItemSets={}
index=0
# blah=np.array([['aa'],['bb'],['vv']])
# print np.delete(blah,1)

# print DataSet
for i in range(32):
	
	
	TempHash={}
	CFreq={}
	for k in range(len(op)):
		CFreq[k]=0
		# print tuple(map(tuple,op[k]))

	# print op
	cp=0
	x=0
	
	while(x<len(op)):
		# print CFreq
		for j in range(9835):
			flag=1
			if x>=len(op):
				break
			# print op[x],
			# print i
			for y in op[x]:

				if DataSet[j][int(y)]!=1:
					flag=0
					break
			if flag==1:
				try:
					CFreq[x]+=1
				except:
					CFreq[x]=1
				# TempHash[tuple(map(tuple,op[x]))]+=1
	
		# print op,
		# print x
	# for x in op1:
		if x>=len(op):
			break
		try:	
			if CFreq[x]<support:
				op=np.delete(op,x,axis=0)
				CFreq.pop(x)
				x-=1
		except:
			q=0
			# op=np.reshape(op,(len(op),1))
		x+=1
	

	# if i>0:
	# 	for its in previous:
	# 		mflag=1
	# 		for iss in range(len(op)):
	# 			tr=checksubset(its.astype(int),op[iss].astype(int))
	# 			# print its,
	# 			# print op[iss],
	# 			# print tr
	# 			if tr:
	# 				try:
	# 					fk=CFreq[iss]
	# 					mflag=0
	# 					break
	# 				except:
	# 					fk=0
	# 			else:
	# 				mflag=0

	# 			# try:
	# 			# 	if CFreq[iss]>=support and checksubset(its,op[iss]) :
	# 			# 		mflag=0
	# 			# 		break
	# 			# except:
	# 			# 	continue
	# 				# mflag=0
	# 				# break
	# 		if mflag==1 and not np.array_equal(its,np.array([])):
	# 			MaximalItemsets[mindex]=its
	# 			# print its
	# 			mindex+=1


	# print op
	op1=apgenn(op)
	# print op

	#printing the frequent itemsets
	for x in range(len(op)):
		try:
			if not np.array_equal(op[x],np.array([])):
				FreqItemSets[index]=(op[x].astype(int),CFreq[x])
				# print index,
				ll=FreqItemSets[index][0]
				for it in range(len(ll)):
					print (dehash[ll[it]],end=''),
					print (',',end=''),
				print ('(',end=''),
				print (CFreq[x],end=''),
				print (')')
				index+=1
		except:
			q=0

	# for x in range(len(op1)):
	# 	flag=1
	# 	for y in range(len(op1[x])):
	# 		print np.delete(op1[x],y)
	# 		if np.delete(op1[x],y) not in op:
	# 			flag=0
	# 	if flag==1:
	# 		op1=np.delete(op1,x)
	previous=op
	op=op1
# print index

# print hash.keys()
# for item in ListOfItems: