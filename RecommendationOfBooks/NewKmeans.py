from __future__ import division
import os
import math
import LoadTags
import random
import sys

FileList=os.listdir('j:/BiShe/FinalCode/TextFile/FinalT')
FileList=[item for item in FileList] 
class Kmeans(object):
    def __init__(self,num):
        self.AllTagList=self.LoadFromFile()
        self.classnumber=num 
        self.eachClass=[]
        for i in range(self.classnumber):
            temp=int(random.uniform(1,59))
            self.eachClass.append([self.AllTagList[temp]])
        self.thisistest=[item for item in self.AllTagList]
        temp=[self.AllTagList[i] for i in range(self.classnumber)]
        self.noClassUser=[item for item in self.AllTagList if item not in temp]
        stt=open('J:/TempTest.txt','a+')
        for zz in self.AllTagList:
            stt.write(str(zz)+'\n\n')


    def LoadFromFile(self):
        '''return [{'120_anice.txt': {0: 48, 1: 5, 2: 15....},{....} ] | it's a list'''
        FinalTagList=[]
        for FileName in FileList:
            nowpath='J:/BiShe/FinalCode/TextFile/FinalT/'+FileName
            ff=open(nowpath,'r')
            TagList=ff.read().split('@')
            FinalTagList.append(LoadTags.count(TagList,FileName))
        return FinalTagList

    def countDistance(self,likeList1,likeList2):
        '''return a number , distance in list1 and list2'''
        temp= [math.pow((likeList1[i]*0.01-likeList2[i]*0.01),2) for i in range(len(likeList2)) ]
        return math.sqrt(sum(temp))

    def countZhixin(self,itemList):
        '''
        :param itemList: it's a list ,each item is a dict !
        :return: a dict | it's zhixin
        '''
        Final=[]
        for counter in range(58):
            temp=0
            for i in range(len(itemList)):
                if isinstance(itemList[i][counter],float):
                    temp+=itemList[i][counter]
            Final.append(temp/len(itemList))
        return Final

    def count222(self,itemList):
        '''
        :param itemList: it's a list ,each item is a dict !
        :return: a dict | it's zhixin
        '''
        Final=[]
        for counter in range(len(itemList[0])):
            temp=0
            for i in range(len(itemList)):
                if isinstance(itemList[i][counter],int):
                    temp+=itemList[i][counter]
            Final.append(temp/len(itemList))
        return Final

    def decideClass(self,classNumber,everyClass,freeUser):
        AllLike=[]
        Final=[]
        demo=[[] for i in range(classNumber)]
        for counter in range(classNumber): 
            myshit=[]
            LikeList=[]
            dataClass=everyClass[counter]
            for item in dataClass:
                tmp1=item.values()
                for tmp2 in tmp1:
                    LikeList.append(tmp2.values())
            ThisLike= self.countZhixin(LikeList)[:]
            for nocount in freeUser:
                istemp=nocount.values()[0]
                if istemp.has_key('name'):
                    del istemp['name']
                    del istemp[-1]
                onepeople=istemp.values()
                myshit.append(self.countDistance(ThisLike,onepeople))
            AllLike.append(myshit)
        for itemp in range(len(AllLike[0])):
            thshit=[]
            for i in range(len(AllLike)):
                thshit.append(AllLike[i][itemp])
            Final.append(thshit.index(min(thshit)))
        for eachitem in Final:
            demo[eachitem].append(freeUser[eachitem])
        cc=1
        for test in demo:
            print 'Group',cc,":",len(test), " | ",
            cc+=1
        return demo
#---------------------
    def demotest(self,classNumber,everyClass,freeUser):
            AllLike=[]
            Final=[]
            for counter in range(1): 
                myshit=[]
                LikeList=[]
                dataClass=everyClass[counter]
                for item in dataClass:
                    tmp1=item.values()
                    for tmp2 in tmp1:
                        LikeList.append(tmp2.values())
                ThisLike= self.countZhixin(LikeList)[:]
                for nocount in freeUser:
                    istemp=nocount.values()[0]
                    if istemp.has_key('name'):
                        del istemp['name']
                        del istemp[-1]
                    onepeople=istemp.values()
                    myshit.append(self.countDistance(ThisLike,onepeople))
                AllLike.append(myshit)

            for counter in range(classNumber-1): 
                myshit=[]
                LikeList=[] 
                dataClass=everyClass[counter]
                for item in dataClass:
                    tmp1=item.values()
                    for tmp2 in tmp1:
                        LikeList.append(tmp2.values())

                ThisLike= self.count222(LikeList)[:]
                for nocount in freeUser:
                    istemp=nocount.values()[0]
                    if istemp.has_key('name'):
                        del istemp['name']
                        del istemp[-1]
                    onepeople=istemp.values()
                    myshit.append(self.countDistance(ThisLike,onepeople))
                AllLike.append(myshit)

            for itemp in range(len(AllLike[0])):
                thshit=[]
                for i in range(len(AllLike)):
                    thshit.append(AllLike[i][itemp])
                Final.append(thshit.index(min(thshit)))
            for eachitem in Final:
                everyClass[eachitem].append(freeUser[eachitem])
            cc=1
            for test in everyClass:
                print 'Group ',cc,":",test," | "
            return everyClass
#---------------------
    def booshit(self,classNumber,everyClass,freeUser):
            AllLike=[]
            Final=[]
        
            for counter in range(classNumber-1): #
                myshit=[]
                LikeList=[] 
                dataClass=everyClass[counter]
                for item in dataClass:
                    tmp1=item.values()
                    for tmp2 in tmp1:
                        LikeList.append(tmp2.values())
                ThisLike= self.count222(LikeList)[:]
                for nocount in freeUser:
                    istemp=nocount.values()[0]
                    if istemp.has_key('name'):
                        del istemp['name']
                        del istemp[-1]
                    onepeople=istemp.values()
                    myshit.append(self.countDistance(ThisLike,onepeople))
                AllLike.append(myshit)
                
            for itemp in range(len(AllLike[0])):
                thshit=[]
                for i in range(len(AllLike)):
                    thshit.append(AllLike[i][itemp])
                Final.append(thshit.index(min(thshit)))
            for eachitem in Final:
                everyClass[eachitem].append(freeUser[eachitem])
            for test in everyClass:
                print 'test',len(test)
            return everyClass

def maintest(k=6):
    try:
        testClass=Kmeans(k)
        print '\n','----------------'*(k)
        demo=testClass.decideClass(testClass.classnumber,testClass.eachClass,testClass.noClassUser)
        print '\n','----------------'*(k)
        newshit=testClass.decideClass(testClass.classnumber,demo,testClass.thisistest)
        print '\n','----------------'*(k)
        newnew=testClass.decideClass(testClass.classnumber,newshit,testClass.thisistest)
        print '\n','----------------'*(k)
        final=testClass.decideClass(testClass.classnumber,newnew,testClass.thisistest)
        print '\n','----------------'*(k)
        tt=testClass.decideClass(testClass.classnumber,final,testClass.thisistest)
        print '\n','----------------'*(k)
        testClass.decideClass(testClass.classnumber,tt,testClass.thisistest)
        print '\n','----------------'*(k)
    except Exception,i:
        os.system("cls")
        maintest(k)

if __name__=='__main__':
    maintest(int(sys.argv[1]))
