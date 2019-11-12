from __future__ import print_function
import argparse
import sys
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import datetime


# helpers
def get_substring(s, leader, trailer):
    end_of_leader = s.index(leader) + len(leader)
    start_of_trailer = s.index(trailer, end_of_leader)
    return s[end_of_leader:start_of_trailer]


def now():
    return datetime.now().strftime('[%y.%m.%d %H:%M:%S] ')


def printunbuff(string):
    print(string, flush=True)

def check():
    found = False  
    if (args.severity == 0):
       # don't want to break on severity so return.
       return found
    with open('sr.xml') as f:
        datafile = f.readlines()
    for line in datafile:
        if 'numflawssev' in line:
#            print('numflawssev processing')
#            print(line)
            if not('numflawssev5="0"' in line): 
#               print('at least one sev 5')
#               print(line)
               found = True
            if (not('numflawssev4="0"' in line) and (args.severity <= 4)): 
#               print('at least one sev 4')
#               print(line)
               found = True
            if (not('numflawssev3="0"' in line) and (args.severity <= 3)): 
#               print('at least one sev 3')
#               print(line)
               found = True
        elif 'severity_desc' in line:
            if ('severity_desc="Very High"' in line):
#               print('at least one very high sca finding')            
#               print(line)
               found = True
            elif (('severity_desc="High"' in line) and (args.severity <= 4)):
#               print('at least one high sca finding')            
#               print(line)
               found = True
            elif (('severity_desc="Medium"' in line) and (args.severity <= 3)):
#               print('at least one Medium sca finding')            
#               print(line)
               found = True
    return found  # Because you finished the search without finding

# args
parser = argparse.ArgumentParser(description='A Python wrapper to the Veracode Java API jar, '
                                             'providing "break the build" functionality',
                                 epilog='Any additional arguments will be passed through to the API jar.',
                                 allow_abbrev=False)
parser.add_argument('apiwrapperjar', help='File path to Veracode API Java wrapper')
parser.add_argument('vid', help='Veracode API credentials ID')
parser.add_argument('vkey', help='Veracode API credentials key')
parser.add_argument('-sr', '--summaryreport', default="sr.xml", help='File path to put summary report in')
parser.add_argument('-bid','--build_id', help='Build id for the build to check')
parser.add_argument('-s','--severity', type=int, default=0,
                    help='Severity to break the build on. 0=none, 1=info, 2=low, 3=medium, 4=high, 5=very high')
args, unparsed = parser.parse_known_args()

#print(args.severity)
#print(args.build_id)
#print(args.summaryreport)
#exit(0)

# setup
base_command = ['java', '-jar', args.apiwrapperjar, '-vid', args.vid, '-vkey', args.vkey]

#print('Build info call being made')
command = base_command + ['-action', 'SummaryReport', '-outputfilepath',args.summaryreport, '-buildid', args.build_id]            
build_info = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
fail = check()
printunbuff(now()+'Checked for flaws severity '+str(args.severity)+' and above.  Fail build = '+str(fail)) 
#print('after check call')
sys.exit(fail)
