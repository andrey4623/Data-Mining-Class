#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import random
import copy

def getSupernodeById(id):
    for x in supernodes:
        if (x.id == id):
            return x

def findTheNodeWithTheLargestValueOfS(supernode):
    
    list1 = supernode.getExternalLinks()
    
    list = []
    
    for x in list1:
        closestneighbor =getSupernodeById(x)
        
        if closestneighbor!=None:
            tempList = closestneighbor.getExternalLinks()
            for y in tempList:
                list.append(y)
    set1 = set(list).difference(set(list1))
    
    list2=[]
    list2.append(supernode.id)
    
    set1 = set1.difference(set(list2))


    #теперь ищем S для каждого нода из полученного списка

    maxValue=None
    supernodeWithMaxValue=0;
    for x in set1:
        closestneighbor =getSupernodeById(x)
        if closestneighbor==None:   continue
        temp = getS(supernode, closestneighbor)
        if maxValue==None:
            maxValue = temp
            supernodeWithMaxValue = x
        else:
            if (temp>maxValue):
                maxValue = temp
                supernodeWithMaxValue=x

    if (maxValue==None):    return None
    result =getSupernodeById(supernodeWithMaxValue)
    return result


def getS(supernode1, supernode2):

    supernode1C =supernode1.getC()
    supernode2C =supernode2.getC()
    
    
    list1 = supernode1.getExternalLinks()
    list2 = supernode2.getExternalLinks()
    
    totallist = []
    for x in list1:
        totallist.append(x)
    
    for x in list2:
        totallist.append(x)


    set1 = set(supernode1.getExternalLinks())
    set2 = set(supernode2.getExternalLinks())
    totalset = set(totallist)
    
    Cu = len(set1)
    Cv = len(set2)
    

    set3 = set(set1).intersection(set2)

    Cw = len(totalset)-len(set3)

    result =(Cu+Cv-Cw)*1.0/(Cu+Cv)
    return result


class Node(object):
    def __init__(self, id):
        self.id=id
        self.externalLinks=[]
    externalLinks=[]
    id=-1
    def getExternalLinks(self):
        return self.externalLinks

class Supernode(object):
    nodes=[]
    
    id=1
  
    def __init__(self):
        self.nodes = []
    
    
    def getC(self):
        return len(self.getExternalLinks())

    def getNodesIds(self):
        list=[]
        for x in self.nodes:
            list.append(x.id)
        return list
    
    def addNode(self, newNode):
        self.nodes.append(newNode)
    
    def getNodes(self):
        return self.nodes
    
    def __contains__(self, x):
        if self.id != x.id: return false;
        if len(self.nodes)!=len(x.nodes):   return false
    
        for x in self.nodes:
            for y in x.nodes:
                if x.id!=y.id:  return false;
                if len(x.externalLinks)!=len(y.externalLinks):  return false
                for z1 in x.externalLinks:
                    for z2 in y.externalLinks:
                        if z1!=z2:  return false
        return true
    

    def getExternalLinks(self):
        externalLinks=[]
       
        for node in self.nodes:
            tempList = node.getExternalLinks()
            for x in self.nodes:
                    if x.id in tempList:    tempList.remove(x.id)

            for x in tempList:
                externalLinks.append(x)
        return set(externalLinks)



def printGraph(supernodes):
    

    output=''
    for supernode in supernodes:
        output += 'Supernode id='+str(supernode.id)+'; nodes = '+  str(supernode.getNodesIds())  +'; links= '+str(supernode.getExternalLinks())+'\n'
    print output
numbernizer=-1


#load data from files
with open('nodes.csv') as f:
    nodesRaw = f.readlines()

with open('edges.csv') as f:
    edgesRaw = f.readlines()

supernodes=[]
F=[]

#create graph
for x in nodesRaw:
    x=x.strip()
    x=x.rstrip()
    node = Node(x)
    node.id = x
    for y in edgesRaw:
       y=y.strip()
       y=y.rstrip()
       temp = y.split()
       if temp[0]==x:
            node.externalLinks.append(temp[1])
    supernode = Supernode()
    supernode.id=numbernizer
    numbernizer-=1
    supernode.addNode(node)
    supernodes.append(supernode)


#проходим еще раз и меняем int в указателях на ссылки на суперноды

for x in range(0,len(supernodes)):
    for node in range(0,len(supernodes[x].nodes)):
        for link in range(0, len(supernodes[x].nodes[node].externalLinks)):
            
            #у нас есть id чувака вконтакте на которого ссылается эта ссылка в виде 150
            #нам надо найти отрицательный номер супернода, который содержит этого чувака под номером 150
            for x2 in range(0,len(supernodes)):
                if supernodes[x].nodes[node].externalLinks[link]==supernodes[x2].nodes[0].id:
                    supernodes[x].nodes[node].externalLinks[link] = supernodes[x2].id


#визуализация загруженного графа
#for x in range(0,len(supernodes)):
#    s=supernodes[x]
#    print 'For supernode '+str(supernodes[x].id)+' number of nodes is '+str(len(supernodes[x].nodes))
#    for y in range(0, len(s.nodes)):
#        print '\tFor Node '+s.nodes[y].id + ' list of external links:'
#        for z in range(0, len(s.nodes[y].externalLinks)):
#            print '\t'+str(s.nodes[y].externalLinks[z])



#algorithm
while (len(supernodes)>0):
    u = random.choice(supernodes)
    
    v = findTheNodeWithTheLargestValueOfS(u)
    if v==None:
        supernodes.remove(u)
        F.append(u)
    #print 'no'
    else:
        if (getS(u,v)>0):
            
            w = Supernode()
            w.id = u.id

            for x in u.nodes:
                w.nodes.append(x)
            
            for x in v.nodes:
                w.nodes.append(x)


            #теперь надо пройтись по всем супернодам, и если они указывают на v, изменить указатель на u
            for ss in range(0,len(supernodes)):
                for nn in range(0,len(supernodes[ss].nodes)):
                    for ll in range(0,len(supernodes[ss].nodes[nn].externalLinks)):
                        if supernodes[ss].nodes[nn].externalLinks[ll] == v.id:
                            supernodes[ss].nodes[nn].externalLinks[ll] = u.id
            supernodes.remove(u)
            supernodes.remove(v)
            supernodes.append(w)
            #print 'merge'

        else:
            
            #print 'move'
            supernodes.remove(u)
            F.append(u)





#print 'Result:'
#output=''
#for supernode in F:
#    output += 'Supernode id='+str(supernode.id)+'; nodes= '
#    for node in supernode.nodes:
#        output+=str(node.id)+' '
#    output+='\n'





#if you want to see the result uncomment the next line:
#printGraph(F)



#export to file



f = open('outputnodes.csv','w')
for x in F:
    f.write(str(abs(x.id)+10000000000)+'\n')
f.close()
f = open('outputedges.csv','w')
for x in F:
    for ll in x.getExternalLinks():
        f.write(str(abs(x.id)+10000000000)+' '+str(abs(int(ll))+10000000000)+'\n')
f.close()

#output=''
#    for supernode in supernodes:
#        output += 'Supernode id='+str(supernode.id)+'; nodes = '+  str(supernode.getNodesIds())  +'; links= '+str(supernode.getExternalLinks())+'\n'
#    print output
#f.write('hi there\n') # python will convert \n to os.linesep
#f.close() # you can omit in most cases as the destructor will call if


print 'Completed'