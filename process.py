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

def getVariables():
	return (bpmCalibrated, calibrated, realBPM, awakeAvgCalculated, awakeAvg, image_processed, sanitized_str)


# Taken from https://www.youtube.com/watch?v=83vFL6d57OI
def process_image(image_path):
  img = cv2.imread(image_path)
  image_processed = False

  gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  kernel = np.ones((1,1), np.uint8)
  dilated_img = cv2.dilate(gray_image, kernel, iterations=1)
  eroded_img = cv2.erode(dilated_img, kernel, iterations=1)

  cv2.imwrite(image_path + "_removed_noise.png", eroded_img)
  thresh_img = cv2.adaptiveThreshold(eroded_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 1, 2)
  cv2.imwrite(image_path + "_thresh.png", thresh_img)
  print "extracting text from image"
  result = pytesseract.image_to_string(Image.open(image_path + "_thresh.png"))
  print 'result text: ' + result

#  originalText = pytesseract.image_to_string(Image.open(image_path))
#  print 'original text: ' + originalText
  words = result.split()  #splitting by whitespace, newlines, tabs, etc
  file = open("textChunks.txt", "w+")

  #sanitized_str = ""
  current_sentence = ""
  pattern = re.compile("[?.,-]")
  print "converting text to speech"
  for word in words:
    if d.check(word):
      sanitized_str += word + " "
      current_sentence += word + " "
      if pattern.match(word):
        encoded_str = current_sentence.encode('utf-8').replace('"', "'")
        print encoded_str
        file.write(encoded_str + "\n")
        os.system('espeak "' + encoded_str + '"')
        current_sentence = ""
  print "sanitized string:"
  print sanitized_str
  image_processed = True
  file.close()

def calibrate(calibrated):
    #global calibrated
    calibrated = True
    print "calibrated: " + str(calibrated)
    return calibrated

# SETUP
def getGlobalVars():
	calibrated = False
	sanitized_str = ""
	image_processed = False

def main():
	d = enchant.Dict("en_US")
	camera = picamera.PiCamera()
	ser = serial.Serial('/dev/ttyACM0')
	print ser.name
	calibrated = False
	sanitized_str = ""
	image_processed = False

	# process_image("good_textonly.png")
	
	t = Timer(15, calibrate, [calibrated])
	t.start()
	
	tempBPMThreshold = 55
	awakeCount = 0
	asleepCount = 0
	lastStateAwake = True
	awakeAvgCalculated = False
	awakeTotal = 0
	awakeAvg = 0
	print "starting loop"
	bpmCalibrated = False
	bpmCalibratedCount = 0
	realBPM = 0
	print "starting loop"
	
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
	
	    if asleepCount == 10:
	      print 'user asleep, capturing image'
	      camera.capture('text.png')
	      process_image("text.png")
	      break
	
	  cv2.waitKey(500) 
	
	ser.close()


if __name__ == "__main__":
	main()
