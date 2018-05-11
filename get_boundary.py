import cv2
from skimage import measure, color
import numpy as np


def get_boundary(image):

    if isinstance(image, str):
        img = cv2.imread(image)
    else:
        img = image
    if len(img.shape) == 3:
        img = color.rgb2gray(img)

    contours = measure.find_contours(img, 0.68, fully_connected='high')
    contours = [contours[i] for i in range(len(contours)) if len(contours[i]) > 100]
    contours_lst = []
    for i in range(len(contours)):
        for j in contours[i]:
            contours_lst.append(j)
    contours_lst = np.array(contours_lst)

    return contours_lst
