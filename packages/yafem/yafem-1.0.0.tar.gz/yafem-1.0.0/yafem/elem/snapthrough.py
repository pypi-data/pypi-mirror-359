import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.linalg import block_diag
from yafem.nodes import nodes
from yafem.elem.core_elem import core_elem
from yafem.elem.snapthrough_func import *

class snapthrough(core_elem):

    #%% class constructor
    def __init__(self, my_nodes, pars):

        # superclass constructor
        super().__init__(my_nodes,pars)

        # link the nodes to the element
        self.my_nodes = my_nodes
        
        # extract parameters and assign default values
        self.extract_pars(pars)

        self.element_dofs(1)

        # initialization of matrices
        self.K =    self.compute_K()
        self.r =    self.compute_r()
        self.K0 =   snapthrough_K0(self.A, self.E, self.a, self.L)
        self.r0 =   snapthrough_r0(self.A, self.E, self.a, self.L)
        self.rmax = snapthrough_rmax(self.A, self.E, self.a, self.L)

    #%% extract parameters
    def extract_pars(self, pars):
        self.E            = pars.get("E", 2.1e11) # young's modulus
        self.A            = pars.get("A", 0.01) # element cross section area
        self.a            = pars.get("a", 1.0) # displacement step
        self.u            = pars.get("u", 1.0) # displacement
        # self.L            = pars.get("L", 1.0) # element length
        self.nodal_labels = pars.get("nodal_labels", [1, 2])

        # extract nodal coordinates
        self.nodal_coords = self.my_nodes.find_coords(self.nodal_labels)
        self.L = np.linalg.norm(self.nodal_coords[1] - self.nodal_coords[0])
    
    #%% Computing element dofs
    def element_dofs(self, dofs_per_node):

        self.dofs = np.empty([dofs_per_node*2,2],dtype=int)

        self.dofs[0:dofs_per_node,0] = self.nodal_labels[0] # Label of first node
        self.dofs[dofs_per_node:,0]  = self.nodal_labels[1] # Label of second node
        self.dofs[:,1] = np.tile(np.arange(0,dofs_per_node), 2) + 1 # Dofs of both nodes
    
        return self.dofs

    #%% Restoring force
    def compute_r(self):

        # Link to the restoring force vector
        r = snapthrough_r(self.A, self.E, self.a, self.L, self.u)

        return r

    #%% Tangent stiffness
    def compute_K(self):

        # Link to the restoring force vector
        K = snapthrough_K(self.A, self.E, self.a, self.L, self.u)

        return K
