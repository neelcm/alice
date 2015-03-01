import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')

import numpy as np
import cv2
import urllib
import pyaudio
import struct
import math
import threading
import time
import cv2.cv as cv
from cv2 import *
def graphicsEngine():
    # 'M', 'J', 'P', 'G'
    # curOpen=cv2.VideoWriter("graphics.mjpg",cv.CV_FOURCC('M', 'J', 'P', 'G'), 15.0, (360, 480), False)
    curOpen=cv2.VideoWriter("graphics.mjpg", cv2.cv.CV_FOURCC(*'MJPG'), 60.0, (360, 480))

    print curOpen.isOpened()
    #curOpen=cv2.VideoWriter("test.jpg",-1,10.0, (480,360),True)
    global curVal
    oldVal=2
    stream=urllib.urlopen('http://169.254.197.231/live')
    if stream==0:
        print "uhoh"
    bytes=''
    numi=0
    while True:
        # print "going"
        bytes+=stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes= bytes[b+2:]
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
            if numi%3==0:
                if (oldVal!=curVal):
                    i= cv2.GaussianBlur( i, (25,25),0 )
                else:
                    i = cv2.cvtColor(i, cv2.COLOR_RGB2BGR)
            else:
                i = cv2.cvtColor(i, cv2.COLOR_RGB2BGR)
            numi+=1
            oldVal=curVal
            
            curOpen.write(i)

            cv2.imshow('i',i)
            # result, buf = cv2.imencode('.jpg', i)
            # print i
            
            if cv2.waitKey(1) ==27:
                exit(0)