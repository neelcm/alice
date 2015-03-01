import requests
import os
from flask import Flask, jsonify, render_template, Response, send_from_directory, send_file
import io

import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')

import cv2

import urllib 
import numpy as np

app = Flask(__name__)

left_ip = '169.254.52.155'
right_ip = ''

''' MISC '''
@app.route('/')
def hello():
    return send_from_directory('templates', 'index.html')

@app.route('/l_stream/')
def l_stream():
	stream=urllib.urlopen('http://169.254.52.155/live')
	bytes=''
	while True:
	    bytes+=stream.read(1024)
	    a = bytes.find('\xff\xd8')
	    b = bytes.find('\xff\xd9')
	    if a!=-1 and b!=-1:
	        jpg = bytes[a:b+2]
	        bytes= bytes[b+2:]
	        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
	        if (oldVal!=curVal):
	            i = cv2.cvtColor(i, cv2.COLOR_RGB2BGR)
	        else:
	            i= cv2.GaussianBlur( i, (25,25),0 );
	        oldVal=curVal
	        cv2.imshow('i',i)
	        if cv2.waitKey(1) ==27:
	            exit(0)
	        # print jpg
    	yield (b'--frame\r\n'
    		b'Content-Type: image/jpeg\r\n\r\n' + bytes + b'\r\n')

@app.route('/live2/')
def live() :
	stream=urllib.urlopen('http://169.254.52.155/live')
	bytes=''
	while True:
	    bytes+=stream.read(1024)
	    a = bytes.find('\xff\xd8')
	    b = bytes.find('\xff\xd9')
	    if a!=-1 and b!=-1:
	        jpg = bytes[a:b+2]
	        bytes= bytes[b+2:]

	        return (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + bytes + b'\r\n')

	        # send_file(io.BytesIO(bytes))
	        # i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
	        # if (oldVal!=curVal):
	        #     i = cv2.cvtColor(i, cv2.COLOR_RGB2BGR)
	        # else:
	        #     i= cv2.GaussianBlur( i, (25,25),0 );
	        # oldVal=curVal
	        # cv2.imshow('i',i)
	        # if cv2.waitKey(1) ==27:
	        #     exit(0)
	        # print jpg
	        # return '<html><body><img>' + bytes + '</img></body></html>'
	    	# yield bytes
	    	# return (b'--frame\r\n'
            #   b'Content-Type: image/jpeg\r\n\r\n' + bytes + b'\r\n')
			
	

@app.route('/r_stream/')
def r_stream():
	return "Right stream"

@app.route('/video_feed')
def video_feed():
	# return Response(live(), mimetype='multipart/x-mixed-replace; boundary=frame')
	return send_from_directory('templates', 'index.html')

def distort_frame(orig_frame):
	# distorted_frame = orig_frame
	distorted_frame = orig_frame
	return (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + distorted_frame + b'\r\n')


if __name__ == "__main__":
    app.run(debug=True)