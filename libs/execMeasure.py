##################################################################
##################################################################
## execMeasure.py			                                    ##
## Author: Julio A. Reyes-Munoz		                            ##
##################################################################
##################################################################

import subprocess
import requests
import re
import pandas as pd
import time

TIME_INTERVAL = '.5'
MAX_SAMPLE_NUMBER = 1

##############################################################################################
########################   START FUNCTIONS DECLARATION   #####################################
##############################################################################################
def getEpoch():
    # Using date on bash for timestamp
    #out = subprocess.check_output(['date','+%s.%N'])
    #out = str(out)[2:-3]
    
    # Using python time module for timestamp
    out = str(time.time())
    return out
   
#========================================================================================
def calculateJitter(delays):
    dlyVect = pd.Series(delays)
    jitter = dlyVect.diff().abs().iloc[1:].mean()
    return jitter
   
#========================================================================================
def execDelay(mParams):
# This function executes ping to get the delay, the output is saved in a temporary file
# input: job parameters from http request
# output: temporary file with the raw output of ping
    tmp = open(mParams['id'],'w')	# Open tmp file
    # Execute ping:
    mCmd = ['ping','-w',str(mParams['duration']),'-D','-i',TIME_INTERVAL,str(mParams['dstIP'])]
    out = subprocess.call(mCmd,stdout=tmp)
   
    tmp.close()				# Close tmp file

    return 0

#========================================================================================
def execLoss(mParams):
# This function executes ping, (one time each 5 seconds until reaching duration time)
# to get the packet loss, the output is saved in a temporary file
# input: job parameters from http request
# output: temporary file with the raw output of several pings
    tmp = open(mParams['id'],'w')	# Open tmp file

    ti = 5				# Time interval (run ping each ti sec)
    tt = int(mParams['duration'])	# Total running time of the experiment
    tr = tt%ti				# Remaining time
   
    # Execute ping every ti seconds:
    if ((tt/ti) > 0):
        mCmd = ['ping','-w',str(ti),'-D','-i',TIME_INTERVAL,str(mParams['dstIP'])]
        for i in range(0,int(tt/ti)):
            out = subprocess.call(mCmd,stdout=tmp)

    # Execute ping for the remaining time:
    if (tr != 0):
        mCmd = ['ping','-w',str(tr),'-D','-i',TIME_INTERVAL,str(mParams['dstIP'])]
        out = subprocess.call(mCmd,stdout=tmp)

   # Execute ping (new code added, ignoring the 5 seconds interval):
   #mCmd = ['ping','-w',str(mParams['duration']),'-D','-i',TIME_INTERVAL,str(mParams['srcIP'])]
   #out = subprocess.call(mCmd,stdout=tmp)

    tmp.close()				# Close tmp file

    return 0

#========================================================================================
def execThroughput(mParams):
# This function executes iperf3 to get the throughput, the output is saved with json
# format in a temporary file
# input: job parameters from http request
# output: temporary file with the output of iperf3 in json format
    tmp = open(mParams['id']+'','w')	# Open tmp file
   
   # Initial timestamp for Iperf:
   #mCmd = ['date','+%s.%N']   
   #tsOut = subprocess.Popen(mCmd,stdout=tmp)
   
    # Execute Iperf:
    mCmd = ['iperf3','-c',str(mParams['dstIP']),'-t',str(mParams['duration']),'-i',TIME_INTERVAL,'-J']
    out = subprocess.Popen(mCmd,stdout=tmp)

    #tsOut.wait()				# Wait for the timestamp process to finish
    out.wait()				# Wait for the iperf3 process to finish

    tmp.close()				# Close tmp file

    return 0

#========================================================================================
def execAll(mParams):
# This function executes iperf3 to get the throughput, and ping to get the packet loss and
# the delay. The output is saved in two temporary files.
# input: job parameters from http request
# output: temporary file with the raw output of several pings and the output of iperf3 in 
#         json format

    # start iperf server
    mReq = requests.get('http://' + mParams['dstIP'] + ':5000/openmeasure/command/execute/startIperfSrv')

    # Open tmp files:
    tmp = open(mParams['id']+'_iperf','w')
    tmp2 = open(mParams['id']+'_ping','w')

    ti = 5				# Time interval (run ping each ti sec)
    tt = int(mParams['duration'])	# Total running time of the experiment
    tr = tt%ti				# Remaining time
    # Initial timestamp for iperf:
    #mCmd = ['date','+%s.%N']   
    #tsOut = subprocess.Popen(mCmd,stdout=tmp)

    if mReq.text == 'OK':
    # Runnnig Iperf:
        mCmd = ['iperf3','-c',str(mParams['dstIP']),'-t',str(mParams['duration']),'-i',TIME_INTERVAL,'-J']
        outI = subprocess.Popen(mCmd,stdout=tmp)
    else:
        print("Iperf Server cannot be initialized!")

    # Execute ping every ti seconds:
    if ((tt/ti) > 0):
        mCmd = ['ping','-w',str(ti),'-D','-i',TIME_INTERVAL,str(mParams['dstIP'])]
        for i in range(0,int(tt/ti)):
            outP = subprocess.Popen(mCmd,stdout=tmp2)
            outP.wait()
            #time.sleep(int(TIME_INTERVAL))

    # Execute ping for the remaining time:
    if (tr != 0):
        mCmd = ['ping','-w',str(tr),'-D','-i',TIME_INTERVAL,str(mParams['dstIP'])]
        outP = subprocess.Popen(mCmd,stdout=tmp2)
        outP.wait()

   # Execute ping (new code added, ignoring the 5 seconds interval):
   #mCmd = ['ping','-w',str(mParams['duration']),'-D','-i',TIME_INTERVAL,str(mParams['srcIP'])]
   #outP = subprocess.Popen(mCmd,stdout=tmp2)
   #outP.wait()
   
    # Wait for the processes to finish:
    #tsOut.wait()
    outI.wait()
    # Close temporary files:
    tmp.close()
    tmp2.close()

    return 0

