import cv2
from skimage import transform, morphology
import numpy as np
import get_pic_rotated_and_broaden


def correct_angle_by_radon(image):
    """
    correct_angle_by_radon(image) -> (img_rotated, rotating_angle)
    :param image: src
    :return: img_rotated and rotating_angle
    """
    img = cv2.imread(image)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bw = cv2.Canny(img_gray, 60, 120)
    for i in bw:
        for j in range(len(i)):
            if 255 == i[j]:
                i[j] = 1
    bw = morphology.skeletonize(bw)   # optional
    theta = list(range(-90, 90))
    R = transform.radon_transform.radon(bw, theta)
    R1 = np.max(R, axis=0)
    theta_max = 90
    while theta_max > 50 or theta_max < -50:
        R2, theta_max = np.max(R1), np.argwhere(R1 == np.max(R1))
        R1[theta_max] = 0
        theta_max -= 91
    img_rotated = get_pic_rotated_and_broaden.get_pic_rotated_and_broaden(img, -theta_max, (255, 255, 255))
    rotating_angle = theta_max

    return img_rotated, rotating_angle
