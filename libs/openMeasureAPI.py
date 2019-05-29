##################################################################
##################################################################
## openMeasureAPI.py			                                ##
## Author: Julio A. Reyes-Munoz		                            ##
##################################################################
##################################################################

import requests
import pandas as pd
from io import BytesIO
import sys

# requests.get('http://127.0.0.1:5000/openmeasure/command/execute/startIperfSrv)
# http://127.0.0.1:5000/openmeasure/api/measure?type=all&duration=10&period=1&srcIP=127.0.0.1&dstIP=127.0.0.1&id=5300

def measure(jobType, duration, period, srcIP, dstIP, host='', jobId='' ):
    if host == '':
        host = srcIP
        
    if jobId == '':
        mReq = requests.get('http://' + host + ':5000/openmeasure/api/measure?type=' + jobType + '&duration=' + duration + '&period=' + period + '&srcIP=' + srcIP + '&dstIP=' + dstIP)
    else:
        mReq = requests.get('http://' + host + ':5000/openmeasure/api/measure?type=' + jobType + '&duration=' + duration + '&period=' + period + '&id=' + jobId + '&srcIP=' + srcIP + '&dstIP=' + dstIP)

    return mReq.text
    
    
def retrieveData(jobId, srcIP, host=''):
    if host == '':
        host = srcIP

    mReq2 = requests.get('http://' + host + ':5000/openmeasure/api/retreive?id=' + jobId + '&srcIP=' + srcIP)
    
    data = pd.read_csv(BytesIO(mReq2.content))
    
    return data


def retrieveCSV(jobId, srcIP, host=''):
    if host == '':
        host = srcIP

    mReq2 = requests.get('http://' + host + ':5000/openmeasure/api/retreive?id=' + jobId + '&srcIP=' + srcIP)
    
    data = pd.read_csv(BytesIO(mReq2.content))
    data.to_csv(jobId + '.csv')	
    
    return 0
