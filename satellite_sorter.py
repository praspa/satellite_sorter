import os
import fnmatch
import json
import hashlib
import argparse
import sys
import pprint

parser = argparse.ArgumentParser(description='Parse a sat inv file.')
parser.add_argument('-f', action='store', dest='input_file', help='The satellite system cache file')
parser.add_argument('-o', action='store', dest='output_file', help='The output satellite system cache file')
parser.add_argument('-n', action='store', dest='num_hide', help='hide n of the latest check-in host ids')

results = parser.parse_args()
input_file = results.input_file
output_file = results.output_file
num_hide = int(results.num_hide)

def validateInput():
    if not os.path.isfile(input_file):
        print("error: provided satelite input file does not exist. Good-bye!")
        sys.exit()

def createEntry(hostname,path,equal):
    tmpDict = { "host":hostname,"path":path,"equal":equal }
    return tmpDict

def printReport(report):
    with open (report_file,'w') as outfile:
        json.dump(report, outfile, indent=4, sort_keys=True)

def parseFile():
    # print "DEBUG: in parseFile()\n"
    entries_dict = {}
    invh = open(input_file,"r")
    host = "init"
    beginEntry = False
    tmpList = []

    for line in invh.readlines():
        # ending with a ':' means we have found a host entry
        # and we are at the end of an entry block too
        if line.rstrip().endswith(':'):
            # print "DEBUG: FOUND A HOST: " + line
            # first case, only do this once with sentinel value
            if host == "init":
                host = line.replace(":","").rstrip()
                # print "DEBUG: first case, found host: " + host + "\n"

            # we are at the end of an entry
            if beginEntry == True:
                # flip the var
                beginEntry = False
                # sort the tmpList based on the second column of the string
                tmpList.sort(key = lambda x: x.split()[1])
                # pop off X number of entries off the list per cmd line args
                reduction = num_hide
                # only operate on positive reductions
                if num_hide > 0:
                    # only pair down the list to the max length of the list
                    if len(tmpList) < reduction:
                        reduction = len(tmpList)
                    tmpList = tmpList[:-reduction]
                # write off the previous entry block to the global dictionary
                # print "DEBUG: adding entries_dict\n"
                entries_dict[host] = tmpList
                # clear the tmpList for the next loop
                tmpList = []

                # set host the new host we find
                host = line.replace(":","").rstrip()
                # print "DEBUG: Found new host: " + host + "\n"
            continue
        # this is a real entry
        elif line[0].isdigit():
            # print "DEBUG: found a real line entry\n"
            tmpList.append(line.rstrip())
        elif line.startswith("----------"):
            # print "DEBUG: found the start of an entry block \n"
            beginEntry = True
        # header crap
        elif line.startswith("System ID"):
            continue
        # header crap
        elif line.startswith("** Generating"):
            continue
        # whitespace
        elif line.startswith(" "):
            continue
        else:
            continue
    #print "DEBUG: Closing file\n"
    invh.close()
    return entries_dict

def createReport():
    total = []

    invh = open(inventory_file)
    for line in invh:
        result = compareBaselines(line.rstrip())
        total = total + result
    invh.close()

    report = {}
    report.update({ "baseline": total })
    printReport(report)

def writeOutput(myDict):
    f = open(output_file, 'w')
    # write some header stuff
    f.write('\n')
    f.write('\n')
    f.write('** Generating system cache **\n')
    f.write('\n')

    for host in myDict:
        f.write(host + ':\n')
        f.write('System ID   Last Checkin\n')
        f.write('----------  -----------------\n')
        # write sorted lines
        for line in myDict[host]:
            f.write(line + '\n')
        # new line between entry blocks
        f.write('\n')
    f.close()  # you can omit in most cases as the destructor will call it

# main
validateInput()
entries_dict = parseFile()
writeOutput(entries_dict)
