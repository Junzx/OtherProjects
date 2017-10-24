import sqlite3
import os

db_path = os.getcwd()+'\Rating.db'
db2_path = os.getcwd()+'\Similiar.db'
file_path =  os.getcwd() + "\Data\\ratings.dat"
str_create_table = "CREATE TABLE Rating(userid VARCHAR (20),movieid VARCHAR (20),rating FLOAT);"

str_create_table2 = "CREATE TABLE SIMILIAR(movieid1 VARCHAR (20),movieid2 VARCHAR (20),similiar VARCHAR (100) )"


class ExtractData(object):
    def __init__(self):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.conn2 = sqlite3.connect(db2_path)
        self.cur2 = self.conn2.cursor()

    def createDB(self):
        self.cur.execute(str_create_table)
        self.cur2.execute(str_create_table2)

    def insert(self,tup_var):
        str_insert = "INSERT INTO Rating VALUES ("+str(tup_var[0])+","+str(tup_var[1])+","+str(tup_var[2])+");"
        self.cur.execute(str_insert)
        # print str_insert

    def loaddata(self):
        with open(file_path,'r') as fhandle:
            for eachline in fhandle:
                self.insert(tuple(eachline.split("::")))

    def final(self):
        self.cur.close()
        self.conn.commit()
        self.conn.close()
        self.cur2.close()
        self.conn2.commit()
        self.conn2.close()

if __name__ == "__main__":
    # data = ExtractData()
    # # print data.conn
    # # data.insert((1,2,4.5))
    # data.createDB()
    # data.loaddata()
    # data.final()
    conn = sqlite3.connect(db2_path)
    cur = conn.cursor()
    tablenames = cur.execute("SELECT name FROM sqlite_master;")
    for i in tablenames.fetchall():
        print i