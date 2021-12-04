import cv2
import numpy as np
import matplotlib.pyplot as plt
from math_char_predictor import get_char_prediction

def get_contour_center(rect):
	x,y,w,h = rect
	return (x + w/2, y + h/2)

def euclidean_distance(p1, p2):
	return (((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2)) ** 0.5

def slope(p1, p2):
	if p1 == p2:
		return 0
	elif (p1[0] - p2[0]) == 0:
		return float('inf')
	else:
		return (p1[1] - p2[1]) / (p1[0] - p2[0])

def get_points_on_box(x, y, w, h):
	top_left = (x,y)
	top_middle = (x + w/2, y)
	top_right = (x + w, y)

	left_middle = (x, y + h/2)
	center = (x + w/2, y + h/2)
	right_middle = (x + w, y + h/2)

	bottom_left = (x, y + h)
	bottom_middle = (x + w/2, y + h)
	bottom_right = (x + w, y + h)

	return {'top_middle': top_middle, 'top_right': top_right, 'center': center, 'right_middle': right_middle, 
			'bottom_right': bottom_right, 'bottom_middle': bottom_middle, 'left_middle': left_middle,
			'top_left': top_left, 'bottom_left': bottom_left}


def get_closest_char_with_conditions(p1, p2_name, chars_to_search, start_idx, condition_func=(lambda x, y, z: True), dist_func=euclidean_distance):
	smallest_dist = float('inf')
	closest_item_idx = None
	for i in range(start_idx, len(chars_to_search)):
		char = chars_to_search[i]
		if condition_func(char, p1, char['key_points'][p2_name]):
			dist = dist_func(p1, char['key_points'][p2_name])
			if  dist < smallest_dist:
				closest_item_idx = i
				smallest_dist = dist
	return closest_item_idx

def parse_sequential_chars(start_idx, chars_to_search, detected_chars=None):
	if detected_chars is None:
		detected_chars = set()
	current_char = chars_to_search[start_idx]
	result = current_char['class']
	detected_chars.add(current_char['key_points']['top_left'] + current_char['key_points']['bottom_right'])
	x_dist_func = lambda p1, p2: abs(p1[0] - p2[0])
	y_dist_func = lambda p1, p2: abs(p1[1] - p2[1])
	# flat_slope_check = lambda c, p1, p2: slope(p1, p2) > -1 and slope(p1, p2) < 1
	# next_char_cond = lambda c, p1, p2: y_dist_func(p1, p2) < max(current_char['height'], c['height'])*0.2 and x_dist_func(p1, p2) < current_char['width']*1.5

	sub_super_cond = lambda c, p1, p2: (y_dist_func(p1, p2) > current_char['height']*0.4 and y_dist_func(p1, p2) < current_char['height']*1.2) and x_dist_func(p1, p2) < current_char['width']*0.33 and (c['key_points']['top_left'] + c['key_points']['bottom_right']) not in detected_chars
	superscript_cond = lambda c, p1, p2: sub_super_cond(c, p1, p2) and p1[1] > p2[1] 
	subscript_cond = lambda c, p1, p2: sub_super_cond(c, p1, p2) and p1[1] < p2[1]
	
	superscript_start_idx = get_closest_char_with_conditions(current_char['key_points']['right_middle'], 'left_middle', chars_to_search, start_idx+1, condition_func=superscript_cond)
	subscript_start_idx = get_closest_char_with_conditions(current_char['key_points']['right_middle'], 'left_middle', chars_to_search, start_idx+1, condition_func=subscript_cond)

	def calculate_y_overlap(c1, c2):
		c1_top_y = c1['key_points']['top_left'][1]
		c1_bottom_y = c1['key_points']['bottom_right'][1]
		c2_top_y = c2['key_points']['top_left'][1]
		c2_bottom_y = c2['key_points']['bottom_right'][1]

		if c1_top_y > c2_bottom_y or c2_top_y > c1_bottom_y:
			return 0
		else:
			return (min(c1_bottom_y, c2_bottom_y) - max(c1_top_y, c2_top_y)) / min(c1['height'], c2['height'])

	next_char_cond = lambda c, p1, p2: (y_dist_func(p1, p2) < max(current_char['height'], c['height'])*0.2 or calculate_y_overlap(current_char, c) > 0.85) and (x_dist_func(p1, p2) < current_char['width']*2.5 or subscript_start_idx or superscript_start_idx) and (c['key_points']['top_left'] + c['key_points']['bottom_right']) not in detected_chars
	next_char_idx = get_closest_char_with_conditions(current_char['key_points']['right_middle'], 'left_middle', chars_to_search, start_idx+1, condition_func=next_char_cond)


	directly_sequential_chars = None
	if next_char_idx is not None:
		directly_sequential_chars = parse_sequential_chars(next_char_idx, chars_to_search, detected_chars=detected_chars)
	if subscript_start_idx is not None:
		result += ('_{' + parse_sequential_chars(subscript_start_idx, chars_to_search, detected_chars=detected_chars) + '}')
	if superscript_start_idx is not None:
		result += ('^{' + parse_sequential_chars(superscript_start_idx, chars_to_search, detected_chars=detected_chars) + '}')
	if directly_sequential_chars is None:
		return result
	else:
		return result + directly_sequential_chars

def segment_combine_and_classify_chars(im_data):
	image = im_data[:, :, ::-1].copy() # convert RGB to BGR
	print(image.shape)
	img_copy = image
	img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# img_gray = cv2.blur(img_gray,(5,5))
	# apply binary thresholding
	ret, thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
	# thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 2)
	kernel = np.ones((3, 3), 'uint8')

	thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

	thresh = cv2.erode(thresh, kernel, iterations=1)

	# # visualize the binary image
	# cv2.imshow('Binary image', thresh)
	# cv2.waitKey(0)

	image_copy = image.copy()
	contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
	# draw contours on the original image
	new_contours = []
	for i, c in enumerate(contours):
		rect = cv2.boundingRect(c)
		x,y,w,h = rect
		if (cv2.contourArea(c) > 120 or w/h > 2) and hierarchy[0][i][-1] == 0 or hierarchy[0][i][-1] == 1:
			new_contours.append(c)
	bounding_rects = set()
	remove_set = set()
	for c1 in new_contours:
		for c2 in new_contours:
			c1_x, c1_y, c1_w, c1_h = cv2.boundingRect(c1)
			c2_x, c2_y, c2_w, c2_h = cv2.boundingRect(c2)
			if not (c1_x == c2_x and c1_y == c2_y and c1_w == c2_w and c1_h == c2_h):
				c1_center = get_contour_center([c1_x, c1_y, c1_w, c1_h])
				c2_center = get_contour_center([c2_x, c2_y, c2_w, c2_h])
				combine_boxes = False
				# detect two horizontal parallel lines as an single contour (equal sign)
				if c2_w/c2_h > 1.8 and c1_w/c1_h > 1.8:
					if abs(c1_center[0] - c2_center[0]) < 0.09*thresh.shape[0] and abs(c1_center[1] - c2_center[1]) < 0.4*thresh.shape[1]:
						combine_boxes = True
				elif c1_w/c1_h < 0.2 and c2_w < c1_w*1.25 and c2_h < c1_h*0.25 and c2_w/c2_h < 1.5: # detect and combine seperate contours that make up '!' and 'i' 
					if ((c2_y - (c1_y + c1_h)) < (0.25*c1_h) or (c1_y - (c2_y + c2_h)) < (0.25*c1_h)) and abs(c1_center[0] - c2_center[0]) < c1_w:
						combine_boxes = True
				
				if combine_boxes:
					remove_set.add((c1_x, c1_y, c1_w, c1_h))
					remove_set.add((c2_x, c2_y, c2_w, c2_h))
					x1, y1, x2, y2 = (min(c1_x, c2_x), min(c1_y, c2_y), max(c1_x+c1_w, c2_x+c2_w), max(c1_y+c1_h, c2_y+c2_h))
					bounding_rects.add((x1,y1,x2-x1,y2-y1))
				else:
					bounding_rects.add((c1_x, c1_y, c1_w, c1_h))


	bounding_rects = bounding_rects - remove_set
	chars = []
	for i, b in enumerate(bounding_rects):
		x, y, w, h = b
		class_str, _ = get_char_prediction(thresh[y:y+h, x:x+w])
		if '\\' in class_str:
			class_str = class_str + ' '
		char = {'data': thresh[y:y+h, x:x+w], 'key_points': get_points_on_box(x,y,w,h), 'class': class_str, 'width': w, 'height': h}
		chars.append(char)
	chars.sort(key=(lambda x: x['key_points']['top_left'][0]))

	return chars

def get_latex(img):
	chars = segment_combine_and_classify_chars(img)
	latex_str = parse_sequential_chars(0, chars)
	return latex_str






