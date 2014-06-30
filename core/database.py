import os
import imp
import sqlite3
class Database(object):
    def __init__(self):
        #self.conn=sqlite3.connect(":memory:")
        self.connect()
    def connect(self):
        firstConnect=not(os.path.isfile("eddie.db"))
        self.conn=sqlite3.connect("eddie.db")
        self.cur=self.conn.cursor()
        if firstConnect:
            print("Generating database")
            self.generate()
    def close(self):
        self.cur.close()
        self.conn.close()
    def generate(self):
        self.cur.execute("pragma foreign_keys = on")
        self.cur.execute("create table exploits (id integer primary key autoincrement not null, name text, description text, author text, file text, path text)")
        self.cur.execute("create table model_exploits (model text, exploit_id integer, foreign key(exploit_id) references exploits(id))")
        path=os.path.dirname(os.path.realpath(__file__))
        exploitPath=os.path.join(os.path.split(path)[0], "plugins", "exploits")
        exploits=os.listdir(exploitPath)
        espoitsExpanded=list(filter(lambda path: (os.path.isfile(path) and path.split(".")[-1]=="py")
                                , map(lambda exploit: os.path.join(exploitPath, exploit),exploits)))
        for exploitFilePath in espoitsExpanded:
            exploitFile=os.path.basename(exploitFilePath)[:-2]
            exploitClass=imp.load_source("plugins.exploits."+exploitFile, exploitFilePath)
            exploitMethod=exploitClass.Exploit()
            self.cur.execute("insert into exploits values(null, ?, ?, ?, ?, ?)", (exploitMethod.name, exploitMethod.description, exploitMethod.author, exploitFile, exploitFilePath))

            exploitID=self.cur.lastrowid
        #    for row in cur.execute("select * from exploits"):
        #        print(row)
        #
        #    print("Name:",exploitMethod.name)
        #    print("Description:",exploitMethod.description)
        #    print("Author:",exploitMethod.author)
        #    print(exploitMethod.affects.split(","))
            routers=exploitMethod.affects.split(",")
            for router in routers:
                self.cur.execute("insert into model_exploits values(?, ?)", (router, exploitID))
        self.conn.commit()

    def rebuild(self):
        self.close()
        os.remove("eddie.db")
        self.connect()
        self.generate()
    def findExploits(self, model):
        print("Searching database for "+ model)
        exploits=[]
        for row in list(self.cur.execute("select * from model_exploits where model=?", (model,))):
            self.cur.execute("select * from exploits where id=?", (row[1], ))
            exploits.append(self.cur.fetchone())
        return(exploits)
