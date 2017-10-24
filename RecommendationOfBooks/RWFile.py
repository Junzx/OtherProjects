# -*- coding:utf-8 -*-
import codecs
def WriteIntoFile(MyString,path=r'J:\Code\Final.txt'):
    try:
        f=open(path,'w')
        temp=str(MyString).decode('GBK')
        temp2=temp.encode('utf-16')
        print type(temp2)
        f.write(temp2)
        f.close()
    except Exception,e:
        print 'Error in RWFile.py!'
        print 'Error is :',e
    else:
        print 'Load finish !'

def ReadFile(path=r'J:\Code\Final.txt'):
    f=codecs.open(path,'r')
    print type(f.read())
    f.close()

if __name__=='__main__':
    ReadFile()
    print '答辩'



