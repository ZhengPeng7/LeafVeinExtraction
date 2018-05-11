import cv2
import numpy as np
from sklearn import cluster
import get_pic_rotated_and_broaden


def split_leaves(image):
    img = cv2.imread(image)
    img = img[:-100, :]     # 防止边缘有拍出白纸的区域

    # 提取叶片
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, threshed_img = cv2.threshold(gray_image, 180, 255, cv2.THRESH_BINARY)

    # 去噪
    _, contours, hierarchy = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    small_areas = [i for i in contours if cv2.contourArea(i) < 500]
    cv2.fillPoly(threshed_img, small_areas, 255)
    threshed_img = 255 - threshed_img
    _, contours, hierarchy = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    small_areas = [i for i in contours if cv2.contourArea(i) < 500]
    cv2.fillPoly(threshed_img, small_areas, 0)
    _, contours, hierarchy = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    small_holes_area = [i for i in contours if cv2.contourArea(i) < 500]
    cv2.fillPoly(threshed_img, small_holes_area, 255)
    _, contours, hierarchy = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    small_contours_idx = [i for i in range(len(contours)) if len(contours[i]) < 50]
    for i in small_contours_idx[::-1]:
        contours.pop(i)

    for i in range(len(contours)):
        t = []
        for j in contours[i].tolist():
            t.append(j[0])
        contours[i] = np.array(t)
    contours = np.array(contours)
    h, w, c = img.shape
    img_all = []
    lt_points = []
    for cnt_idx in range(len(contours)):
        top_left_point = np.amin(contours[cnt_idx], axis=0)
        bottom_right_point = np.amax(contours[cnt_idx], axis=0)
        lt_points.append(top_left_point.tolist())
        im = img[max(0, top_left_point[1] - 5):min(h, bottom_right_point[1] + 5),
                 max(0, top_left_point[0] - 5):min(w, bottom_right_point[0] + 5)]

        # 提取叶片
        gray_im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, threshed_im = cv2.threshold(gray_im, 180, 255, cv2.THRESH_BINARY_INV)

        # 去噪
        threshed_im = get_pic_rotated_and_broaden.get_pic_rotated_and_broaden(threshed_im, -5, 0)
        threshed_im = get_pic_rotated_and_broaden.get_pic_rotated_and_broaden(threshed_im, 5, 0)
        im = get_pic_rotated_and_broaden.get_pic_rotated_and_broaden(im, -5, 0)
        im = get_pic_rotated_and_broaden.get_pic_rotated_and_broaden(im, 5, 0)
        _, contours_im, hierarchy = cv2.findContours(threshed_im, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        small_areas_im = [i for i in contours_im if cv2.contourArea(i) < 500]
        cv2.fillPoly(threshed_im, small_areas_im, 255)

        _, contours_im, hierarchy = cv2.findContours(threshed_im, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        small_holes_area_im = [i for i in contours_im if cv2.contourArea(i) < 7000]
        cv2.fillPoly(threshed_im, small_holes_area_im, 0)
        threshed_im = cv2.dilate(threshed_im, kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5)))
        threshed_im = cv2.cvtColor(threshed_im, cv2.COLOR_GRAY2RGB)

        threshed_im_inv = 255 - threshed_im
        split_img = cv2.bitwise_or(threshed_im_inv, im)
        # plt.imshow(cv2.cvtColor(split_img, cv2.COLOR_BGR2RGB))
        if np.sum(split_img // 255) > split_img.shape[0] * split_img.shape[1] * split_img.shape[2] / 1.5:
            lt_points.pop()
            continue
        img_all.append(split_img)

        # plt.show()

    # print('lt_points:', lt_points)
    # l_axis = [i[0] for i in lt_points]
    t_axis = [[i[1], 0] for i in lt_points]
    # print('l_axis:', l_axis)
    # print('t_axis:', t_axis)

    [_, label, _] = cluster.k_means(t_axis, 2)
    # print('label:', label)
    first_part = lt_points[label.tolist().index(1)][1] > lt_points[label.tolist().index(0)][1]
    top_points = []
    bottom_points = []
    for i in range(len(label)):
        if first_part:
            if label[i]:
                bottom_points.append(lt_points[i])
            else:
                top_points.append(lt_points[i])
        else:
            if label[i]:
                top_points.append(lt_points[i])
            else:
                bottom_points.append(lt_points[i])
    top_points_sorted = sorted(top_points, key=lambda x: x[0])
    bottom_points_sorted = sorted(bottom_points, key=lambda x: x[0])

    # print('top_points_sorted:', top_points_sorted)
    # print('bottom_points_sorted:', bottom_points_sorted)
    top_points_idx_sorted = []
    bottom_points_idx_sorted = []
    for i in top_points_sorted:
        top_points_idx_sorted.append(lt_points.index(i))
    for i in bottom_points_sorted:
        bottom_points_idx_sorted.append(lt_points.index(i))
    img_all_sorted = []
    for i in top_points_idx_sorted:
        img_all_sorted.append(img_all[i])
    for i in bottom_points_idx_sorted:
        img_all_sorted.append(img_all[i])

    return img_all_sorted
