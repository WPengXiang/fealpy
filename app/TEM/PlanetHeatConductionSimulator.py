import numpy as np
import matplotlib.pyplot as plt
import pyamg
import meshio
import sys
import copy

from fealpy.functionspace.WedgeLagrangeFiniteElementSpace import WedgeLagrangeFiniteElementSpace
from fealpy.mesh import  LagrangeTriangleMesh, LagrangeWedgeMesh
from fealpy.writer import MeshWriter
from fealpy.decorator import cartesian, barycentric
from scipy.sparse.linalg import spsolve
from fealpy.tools.show import showmultirate, show_error_table

from nonlinear_robin import nonlinear_robin

class PlanetHeatConductionSimulator():
    def __init__(self, pde, mesh, p=1):
        self.space = WedgeLagrangeFiniteElementSpace(mesh, p=p)
        self.mesh = self.space.mesh
        self.pde = pde
        self.nr = nonlinear_robin(self.pde, self.space, self.mesh, p=p)
        
        self.M = self.space.mass_matrix()
        self.A = self.space.stiff_matrix()
        
        self.mesh.meshdata['A'] = 0.1 # 邦德反照率
        self.mesh.meshdata['epsilon'] = 0.9 # 辐射率
        self.mesh.meshdata['rho'] = 1400 # kg/m^3 密度
        self.mesh.meshdata['c'] = 1200 # Jkg^-1K^-1 比热容
        self.mesh.meshdata['kappa'] = 0.02 # Wm^-1K^-1 热导率
        self.mesh.meshdata['sigma'] = 5.6367e-8 # 玻尔兹曼常数
        self.mesh.meshdata['q'] = 1367.5 # W/m^2 太阳辐射通量
        self.mesh.meshdata['mu0'] = self.pde.init_mu()  # max(cos beta,0) 太阳高度角参数

    def time_mesh(self, NT=100):
        from fealpy.timeintegratoralg.timeline import UniformTimeLine
        timeline = UniformTimeLine(0, 5, NT)
        return timeline

    def init_solution(self, timeline):
        NL = timeline.number_of_time_levels()
        gdof = self.space.number_of_global_dofs()
        uh = np.zeros((gdof, NL), dtype=np.float)
        uh[:, 0] = 150
        return uh

    def apply_boundary_condition(self, A, b, uh, timeline):
        from fealpy.boundarycondition import RobinBC
        from fealpy.boundarycondition import NeumannBC
        from fealpy.boundarycondition import DirichletBC
        t0 = timeline.current_time_level()
        t1 = timeline.next_time_level()
        i = timeline.current

        # 对 robin 边界条件进行处理
        bc = RobinBC(self.space, lambda x, n:self.pde.robin(x, n, t0), threshold=self.pde.is_robin_boundary)
        A0, b = bc.apply(A, b)
       
       # 对 neumann 边界条件进行处理
        bc = NeumannBC(self.space, lambda x, n:self.pde.neumann(x, n, t0), threshold=self.pde.is_neumann_boundary)
        b = bc.apply(b) # 混合边界条件不需要输入矩阵A
        return b

    def solve(self, uh, timeline):
        '''  piccard 迭代  C-N 方法 '''
        from nonlinear_robin import nonlinear_robin

        i = timeline.current
        t1 = timeline.next_time_level()
        dt = timeline.current_time_step_length()
        F = self.pde.right_vector(uh, timeline)

        # 网格数据
        rho = self.mesh.meshdata['rho']
        c = self.mesh.meshdata['c']
        kappa = self.mesh.meshdata['kappa']
        epsilon = self.mesh.meshdata['epsilon']
        sigma = self.mesh.meshdata['sigma']

        A = kappa*self.A
        M = rho*c*self.M
        b = self.apply_boundary_condition(A, F, uh, timeline)
        
        e = 0.0000000001
        error = 1
        xi_new = self.space.function()
        xi_new[:] = copy.deepcopy(uh[:, i])
        while error > e:
            xi_tmp = copy.deepcopy(xi_new[:])
            R = self.nr.robin_bc(A, xi_new, lambda x, n:self.pde.robin(x,
                n, t1), threshold=self.pde.is_robin_boundary)
            r = M@uh[:, i] - 0.5*dt*R@uh[:,i] + dt*b
            R = M + 0.5*dt*R
            ml = pyamg.ruge_stuben_solver(R)
            xi_new[:] = ml.solve(r, tol=1e-12, accel='cg').reshape(-1)
