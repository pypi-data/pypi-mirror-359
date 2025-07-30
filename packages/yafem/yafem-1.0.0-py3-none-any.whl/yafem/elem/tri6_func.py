import numpy

def jac(_Dummy_34, _Dummy_35):
    [x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6] = _Dummy_34
    [zeta1, zeta2, zeta3] = _Dummy_35
    return numpy.array([[1, 1, 1], [x1*(4*zeta1 - 1) + 4*x4*zeta2 + 4*x6*zeta3, x2*(4*zeta2 - 1) + 4*x4*zeta1 + 4*x5*zeta3, x3*(4*zeta3 - 1) + 4*x5*zeta2 + 4*x6*zeta1], [y1*(4*zeta1 - 1) + 4*y4*zeta2 + 4*y6*zeta3, y2*(4*zeta2 - 1) + 4*y4*zeta1 + 4*y5*zeta3, y3*(4*zeta3 - 1) + 4*y5*zeta2 + 4*y6*zeta1]])

def phi(_Dummy_36):
    [zeta1, zeta2, zeta3] = _Dummy_36
    return numpy.array([[zeta1*(2*zeta1 - 1)], [zeta2*(2*zeta2 - 1)], [zeta3*(2*zeta3 - 1)], [4*zeta1*zeta2], [4*zeta2*zeta3], [4*zeta1*zeta3]])

def A_func(_Dummy_37):
    [x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6] = _Dummy_37
    return (1/2)*x1*y2 - 1/2*x1*y3 - 1/2*x2*y1 + (1/2)*x2*y3 + (1/2)*x3*y1 - 1/2*x3*y2

def N_func(_Dummy_38, _Dummy_39, z):
    [x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6] = _Dummy_38
    [zeta1, zeta2, zeta3] = _Dummy_39
    return numpy.array([[zeta1*(2*zeta1 - 1), 0, 0, 0, -z*zeta1*(2*zeta1 - 1), zeta2*(2*zeta2 - 1), 0, 0, 0, -z*zeta2*(2*zeta2 - 1), zeta3*(2*zeta3 - 1), 0, 0, 0, -z*zeta3*(2*zeta3 - 1), 4*zeta1*zeta2, 0, 0, 0, -4*z*zeta1*zeta2, 4*zeta2*zeta3, 0, 0, 0, -4*z*zeta2*zeta3, 4*zeta1*zeta3, 0, 0, 0, -4*z*zeta1*zeta3], [0, zeta1*(2*zeta1 - 1), 0, z*zeta1*(2*zeta1 - 1), 0, 0, zeta2*(2*zeta2 - 1), 0, z*zeta2*(2*zeta2 - 1), 0, 0, zeta3*(2*zeta3 - 1), 0, z*zeta3*(2*zeta3 - 1), 0, 0, 4*zeta1*zeta2, 0, 4*z*zeta1*zeta2, 0, 0, 4*zeta2*zeta3, 0, 4*z*zeta2*zeta3, 0, 0, 4*zeta1*zeta3, 0, 4*z*zeta1*zeta3, 0], [0, 0, zeta1*(2*zeta1 - 1), 0, 0, 0, 0, zeta2*(2*zeta2 - 1), 0, 0, 0, 0, zeta3*(2*zeta3 - 1), 0, 0, 0, 0, 4*zeta1*zeta2, 0, 0, 0, 0, 4*zeta2*zeta3, 0, 0, 0, 0, 4*zeta1*zeta3, 0, 0]])

def B_b():
    return numpy.array([[1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 1, 0, 1, 0], [0, 1, 1, 0, 0, 0, 0, 0]])

def D_func(E, nu):
    return numpy.array([[-E/(nu**2 - 1), -E*nu/(nu**2 - 1), 0, 0, 0], [-E*nu/(nu**2 - 1), -E/(nu**2 - 1), 0, 0, 0], [0, 0, E/(2*nu + 2), 0, 0], [0, 0, 0, E/(2*nu + 2), 0], [0, 0, 0, 0, E/(2*nu + 2)]])

def I():
    return numpy.array([[0, 0], [1, 0], [0, 1]])

