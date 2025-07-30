import numpy

def beam2d_gen_Kl(A, E, I, L, alpha, fa, fb, k0a, k0b, rho, theta):
    return numpy.array([[A*E/L + (1/3)*L*k0a, 0, 0, -A*E/L + (1/6)*L*k0a, 0, 0], [0, 12*E*I/L**3 + (13/35)*L*k0b, (1/210)*(1260*E*I + 11*L**4*k0b)/L**2, 0, -12*E*I/L**3 + (9/70)*L*k0b, (1/420)*(2520*E*I - 13*L**4*k0b)/L**2], [0, (1/210)*(1260*E*I + 11*L**4*k0b)/L**2, (1/105)*(420*E*I + L**4*k0b)/L, 0, (1/420)*(-2520*E*I + 13*L**4*k0b)/L**2, (1/140)*(280*E*I - L**4*k0b)/L], [-A*E/L + (1/6)*L*k0a, 0, 0, A*E/L + (1/3)*L*k0a, 0, 0], [0, -12*E*I/L**3 + (9/70)*L*k0b, (1/420)*(-2520*E*I + 13*L**4*k0b)/L**2, 0, 12*E*I/L**3 + (13/35)*L*k0b, (1/210)*(-1260*E*I - 11*L**4*k0b)/L**2], [0, (1/420)*(2520*E*I - 13*L**4*k0b)/L**2, (1/140)*(280*E*I - L**4*k0b)/L, 0, (1/210)*(-1260*E*I - 11*L**4*k0b)/L**2, (1/105)*(420*E*I + L**4*k0b)/L]])

def beam2d_gen_Ml(A, E, I, L, alpha, fa, fb, k0a, k0b, rho, theta):
    return numpy.array([[(1/3)*A*L*rho, 0, 0, (1/6)*A*L*rho, 0, 0], [0, (13/35)*A*L*rho, (11/210)*A*L**2*rho, 0, (9/70)*A*L*rho, -13/420*A*L**2*rho], [0, (11/210)*A*L**2*rho, (1/105)*A*L**3*rho, 0, (13/420)*A*L**2*rho, -1/140*A*L**3*rho], [(1/6)*A*L*rho, 0, 0, (1/3)*A*L*rho, 0, 0], [0, (9/70)*A*L*rho, (13/420)*A*L**2*rho, 0, (13/35)*A*L*rho, -11/210*A*L**2*rho], [0, -13/420*A*L**2*rho, -1/140*A*L**3*rho, 0, -11/210*A*L**2*rho, (1/105)*A*L**3*rho]])

def beam2d_gen_rl(A, E, I, L, alpha, fa, fb, k0a, k0b, rho, theta):
    return numpy.array([[-A*E*alpha*theta + (1/2)*L*fa], [(1/2)*L*fb], [(1/12)*L**2*fb], [A*E*alpha*theta + (1/2)*L*fa], [(1/2)*L*fb], [-1/12*L**2*fb]])

def beam2d_gen_Nl(A, E, I, L, alpha, fa, fb, k0a, k0b, rho, theta):
    return numpy.array([[0, 0, 0, 1, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0]])

def beam2d_gen_Bl(A, E, I, L, alpha, fa, fb, k0a, k0b, rho, theta):
    return numpy.array([[-1/L, 0, 0, L**(-1.0), 0, 0], [0, -6/L**2, -4/L, 0, 6/L**2, -2/L], [0, 6/L**2, 2/L, 0, -6/L**2, 4/L]])

def beam2d_gen_Dcs_mid(A, E, I, L, alpha, fa, fb, k0a, k0b, rho, theta):
    return numpy.array([[A*E, 0, 0], [0, E*I, 0], [0, 0, E*I]])