#            xi_new[:] = spsolve(R, b).reshape(-1)
            error = np.max(np.abs(xi_tmp-xi_new[:]))
        uh[:, i+1] = xi_new

class TPMModel():
    def __init__(self):
        pass

    def init_mesh(self, n=0, h=0.005, nh=100, p=1):
        fname = 'initial/file1.vtu'
        data = meshio.read(fname)
        node = data.points
        cell = data.cells[0][1]

        mesh = LagrangeTriangleMesh(node*500, cell, p=p)
        mesh.uniform_refine(n)
        mesh = LagrangeWedgeMesh(mesh, h, nh, p=p)

        self.mesh = mesh
        self.p = p
        return mesh

    def init_mu(self):
        boundary_face_index = self.is_robin_boundary(0)
        qf0, qf1 = self.mesh.integrator(self.p, 'face')
        bcs, ws = qf0.get_quadrature_points_and_weights()
        m = mesh.boundary_tri_face_unit_normal(bcs, index=boundary_face_index)

        # 小行星外法向
        n = np.array([1, 1, 1]) # 指向太阳的方向
        n = n/np.sqrt(np.dot(n, n))

        mu = np.dot(m, n)
        mu[mu<0] = 0
        return mu
    
    def right_vector(self, uh, timeline):
        shape = uh.shape[0]
        f = np.zeros(shape, dtype=np.float)
        return f 
    
    @cartesian
    def neumann(self, p, n, t):
        gN = np.zeros((p.shape[0], p.shape[1]), dtype=np.float)
        return gN

    @cartesian
    def is_neumann_boundary(self, p):
        tface, qface = self.mesh.entity('face')
        NTF = len(tface)
        boundary_neumann_tface_index = np.zeros(NTF, dtype=np.bool_)
        boundary_neumann_tface_index[-NTF//2:] = True
        return boundary_neumann_tface_index 

    @cartesian    
    def robin(self, p, n, t):
        """ Robin boundary condition
        """
        A = self.mesh.meshdata['A']
        q = self.mesh.meshdata['q']
        mu = self.mesh.meshdata['mu0']
       
        epsilon = self.mesh.meshdata['epsilon']
        sigma = self.mesh.meshdata['sigma']
        
        n = np.ones((p.shape[0], p.shape[1]),dtype=np.float)
        shape = len(n.shape)*(1, )
        kappa = -epsilon*sigma*np.array([1.0], dtype=np.float64).reshape(shape)
        return -(1-A)*q*mu*n, kappa
    
    @cartesian
    def is_robin_boundary(self, p):
        tface, qface = self.mesh.entity('face')
        NTF = len(tface)
        boundary_robin_tface_index = np.zeros(NTF, dtype=np.bool_)
        boundary_robin_tface_index[:NTF//2] = True
        return boundary_robin_tface_index 

if __name__ == '__main__':
    p = int(sys.argv[1])
    n = int(sys.argv[2])
    NT = int(sys.argv[3])
    maxit = int(sys.argv[4])
#    h = float(sys.argv[5])
#    nh = int(sys.argv[6])
    h = 0.5
    nh = 1

    pde = TPMModel()
    mesh = pde.init_mesh(n=n, h=h, nh=nh, p=p)

    simulator  = PlanetHeatConductionSimulator(pde, mesh)

    timeline = simulator.time_mesh(NT=NT)

    Ndof = np.zeros(maxit, dtype=np.float)
    
    for i in range(maxit):
        print(i)
        model = PlanetHeatConductionSimulator(pde, mesh, p=p)
        
        Ndof[i] = model.space.number_of_global_dofs()

        uh = model.init_solution(timeline)

        timeline.time_integration(uh, model, spsolve)

        if i < maxit-1:
            timeline.uniform_refine()
#                mesh.uniform_refine()
            n = n+1
            h = h/2
            nh = nh*2
            mesh = pde.init_mesh(n=n, h=h, nh=nh)
        uh = model.space.function(array=uh[:, -1])
        print('uh:', uh)

    np.savetxt('01solution', uh)

    mesh.to_vtk(fname='test.vtu') 
    fig = plt.figure()
    axes = fig.gca(projection='3d')
    uh.add_plot(axes, cmap='rainbow')

#    show_error_table(Ndof, errorType, errorMatrix)
#    showmultirate(plt, 0, Ndof, errorMatrix, errorType)
#    plt.show()

