import cv2
import numpy as np


def local_enhancement(image):

    img = cv2.imread(image, 0)
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(10, 10))
    img_equalized = clahe.apply(img)

    h, w = img.shape
    # img_GB = cv2.GaussianBlur(img, (3, 3), 0)
    img_GB = cv2.bilateralFilter(img, 3, 50, 50)
    canny_threshold_common = [40, 100]
    canny_threshold_enhanced = [30, 60]
    edge_canny_up = cv2.Canny(img_GB[:round(h/6), round(w/2)-20:round(w/2)+20], *canny_threshold_common, apertureSize=3)
    edge_canny_middle = cv2.Canny(img_GB[round(h/6):round(h/2), round(w/2)-20:round(w/2)+20],
                                  *canny_threshold_enhanced, apertureSize=3)
    t = list(edge_canny_middle.ravel() == 255).count(1)/len(list(edge_canny_middle.ravel()))

    while not 1/40 < t < 1/20:
        # print(t)
        if t <= 1/40:
            canny_threshold_enhanced = [canny_threshold_enhanced[0] - 1, canny_threshold_enhanced[1] - 1]
        else:
            canny_threshold_enhanced = [canny_threshold_enhanced[0] + 1, canny_threshold_enhanced[1] + 1]
        edge_canny_middle = cv2.Canny(img_GB[round(h / 6):round(h / 2), round(w / 2) - 20:round(w / 2) + 20],
                                      *canny_threshold_enhanced, apertureSize=3)
        t = list(edge_canny_middle.ravel() == 255).count(1) / len(list(edge_canny_middle.ravel()))
    edge_canny_down = cv2.Canny(img_GB[round(h/2):, round(w/2)-20:round(w/2)+20], *canny_threshold_common, apertureSize=3)
    edge_canny_middle_horizontally = np.vstack((edge_canny_up, edge_canny_middle, edge_canny_down))
    edge_canny_left = cv2.Canny(img_GB[:, :round(w/2)-20], *canny_threshold_common, apertureSize=3)
    edge_canny_right = cv2.Canny(img_GB[:, round(w/2)+20:], *canny_threshold_common, apertureSize=3)
    edge_canny = np.hstack((edge_canny_left, edge_canny_middle_horizontally, edge_canny_right))

    edge_equalized = cv2.Canny(img_equalized, *canny_threshold_common, apertureSize=3)

    # edge_canny, contours, hierarchy = cv2.findContours(edge_canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # small_areas = [i for i in contours if cv2.contourArea(i) < 1]
    # cv2.fillPoly(edge_canny, small_areas, 0)
    #
    # edge_equalized, contours, hierarchy = cv2.findContours(edge_equalized, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # small_areas = [i for i in contours if cv2.contourArea(i) < 20]
    # cv2.fillPoly(edge_equalized, small_areas, 0)

    # 形态学处理
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 4))
    edge_canny = cv2.dilate(edge_canny, kernel)
    edge_canny = cv2.dilate(edge_canny, kernel)
    edge_canny = cv2.dilate(edge_canny, kernel)
    edge_canny = cv2.erode(edge_canny, kernel)

    edge_canny = cv2.morphologyEx(edge_canny, cv2.MORPH_CLOSE, kernel)
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edge_canny = cv2.morphologyEx(edge_canny, cv2.MORPH_CLOSE, kernel2)

    # 形态学处理
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    edge_equalized = cv2.dilate(edge_equalized, kernel)
    edge_equalized = cv2.dilate(edge_equalized, kernel)
    edge_equalized = cv2.dilate(edge_equalized, kernel)
    edge_equalized = cv2.erode(edge_equalized, kernel)

    edge_equalized = cv2.morphologyEx(edge_equalized, cv2.MORPH_CLOSE, kernel)
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edge_equalized = cv2.morphologyEx(edge_equalized, cv2.MORPH_CLOSE, kernel2)

    return img, img_equalized, edge_canny, edge_equalized
