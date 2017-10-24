# -*- coding:utf-8 -*-
import urllib2
import re

def WriteStrList(StringList):
    f = open(r'J:/BiShe/FinalCode/TextFile/HotTags.txt', 'a+')
    for item in StringList:
        f.write(item)
    f.close()

def WriteString(MyString):
    f=open(r'J:/BiShe/FinalCode/TextFile/StrTEXT.txt','w+')
    f.write(MyString)
    f.close()

def GetHotTags():
    '''Start '''
    HotUrl = r'https://book.douban.com/tag/?view=type&icn=index-sorttags-all'
    conn = urllib2.urlopen(HotUrl)
    reWords = r'<a href="https://www.douban.com/tag/(.*?)/\?focus=book"'
    pattern = re.compile(reWords)
    final = re.findall(pattern, conn.read())
    return final

def Tag2Url(Tagname):
    '''Receive :Tagname list,
       Return :Tag url list'''
    urllist=[]
    for item in Tagname:
        tempurl=r'https://www.douban.com/tag/' + item + '/?focus=book\n'
        urllist.append(tempurl)
    return urllist 

def GetTagsFromOnePage(TagName):
    try:
        TagUrl = r'https://www.douban.com/tag/' + TagName + r'/?focus=book'
        conn=urllib2.urlopen(TagUrl)
        reWords=r'source=related">(.*?)</a>'
        pattern=re.compile(reWords)
        final=re.findall(pattern,conn.read())
        return final
    except Exception,e:
        print "Error there"
        return ['Sorry!']

def Sp_main(TagList):
    try:
        TagL=TagList[:]
        for iii in range(len(TagList)):
            oneTag=TagList.pop(0)
            templist=GetTagsFromOnePage(oneTag)
            TagL.extend([i for i in templist if i not in TagL])
        return TagL
    except Exception,e:
        print e

def GetEachPage(TagList):
    try:
        f=open(r'J:/BiShe/FinalCode/TextFile/Kang.txt','a+')
        i=0
        for item in TagList:
            templist=GetTagsFromOnePage(item)
            temp=(item+'/')
            temp+=("".join([t+'/' for t in templist]))
            temp+='\n'
            f.write(temp)
            print i
            i+=1

    except Exception,e:
        print e



def main():
    f=open(r'J:/BiShe/FinalCode/TextFile/HotTags.txt', 'a+')
    TagName=[]
    HotTagName=GetHotTags()
    GetEachPage(HotTagName)
    f.close()

if __name__ == '__main__':
    main()