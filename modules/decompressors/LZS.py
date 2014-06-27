import sys
#LZS decompressor
#Pythonized version of http://piotrbania.com/all/utils/RomDecoder.c by Poitr Bania
ROM={
    "version":0,
    "size":0,
    "offset":0,
    "name":""}

def convert16to9bit(s):
    return(s[0]<<8^s[1])

def getBits(Lzs, numberOfBits):
    bytePos=int(Lzs["srcPos"]/8)
    bitPos=Lzs["srcPos"]%8
    out=(Lzs["src"][bytePos]<<16)|(Lzs["src"][bytePos+1]<<8)|(Lzs["src"][bytePos+2])
    out=(out>>(24-numberOfBits-bitPos))&((1<<numberOfBits)-1)
    Lzs["srcPos"]+=numberOfBits
    return (out)
def getLen(Lzs):
    bits=0
    length=2;
    while(True):
        bits=getBits(Lzs, 2)
        length+=bits
        if((bits!=3)or(length>=8)):
            break
    if (length==8):
        while(True):
            bits=getBits(Lzs, 4)
            length+=bits
            if(bits!=15):
                break
    return(length)

def lzsUnpack(Lzs):
    for i in range(len(Lzs["src"])):
        tag=getBits(Lzs, 1)
        if tag==0:
            Lzs["dst"]+=chr(getBits(Lzs, 8)).encode()
            continue
        tag=getBits(Lzs, 1)
        offset = getBits(Lzs, (7 if (tag == 1) else 11))
        if (tag==1 and offset==0):
            break
        repeats=getLen(Lzs)
        for i in range(repeats):
            Lzs["dst"]+=chr(Lzs["dst"][-offset]).encode()

def lzsUnpackFile(data):
    BASE_OFFSET=0x2000
    PASS_OFFSET=0x14

    base=BASE_OFFSET
    files={}
    while(True):
        ROM["size"]=(convert16to9bit(data[base+2:base+4]))
        ROM["offset"]=(convert16to9bit(data[base+4:base+6]))
        ROM["name"]=(data[base+6:base+20]).decode().rstrip(chr(0x00))
        if (len(ROM["name"])<1):
            break
        Lzs={
            "src":data[(BASE_OFFSET+ROM["offset"]+0xc+4) : (BASE_OFFSET+ROM["offset"]+0xc+4+ROM["size"])],
            "srcPos":0,
            "dst":b'',
            }
        if (len(Lzs["src"])>0 and Lzs["src"][0]!=0x00):
            lzsUnpack(Lzs);
            files[ROM["name"]]=Lzs["dst"]
        base+=20
    return(files)

#files=lzsUnpackFile(text)
#print(list(files.keys()))
#f=open(sys.argv[1], "rb")
#text = f.read()
#f.close()
