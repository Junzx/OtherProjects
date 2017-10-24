import urllib2
import re
import RWFile
import time
import cookielib

def SetCookie():
    myCookie=cookielib.CookieJar()
    myHandler=urllib2.HTTPCookieProcessor(myCookie)
    myOpener=urllib2.build_opener(myHandler)
    ors=myOpener.open('https://www.douban.com')
    CookieString=""
    for item in myCookie:
        CookieString+=(item.name+'='+item.value+';')
    return CookieString


def DownloadData(Username,NowCookie):
    try:
        MyUrl = r'https://book.douban.com/people/' + Username
        hdr={'Host':' www.douban.com',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Upgrade-Insecure-Requests':' 1',
           'User-Agent':' Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
            'DNT':' 1',
            'Referer': MyUrl,
            'Accept-Encoding': 'deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cookie':NowCookie
             }
        req = urllib2.Request(MyUrl, headers=hdr)
        return urllib2.urlopen(req).read()
    except Exception,e:
        print e
        return 'shit '
def testUser(UsernameItem,MyString):
    try:
        rewords=r'https://book.douban.com/people/'+UsernameItem+'/collect" target="_blank">(\d+)(\S+)</a>'
        pattern=re.compile(rewords)
        temp=re.findall(pattern,MyString)
        return temp[0][0]
    except Exception,e:
        return -2

NowCookie='bid="oXssZP0Ez58"; ll="108288"; gr_user_id=5c4eeb34-dd26-4909-8be2-9e06939a6181; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=73b23ad4-b96a-4121-8db2-fa98d2b83a3d; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1460895607%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_id.100001.3ac3=74f5bc6b4cfa21f8.1460777780.3.1460895607.1460880908.; _pk_ses.100001.3ac3=*'
def main(ItemName):
    if int(testUser(ItemName,DownloadData(Username=ItemName,NowCookie=SetCookie()))) >=200:
        return 1
    else:
        return -1

def ShitAllUser(inname,outname):
    f1path=r'J:/BiShe/FinalCode/TextFile/'+inname+r'.txt'
    f2path=r'J:/BiShe/FinalCode/TextFile/'+outname+r'.txt'
    print f1path,' | ',f2path
    f1=open(f1path,'r')
    f2=open(f2path,'a+')
    for item in f1.readlines():
        item= item.strip("\n").strip("/")
        if main(item)==1:
            f2.write(item+'\n')
        else:
            print item
        time.sleep(2)
    f1.close()
    f2.close()

if __name__=='__main__':
    ShitAllUser('NewUser2','wtf1')
    ShitAllUser('NewUser3','wtf2')