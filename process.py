import cv2
import numpy as np
from PIL import Image
import pytesseract
import os
import serial
from threading import Timer
import picamera
import enchant
import re
from gtts import gTTS
import os
import transform

def getVariables():
  	global bpmCalibrated, calibrated, realBPM, awakeAvgCalculated, awakeAvg, image_processed, sanitized_str
	return (bpmCalibrated, calibrated, realBPM, awakeAvgCalculated, awakeAvg, image_processed, sanitized_str)

def calibrate():
    global calibrated
    calibrated = True
    print "calibrated: " + str(calibrated)

# SETUP
d = enchant.Dict("en_US")
calibrated = False
sanitized_str = ""
image_processed = False

# process_image("good_textonly.png")

tempBPMThreshold = 55
awakeCount = 0
asleepCount = 0
lastStateAwake = True
awakeAvgCalculated = False
awakeTotal = 0
awakeAvg = 0
bpmCalibrated = False
bpmCalibratedCount = 0
realBPM = 0

def main():
	camera = picamera.PiCamera()
	ser = serial.Serial('/dev/ttyACM0')
	print ser.name

  	global calibrated, tempBPMThreshold, awakeCount, asleepCount, lastStateAwake, awakeAvgCalculated, awakeTotal, awakeAvg, bpmCalibrated, bpmCalibratedCount, realBPM

	print "starting loop"

	t = Timer(15, calibrate)
 	t.start()
	
	while True:
	  print "calibrated: " + str(calibrated)
	
	  awake = True
	  BPMSerial = ser.readline()
	#  print 'BPMSerial' + BPMSerial
	  stringBPM = str(BPMSerial).split('\\')[0]
	#  print 'stringBPM' + stringBPM
	  finalStringBPM = stringBPM
	  print 'finalBPM: ' + finalStringBPM
	  #realBPM = 0
	  try:
	    # if finalStringBPM != '':
	    BPM = int(finalStringBPM)
	    if BPM < 80:
	      bpmCalibratedCount += 1
	      realBPM = BPM
	      if not bpmCalibrated and bpmCalibratedCount == 15:
	        bpmCalibrated = True
	    else:
	      bpmCalibratedCount = 0
	  except Exception as e:
	    print e
	  print "bpm calibrated: " + str(bpmCalibrated)
	  if calibrated and bpmCalibrated:
	    # asleep heart rate is typically 10-15 beats per minute lower than awake and resting heart rate
	    awake = (realBPM > (awakeAvg-10)) if awakeAvgCalculated else (realBPM > tempBPMThreshold)
	    print "Awake: " + str(awake)
	
	    # if awakeAvg heartrate has not been calculated yet, calculate it
	    if awake and not awakeAvgCalculated:
	      awakeTotal += realBPM
	
	    if awake != lastStateAwake:
	      awakeCount = 1 if awake else 0
	      asleepCount = 0 if awake else 1
	      if not awakeAvgCalculated:
	        awakeTotal = 0
	    else:
	      awakeCount += 1 if awake else 0
	      asleepCount += 0 if awake else 1
	    lastStateAwake = awake
	
	    if awake and not awakeAvgCalculated:
	      awakeAvg = awakeTotal / awakeCount
	      if awakeCount == 20:
	        awakeAvgCalculated = True
	        print "Average awake heart rate calcalated: " + str(awakeAvg)
	
	   #if asleepCount == 10:
            if calibrated:
	      image_processed = False
	      print 'user asleep, capturing image'
	      camera.capture('text.png')
	      inputImage = cv2.imread('text.png')
	      finalImage = transform.transform_image(inputImage)
	      cv2.imwrite('processed.png', finalImage)

	      sanitized_str = pytesseract.image_to_string(Image.open("warped.png"))
              print "sanitized string: " + sanitized_str
	      tts = gTTS(text=sanitized_str, lang='en')
	      tts.save("speech.mp3")
	      image_processed = True
	      os.system("mpg321 speech.mp3")
	      break
	
	  # cv2.waitKey(500) 
	
	ser.close()


if __name__ == "__main__":
	main()
