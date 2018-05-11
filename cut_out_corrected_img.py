import cv2
import numpy as np
import correct_angle_by_radon


def cut_out_corrected_img(image):
    if isinstance(image, str):
        img, _ = correct_angle_by_radon.correct_angle_by_radon(image)
    else:
        img = image
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img
    ret, img_bw = cv2.threshold(img_gray, 180, 255, cv2.THRESH_BINARY)
    _, cnt, _ = cv2.findContours(img_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    img_bw = np.array(255 - img_bw)
    _, contours, _ = cv2.findContours(img_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    small_areas = [i for i in contours if cv2.contourArea(i) < 200]
    cv2.fillPoly(img_bw, small_areas, 0)
    _, contours, _ = cv2.findContours(img_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # print('contours:', contours)
    for i in range(len(contours)):
        cv2.drawContours(img, contours, i, (255, 255, 255), thickness=4)
    cnt = contours[0]
    cnt = np.squeeze(cnt)
    border = [[0, 0], [0, 0]]
    for i in range(img_bw.shape[0]):
        if img_bw[i, :].any():
            border[0][0] = i - 2
            break
    for i in range(img_bw.shape[0]-1, -1, -1):
        if img_bw[i, :].any():
            border[0][1] = i + 2
            break
    for i in range(img_bw.shape[1]):
        if img_bw[:, i].any():
            border[1][0] = i - 2
            break
    for i in range(img_bw.shape[1]-1, -1, -1):
        if img_bw[:, i].any():
            border[1][1] = i + 2
            break
    cut_out_img = img[max(0, border[0][0]):min(img.shape[0], border[0][1]),
                      max(0, border[1][0]):min(img.shape[1], border[1][1])]
    # print('border_points:', [max(0, border[0][0]), min(img.shape[0], border[0][1]),
    #                            max(0, border[1][0]), min(img.shape[1], border[1][1])])
    return cut_out_img
