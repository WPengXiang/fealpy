import numpy as np 
from typing import Union, Optional, Sequence, Tuple, Any

from .utils import entitymethod, estr2dim

from ..backend import backend_manager as bm 
from ..typing import TensorLike, Index, _S
from .. import logger

from .mesh_base import StructuredMesh

class UniformMesh2d(StructuredMesh):
    def __init__(self,
                 extent: Tuple[int, int, int, int],
                 h: Tuple[float, float] = (1.0, 1.0),
                 origin: Tuple[float, float] = (0.0, 0.0)):
        super().__init__(TD=2)
        # Mesh properties
        self.extent: Tuple[int, int, int, int] = extent
        self.h: Tuple[float, float] = h
        self.origin: Tuple[float, float] = origin

        # Mesh dimensions
        self.nx = self.extent[1] - self.extent[0]
        self.ny = self.extent[3] - self.extent[2]
        self.NN = (self.nx + 1) * (self.ny + 1)
        self.NE = self.ny * (self.nx + 1) + self.nx * (self.ny + 1)
        self.NF = self.NE
        self.NC = self.nx * self.ny

        self.nodedata = {}
        self.edgedata = {}
        self.facedata = self.edgedata
        self.celldata = {}
        self.meshdata = {}

        self.meshtype = 'UniformMesh2d'

        self.face_to_ipoint = self.edge_to_ipoint

    @property
    def ftype(self) -> Any:
        h = self.h
        if h is None:
            raise RuntimeError('Can not get the float type as the h '
                               'has not been assigned.')
        return type(h[0])
    
    @property
    def itype(self) -> Any:
        extent = self.extent
        if extent is None:
            raise RuntimeError('Can not get the int type as the extent '
                               'has not been assigned.')
        return type(extent[0])

    @entitymethod(0)
    def _get_node(self):
        GD = 2
        nx = self.nx
        ny = self.ny
        box = [self.origin[0], self.origin[0] + nx * self.h[0],
               self.origin[1], self.origin[1] + ny * self.h[1]]
        x = bm.linspace(box[0], box[1], nx + 1)
        y = bm.linspace(box[2], box[3], ny + 1)
        xx, yy = bm.meshgrid(x, y, indexing='ij')
        node = bm.zeros((nx + 1, ny + 1, GD), dtype=self.ftype)
        #node = bm.zeros((nx + 1, ny + 1, GD), dtype=bm.float64)
        #node[..., 0] = xx
        #node[..., 1] = yy
        node = bm.concatenate((xx[..., np.newaxis], yy[..., np.newaxis]), axis=-1)

        return node
    
    @entitymethod(1)
    def _get_edge(self):
        nx = self.nx
        ny = self.ny

        NN = self.NN
        NE = self.NE

        idx = bm.arange(NN, dtype=self.itype).reshape(nx + 1, ny + 1)
        edge = bm.zeros((NE, 2), dtype=self.itype)
        #edge = bm.zeros((NE, 2), dtype=bm.int32)

        if bm.backend_name == 'numpy' or bm.backend_name == 'pytorch':
            NE0 = 0
            NE1 = nx * (ny + 1)
            edge[NE0:NE1, 0] = idx[:-1, :].reshape(-1)
            edge[NE0:NE1, 1] = idx[1:, :].reshape(-1)
            edge[NE0 + ny:NE1:ny + 1, :] = bm.flip(edge[NE0 + ny:NE1:ny + 1], axis=[1])

            #edge[NE0 + ny:NE1:ny + 1, :] = edge[NE0 + ny:NE1:ny + 1, -1::-1]

            NE0 = NE1
            NE1 += ny * (nx + 1)
            edge[NE0:NE1, 0] = idx[:, :-1].reshape(-1)
            edge[NE0:NE1, 1] = idx[:, 1:].reshape(-1)
            edge[NE0:NE0 + ny, :] = bm.flip(edge[NE0:NE0 + ny], axis=[1])

            #edge[NE0:NE0 + ny, :] = edge[NE0:NE0 + ny, -1::-1]

            return edge
        elif bm.backend_name == 'jax':
            raise NotImplementedError("Jax backend is not yet implemented.")
        else:
            raise NotImplementedError("Backend is not yet implemented.")
    
    @entitymethod(2)
    def _get_cell(self):
        nx = self.nx
        ny = self.ny

        NN = self.NN
        NC = self.NC
        cell = bm.zeros((NC, 4), dtype=self.itype)
        #cell = bm.zeros((NC, 4), dtype=bm.int32)
        idx = bm.arange(NN).reshape(nx + 1, ny + 1)
        c = idx[:-1, :-1]
        #cell[:, 0] = c.reshape(-1)
        #cell[:, 1] = cell[:, 0] + 1
        #cell[:, 2] = cell[:, 0] + ny + 1
        #cell[:, 3] = cell[:, 2] + 1
        cell_0 = c.reshape(-1)
        cell_1 = cell_0 + 1
        cell_2 = cell_0 + ny + 1
        cell_3 = cell_2 + 1
        cell = bm.concatenate([cell_0[:, None], cell_1[:, None], cell_2[:, None], cell_3[:, None]], axis=-1)

        return cell
    
    def entity(self, etype: Union[int, str], index=_S) -> TensorLike:
        GD = 2
        if isinstance(etype, str):
           etype = estr2dim(self, etype)
        # if etype in {'cell', 2}:
        #     return self.cell[index, ...]
        # elif etype in {'edge', 'face', 1}:
        #     return self.edge[index, ...]
        # elif etype in {'node', 0}:
        #     return self.node.reshape(-1, GD)[index, ...]
        if etype == 2:
            return self.cell[index, ...]
        elif etype == 1:
            return self.edge[index, ...]
        elif etype == 0:
            return self.node.reshape(-1, GD)[index, ...]
        else:
            raise ValueError("`etype` is wrong!")
    
    def entity_measure(self, etype: Union[int, str]) -> TensorLike:
       if isinstance(etype, str):
           etype = estr2dim(self, etype)
       if etype == 0:
           return bm.tensor(0, dtype=self.ftype)
       elif etype == 1:
           return self.h[0], self.h[1]
       elif etype == 2:
           return self.h[0] * self.h[1]
       else:
           raise ValueError(f"Unsupported entity or top-dimension: {etype}")
    
    def quadrature_formula(self, q, etype:Union[int, str]='cell'):
        from ..quadrature import GaussLegendreQuadrature, TensorProductQuadrature
        if isinstance(etype, str):
            etype = estr2dim(self, etype)
        qf = GaussLegendreQuadrature(q)
        if etype == 2:
            return TensorProductQuadrature((qf, qf))
        elif etype == 1:
            return qf
        else:
            raise ValueError(f"entity type: {etype} is wrong!")

    def number_of_local_ipoints(self, p, iptype='cell'):
        if iptype in {'cell', 2}:
            return (p+1) * (p+1)
        elif iptype in {'face', 'edge',  1}:
            return p + 1
        elif iptype in {'node', 0}:
            return 1
        
    def number_of_global_ipoints(self, p: int) -> int:
        NN = self.number_of_nodes()
        NE = self.number_of_edges()
        NC = self.number_of_cells()
        return NN + (p-1)*NE + (p-1)*(p-1)*NC

    def interpolation_points(self, p):
        cell = self.cell
        edge = self.edge
        node = self.entity('node')

        GD = self.geo_dimension()
        if p <= 0:
            raise ValueError("p must be a integer larger than 0.")
        if p == 1:
            return node.reshape(-1, GD)

        NN = self.number_of_nodes()
        gdof = self.number_of_global_ipoints(p)
        ipoints = bm.zeros((gdof, GD), dtype=self.ftype)
        ipoints[:NN, :] = node

        NE = self.number_of_edges()
        multiIndex = self.multi_index_matrix(p, 1)
        w = multiIndex[1:-1, :] / p
        ipoints[NN:NN + (p-1) * NE, :] = bm.einsum('ij, ...jm -> ...im', w,
                node[edge,:]).reshape(-1, GD)

        w = np.einsum('im, jn -> ijmn', w, w).reshape(-1, 4)
        ipoints[NN + (p-1) * NE:, :] = bm.einsum('ij, kj... -> ki...', w,
                node[cell[:]]).reshape(-1, GD)

        return ipoints
    
    def jacobi_matrix(self, bcs: TensorLike, index: Index=_S) -> TensorLike:
        """
        @brief 计算参考单元 (xi, eta) 到实际 Lagrange 四边形(x) 之间映射的 Jacobi 矩阵。

        x(xi, eta) = phi_0 x_0 + phi_1 x_1 + ... + phi_{ldof-1} x_{ldof-1}
        """
        node = self.entity('node')
        cell = self.entity('cell', index=index)
        gphi = self.grad_shape_function(bcs, p=1, variables='u', index=index)
        J = bm.einsum( 'cim, ...in->...cmn', node[cell[:]], gphi)

        return J
    
    def first_fundamental_form(self, J: TensorLike) -> TensorLike:
        """
        @brief 由 Jacobi 矩阵计算第一基本形式。
        """
        TD = J.shape[-1]

        shape = J.shape[0:-2] + (TD, TD)
        G = bm.zeros(shape, dtype=self.ftype)
        for i in range(TD):
            G[..., i, i] = bm.einsum('...d, ...d -> ...', J[..., i], J[..., i])
            for j in range(i+1, TD):
                G[..., i, j] = bm.einsum('...d, ...d -> ...', J[..., i], J[..., j])
                G[..., j, i] = G[..., i, j]
        return G
       
    def shape_function(self, bcs: TensorLike, p: int=1, 
                    mi: Optional[TensorLike]=None) -> TensorLike:
        assert isinstance(bcs, tuple)

        TD = bcs[0].shape[-1] - 1
        if mi is None:
            mi = bm.multi_index_matrix(p, TD, dtype=self.itype)
        phi = [bm.simplex_shape_function(val, p, mi) for val in bcs]
        ldof = self.number_of_local_ipoints(p)

        return bm.einsum('im, jn -> ijmn', phi[0], phi[1]).reshape(-1, ldof)
    
    def grad_shape_function(self, bcs: Tuple[TensorLike], p: int=1, index: Index=_S, 
                        variables: str='x') -> TensorLike:
        assert isinstance(bcs, tuple)

        Dlambda = bm.array([-1, 1], dtype=self.ftype)

        phi0 = bm.simplex_shape_function(bcs[0], p=p)
        R0 = bm.simplex_grad_shape_function(bcs[0], p=p)
        gphi0 = bm.einsum('...ij, j -> ...i', R0, Dlambda) # (..., ldof)

        phi1 = bm.simplex_shape_function(bcs[1], p=p)
        R1 = bm.simplex_grad_shape_function(bcs[1], p=p)
        gphi1 = bm.einsum('...ij, j->...i', R1, Dlambda) # (..., ldof)

        n = phi0.shape[0] * phi1.shape[0]
        ldof = phi0.shape[-1] * phi1.shape[-1]

        shape = (n, ldof, 2)
        gphi = bm.zeros(shape, dtype=self.ftype)

        gphi[..., 0] = bm.einsum('im, kn -> ikmn', gphi0, phi1).reshape(-1, ldof)
        gphi[..., 1] = bm.einsum('im, kn -> ikmn', phi0, gphi1).reshape(-1, ldof)

        if variables == 'u':
            return gphi
        elif variables == 'x':
            J = self.jacobi_matrix(bcs, index=index)
            G = self.first_fundamental_form(J)
            G = bm.linalg.inv(G)
            gphi = bm.einsum('...ikm, ...imn, ...ln -> ...ilk', J, G, gphi)
            return gphi
    
    def uniform_refine(self, n=1):
        # TODO: There is a problem with this code
        for i in range(n):
            self.extent = [i * 2 for i in self.extent]
            self.h = [h / 2.0 for h in self.h]
            self.nx = self.extent[1] - self.extent[0]
            self.ny = self.extent[3] - self.extent[2]

            self.NC = self.nx * self.ny
            self.NF = self.NE
            self.NE = self.ny * (self.nx + 1) + self.nx * (self.ny + 1)
            self.NN = (self.nx + 1) * (self.ny + 1)
        
        del self.node
        del self.edge
        del self.cell
        # TODO: Implement cache clearing mechanism


