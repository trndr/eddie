import sys
import urllib.request
import hashlib
from html.parser import HTMLParser
import json
import socket
from collections import OrderedDict

class HTMLHeadSimplifier(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inHead=False
        self.addData=False
        self.condensedHeader=""
    def handle_starttag(self, tag, attrs):
        if (tag=="head"):
            self.inHead=True
        else:
            if self.inHead:
                if tag=="title":
                    self.addData=True
                    self.condensedHeader+=tag
                if tag=="script":
                    for i in attrs:
                        for j in i:
                            if j=="src":
                                self.condensedHeader+=str(tag)+str(attrs)
                if tag=="meta":
                    self.condensedHeader+=str(tag)+str(attrs)
                if tag=="link":
                    self.condensedHeader+=str(tag)+str(attrs)
    def handle_endtag(self, tag):
        if (tag=="head"):
            self.inHead=False
        else:
            self.addData=False
    def handle_data(self, data):
        if self.inHead and self.addData:
            self.condensedHeader+=data

def getHeadSimplified(text):
    htmlParser=HTMLHeadSimplifier()
    htmlParser.feed(text)
    return(htmlParser.condensedHeader)


def SimpleHtmlHeader(url):
    #req=urllib.request.Request(url)
    response=OrderedDict()
    try:
        req=urllib.request.urlopen(url, timeout=2)
        response["code"]=req.code
        for i in req.info():
            response[i]=req.info()[i]
        text=req.read().decode()
        text=getHeadSimplified(text)
        text=text.encode()
        response["condensedHead"]=text
        response["status"]=req.reason
    except urllib.error.HTTPError as req:
        response["code"]=req.code
        for i in req.info():
            response[i]=req.info()[i]
        response["status"]=req.reason
    except Exception as ex:
        response["status"]=str(ex)
    return(response)
def identifyByHttp(arg):
    url="http://"+arg[0]
    return(str(SimpleHtmlHeader(url)))
def getHttpResponse(arg, port=80):
    response={}
    try:
        a=socket.create_connection((arg, port))
        a.close()
        
        url="http://"+arg+":"+str(port)
        response=SimpleHtmlHeader(url)
        try:
            response.pop("Date")
        except:
            pass
        finger=""
        for element in response:
            finger+=str(element) + str(response[element])
        response["sha1"]=hashlib.sha1(finger.encode()).hexdigest()
        try:
            response.pop("condensedHead")
        except:
            pass
    except Exception as ex:
        response["status"]=ex.strerror

    return(response)
def getTelnetResponse(arg, port=23):
    response={}
    message=b''
    try:
        response["status"]="connected"
        a=socket.create_connection((arg, port))
        a.settimeout(1.0)
        message=b''
        while True:
            try:
                message+=a.recv(512)
            except:
                break
        response["sha1"]=hashlib.sha1(message).hexdigest()
        a.close()
    except Exception as ex:
        response["status"]=ex.strerror
    return(response)
    
def getFingerPrints(ipaddress, htmlPort=80, telnetPort=23):
    fingerPrints={"possibleNumberOfMatches":0}
    if (htmlPort>0):
        fingerPrints["http"]=getHttpResponse(ipaddress, htmlPort)
        if "sha1" in fingerPrints["http"]:
            fingerPrints["possibleNumberOfMatches"]+=1
    if (telnetPort>0):
        fingerPrints["telnet"]=getTelnetResponse(ipaddress, telnetPort)
        if "sha1" in fingerPrints["telnet"]:
            fingerPrints["possibleNumberOfMatches"]+=1
    return(fingerPrints)

def findMatches(fingerPrints):
    f=open("signatures", "r")
    routers=[]
    try:
        routers=json.load(f)
    except:
        pass
    f.close()
    matches={}
    for router in range(len(routers)):
        try:
            if (routers[router]["http"]["sha1"]==fingerPrints["http"]["sha1"]):
                if (router not in matches):
                    matches[router]=1
                else:
                    matches[router]+=1
        except KeyError:
            pass
        try:
            if (routers[router]["telnet"]["sha1"]==fingerPrints["telnet"]["sha1"]):
                if (router not in matches):
                    matches[router]=1
                else:
                    matches[router]+=1
        except KeyError:
            pass
    sortedMatches=sorted(matches.items(), key=lambda x:-x[1])
    possibleMatchse=list(map(lambda x: routers[x[0]],sortedMatches))
    for i in range(len(possibleMatchse)):
        possibleMatchse[i]["matches"]=sortedMatches[i][1]
    return(possibleMatchse)

def jsonify(fingerPrints):
    return(json.dumps(fingerPrints, indent=4, sort_keys=True))



if __name__=="__main__":
    f=open("signatures2", "r")
    routers=[]
    try:
        routers=json.load(f)
    except:
        pass
    f.close()
    info={"Manufacturer":"D-Link",
            "Model":"DLS-320B",
            "Hardware version":"Z1",
            "Firmware":"Vanilla",
            "OS":"ZyNOS",
            "Version":"v1.04"
            }
    info["http"]=getHttpResponse(sys.argv[1])
    info["telnet"]=getTelnetResponse(sys.argv[1])
#    routers=[info]
    foundMatch=False
    for i in routers:
        if i["http"]["sha1"]==info["http"]["sha1"]:
            print(i)
    routers.append(info)
    f=open("signatures2", "w")
    f.write(json.dumps(routers, indent=4, sort_keys=True))
    f.close()
