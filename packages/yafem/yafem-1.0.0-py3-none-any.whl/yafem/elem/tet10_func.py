import numpy

def jac(_Dummy_34, _Dummy_35):
    [x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, x5, y5, z5, x6, y6, z6, x7, y7, z7, x8, y8, z8, x9, y9, z9, x10, y10, z10] = _Dummy_34
    [zeta1, zeta2, zeta3, zeta4] = _Dummy_35
    return numpy.array([[1, 1, 1, 1], [x1*(4*zeta1 - 1) + 4*x5*zeta2 + 4*x7*zeta3 + 4*x8*zeta4, x2*(4*zeta2 - 1) + 4*x5*zeta1 + 4*x6*zeta3 + 4*x9*zeta4, 4*x10*zeta4 + x3*(4*zeta3 - 1) + 4*x6*zeta2 + 4*x7*zeta1, 4*x10*zeta3 + x4*(4*zeta4 - 1) + 4*x8*zeta1 + 4*x9*zeta2], [y1*(4*zeta1 - 1) + 4*y5*zeta2 + 4*y7*zeta3 + 4*y8*zeta4, y2*(4*zeta2 - 1) + 4*y5*zeta1 + 4*y6*zeta3 + 4*y9*zeta4, 4*y10*zeta4 + y3*(4*zeta3 - 1) + 4*y6*zeta2 + 4*y7*zeta1, 4*y10*zeta3 + y4*(4*zeta4 - 1) + 4*y8*zeta1 + 4*y9*zeta2], [z1*(4*zeta1 - 1) + 4*z5*zeta2 + 4*z7*zeta3 + 4*z8*zeta4, z2*(4*zeta2 - 1) + 4*z5*zeta1 + 4*z6*zeta3 + 4*z9*zeta4, 4*z10*zeta4 + z3*(4*zeta3 - 1) + 4*z6*zeta2 + 4*z7*zeta1, 4*z10*zeta3 + z4*(4*zeta4 - 1) + 4*z8*zeta1 + 4*z9*zeta2]])

def N(_Dummy_36, _Dummy_37):
    [x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, x5, y5, z5, x6, y6, z6, x7, y7, z7, x8, y8, z8, x9, y9, z9, x10, y10, z10] = _Dummy_36
    [zeta1, zeta2, zeta3, zeta4] = _Dummy_37
    return numpy.array([[zeta1*(2*zeta1 - 1), 0, 0, zeta2*(2*zeta2 - 1), 0, 0, zeta3*(2*zeta3 - 1), 0, 0, zeta4*(2*zeta4 - 1), 0, 0, 4*zeta1*zeta2, 0, 0, 4*zeta2*zeta3, 0, 0, 4*zeta1*zeta3, 0, 0, 4*zeta1*zeta4, 0, 0, 4*zeta2*zeta4, 0, 0, 4*zeta3*zeta4, 0, 0], [0, zeta1*(2*zeta1 - 1), 0, 0, zeta2*(2*zeta2 - 1), 0, 0, zeta3*(2*zeta3 - 1), 0, 0, zeta4*(2*zeta4 - 1), 0, 0, 4*zeta1*zeta2, 0, 0, 4*zeta2*zeta3, 0, 0, 4*zeta1*zeta3, 0, 0, 4*zeta1*zeta4, 0, 0, 4*zeta2*zeta4, 0, 0, 4*zeta3*zeta4, 0], [0, 0, zeta1*(2*zeta1 - 1), 0, 0, zeta2*(2*zeta2 - 1), 0, 0, zeta3*(2*zeta3 - 1), 0, 0, zeta4*(2*zeta4 - 1), 0, 0, 4*zeta1*zeta2, 0, 0, 4*zeta2*zeta3, 0, 0, 4*zeta1*zeta3, 0, 0, 4*zeta1*zeta4, 0, 0, 4*zeta2*zeta4, 0, 0, 4*zeta3*zeta4]])

