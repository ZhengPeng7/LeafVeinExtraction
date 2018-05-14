import numpy as np
from scipy.interpolate import UnivariateSpline


def get_curvature(x, y=None, error=0.1):
    if y is None:
        x, y = x.real, x.imag

    t = np.arange(x.shape[0])
    std = error * np.ones_like(x)

    fx = UnivariateSpline(t, x, k=4, w=1 / np.sqrt(std))
    fy = UnivariateSpline(t, y, k=4, w=1 / np.sqrt(std))

    x_1d = fx.derivative(1)(t)
    x_2d = fx.derivative(2)(t)
    y_1d = fy.derivative(1)(t)
    y_2d = fy.derivative(2)(t)
    curvature = abs((y_1d* x_2d - x_1d* y_2d)) / np.power(x_1d** 2 + y_1d** 2, 3 / 2)
    # print('curcature:', curvature)
    return curvature
