# -*- coding:utf-8 -*-
import re
import urllib
import urllib2
import cookielib
import RWFile


def SetCookie():
    myCookie=cookielib.CookieJar()
    myHandler=urllib2.HTTPCookieProcessor(myCookie)
    myOpener=urllib2.build_opener(myHandler)
    ors=myOpener.open('https://www.douban.com')
    CookieString=""
    for item in myCookie:
        CookieString+=(item.name+'='+item.value+';')
    return CookieString

def init(Bookid):
    NowCookie=SetCookie()
    BookUrl=r'https://book.douban.com/subject/'+str(Bookid)+r'/'
    hdr={
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Language':' zh-CN',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
        'Accept-Encoding': 'deflate',
        'Host': 'book.douban.com',
        'DNT': '1',
        'Connection':'Keep-Alive',
        'Cookie':NowCookie
    }
    BookConn=urllib.urlopen(BookUrl)
    req=urllib2.Request(BookUrl,headers=hdr)
    BookString=urllib2.urlopen(req).read()
    BookConn.close()
    return BookString

def GetPbookTag(BookString):
    '''Get tags of page book
       return a list'''
    if str(BookString).find('class="  tag"')==-1: 
        return 'No Tags'
    ReWords=r'<a class="  tag"([\s\S]*?)</div>'
    pattern=re.compile(ReWords)
    item=re.findall(pattern,str(BookString))    
    FlagString=item[0]
    split_name=r'/tag/(.*?)>.*?/'
    pattern_name=re.compile(split_name)
    itemName=re.findall(pattern_name,FlagString)
    itemName=[i.strip('"') for i in itemName]
    return "/".join(itemName)

def GetPBookName(BookString):
    ReWords=r'property="v:itemreviewed">(.*?)</span>'
    pattern=re.compile(ReWords)
    item=re.findall(pattern,BookString)
    return item

def ThisMain(BookId):
    return GetPbookTag(init(Bookid=BookId))

if __name__=='__main__':
    SetCookie()
    print GetPbookTag(init(26673853))
    print GetPBookName(init(26575812))
    print ThisMain(10473356)