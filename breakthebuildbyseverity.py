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
    if (args.debug):
       print(string, flush=True, file=sys.stderr)

def check():
    found = 0  
    if (args.severity == 0):
       # don't want to break on severity so return.
       return found
    with open(args.summaryreport) as f:
        datafile = f.readlines()
    for line in datafile:
        if 'numflawssev' in line:
            printunbuff('numflawssev processing')
            printunbuff(line)
            if not('numflawssev5="0"' in line): 
               printunbuff('at least one sev 5')
               printunbuff(line)
               found = 1
            if (not('numflawssev4="0"' in line) and (args.severity <= 4)): 
               printunbuff('at least one sev 4')
               printunbuff(line)
               found = 1
            if (not('numflawssev3="0"' in line) and (args.severity <= 3)): 
               printunbuff('at least one sev 3')
               printunbuff(line)
               found = 1
        elif 'severity_desc' in line:
            if ('severity_desc="Very High"' in line):
               printunbuff('at least one very high sca finding')            
               printunbuff(line)
               found = 1
            elif (('severity_desc="High"' in line) and (args.severity <= 4)):
               printunbuff('at least one high sca finding')            
               printunbuff(line)
               found = 1
            elif (('severity_desc="Medium"' in line) and (args.severity <= 3)):
               printunbuff('at least one Medium sca finding')            
               printunbuff(line)
               found = 1
    return found  

# args
parser = argparse.ArgumentParser(description='A Python wrapper to the Veracode Java API jar, '
                                             'providing "break the build by severity" functionality',
                                 epilog='Any additional arguments will be passed through to the API jar.',
                                 allow_abbrev=False)
parser.add_argument('apiwrapperjar', help='File path to Veracode API Java wrapper')
parser.add_argument('vid', help='Veracode API credentials ID')
parser.add_argument('vkey', help='Veracode API credentials key')
parser.add_argument('-s','--severity', type=int, default=0,
                    help='Severity to break the build on. 0=none, 1=info, 2=low, 3=medium, 4=high, 5=very high')
parser.add_argument('-b', '--breakthebuild', action="store_true",
                    help='Exit code non-zero if scan does not pass policy')
parser.add_argument('-wi', '--waitinterval', type=int, default=60,
                    help='Time interval in seconds between scan policy status checks, default = 60s')
parser.add_argument('-wm', '--waitmax', type=int, default=3600,
                    help='Maximum time in seconds to wait for scan to complete, default = 3600s')
parser.add_argument('--debug', default=False, help='Print debug messages if True')
parser.add_argument('-sr', '--summaryreport', default="sr.xml", help='File to create summary report in')
args, unparsed = parser.parse_known_args()

# setup
base_command = ['java', '-jar', args.apiwrapperjar, '-vid', args.vid, '-vkey', args.vkey]

# uploadandscan wrapper action
command = base_command + ['-action', 'UploadAndScan'] + unparsed
printunbuff(now() + 'Running command: ' + ' '.join(['java', '-jar', args.apiwrapperjar, '-vid', args.vid[:6] +
                                                    '...', '-vkey', '*****', '-action', 'UploadAndScan'] + unparsed))
upload = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
printunbuff(upload.stdout.decode())

if upload.returncode == 0:
    try:
        app_id = get_substring(upload.stdout.decode(), 'appid=', ')')
        build_id = get_substring(upload.stdout.decode(), 'The build_id of the new build is "', '"')
    except ValueError as e:
        printunbuff(e)
        sys.exit(1)

    # watch scan status for policy pass/fail
    if args.breakthebuild:
        command = base_command + ['-action', 'GetBuildInfo', '-appid', app_id, '-buildid', build_id]

        wait_so_far = 0
        while wait_so_far <= args.waitmax:
            time.sleep(args.waitinterval)
            build_info = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            printunbuff(now() + 'Checking scan status [' +
                        str(wait_so_far // args.waitinterval) + '/' +
                        str(args.waitmax // args.waitinterval) + ']')

            if 'results_ready="true"' in build_info.stdout.decode():
                # Wait for policy compliance calculation to complete
                while True:
                    policy_compliance_status = get_substring(build_info.stdout.decode(), 'policy_compliance_status="', '"')
#                    printunbuff(now()+'Scan complete, policy compliance status: '+ policy_compliance_status)
                    if policy_compliance_status not in ['Calculating...', 'Not Assessed']:
                        printunbuff(now()+'Scan complete, policy compliance status: '+ policy_compliance_status)
                        if policy_compliance_status in ['Conditional Pass', 'Pass', 'Did Not Pass']:
                            command = base_command + ['-action', 'SummaryReport', '-outputfilepath='+str(args.summaryreport), '-buildid', build_id]            
                            build_info = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            fail = check()
                            if fail == 0:
                               print(now()+'Checked for flaws severity '+str(args.severity)+' and above.  Fail build = False', file=sys.stderr) 
                               sys.exit(0)
                            else:
                               print(now()+'Checked for flaws severity '+str(args.severity)+' and above.  Fail build = True', file=sys.stderr) 
                               sys.exit(1)
                    else:
                        time.sleep(args.waitinterval)
                        build_info = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        printunbuff(now() + 'Scan complete, checking policy status')
            else:
                wait_so_far += args.waitinterval

        printunbuff(now() + 'Scan did not complete within maximum wait time.')
        sys.exit(1)
else:
    sys.exit(upload.returncode)
