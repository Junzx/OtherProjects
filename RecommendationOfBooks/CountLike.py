import sqlite3
import GetTag
import time
import LoadTags

class SqlInit(object):
    def __init__(self):
        self.oldconn=sqlite3.connect(r'J:/BiShe/FinalCode/DataBase/New.db')
        self.oldcurr=self.oldconn.cursor()
        self.UserList=self.oldcurr.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()

    def GetTableNameList(self):
        return [str(item[0]) for item in self.UserList]

    def SelectOneTable(self,TableName):
        SqlStr='SELECT * FROM '+TableName
        return self.oldcurr.execute(SqlStr).fetchall()

def main():
    Log=open(r'J:/BiShe/FinalCode/TextFile/TagsLog.txt','a+')
    UserLike=open('J:/BiShe/FinalCode/TextFile/UserLike/UserLike.txt','a+')
    TestClass=SqlInit()
    NameList= TestClass.GetTableNameList()
    for item in NameList:
        Log.write(item+'\n')
        mypath='J:/BiShe/FinalCode/TextFile/UserLike/'+item+'.txt'
        f=open(mypath,'a+')
        datalist=TestClass.SelectOneTable(item) 
        IdList=[]
        TagStrList=[]
        for eachString in datalist:
            time1=time.localtime(time.time())[4]
            TagString=GetTag.ThisMain(eachString[1]) 
            print item,TagString
            f.write(TagString+'@')
            TagStrList.append(TagString)
            
            time.sleep(1)
            time2=time.localtime(time.time())[4]
            if time2-time1>5:
                continue
        f.close()
        UserLike.write(str(LoadTags.count(TagStrList)))
        UserLike.close()
    Log.close()

if __name__=='__main__':
    main()