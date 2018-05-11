def get_initial_seed(img, side):
    """
    function: 获得增长初始点
    :param img: 源二值边缘
    :param side: 增长方向
    :return:initial_seed: 初始种子点, direction: 增长掩码
    """
    seed = []
    h, w = img.shape
    flag = 0
    initial_seed, direction = (0, 0), 0
    if side == 'top':
        direction = [[1, 1], [0, 1], [-1, 1], [1, 0], [-1, 0]]
        for i in range(h):
            for j in range(round(w/2)-20, round(w/2)+20):
                if img[i, j] == 255:
                    seed.append((j, i))
                    flag = 1
            if flag:
                initial_seed = seed[int(len(seed) / 2)]
                break
    elif side == 'bottom':
        direction = [[-1, -1], [0, -1], [1, -1], [1, 0], [-1, 0]]
        for i in range(h - 1, -1, -1):
            for j in range(round(w/2)-20, round(w/2)+20):
                if img[i, j] == 255:
                    seed.append((j, i))
                    flag = 1
            if flag:
                initial_seed = seed[int(len(seed) / 2)]
                break
    elif side == 'left':
        direction = [[0, -1], [1, -1], [1, 1], [0, 1], [1, 0]]
        for j in range(round(w/2)-20, round(w/2)+20):
            for i in range(h):
                if img[i, j] == 255:
                    seed.append((j, i))
                    flag = 1
            if flag:
                initial_seed = seed[int(len(seed) / 2)]
                break
    elif side == 'right':
        direction = [[-1, -1], [0, -1], [0, 1], [-1, 1], [-1, 0]]
        for j in range(round(w/2)+20-1, round(w/2)-20-1, -1):
            for i in range(h):
                if img[i, j] == 255:
                    seed.append((j, i))
                    flag = 1
            if flag:
                initial_seed = seed[int(len(seed) / 2)]
                break
    elif side == 'all':
        direction = [[-1, -1], [0, -1], [1, -1], [1, 1], [0, 1], [-1, 1], [1, 0], [-1, 0]]
        for i in range(h - 1, -1, -1):
            for j in range(round(w/2)-20, round(w/2)+20):
                if img[i, j] == 255:
                    seed.append((j, i))
                    flag = 1
            if flag:
                initial_seed = seed[int(len(seed) / 2)]
                break
    else:
        print('Invalid side')

    return initial_seed, direction
