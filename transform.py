import numpy as np
import cv2
import pytesseract

inputImage = cv2.imread('cleanText.png')


def transform_image(image):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	kernel = np.ones((1,1), np.uint8)
	dilated = cv2.dilate(gray, kernel, iterations=1)
	eroded = cv2.erode(dilated, kernel, iterations=1)
	final = cv2.adaptiveThreshold(eroded, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 10)

	ratio = image.shape[0] / 500.0
	r = 500.0 / image.shape[1]
	dim = (500, int(image.shape[0] * r))
	orig = image.copy()
	image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(gray, 75, 200)

	img, cnts, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

	rectangleShape = False
	# loop over the contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	 
		# if our approximated contour has four points, then we
		# can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			rectangleShape = True
			break
	 

	if rectangleShape:
		outline = image.copy()
		cv2.drawContours(outline, [screenCnt], -1, (0, 255, 0), 2)
		cv2.imshow("Outline", outline)

		warped = four_point_transform(orig, screenCnt.reshape(4, 2) / r)

		warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
		final = cv2.adaptiveThreshold(warped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 15)

	return final





def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
 
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
 
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
 
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
 
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
 
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
 
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
 
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
 
	# return the warped image
	return warped 
# perform the actual resizing of the image and show it

final = transform_image(inputImage)
cv2.imwrite('warped.png', final)

# 	if len(approx) == 4:
# 		screenCnt = approx
# 		break
 
# show the contour (outline) of the piece of paper
#print "STEP 2: Find contours of paper"
# cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
# cv2.imshow("Outline", image)


# 