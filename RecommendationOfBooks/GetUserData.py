'''You should call function 'Initialize(PageNumber)',
   return a list with many dicts'''
# -*- coding:utf-8 -*-
import re
import urllib
import urllib2
import RWFile
import GetTagWithId
import sqlite3

def OpenSqlConn():
    OpenDB=sqlite3.connect(r'J:/Code/UserData.db')
    return OpenDB

def CreateTable(cur,TableName):
    cur=cur.cursor()
    SqlStr=r'CREATE TABLE '+TableName+'(BookName VARCHAR (100),Tags VARCHAR (300),BookId INTEGER PRIMARY KEY,Star INTEGER );'
    cur.execute(SqlStr)

def InsertData(cur,Name,Id,Star,Tags,TableName):
    cur=cur.cursor()
    Name="'"+str(Name)+"'"
    Tags="'"+str(Tags)+"'"
    SqlStr='INSERT INTO '+TableName+' VALUES ('+Name+','+Tags+','+str(Id)+','+str(Star)+');'
    cur.execute(SqlStr)

def CommitIt(cur):
    cur.commit()

def CloseIt(cur):
    cur.close()

def GetUserPage(NowCookie, MyDict, UserName='twopersons'):
    '''you need to define cookie,dict,username,
       this function is build for getting page html
       return a string'''
    try:
        MyUrl = r'https://book.douban.com/people/' + UserName + r'/collect'
        hdr = {'Host': 'book.douban.com', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': ' Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
               'DNT': '1', 'Referer': MyUrl,
               'Accept-Encoding': 'deflate, sdch', 'Accept-Language': 'zh-CN,zh;q=0.8', 'Cookie': NowCookie}
        UserUrl = MyUrl + '?' + urllib.urlencode(MyDict)
        req = urllib2.Request(UserUrl, headers=hdr)
    except Exception,e:
        print 'Error in GetUserData.py...'
        print 'Error in GetUserPage function...'
        print 'Error is :',e
    else:
        return urllib2.urlopen(req).read()

def GetBookItem(PageHtml):
    '''receive a pagehtml(string),
    return item STRING which have name ,id,stars'''
    ReWords = r'<li class="subject-item">([\s\S]*?)</li>'
    pattern = re.compile(ReWords)
    return re.findall(pattern, PageHtml)

def GetBookName(ItemString):
    start_index = ItemString.find('title')
    end_index = ItemString.find('"', start_index + 7, start_index + 200)
    if start_index != -1:
        BookName = ItemString[start_index + 7:end_index]
    else:
        return 'None!'
    return BookName

def GetBookId(ItemString):
    ReWords = r"subject_id:'(\d+)"
    pattern = re.compile(ReWords)
    return re.findall(pattern, ItemString)[0]

def GetBookStar(ItemString):
    try:
        ReWords = r'<span class="(\S+)"></span>'
        pattern = re.compile(ReWords)
        return re.findall(pattern, ItemString)[0]
    except Exception, e:
        return 'None!'

def Initialize(PageNumber=1):
    '''receice page number,
       return some dicts in a list'''
    NowCookie = 'bid="YyPlU1Z1kCw"; ll="108288"; ap=1; regpop=1; gr_user_id=79802bba-8499-4a27-8222-0928d20a48e7; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=fc13603b-394a-4047-abef-b86ee0a444f2; viewed="3725128_26490949"; _pk_id.100001.3ac3=2ccc234ca2cbff2c.1459922551.1.1459924145.1459922551.; _pk_ses.100001.3ac3=*'
    Username = r'twopersons'
    FinalList = []
    startnumber=0
    cur=OpenSqlConn()
    CreateTable(cur,Username)
    for i in range(PageNumber):
        mydict = {'start': str(startnumber), 'sort': 'time', 'rating': 'all', 'filter': 'all', 'mode': 'grid'}
        Page = GetUserPage(NowCookie=NowCookie, MyDict=mydict, UserName=Username)
        BookItem = GetBookItem(Page)
        startnumber += 15
        for item in BookItem:
            InsertData(cur,
                       GetBookName(item),
                       GetBookId(item),
                       GetBookStar(item)[6],
                       # 3,
                       GetTagWithId.GetPbookTag(GetBookId(item)),
                       Username,
                       )
        CommitIt(cur)
    CloseIt(cur)
    print 'Finish!!!!!!!'


if __name__ == '__main__':
    RWFile.WriteIntoFile(Initialize(1))
    Initialize(2)