#========================================================================================
def execThroughputRT(mParams):
    tmpFile = open('./jobs/' + mParams['id']+'.csv','a')	# Open tmp file
    tmpFile.write('time,bandwidth(bps)\n')
    tmpFile.close()				# Close tmp file
   
    p1 = re.compile('bits_per_second')
    p2 = re.compile('\d+\.\d+')
    #mCmd = ['iperf3', '-c', '127.0.0.1', '-t', '1', '-i', '1', '-J']
    mCmd = ['iperf3','-c',str(mParams['dstIP']),'-t', '1', '-i', '1', '-J']
    ts = 0
    tInit = float(getEpoch())
    currPer = tInit + int(mParams['period'])
    tmp = []
    while((float(getEpoch()) - tInit) < int(mParams['duration'])):
        if(len(tmp) < MAX_SAMPLE_NUMBER):
            # Start Iperf Srv:
            mReq = requests.get('http://' + mParams['dstIP'] + ':5000/openmeasure/command/execute/startIperfSrv')       
            if mReq.text == 'OK':
                # Execute Iperf:
                out = subprocess.Popen(mCmd,stdout=subprocess.PIPE)
                line = out.stdout.readline().decode("utf-8")
                while(line != ''):
                    if p1.search(line):
                        bw = float(p2.findall(line)[0])
                        break
                    line = out.stdout.readline().decode("utf-8")
                tmp.append(bw)
                out.wait()				# Wait for the iperf3 process to finish
        else:
            time.sleep(1)
            print('...')
        if(float(getEpoch()) > currPer):
            print(tmp)
            avgBw = pd.Series(tmp).mean()   # Get avg bandwidth during a period
            ts = ts + int(mParams['period'])
            if(ts > int(mParams['duration'])):
                ts = int(mParams['duration'])
            tmpFile = open('./jobs/' + mParams['id']+'.csv','a')	# Open tmp file
            tmpFile.write('%.4f,%f\n' % (ts + tInit, avgBw))
            tmpFile.close()				# Close tmp file
            tmp = []
            currPer = currPer + int(mParams['period'])

    return 0
    
#========================================================================================
def execDelayRT(mParams):
    tmpFile = open('./jobs/' + mParams['id']+'.csv','a')	# Open tmp file
    tmpFile.write('time,delay(ms)\n')
    tmpFile.close()				# Close tmp file
   
    p1 = re.compile('time=\d+\.\d+')
    p2 = re.compile('\d+\.\d+')

    mCmd = ['ping','-w','3','-i', '.2', '-s', '24', str(mParams['dstIP'])]
    #mCmd = ['ping','-w','3','-i','.2','-s','24','127.0.0.1']
    
    tInit = float(getEpoch())
    currPer = 0
    ts = 0
    delays = []
    while((float(getEpoch()) - tInit) < int(mParams['duration'])):
        if(float(getEpoch()) > (tInit + currPer)):  # execute ping when time is greater than tInit plus current period
            out = subprocess.Popen(mCmd,stdout=subprocess.PIPE)
            line = out.stdout.readline().decode("utf-8")
            while(line != ''):
                if(p1.search(line)):
                    dly = p1.findall(line)
                    delays.append(float(p2.findall(dly[0])[0]))
                line = out.stdout.readline().decode("utf-8")
            avgDelay = round(pd.Series(delays).mean(),3)
            out.wait()				# Wait for the iperf3 process to finish
            currPer = currPer + int(mParams['period'])
            ts = ts + int(mParams['period'])
            if(ts > int(mParams['duration'])):
                ts = int(mParams['duration'])
            tmpFile = open('./jobs/' + mParams['id']+'.csv','a')	# Open tmp file
            tmpFile.write('%.4f,%.3f\n' % (ts + tInit, avgDelay))
            tmpFile.close()				# Close tmp file
            delays = []
            print(avgDelay)
        else:
            time.sleep(1)
            print('...')

        
    return avgDelay

