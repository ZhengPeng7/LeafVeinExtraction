import numpy as np
from sklearn.cluster import k_means
from scipy import optimize


def get_angle_vertical(points, angle_main_vein=0):
    pts = points.copy()
    pts = np.array(pts)
    [centroids, labels, interia] = k_means(pts, 5)
    if not angle_main_vein:
        def f_1(x, k, b):
            return k*x + b
        x0 = centroids[:, 0]
        y0 = centroids[:, 1]
        k, b = optimize.curve_fit(f_1, x0, y0)[0]
        return np.arctan(k) * 180 / np.pi
    pts = sorted(centroids, key=lambda x: x[0], reverse=True)[:2]
    tan_value = (pts[1][1] - pts[0][1]) / (pts[0][0] - pts[1][0])
    angle_vertical = np.arctan(tan_value) * 180 / np.pi

    return angle_vertical - angle_main_vein
