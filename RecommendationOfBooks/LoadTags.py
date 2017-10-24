#-*- coding:utf-8 -*-
from __future__ import division
class TagInit(object):
    def __init__(self):
        self.fp=open(r'J:/BiShe/FinalCode/TextFile/demo.txt','r')
        self.Like={}
        for i in range(58):
            self.Like[i]=float(0)
        self.Like[-1]=0
        self.ReadFile()

    def ReadFile(self):
        self.TagDict={}
        i=0
        for eachString in self.fp.readlines():
            self.TagDict[i]=eachString[eachString.find(':')+1:].strip('\n').strip('/').split('/')
            i+=1
        if i!=58:
            print 'Something Error...'

    def GetIndex(self,itemname):
        for i in range(len(self.TagDict)):
            if itemname in self.TagDict[i]:
                return i
            else:
                i+=1
            if i==58:
                return -1

    def ReTagString(self,TagString):
        if TagString.find('$')==-1:
            TheStar=0
        else:
            TheStar=TagString[TagString.find('$')+1:]
        BookTagList=TagString.strip('/').split('/')
        for item in BookTagList:
            # print item
            self.Like[self.GetIndex(item)]+=float(0.2*int(TheStar))

def count(TagList,username):
    TestClass=TagInit()
    for itemTagStr in TagList:
        if itemTagStr=='':
            break
        TestClass.ReTagString(itemTagStr)
    TestClass.Like['name']=username
    return {username:TestClass.Like}  # it's a test {name: {like}}

def main():
    teststr='家装/手工本/职业发展/作家/$3'
    teststr2='搭讪/影像/菜谱/甜点/自我/小说/打啊打/传记$4'
    teststr3='徐志摩/人间四月天/剧本/王惠玲/传记/小说/爱情/文学/$2'
    f=open('J:/tsttss.txt','a+')
    print count([teststr,teststr2,teststr3],'aaa')

if __name__ == '__main__':
    main()
