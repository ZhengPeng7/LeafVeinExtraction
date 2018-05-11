import numpy as np
import matplotlib.pyplot as plt
import get_image_broadened
import cv2


def show_images(images_marked, images_shape, column, alignment='left'):
    # 求最大长和最大宽
    h_max, w_max = np.amax(images_shape, axis=0)[:2]
    img_line_buffer = []
    img_lines = []
    counter_col = 0

    for i in range(len(images_marked)):
        bg_color = tuple(images_marked[i][0][0]) if images_marked[i].shape == 3 else images_marked[i][0][0]
        counter_col += 1
        t = get_image_broadened.get_image_broadened(images_marked[i], h_max, w_max)
        img_line_buffer.append(t)
        if counter_col > column - 1:
            img_lines.append(np.hstack(img_line_buffer))
            img_line_buffer = []
            counter_col = 0
            continue
        if i == len(images_marked) - 1:
            appendix_bg_color_space = np.array([[bg_color] * (w_max * (column - len(images_marked) % column))] * h_max)
            img_line_buffer = np.squeeze(np.array(img_line_buffer))
            if alignment == 'left':
                img_lines.append(np.hstack((np.hstack(img_line_buffer), appendix_bg_color_space)))
            else:
                img_lines.append(np.hstack((appendix_bg_color_space, img_line_buffer)))
    img_joined = np.vstack(img_lines)
    if 3 == img_joined.shape:
        img_joined = cv2.cvtColor(img_joined, cv2.COLOR_BGR2RGB)

    return img_joined
