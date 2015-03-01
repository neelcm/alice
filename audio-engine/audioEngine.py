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
INITIAL_TAP_THRESHOLD = 0.05
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100  
INPUT_BLOCK_TIME = 0.025
ALPHA = 0.8
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if we get this many noisy blocks in a row, increase the threshold
OVERSENSITIVE = 0.15/INPUT_BLOCK_TIME                    
# if we get this many quiet blocks in a row, decrease the threshold
UNDERSENSITIVE = 0.15/INPUT_BLOCK_TIME 
# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME
MIN_DOWN_TIME = .25/INPUT_BLOCK_TIME
def get_rms( block ):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...
    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )
    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n
    return math.sqrt( sum_squares / count )
class TapTester(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS+1 
        self.quietcount = 0 
        self.errorcount = 0
        self.countaftertap = MIN_DOWN_TIME
    def stop(self):
        self.stream.close()
    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )
            for keyword in ["mic","input"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index
        if device_index == None:
            print( "No preferred input found; using default input device." )
        return device_index
    def open_mic_stream( self ):
        device_index = self.find_input_device()
        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)
        return stream
    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError, e:
            # dammit. 
            self.errorcount += 1
            self.noisycount = 1
            return 2
        amplitude = get_rms( block )
        self.countaftertap += 1
        if amplitude > self.tap_threshold:
            # noisy block
            self.quietcount = 0
            self.noisycount += 1
            if self.noisycount > OVERSENSITIVE:
                # turn down the sensitivity
                self.tap_threshold *= (1.0/ALPHA)
                self.noisycount = 0
        else:            
            #print "quiet block"
            # quiet block.
            if 1 <= self.noisycount <= MAX_TAP_BLOCKS and self.countaftertap >= MIN_DOWN_TIME:
                self.countaftertap = 0
            self.noisycount = 0
            self.quietcount += 1
            if self.quietcount > UNDERSENSITIVE:
                # turn up the sensitivity
                self.tap_threshold *= (1.0*ALPHA)
                self.quietcount = 0
            return 1
curVal=0
def musicLoop():
    global curVal
    tt = TapTester()
    while True:
        curVal= tt.listen()