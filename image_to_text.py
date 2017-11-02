import cv2
import numpy as np
from PIL import Image
import pytesseract
import os

def teardown():
  camera.release()
  cv2.destroyAllWindows()

# Taken from https://www.youtube.com/watch?v=83vFL6d57OI
def process_image(image_path):
  img = cv2.imread(image_path)

  gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  kernel = np.ones((1,1), np.uint8)
  img = cv2.dilate(gray_image, kernel, iterations=1)
  img = cv2.erode(img, kernel, iterations=1)

  cv2.imwrite(image_path + "_removed_noise.png", img)
  img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
  cv2.imwrite(image_path + "_thresh.png", img)
  result = pytesseract.image_to_string(Image.open(image_path + "_thresh.png"))
  print(result)
  os.system("say " + "'" + result + "'")
  teardown()


# SETUP
camera_port = 1
camera = cv2.VideoCapture(camera_port)

while True:
  ret, frame = camera.read()
  cv2.imshow('window',frame)
  k = cv2.waitKey(1) & 0xFF
  if k == ord('a'):
    print('capturing an image')
    cv2.imwrite('camera_image.png', frame)
  if k == ord('q'): #press 'q' to stop
    print('quitting')
    break

teardown()


process_image("camera_image.png")

