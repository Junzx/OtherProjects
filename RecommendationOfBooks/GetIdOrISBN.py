'''Receive a HTML doc ,
   return Id or ISBN list'''
# -*- coding:utf-8 -*-
import re
import urllib
import urllib2

def GetBookUrlList(FuncUrl):
    '''Receive a search url,
       return a url list of each book'''
    try:
        conn=urllib2.urlopen(FuncUrl)
        Page=conn.read()
        ReWords=r'<div class="info">([\s\S]*?)title'
        pattern=re.compile(ReWords)
        items=re.findall(pattern,str(Page))
        HrefList=[]
        for mystr in items:
            MIndex=mystr.index('href')
            HrefList.append(mystr[MIndex+5:].strip(' ').strip('"'))
    except Exception,e:
        print 'Error in GetIdOrISBN.py...'
        print 'Error in GetUrlList function...'
        print 'Error is :',e
    else:
        return HrefList

def GetIdList(UrlList):
    '''rective a urllist,
       return a Id list'''
    IdList=[]
    for item in UrlList:
        BookId="".join([i for i in item if i in '0123456789'])
        IdList.append(BookId)
    return IdList

def GetISBNList(UrlList):
    '''receive a urllist,
       return a ISBN list'''
    ISBNList=[]
    for EachUrl in UrlList:
        conn=urllib2.urlopen(EachUrl)
        Page=conn.read()
        ReWords=r'ISBN:</span> ([\s\S]*?)<br>'
        pattern=re.compile(ReWords)
        items=re.findall(pattern,Page)
        ISBN_Num=""
        for i in str(items):
            if i not in '0123456789':
                break
            ISBN_Num+=i
        ISBNList.append( "".join([i for i in str(items)[:20].strip('[') if i in '0123456789']))
    return ISBNList

if __name__=='__main__':
    searchurl=r'https://book.douban.com/subject_search?search_text=python&cat=1001'
    UrlList= GetBookUrlList(searchurl)
    print len(GetIdList(UrlList))
    print GetISBNList(UrlList)