#========================================================================================
def execLossRT(mParams):
    tmpFile = open('./jobs/' + mParams['id']+'.csv','a')	# Open tmp file
    tmpFile.write('time,loss(percent)\n')
    tmpFile.close()				# Close tmp file
   
    p1 = re.compile('\d+\%')
    p2 = re.compile('\d+')

    mCmd = ['ping','-w','3','-i', '.2', '-s', '24', str(mParams['dstIP'])]
    #mCmd = ['ping','-w','3','-i','.2','-s','24','127.0.0.1']
    
    tInit = float(getEpoch())
    currPer = 0
    ts = 0
    while((float(getEpoch()) - tInit) < int(mParams['duration'])):
        if(float(getEpoch()) > (tInit + currPer)):  # execute ping when time is greater than tInit plus current period
            out = subprocess.Popen(mCmd,stdout=subprocess.PIPE)
            line = out.stdout.readline().decode("utf-8")
            while(line != ''):
                if(p1.search(line)):
                    loss = p1.findall(line)[0]
                    loss = int(p2.findall(loss)[0])
                line = out.stdout.readline().decode("utf-8")
            out.wait()				# Wait for the iperf3 process to finish
            currPer = currPer + int(mParams['period'])
            ts = ts + int(mParams['period'])
            if(ts > int(mParams['duration'])):
                ts = int(mParams['duration'])
            tmpFile = open('./jobs/' + mParams['id']+'.csv','a')	# Open tmp file
            tmpFile.write('%.4f,%d\n' % (ts + tInit, loss))
            tmpFile.close()				# Close tmp file
        else:
            time.sleep(1)
            print('...')

        
    return 0
    
#========================================================================================
def execAllRT(mParams):
    tmpFile = open('./jobs/' + mParams['id']+'.csv','a')	# Open tmp file
    tmpFile.write('time,bandwidth(bps),delay(ms),loss(percent),jitter(ms^2)\n')
    tmpFile.close()				# Close tmp file
    
    # for throughput:
    p1 = re.compile('bits_per_second')
    p2 = re.compile('\d+\.\d+')
    # for delay:
    p3 = re.compile('time=\d+\.\d+')
    p4 = re.compile('\d+\.\d+')
    #for loss:
    p5 = re.compile('\d+\%')
    p6 = re.compile('\d+')
    
    
    mCmd1 = ['iperf3','-c',str(mParams['dstIP']),'-t', '1', '-i', '1', '-J']
    mCmd2 = ['ping','-w','3','-i', '.2', '-s', '24', str(mParams['dstIP'])]
    
    ts = 0
    tInit = float(getEpoch())
    iperfPer = tInit + int(mParams['period'])
    pingPer = 0
    tmp = []
    delays = []
    while((float(getEpoch()) - tInit) < int(mParams['duration'])):
        # PING section:
        if(float(getEpoch()) > (tInit + pingPer)):  # execute ping when time is greater than tInit plus current period
            out = subprocess.Popen(mCmd2,stdout=subprocess.PIPE)
            print('PING START')
            line1 = out.stdout.readline().decode("utf-8")
            while(line1 != ''):
                if(p3.search(line1)):
                    dly = p3.findall(line1)
                    delays.append(float(p4.findall(dly[0])[0]))
                if(p5.search(line1)):
                    loss = p5.findall(line1)[0]
                    loss = int(p6.findall(loss)[0])
                line1 = out.stdout.readline().decode("utf-8")
            pingPer = pingPer + int(mParams['period'])

            
        if(len(tmp) < MAX_SAMPLE_NUMBER):
            # Start Iperf Srv:
            mReq = requests.get('http://' + mParams['dstIP'] + ':5000/openmeasure/command/execute/startIperfSrv')       
            if mReq.text == 'OK':
                # Execute Iperf:
                out1 = subprocess.Popen(mCmd1,stdout=subprocess.PIPE)
                print('IPERF START')
                line = out1.stdout.readline().decode("utf-8")
                while(line != ''):
                    if p1.search(line):
                        bw = float(p2.findall(line)[0])
                        break
                    line = out1.stdout.readline().decode("utf-8")
                    avgDly = round(pd.Series(delays).mean(),3)
                    jitter = float(round(calculateJitter(delays),3))
                tmp.append(bw)
                
        else:
            time.sleep(1)
            print('...')  

            
        if(float(getEpoch()) > iperfPer):
            avgBw = pd.Series(tmp).mean()   # Get avg bandwidth during a period
            ts = ts + int(mParams['period'])
            if(ts > int(mParams['duration'])):
                ts = int(mParams['duration'])
            tmpFile = open('./jobs/' + mParams['id']+'.csv','a')	# Open tmp file
            tmpFile.write('%.4f,%f,%.3f,%d,%.3f\n' % (ts + tInit, avgBw, avgDly,loss,jitter))
            tmpFile.close()				# Close tmp file
            tmp = []
            delays = []
            iperfPer = iperfPer + int(mParams['period'])
            
        out.wait()				# Wait for the ping process to finish 
        out1.wait()				# Wait for the iperf3 process to finish

    return 0
##############################################################################################
########################   END FUNCTIONS DECLARATION   #######################################
##############################################################################################











