import cv2
import numpy as np
import matplotlib.pyplot as plt
import region_grow
import get_boundary


def extract_vein_by_region_grow(edges_canny, image, threshold_perimeter, threshold_kernel_boundary):
    """
    edges_canny, image, threshold_perimeter, threshold_kernel_boundary -> vein, main_vein, vein_points, main_vein_points
    :param edges_canny: edges_canny.
    :param image: path_name of leave.
    :param threshold_perimeter: tolerated threshold of perimeter of contours, to get rid of the fractions of boundary.
    :param threshold_kernel_boundary: width of dilated boundary, to get rid of the boundary.
    :return: vein, main_vein, vein_points, main_vein_points.
    """
    img_ori_gray = cv2.imread(image, 0)
    # cut out boundary
    boundary = get_boundary.get_boundary(image)
    canvas_boundary = np.zeros(edges_canny.shape[:2], dtype=np.uint8)
    for i in boundary:
        canvas_boundary[int(i[0]), int(i[1])] = 255
    kernel_boundary = cv2.getStructuringElement(cv2.MORPH_RECT, threshold_kernel_boundary)
    canvas_boundary = cv2.dilate(canvas_boundary, kernel_boundary)  # 膨胀后的边框
    opened = cv2.bitwise_or(edges_canny, canvas_boundary)
    res_all = region_grow.region_grow(opened, 'all')

    # 得到叶脉并依区域周长去噪
    vein = cv2.subtract(res_all, canvas_boundary)
    # plt.imshow(vein, plt.cm.gray)
    # plt.suptitle('vein')
    # plt.show()
    # 连接断裂的主叶脉
    h, w = vein.shape
    # denoise
    vein[:, round(w / 2) - 20:round(w / 2) + 20], contours, hierarchy = \
        cv2.findContours(vein[:, round(w/2)-20:round(w/2)+20], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    small_perimeters = [i for i in contours if len(i) < 10]   # 删短周长的区域
    cv2.fillPoly(vein[:, round(w/2)-20:round(w/2)+20], small_perimeters, 0)
    # plt.imshow(vein[:, round(w/2)-20:round(w/2)+20], plt.cm.gray)
    # plt.suptitle('First One')
    # plt.show()
    # temporary end
    vein_end = [0, 0]
    start_point_prev = [-1, -1]
    # get the bottom index
    for end_idx in range(len(vein[::-1, round(w/2)-20:round(w/2)+20])):
        if vein[end_idx, :].any():
            for j in range(len(vein[end_idx, round(w/2)-20:round(w/2)+20])):
                if vein[:, round(w/2)-20:round(w/2)+20][end_idx][j] == 255:
                    vein_end = [end_idx, j+1]
    for i in range(len(vein[:vein_end[0], round(w/2)-20:round(w/2)+20])):
        if i != 0:
            if start_point and end_point and i in list(range(0, end_point[0])):
                continue
        # print('i:{}'.format(i))
        start_point = []
        end_point = []
        flag_end = 'go'
        flag_continue_for_i = 'go'

        # get start_point and end_point
        for j in range(len(vein[0:vein_end[0], round(w/2)-20:round(w/2)+20])):
            if flag_end == 'brk':
                break
            if vein[:, round(w/2)-20:round(w/2)+20][j].any() and start_point == []:
                if not vein[:, round(w/2)-20:round(w/2)+20][j+1].any():
                    for k in range(len(vein[:, round(w/2)-20:round(w/2)+20][j])):
                        if vein[:, round(w/2)-20:round(w/2)+20][j][k] == 255:
                            start_point = [j, (k+round(w/2)-20)+1]

                            # print('start_point:', start_point)
                            if start_point[0] == start_point_prev[0]:
                                flag_continue_for_i = 'cnt'
                            start_point_prev = start_point.copy()
                            break
            if flag_continue_for_i == 'cnt':
                break
            if not vein[:, round(w/2)-20:round(w/2)+20][j].any() and start_point != [] and end_point == []:
                # print("All zeros in %d-th line." % j)
                if vein[:, round(w/2)-20:round(w/2)+20][j+1].any():
                    for k in range(len(vein[:, round(w/2)-20:round(w/2)+20][j])):
                        if vein[:, round(w/2)-20:round(w/2)+20][j+1][k] == 255:
                            end_point = [j+1, (k+round(w/2)-20)+1]
                            # print('end_point:', end_point)
                            flag_end = 'brk'
                            break
            else:
                continue
        # get points end
        if not start_point or not end_point or flag_continue_for_i == 'cnt':
            continue

        canny_threshold_enhanced_locally = [30, 60]
        # print(start_point, end_point)
        # print([start_point[0], end_point[0], min(start_point[1], end_point[1]), max(start_point[1], end_point[1])])
        vein_enhanced_locally = img_ori_gray[start_point[0]:end_point[0],
                                     min(start_point[1], end_point[1]):max(start_point[1], end_point[1])+1]
        # print("vein_enhanced_locally", vein_enhanced_locally.shape, type(vein_enhanced_locally))
        # vein_enhanced_locally_GB = cv2.bilateralFilter(vein_enhanced_locally, 9, 75, 75)
        # print('rect:', [start_point[0], end_point[0],
        #                 min(start_point[1], end_point[1]), max(start_point[1], end_point[1])+1])
        # plt.imshow(vein_enhanced_locally, cmap="gray")
        # plt.show()
        edge_enhanced_locally = cv2.Canny(vein_enhanced_locally, *canny_threshold_enhanced_locally, apertureSize=3)
        # for i in vein_enhanced_locally:
        #     print(i)
        # for i in range(10):
        #     print("")
        # for i in vein_enhanced_locally_GB:
        #     print(i)
        white_pixel_percentage = list(edge_enhanced_locally.ravel() == 255).count(1) /\
                                 len(list(edge_enhanced_locally.ravel()))
        start_point_check = [-1, -1]
        counter_canny_adjustment = 0
        counter_prevent_dead_loop = 2
        white_pixel_percentage_prev = 0

        while not 1/40 < white_pixel_percentage < 1/20 and (start_point_check == [-1, -1] or
                                                                    start_point_check[1] >= start_point[0]):
            if not counter_prevent_dead_loop:
                # print('final white_pixel_percentage: {}'.format(white_pixel_percentage))
                break
            # code of adjustment on threshold of canny
            if white_pixel_percentage <= 1/40:
                canny_threshold_enhanced_locally = [canny_threshold_enhanced_locally[0] - 1,
                                                    canny_threshold_enhanced_locally[1] - 1]
            else:
                canny_threshold_enhanced_locally = [canny_threshold_enhanced_locally[0] + 1,
                                                    canny_threshold_enhanced_locally[1] + 1]
            # print("vein_enhanced_locally", vein_enhanced_locally.shape, type(vein_enhanced_locally))
            # vein_enhanced_locally_GB = cv2.bilateralFilter(vein_enhanced_locally, 9, 75, 75)
            edge_enhanced_locally = cv2.Canny(vein_enhanced_locally, *canny_threshold_enhanced_locally, apertureSize=3)
            # print('vein_enhanced_locally_GB:', vein_enhanced_locally_GB.shape, type(vein_enhanced_locally_GB))
            # print("vein_enhanced_locally_GB.shape_in_while:", vein_enhanced_locally_GB.shape)
            white_pixel_percentage = (np.sum(edge_enhanced_locally==1) /
                                         len(list(edge_enhanced_locally.ravel())))
            if white_pixel_percentage == white_pixel_percentage_prev:
                counter_prevent_dead_loop -= 1
            white_pixel_percentage_prev = white_pixel_percentage
            # print('{}-th white_pixel_percentage:{}'.format(counter_canny_adjustment,
            #                                                     white_pixel_percentage))
            counter_canny_adjustment += 1
            # CHECK IF THE BRANCH HAS EXTENDED
            for k in range(len(vein[:, round(w / 2) - 20:round(w / 2) + 20])):
                if vein[:, round(w / 2) - 20:round(w / 2) + 20][k].any():
                    if not vein[:, round(w / 2) - 20:round(w / 2) + 20][min(vein.shape[0]-1, k + 1)].any():
                        for j in range(len(vein[:, round(w / 2) - 20:round(w / 2) + 20][k])):
                            if vein[:, round(w / 2) - 20:round(w / 2) + 20][k][j] == 255:
                                start_point_check = [k, j + 1]
                                break
            # CHECK END
            # print('final white_pixel_percentage: {}'.format(white_pixel_percentage))
        # while end
        vein[start_point[0]:end_point[0], min(start_point[1], end_point[1]):max(start_point[1], end_point[1])+1] = \
            edge_enhanced_locally
        # plt.imshow(vein, plt.cm.gray)
        # plt.suptitle('In Iteration')
        # plt.show()
    # for end

    # denoise
    vein[:, round(w / 2) - 20:round(w / 2) + 20], contours, hierarchy = \
        cv2.findContours(vein[:, round(w/2)-20:round(w/2)+20], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    small_perimeters = [i for i in contours if len(i) < 10]   # 删短周长的区域
    cv2.fillPoly(vein[:, round(w/2)-20:round(w/2)+20], small_perimeters, 0)
    # plt.imshow(vein[:, round(w/2)-20:round(w/2)+20], plt.cm.gray)
    # plt.suptitle('Last One')
    # plt.show()

    vein, contours, hierarchy = cv2.findContours(vein, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    small_perimeters = [i for i in contours if len(i) < threshold_perimeter]   # 删短周长的区域
    cv2.fillPoly(vein, small_perimeters, 0)

    # 上 -> 下
    res_top = region_grow.region_grow(vein, 'top')
    kernel_main_vein = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    res_top = cv2.dilate(res_top, kernel_main_vein)
    res_top = cv2.dilate(res_top, kernel_main_vein)
    main_vein = cv2.bitwise_and(vein, res_top)

    # fig_1, axes = plt.subplots(1, 3, figsize=(16, 8))
    # ax1, ax2, ax3 = axes.ravel()
    # ax1.imshow(vein, plt.cm.gray)
    # ax1.set_title('vein')
    # ax2.imshow(res_top, plt.cm.gray)
    # ax2.set_title('grow_from_top')
    # ax3.imshow(main_vein, plt.cm.gray)
    # ax3.set_title('main_vein')
    # plt.show()
    # main_vein, contours, hierarchy = cv2.findContours(main_vein, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # small_perimeters = [i for i in contours if len(i) < 0]   # 删短周长的区域
    # cv2.fillPoly(main_vein, small_perimeters, 0)

    # save points
    vein_points = []
    for i in range(vein.shape[0]):
        for j in range(vein.shape[1]):
            if vein[i, j] == 255:
                vein_points.append([i, j])
    main_vein_points = []
    for i in range(main_vein.shape[0]):
        for j in range(main_vein.shape[1]):
            if main_vein[i, j] == 255:
                main_vein_points.append([i, j])
    main_vein_points = np.array(main_vein_points)
    # for i in main_vein_points:
    #     # print(i)
    #     plt.scatter(i[1], i[0], c="red")
    # ax = plt.gca()
    # ax.set_aspect(1)
    # plt.figure()
    # plt.imshow(main_vein, cmap="gray")
    # plt.show()

    return vein, main_vein, vein_points, main_vein_points
