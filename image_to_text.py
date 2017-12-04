import cv2
import numpy as np
from PIL import Image
import pytesseract
import os
import serial
from threading import Timer

calibrated = False

def teardown():
  camera.release()
  cv2.destroyAllWindows()
  ser.close()

# Taken from https://www.youtube.com/watch?v=83vFL6d57OI
def process_image(image_path):
  print("processing image")
  img = cv2.imread(image_path)
  original = img
  gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  kernel = np.ones((1,1), np.uint8)
  img = cv2.dilate(gray_image, kernel, iterations=1)
  img = cv2.erode(img, kernel, iterations=1)

  cv2.imwrite(image_path + "_removed_noise.png", img)
  img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
  cv2.imwrite(image_path + "_thresh.png", img)
  result = pytesseract.image_to_string(Image.open(image_path + "_thresh.png"))
  
  # print(result)
  # os.system("say " + "'" + result + "'")
  originalText = pytesseract.image_to_string(Image.open(image_path))
  print(originalText)
  os.system("say " + "'" + originalText + "'")

def calibrate():
    global calibrated
    calibrated = True

    print("calibrated!")

# SETUP
bpmThreshold = 85
camera_port = 1
camera = cv2.VideoCapture(camera_port)
ser = serial.Serial('/dev/cu.usbmodem1411')
print (ser.name)

t = Timer(15, calibrate)
t.start()

print("listening to user heart rate")

while True:
  # print("calibrated" + str(calibrated))
  awake = True
  ret, frame = camera.read()
  cv2.imshow('window',frame)
  k = cv2.waitKey(1) & 0xFF
  if k == ord('a'):
    print('capturing an image')
    cv2.imwrite('camera_image.png', frame)
  if k == ord('q'): #press 'q' to stop
    print('quitting')
    break
  BPMSerial = ser.readline()
  print("BPMSerial", BPMSerial)
  stringBPM = str(BPMSerial).split('\\')[0]
  print("stringBPM", stringBPM)
  finalStringBPM = (stringBPM[2:])
  print("finalBPM", finalStringBPM)
  if finalStringBPM != '':
      BPM = int(finalStringBPM)
      awake = (BPM > bpmThreshold)
      print("Awake: " + str(awake))

  if not awake and calibrated:
      print('user is asleep, capturing image')
      cv2.imwrite('text.png', frame)
      break
  cv2.waitKey(500)


teardown()

process_image("text.png")