def D(E, nu):
    return numpy.array([[E*(nu - 1)/(2*nu**2 + nu - 1), -E*nu/(2*nu**2 + nu - 1), -E*nu/(2*nu**2 + nu - 1), 0, 0, 0], [-E*nu/(2*nu**2 + nu - 1), E*(nu - 1)/(2*nu**2 + nu - 1), -E*nu/(2*nu**2 + nu - 1), 0, 0, 0], [-E*nu/(2*nu**2 + nu - 1), -E*nu/(2*nu**2 + nu - 1), E*(nu - 1)/(2*nu**2 + nu - 1), 0, 0, 0], [0, 0, 0, (1/2)*E/(nu + 1), 0, 0], [0, 0, 0, 0, (1/2)*E/(nu + 1), 0], [0, 0, 0, 0, 0, (1/2)*E/(nu + 1)]])

def B2(_Dummy_38, _Dummy_39):
    [x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, x5, y5, z5, x6, y6, z6, x7, y7, z7, x8, y8, z8, x9, y9, z9, x10, y10, z10] = _Dummy_38
    [zeta1, zeta2, zeta3, zeta4] = _Dummy_39
    return numpy.array([[4*zeta1 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 0, 0, 0, 0, 4*zeta3, 0, 0, 4*zeta4, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 4*zeta2 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta1, 0, 0, 4*zeta3, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta4, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 4*zeta3 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 0, 4*zeta1, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta4, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta4 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta1, 0, 0, 4*zeta2, 0, 0, 4*zeta3, 0, 0], [0, 4*zeta1 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 0, 0, 0, 0, 4*zeta3, 0, 0, 4*zeta4, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 4*zeta2 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta1, 0, 0, 4*zeta3, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta4, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 4*zeta3 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 0, 4*zeta1, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta4, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta4 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta1, 0, 0, 4*zeta2, 0, 0, 4*zeta3, 0], [0, 0, 4*zeta1 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 0, 0, 0, 0, 4*zeta3, 0, 0, 4*zeta4, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 4*zeta2 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta1, 0, 0, 4*zeta3, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta4, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 4*zeta3 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta2, 0, 0, 4*zeta1, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta4], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta4 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*zeta1, 0, 0, 4*zeta2, 0, 0, 4*zeta3]])

def gp():
    return numpy.array([[1/4 + (3/20)*numpy.sqrt(5), 1/4 - 1/20*numpy.sqrt(5), 1/4 - 1/20*numpy.sqrt(5), 1/4 - 1/20*numpy.sqrt(5)], [1/4 - 1/20*numpy.sqrt(5), 1/4 + (3/20)*numpy.sqrt(5), 1/4 - 1/20*numpy.sqrt(5), 1/4 - 1/20*numpy.sqrt(5)], [1/4 - 1/20*numpy.sqrt(5), 1/4 - 1/20*numpy.sqrt(5), 1/4 + (3/20)*numpy.sqrt(5), 1/4 - 1/20*numpy.sqrt(5)], [1/4 - 1/20*numpy.sqrt(5), 1/4 - 1/20*numpy.sqrt(5), 1/4 - 1/20*numpy.sqrt(5), 1/4 + (3/20)*numpy.sqrt(5)]])

def gw():
    return numpy.array([[0.25], [0.25], [0.25], [0.25]])

def V(x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, x5, y5, z5, x6, y6, z6, x7, y7, z7, x8, y8, z8, x9, y9, z9, x10, y10, z10):
    return -1/6*x1*y2*z3 + (1/6)*x1*y2*z4 + (1/6)*x1*y3*z2 - 1/6*x1*y3*z4 - 1/6*x1*y4*z2 + (1/6)*x1*y4*z3 + (1/6)*x2*y1*z3 - 1/6*x2*y1*z4 - 1/6*x2*y3*z1 + (1/6)*x2*y3*z4 + (1/6)*x2*y4*z1 - 1/6*x2*y4*z3 - 1/6*x3*y1*z2 + (1/6)*x3*y1*z4 + (1/6)*x3*y2*z1 - 1/6*x3*y2*z4 - 1/6*x3*y4*z1 + (1/6)*x3*y4*z2 + (1/6)*x4*y1*z2 - 1/6*x4*y1*z3 - 1/6*x4*y2*z1 + (1/6)*x4*y2*z3 + (1/6)*x4*y3*z1 - 1/6*x4*y3*z2

