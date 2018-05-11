import numpy as np


def get_image_broadened(img, h, w):
    """
    在原图的基础上, 以原底色扩展它的右, 下, 使得其高为h, 宽为w.
    :param img: 原图
    :param h: 目标高度
    :param w: 目标宽度
    :return: 扩展后的图
    """
    img_broadened = img.copy()
    bg_color = img[0][0]
    if h > img_broadened.shape[0]:
        appendix_y = np.array([[bg_color] * img_broadened.shape[1]] * (h - img_broadened.shape[0]))
        img_broadened = np.vstack((img_broadened, appendix_y))
    if w > img_broadened.shape[1]:
        appendix_x = np.array([[bg_color] * (w - img_broadened.shape[1])] * h)
        img_broadened = np.hstack((img_broadened, appendix_x))
    return img_broadened
