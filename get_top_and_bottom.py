import numpy as np
import cv2
import matplotlib.pyplot as plt
import get_pic_rotated_and_broaden
import correct_angle_by_radon
import get_angle_vertical
import extract_vein_by_region_grow
from skimage import morphology
import local_enhancement
import get_boundary
import region_grow
from skimage import morphology


def get_top_and_bottom(image, inclination_angle):
    img_rotated, rotating_angle = correct_angle_by_radon.correct_angle_by_radon(image)
    gray = cv2.cvtColor(img_rotated, cv2.COLOR_BGR2GRAY)
    ret, bw = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    _, contours, hierarchy = cv2.findContours(bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    small_areas = [i for i in contours if cv2.contourArea(i) < 500]
    cv2.fillPoly(bw, small_areas, 255)
    bw = 255 - bw
    row_idx = bw.ravel().tolist().index(255) // bw.shape[1]
    col_idx = int(round(np.mean(np.where(bw[row_idx, :] == 255))))
    top = (row_idx, col_idx)
    bottom = (np.where(bw[:, col_idx] == 255)[0][-1], col_idx+10)
    cv2.line(img_rotated, top[::-1], bottom[::-1], (255, 0, 0), thickness=3)
    cv2.circle(img_rotated, top[::-1], 9, (0, 0, 255))
    cv2.circle(img_rotated, bottom[::-1], 9, (0, 0, 255))
    inclination_angle_radian = inclination_angle * np.pi / 180
    slope = np.tan(inclination_angle_radian)
    extended_from_top = (round(top[0] + 500), int(round(top[1] - 500 * slope)))
    # confirm the contour
    _, cnt, _ = cv2.findContours(bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    canvas0 = np.zeros_like(img_rotated, dtype=np.uint8)
    canvas1 = np.zeros_like(img_rotated, dtype=np.uint8)
    # print("top={} and extended_from_top={}".format(top, extended_from_top))
    cv2.line(canvas0, top[::-1], extended_from_top[::-1], color=(255, 255, 0), thickness=1)
    cv2.drawContours(canvas1, cnt, 0, color=(0, 255, 255), thickness=1)
    canvas = cv2.bitwise_or(canvas0, canvas1)
    idx_ravel_left = canvas.reshape(canvas.shape[0] * canvas.shape[1], -1).tolist().index([255, 255, 255])
    idx_row_left = idx_ravel_left // canvas.shape[1]
    idx_col_left = idx_ravel_left % canvas.shape[1]
    idx_ravel_right = len(canvas.ravel()) // 3 -\
                      canvas.reshape(canvas.shape[0] * canvas.shape[1], -1)[::-1].tolist().index([255, 255, 255])
    idx_row_right = idx_ravel_right // canvas.shape[1]
    idx_col_right = idx_ravel_right % canvas.shape[1]
    cv2.circle(canvas, (idx_col_right, idx_row_right), 5, (0, 0, 255))

    return top, bottom


def main():
    image = 'sucken_leaves/sucken_leaf_0.jpg'
    img, img_equalized, edge_canny, edge_equalized = local_enhancement.local_enhancement(image)
    vein, main_vein, vein_points, main_vein_points = \
        extract_vein_by_region_grow.extract_vein_by_region_grow(edge_canny, image, 150, (15, 15))

    other_vein = cv2.subtract(vein, main_vein)
    _, contours, hierarchy = cv2.findContours(other_vein, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    small_perimeters = [j for j in contours if len(j) < 50]  # 删短周长的区域
    cv2.fillPoly(other_vein, small_perimeters, 0)
    _, contours, hierarchy = cv2.findContours(other_vein, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    pt = []
    skin = morphology.skeletonize((main_vein / 255).astype(np.uint8)) * 255
    for j in range(skin.shape[0]):
        for k in range(skin.shape[0]):
            if skin[j][k]:
                pt.append([j, k])
    pt = np.array(pt)
    angle = 0
    text_place = 0
    current_angle = get_angle_vertical.get_angle_vertical(pt)
    angle = current_angle
    img = cv2.imread(image)
    top, bottom = get_top_and_bottom(image, angle)
    cv2.circle(img, top[::-1], 10, (0, 0, 255), thickness=7)
    cv2.circle(img, bottom[::-1], 10, (0, 0, 255), thickness=7)
    #
    img_ori_gray = cv2.imread(image, 0)
    # cut out boundary
    boundary = get_boundary.get_boundary(image)
    canvas_boundary = np.zeros(edge_canny.shape[:2], dtype=np.uint8)
    for i in boundary:
        canvas_boundary[int(i[0]), int(i[1])] = 255
    kernel_boundary = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    canvas_boundary = cv2.dilate(canvas_boundary, kernel_boundary)
    plt.imshow(canvas_boundary, cmap="gray")
    plt.show()


if __name__ == '__main__':
    main()
