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

calibrated = False

def teardown():
#  camera.release()
#  cv2.destroyAllWindows()
  ser.close()
  quit()

# Taken from https://www.youtube.com/watch?v=83vFL6d57OI
def process_image(image_path):
  img = cv2.imread(image_path)

  gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  kernel = np.ones((1,1), np.uint8)
  dilated_img = cv2.dilate(gray_image, kernel, iterations=1)
  eroded_img = cv2.erode(dilated_img, kernel, iterations=1)

  cv2.imwrite(image_path + "_removed_noise.png", eroded_img)
  thresh_img = cv2.adaptiveThreshold(eroded_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
  cv2.imwrite(image_path + "_thresh.png", thresh_img)
  print "extracting text from image"
  result = pytesseract.image_to_string(Image.open(image_path + "_thresh.png"))
  print 'result text: ' + result

#  originalText = pytesseract.image_to_string(Image.open(image_path))
#  print 'original text: ' + originalText
  words = result.split()  #splitting by whitespace, newlines, tabs, etc
  file = open("textChunks.txt", "w+")

  sanitized_str = ""
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
  file.close()
  teardown()

def calibrate():
    global calibrated
    calibrated = True
    print "calibrated" + str(calibrated)

# SETUP
d = enchant.Dict("en_US")
bpmThreshold = 65
#camera_port = 2
#camera = cv2.VideoCapture(camera_port)
camera = picamera.PiCamera()
ser = serial.Serial('/dev/ttyACM0')
print ser.name

process_image("good_textonly.png")

t = Timer(15, calibrate)
t.start()

print "starting loop"

while True:


  print "calibrated" + str(calibrated)
  awake = True
#  ret, frame = camera.read()
#  cv2.imshow('window',frame)
#  k = cv2.waitKey(1) & 0xFF
#  if k == ord('a'):
#    print('capturing an image')
#    cv2.imwrite('camera_image.png', frame)
#  if k == ord('q'): #press 'q' to stop
#    print('quitting')
#    break
  BPMSerial = ser.readline()
#  print 'BPMSerial' + BPMSerial
  stringBPM = str(BPMSerial).split('\\')[0]
#  print 'stringBPM' + stringBPM
#  finalStringBPM = (stringBPM[2:])
  finalStringBPM = stringBPM
  print 'finalBPM' + finalStringBPM
#  try:
  if finalStringBPM != '':
      BPM = int(finalStringBPM)
      awake = (BPM > bpmThreshold)
      print "Awake: " + str(awake)
#  except Exception as e:
#      print e

  if not awake and calibrated:
      print 'user asleep, capturing image'
#      cv2.imwrite('text.png', frame)
      camera.capture('text.png')
      break
#  cv2.waitKey(500)



  # beats = int.from_bytes(BPM, byteorder='big')
  # print(beats)


teardown()


#process_image("good_textonly.jpg")
