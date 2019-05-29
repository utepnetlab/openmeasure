#!flask/bin/python

##################################################################
##################################################################
## openMeasure			                                    ##
## Author: Julio A. Reyes-Munoz		                ##
##################################################################
##################################################################
# This is the main openMeasure source code. This script uses Flask
# to run the server and to handle the incoming http requests.
#
# 			HOW TO USE:
# 1. All computers must meet the following dependencies: ping and
#    iperf3 binaries, flask and pandas python libraries
# 2. Execute 'python openMeasure.py' on all the hosts involved
# 3. Send the corresponding http requests through a web browser or
#    a python script
#
# A csv file with the corresponding measurements will be created
# inside the jobs folder. This file can be remotely retrieved.
#-----------------------------------------------------------------


# Import libraries
import sys
from flask import Flask, request, send_file
import subprocess
import requests
sys.path.append('./libs')
import execMeasure as em


# Create instance of Flask:
app = Flask('openMeasure')


# In the measure path, get the corresponding measurements and create CSV file:
@app.route('/openmeasure/api/measure', methods=['GET'])
def measure():
    if request.method == 'GET':
        #print(request.host)           # 127.0.0.1:5000
        #print(request.host_url)       # http://127.0.0.1:5000/
        #print(request.remote_addr)    # 127.0.0.1
        #print(request.url)            # http://127.0.0.1:5000/openmeasure/api/measure?type=all&duration=4&id=5390&srcIP=127.0.0.1&dstIP=127.0.0.1
        #print(request.url_root)       # http://127.0.0.1:5000/
        #print(request.endpoint)       # measure
        #print(request.base_url)       # http://127.0.0.1:5000/openmeasure/api/measure

        # Handling URL parameters:
        #------------------------------------------------------------------------------------- 
        param0 = request.args				# Get job parameters from http request
        param = {}
        for i in param0:
            param[i] = param0[i]
            
        # The following lines handle the case when some parameter is missing:
        if not('type' in param):
            return "Please input the type of measurment to perform (type)"
        if not('srcIP' in param):
            return "Please input the ip address of the source host (srcIP)"
        if not('dstIP' in param):
            return "Please input the ip address of the destination host (dstIP)"
        if not('duration' in param):
            return "Please input the duration of the measurement in seconds (duration)"
        if not('period' in param):
            return "Please input the period of the samples in seconds (period)"
        if not('id' in param):
            param ['id'] = em.getEpoch()
        if len(param)>6:
            return "URL ERROR! (Too many parameters)"

        myIP = request.host
        myIP = myIP.split(':')[0]
        if myIP == param['srcIP']:  # When I'm the source host
            #mReq = requests.get('http://' + param['dstIP'] + ':5000/openmeasure/command/execute/startIperfSrv')
            #if mReq.text == 'OK':
            # Execution section:
            #-----------------------------------------------------------------------------------------
            # The following lines call the functions for executing the measurements and formatting the
            # data, based on the measurement type requested:
            if (param['type'] == "delay"):
                jobEx = em.execDelayRT(param)			# Job execution
                #fmtData = ff.fmtDly(param['id'])		# Format the data
            elif (param['type'] == "loss"):
                jobEx = em.execLossRT(param)			# Job execution
                #fmtData = ff.fmtLoss(param['id'])		# Format the data
            elif (param['type'] == "throughput"):
                jobEx = em.execThroughputRT(param)			# Job execution
                #fmtData = ff.fmtThrou(param['id'])		# Format the data
            elif param['type'] == "all":
                jobEx = em.execAllRT(param)				# Job execution
                #fmtData = ff.getboth(param['id'])		# Format the data
            else:
                return "The selected mesurement type does not exist. (types: all, delay, loss, throughput)"

            #ff.createCSV(fmtData)				# Create CSV file
            #ff.rmTemp(param)					# Remove temporary file
            
            return param['id']
            #else:
            #  return "Iperf Server cannot be initialized!"

        else:   # When I'm not the source host
        # send request to the source: /measure?type=' + jobType + '&duration=' + duration + '&period=' + period + '&id=' + jobId + '&srcIP=' + srcIP + '&dstIP=' + dstIP)
            mReq = requests.get('http://' + param['srcIP'] + ':5000/openmeasure/api/measure?type=' + param['type'] + '&duration=' + param['duration'] + '&period=' + param['period'] + '&id=' + param['id'] + '&srcIP=' + param['srcIP'] + '&dstIP=' + param['dstIP'])
            # FIX SHORT-TERM TODO NUM 3:
            return param['id']  # Instead of returning request sent to src, returns the jobID 

      
# In the retreive path, get the CSV file corresponding to a job ID:
@app.route('/openmeasure/api/retreive', methods=['GET'])
def retrieve():
    if request.method == 'GET':
    # Handling URL parameters:
    #------------------------------------------------------------------------------------- 
        param = request.args				# Get job parameters from http request
        
        # Checking the parameters of the query:
        try:
            jobID = param['id']
        except KeyError as e:
            return "Please input the ID of the measurements to retrieve"
        try:
            srcIP = param['srcIP']
        except KeyError as e:
            return "Please input a OpenMeasure host in the measured network"  
        if len(param)>2:
            return "URL ERROR! (Too many parameters)"
        myIP = request.host
        myIP = myIP.split(':')[0]
        if myIP == param['srcIP']:   # When I'm the source host
            csvName = './jobs/' + jobID + '.csv'		# csv to retrieve
  
            # Sending the requested file, and handling the event where the file does not exist:
            try:
                return send_file(csvName,mimetype='text/csv',as_attachment=True,attachment_filename=(jobID + '.csv'))
            except:
                return "Job " + jobID + " was not found at " + srcIP + "!"
        else:   # When I'm not the source host
            mReq = requests.get('http://' + param['srcIP'] + ':5000/openmeasure/api/retreive?id=' + param['id'] + '&srcIP=' + param['srcIP'])
            return mReq.content


# Query for starting the iperf server to handle one conection:
@app.route('/openmeasure/command/execute/startIperfSrv', methods=['GET'])
def startIperfSrv():
    if request.method == 'GET':
        # Execute iperf3 in server mode as a daemon:
        out = subprocess.call(['iperf3', '-sD', '-1'])
        print('Iperf Srv Started')
        return 'OK'


# Running openMeasure:
if __name__ == '__main__':
    #app.run(debug=False)				# Uncomment to work on the localhost
    app.run(debug=False,host='0.0.0.0')		# Uncomment to work on a local network








