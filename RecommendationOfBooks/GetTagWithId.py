'''Get tags of book with id
   Recetive a Id and flag
   return tags of one book '''
# -*- coding:utf-8 -*-
import re
import urllib
import urllib2


def GetEbookTag(Bookid):
    '''Get tags of Ebook,
       return a list'''
    BookUrl=r'https://read.douban.com/ebook/'+repr(Bookid)+r'/?dcs=book-search'
    BookConn=urllib2.urlopen(BookUrl)
    BookString=BookConn.read()
    ReWords=r'<ul class="tags">([\s\S]*?)</ul>'
    pattern=re.compile(ReWords)
    items=re.findall(pattern,str(BookString))
    FlagString=items[0]
    split_name=r'class="tag-name">(.+?)</span>'
    pattern_name=re.compile(split_name)
    itemName=re.findall(pattern_name,FlagString)
    split_total=r'class="tag-total">(.+?)</span>'
    pattern_total=re.compile(split_total)
    itemTotal=re.findall(pattern_total,FlagString)
    BookConn.close()
    return itemName

def GetPbookTag(Bookid):
    '''Get tags of page book
       return a list'''
    BookUrl=r'https://book.douban.com/subject/'+str(Bookid)+r'/'
    BookConn=urllib.urlopen(BookUrl)
    BookString=BookConn.read()
    if str(BookString).find('class="  tag"')==-1: # some book don't have tags
        return ['No Tags']
    ReWords=r'<a class="  tag"([\s\S]*?)</div>'
    pattern=re.compile(ReWords)
    item=re.findall(pattern,str(BookString))    #len(item)=1 ,item is a list ,item[l] is a long string,so use split
    FlagString=item[0]
    split_name=r'/tag/(.*?)/'
    pattern_name=re.compile(split_name)
    itemName=re.findall(pattern_name,FlagString)
    return "/".join(itemName)


def Test(Bookid):
    BookUrl=r'https://book.douban.com/subject/'+str(Bookid)+r'/'
    print BookUrl
    BookConn=urllib.urlopen(BookUrl)
    BookString=BookConn.read()
    if str(BookString).find('class="  tag"')==-1:
       return ['No Tags']
    ReWords=r'<a class="  tag"([\s\S]*?)</div>'
    pattern=re.compile(ReWords)
    item=re.findall(pattern,str(BookString))
    FlagString=item[0]
    split_name=r'/tag/(.*?)/'
    pattern_name=re.compile(split_name)
    itemName=re.findall(pattern_name,FlagString)
    return itemName


if __name__=='__main__':
    print GetPbookTag(26324187)
    f=open('J:\Code\zzz.txt','w+')
    f.write(GetPbookTag(26324187))
    f.close()