def B_xy(_Dummy_40, _Dummy_41, z):
    [x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6] = _Dummy_40
    [zeta1, zeta2, zeta3] = _Dummy_41
    return numpy.array([[4*zeta1 - 1, 0, 0, 0, -z*(4*zeta1 - 1), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 0, 0, -4*z*zeta2, 0, 0, 0, 0, 0, 4*zeta3, 0, 0, 0, -4*z*zeta3], [0, 0, 0, 0, 0, 4*zeta2 - 1, 0, 0, 0, -z*(4*zeta2 - 1), 0, 0, 0, 0, 0, 4*zeta1, 0, 0, 0, -4*z*zeta1, 4*zeta3, 0, 0, 0, -4*z*zeta3, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta3 - 1, 0, 0, 0, -z*(4*zeta3 - 1), 0, 0, 0, 0, 0, 4*zeta2, 0, 0, 0, -4*z*zeta2, 4*zeta1, 0, 0, 0, -4*z*zeta1], [0, 4*zeta1 - 1, 0, z*(4*zeta1 - 1), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 4*z*zeta2, 0, 0, 0, 0, 0, 0, 0, 4*zeta3, 0, 4*z*zeta3, 0], [0, 0, 0, 0, 0, 0, 4*zeta2 - 1, 0, z*(4*zeta2 - 1), 0, 0, 0, 0, 0, 0, 0, 4*zeta1, 0, 4*z*zeta1, 0, 0, 4*zeta3, 0, 4*z*zeta3, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta3 - 1, 0, z*(4*zeta3 - 1), 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 4*z*zeta2, 0, 0, 4*zeta1, 0, 4*z*zeta1, 0], [0, 0, 4*zeta1 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta3, 0, 0], [0, 0, 0, 0, 0, 0, 0, 4*zeta2 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta1, 0, 0, 0, 0, 4*zeta3, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta3 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 0, 0, 0, 4*zeta1, 0, 0]])

def B_z(_Dummy_42, _Dummy_43):
    [x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6] = _Dummy_42
    [zeta1, zeta2, zeta3] = _Dummy_43
    return numpy.array([[0, 0, 0, 0, -zeta1*(2*zeta1 - 1), 0, 0, 0, 0, -zeta2*(2*zeta2 - 1), 0, 0, 0, 0, -zeta3*(2*zeta3 - 1), 0, 0, 0, 0, -4*zeta1*zeta2, 0, 0, 0, 0, -4*zeta2*zeta3, 0, 0, 0, 0, -4*zeta1*zeta3], [0, 0, 0, zeta1*(2*zeta1 - 1), 0, 0, 0, 0, zeta2*(2*zeta2 - 1), 0, 0, 0, 0, zeta3*(2*zeta3 - 1), 0, 0, 0, 0, 4*zeta1*zeta2, 0, 0, 0, 0, 4*zeta2*zeta3, 0, 0, 0, 0, 4*zeta1*zeta3, 0]])

def gp_xy_3():
    return numpy.array([[0.666666666666667, 0.166666666666667, 0.166666666666667], [0.166666666666667, 0.666666666666667, 0.166666666666667], [0.166666666666667, 0.166666666666667, 0.666666666666667]])

def gw_xy_3():
    return numpy.array([[0.333333333333333], [0.333333333333333], [0.333333333333333]])

def gp_xy_6():
    return numpy.array([[0.10810301816807, 0.445948490915965, 0.445948490915965], [0.445948490915965, 0.10810301816807, 0.445948490915965], [0.445948490915965, 0.445948490915965, 0.10810301816807], [0.816847572980459, 0.0915762135097707, 0.0915762135097707], [0.0915762135097707, 0.816847572980459, 0.0915762135097707], [0.0915762135097707, 0.0915762135097707, 0.816847572980459]])

def gw_xy_6():
    return numpy.array([[0.223381589678011], [0.223381589678011], [0.223381589678011], [0.109951743655322], [0.109951743655322], [0.109951743655322]])

def gp_z():
    return numpy.array([[-1], [0], [1]])

def gw_z():
    return numpy.array([[0.333333333333333], [1.33333333333333], [0.333333333333333]])

