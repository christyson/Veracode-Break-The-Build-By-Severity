This project contains three python scripts:
    
    1. breadthebuildbyseverity.py    - this will start an upload and scan, 
                                       wait for it to complete and then once that is done 
                                       gather a summary report and fail if there are SAST 
                                       or SCA flaws of the severity selected or higher
    2. breakbyseverity.py            - this will take a build id and gather a summary report 
                                       and fail if there are SAST or SCA flaws of the severity
                                       selected or higher
    3. checkseverity.py              - this will take a summary report and fail if there are 
                                       SAST or SCA flaws of the severity selected or higher

Note: all are designed to work with python 3
    
usage: breakthebuildbyseverity.py [-h] [-s SEVERITY] [-b] [-wi WAITINTERVAL]
                                  [-wm WAITMAX]
                                  apiwrapperjar vid vkey

A Python wrapper to the Veracode Java API jar, providing "break the build by
severity" functionality

positional arguments:
  apiwrapperjar         File path to Veracode API Java wrapper
  vid                   Veracode API credentials ID
  vkey                  Veracode API credentials key

optional arguments:
  -h, --help            show this help message and exit
  -s SEVERITY, --severity SEVERITY
                        Severity to break the build on. 0=none, 1=info, 2=low,
                        3=medium, 4=high, 5=very high
  -b, --breakthebuild   Exit code non-zero if scan does not pass policy
  -wi WAITINTERVAL, --waitinterval WAITINTERVAL
                        Time interval in seconds between scan policy status
                        checks, default = 60s
  -wm WAITMAX, --waitmax WAITMAX
                        Maximum time in seconds to wait for scan to complete,
                        default = 3600s

Any additional arguments will be passed through to the API jar.


usage: breakbyseverity.py [-h] [-sr SUMMARYREPORT] [-bid BUILD_ID]
                          [-s SEVERITY]
                          apiwrapperjar vid vkey

A Python wrapper to the Veracode Java API jar, providing "check a build and
break by severity" functionality

positional arguments:
  apiwrapperjar         File path to Veracode API Java wrapper
  vid                   Veracode API credentials ID
  vkey                  Veracode API credentials key

optional arguments:
  -h, --help            show this help message and exit
  -sr SUMMARYREPORT, --summaryreport SUMMARYREPORT
                        File path to put summary report in
  -bid BUILD_ID, --build_id BUILD_ID
                        Build id for the build to check
  -s SEVERITY, --severity SEVERITY
                        Severity to break the build on. 0=none, 1=info, 2=low,
                        3=medium, 4=high, 5=very high

Any additional arguments will be passed through to the API jar.


usage: checkseverity.py [-h] [-sr SUMMARYREPORT] [-s SEVERITY] [--debug DEBUG]

A Python wrapper providing "check a build result and fail by severity"
functionality

optional arguments:
  -h, --help            show this help message and exit
  -sr SUMMARYREPORT, --summaryreport SUMMARYREPORT
                        File path to read summary report from
  -s SEVERITY, --severity SEVERITY
                        Severity to break the build on. 0=none, 1=info, 2=low,
                        3=medium, 4=high, 5=very high
  --debug DEBUG         Print debug messages if True
    