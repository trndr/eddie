import argparse
import fingerPrint
import imp
import core.database
def identify(args):
    descriptionStrings=["Manufacturer","Model", "Hardware version", "Firmware", "Version", "OS"]
    fingerPrints=(fingerPrint.getFingerPrints(args.ipaddress, htmlPort=args.htmlport, telnetPort=args.telnetport))
    candidates=fingerPrint.findMatches(fingerPrints)
    if len(candidates)>0:
        print("Most likely candidate with "+str(candidates[0]["matches"])+" matches out of "+str(fingerPrints["possibleNumberOfMatches"]))
        for i in descriptionStrings:
            if i in candidates[0]:
                print(i+": "+candidates[0][i])
        exploits=db.findExploits(candidates[0]["Model"])
        if (len(exploits)>0):
            print("It has "+str(len(exploits))+" known exploit" +("s" if len(exploits)>1 else ""))
        else:
            print("No exploits for this device have been added yet")
    return((fingerPrints,candidates, exploits))
def exploit(args):
    fingerPrints, candidates, exploits=identify(args)
    if (len(exploits)>0):
        for exploitNumber in range(len(exploits)):
            identificationNumber, name, description, author, filename, filepath=exploits[exploitNumber]
            print("-"*80)
            print(str(exploitNumber+1)+":")
            print("Name: "+name)
            print("Description: "+description)
            print("Author: "+author)

        print("-"*80)
        print("""Standard disclaimer:
        Only for research and educational purposes.
        Do NOT use this software on any device without explicit permission
        Any damage material or otherwise, which might be or is caused by this software is the sole liability of the user of the software""")
        answer=input("If you fully understand the disclaimer and are you absolutely sure you want to continue\n Select which exploit to run: ")
        if answer.isdigit() and int(answer)-1 in range(len(exploits)):
            exploitNumber=int(answer)-1
            identificationNumber, name, description, author, filename, filepath=exploits[exploitNumber]
            exploitClass=imp.load_source("plugins.exploits."+filename, filepath)
            exploitMethod=exploitClass.Exploit()
            exploitMethod.exploit(args.ipaddress)

def jsonfingerprint(args):
    fingerPrints=(fingerPrint.getFingerPrints(args.ipaddress, htmlPort=args.htmlport, telnetPort=args.telnetport))
    if ("possibleNumberOfMatches" in fingerPrints):
        fingerPrints.pop("possibleNumberOfMatches")
    print(fingerPrint.jsonify(fingerPrints))

parser=argparse.ArgumentParser(
        description="Eddie the script kiddie butler is made to assist in identifying embedded devices",
        )
parser.add_argument("ipaddress", type=str, help="IP address of the target")
parser.add_argument("--html-port", type=int, help="HTML Port (default: %(default)s)", default=80, dest="htmlport", metavar="<port>")
parser.add_argument("--telnet-port", type=int, help="Telnet Port (default: %(default)s)", default=23, dest="telnetport", metavar="<port>")
group= parser.add_mutually_exclusive_group()
group.add_argument("--identify", dest="method", action="store_const", const=identify)
group.add_argument("--exploit", dest="method", action="store_const", const=exploit)
group.add_argument("--json-fingerprint", dest="method", action="store_const", const=jsonfingerprint)
parser.set_defaults(method=identify)

db=core.database.Database()

def main(args):
    args.method(args)

if __name__=="__main__":
    main(parser.parse_args())
