import cv2
import numpy as np
import get_initial_seed


def region_grow(img, side, th=1):
    """
    function: 区域增长法
    description: 生长结果区域标记为白色(255), 背景色为黑色(0)
    parameters: img: 源图像, side: 增长大方向, pt: 起始种子点, th: 生长的阈值.
    """

    # get initial seed
    initial_seed, direction = get_initial_seed.get_initial_seed(img, side)
    growing_pt = [0, 0]  # 试探生长点

    canvas = np.zeros(img.shape, np.uint8)  # 创建画板

    pt_stack = [initial_seed]                 # 生长点栈, 将生长点压入栈中
    # cv2.imshow('initial_seed_img:', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # print('initial_seed:', initial_seed)
    canvas[initial_seed[1], initial_seed[0]] = 255      # 标记生长点
    seed_value = img[initial_seed[1], initial_seed[0]]   # 记录生长点灰度值的(255)

    while pt_stack:                # 若生长栈空则停止
        initial_seed = pt_stack.pop()

        # 分别对5/8个方向上的点进行生长
        for i in range(len(direction)):
            growing_pt[0] = initial_seed[0] + direction[i][0]
            growing_pt[1] = initial_seed[1] + direction[i][1]
            # 检查是否是边缘点
            if growing_pt[0] < 0 or growing_pt[1] < 0 or growing_pt[0] > \
                    img.shape[1]-1 or growing_pt[1] > img.shape[0] - 1:
                continue
            flag_grow = canvas[growing_pt[1], growing_pt[0]]     # 当前待生长点的灰度值

            if flag_grow == 0:
                current_value = img[growing_pt[1], growing_pt[0]]
                if abs(seed_value - current_value) < th:        # 与初始种子点像素差小于阈值
                    canvas[growing_pt[1], growing_pt[0]] = 255
                    pt_stack.append(growing_pt.copy())           # 新生长点入栈

    return canvas.copy()
