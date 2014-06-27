class Exploit(object):
    def __init__(self):
        self.init()
        print("Name: "+self.name)
        print("Description: "+self.description)
        print("Author: "+self.author)
    def init(self):
        self.name=""
        self.author=""
        self.description=""
