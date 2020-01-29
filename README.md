# Veracode-Break-The-Build-By-Severity

This project contains three python scripts useful for working with Veracode projects:
    
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

## breakthebuildbyseverity.py
<pre><code>    
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
  -d, --debug           Print debug messages if present
Any additional arguments will be passed through to the API jar.
</pre></code>    

## Example stage to use this after a Veracode scan in a Jenkins pipeline
<pre><code>
   stage('Veracode Scan and Break the build by severity') {
      // Check severity of results
      sh 'wget -q -O btbbsseverity.py https://raw.githubusercontent.com/christyson/Veracode-Break-The-Build-By-Severity/master/breakthebuildbyseverity.py'
      sh 'wget -q -O veracode-wrapper.jar https://repo1.maven.org/maven2/com/veracode/vosp/api/wrappers/vosp-api-wrappers-java/${VERACODE_WRAPPER_VERSION}/vosp-api-wrappers-java-${VERACODE_WRAPPER_VERSION}.jar'

      withCredentials([usernamePassword(credentialsId: 'Veracode', passwordVariable: 'VERACODEKEY', usernameVariable: 'VERACODEID')]) {
         sh '''
           python3 btbbsseverity.py veracode-wrapper.jar ${VERACODEID} ${VERACODEKEY} -s=${VC_Severity} -b ${VC_Debug} -appname "${VC_ProjectName}" -filepath **/**.war -createprofile true -autoscan true -version ${BUILD_NUMBER}
         '''
      }
    }
</pre></code>    
![Jenkins Variables](https://github.com/christyson/Veracode-Break-The-Build-By-Severity/blob/master/bbts_Jenkins_Variables.PNG)

Note: The latest version of the Java API wrapper can be found in the Maven Central Repository under the group ID com.veracode.vosp.api.wrappers. 

## breakbyseverity.py
<pre><code>    
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
</pre></code>    

## checkseverity.py
<pre><code>    
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
</pre></code>    


## Example stage to use this after a Veracode scan in a Jenkins pipeline
<pre><code>
stage('Veracode Check status') {
      // Check severity of results
      sh 'wget -q -O checkseverity.py https://raw.githubusercontent.com/christyson/Veracode-Break-The-Build-By-Severity/master/checkseverity.py'
      sh 'wget -q -O veracode-wrapper.jar https://repo1.maven.org/maven2/com/veracode/vosp/api/wrappers/vosp-api-wrappers-java/${VERACODE_WRAPPER_VERSION}/vosp-api-wrappers-java-${VERACODE_WRAPPER_VERSION}.jar'

      withCredentials([usernamePassword(credentialsId: 'Veracode', passwordVariable: 'VERACODEKEY', usernameVariable: 'VERACODEID')]) {
         sh '''
           logFilename=${JENKINS_HOME}/jobs/${JOB_NAME}/builds/${BUILD_NUMBER}/log
           srfilename=${JENKINS_HOME}/jobs/${JOB_NAME}/builds/${BUILD_NUMBER}/sr.xml
           buildid=$(grep 'The build_id of the new build is "' ${logFilename} | grep -oE '"[0-9][0-9]*"'| tr -d '"')
           java -jar veracode-wrapper.jar -vid ${VERACODEID} -vkey ${VERACODEKEY} -action SummaryReport -outputfilepath=${srfilename} -buildid=${buildid}
           python3 checkseverity.py -s=${VC_Severity} -sr=${srfilename}
           echo $?
         '''
      } 
    }
</pre></code>
![Jenkins Variables](https://github.com/christyson/Veracode-Break-The-Build-By-Severity/blob/master/Jenkins_Variables.PNG)

Note: The latest version of the Java API wrapper can be found in the Maven Central Repository under the group ID com.veracode.vosp.api.wrappers. 
