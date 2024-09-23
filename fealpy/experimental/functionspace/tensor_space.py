
from typing import Tuple, Union, Callable
from math import prod

from ..backend import backend_manager as bm
from ..typing import TensorLike, Size, _S
from .functional import generate_tensor_basis, generate_tensor_grad_basis
from .space import FunctionSpace, _S, Index
from .utils import to_tensor_dof
from fealpy.decorator import barycentric, cartesian


class TensorFunctionSpace(FunctionSpace):
    def __init__(self, scalar_space: FunctionSpace, shape: Tuple[int, ...]) -> None:
        """_summary_

        Parameters:
            scalar_space (FunctionSpace): The scalar space to build tensor space from.\n
            shape (int, ...): Shape of each dof.
                Requires a `-1` be the first or last element to mark the priority
                of the DoF in arrangement.
        """
        self.scalar_space = scalar_space
        self.shape = shape

        if len(shape) < 2:
            raise ValueError('shape must be a tuple of at least two element')

        if shape[0] == -1:
            self.dof_shape = tuple(shape[1:])
            self.dof_priority = False
        elif shape[-1] == -1:
            self.dof_shape = tuple(shape[:-1])
            self.dof_priority = True
        else:
            raise ValueError('`-1` is required as the first or last element')
        
        self.p = self.scalar_space.p

    @property
    def mesh(self):
        return self.scalar_space.mesh

    @property
    def device(self): return self.scalar_space.device
    @property
    def ftype(self): return self.scalar_space.ftype
    @property
    def itype(self): return self.scalar_space.itype

    @property
    def dof_numel(self) -> int:
        return prod(self.dof_shape)

    @property
    def dof_ndim(self) -> int:
        return len(self.dof_shape)

    def number_of_global_dofs(self) -> int:
        return self.dof_numel * self.scalar_space.number_of_global_dofs()

    def number_of_local_dofs(self, doftype='cell') -> int:
        return self.dof_numel * self.scalar_space.number_of_local_dofs(doftype)

    def basis(self, p: TensorLike, index: Index=_S, **kwargs) -> TensorLike:
        phi = self.scalar_space.basis(p, index, **kwargs) # (NC, NQ, ldof)
        return generate_tensor_basis(phi, self.dof_shape, self.dof_priority)

    def grad_basis(self, p: TensorLike, index: Index=_S, **kwargs) -> TensorLike:
        gphi = self.scalar_space.grad_basis(p, index, **kwargs)
        return generate_tensor_grad_basis(gphi, self.dof_shape, self.dof_priority)

    def cell_to_dof(self) -> TensorLike:
        """Get the cell to dof mapping.

        Returns:
            Tensor: Cell to dof mapping, shaped (NC, ldof*dof_numel).
        """
        return to_tensor_dof(
            self.scalar_space.cell_to_dof(),
            self.dof_numel,
            self.scalar_space.number_of_global_dofs(),
            self.dof_priority
        )

    def face_to_dof(self) -> TensorLike:
        """Get the face to dof mapping.

        Returns:
            Tensor: Face to dof mapping, shaped (NF, ldof*dof_numel).
        """
        return to_tensor_dof(
            self.scalar_space.face_to_dof(),
            self.dof_numel,
            self.scalar_space.number_of_global_dofs(),
            self.dof_priority
        )

    def interpolation_points(self) -> TensorLike:

        return self.scalar_space.interpolation_points()
    
    def interpolate(self, u: Union[Callable[..., TensorLike], TensorLike], ) -> TensorLike:

        if self.dof_priority:
            uI = self.scalar_space.interpolate(u)
            ndim = len(self.shape)
            uI = bm.swapaxes(uI, ndim-1, ndim-2) 
        else:
            uI = self.scalar_space.interpolate(u)   

        return uI.reshape(-1)
    
    def is_boundary_dof(self, threshold=None) -> TensorLike:
        """
        Return boolean values indicating boundary degrees of freedom (dofs).

        Parameters:
        threshold (callable, tuple of callables, or None, optional): 
            A function or a tuple used to determine boundary conditions. 
            - If a function, it should return a boolean array indicating which edges are on the boundary. 
            - If a tuple, the first element should be a function that returns a boolean array for boundary edges, 
            the second element should be a function or array that specifies nodes, and the third element should be a 
            function or array that returns direction flags.
            - The direction flags can be either:
                - A boolean array (e.g., [True, False]) specifying which directions to apply the boundary condition 
                (True for applying the condition, False for not applying).
                - An integer array (e.g., [1, 0]) where non-zero values specify the directions to apply the boundary 
                condition (1 for applying, 0 for not applying).
            - If `direction_flags` is provided and its shape matches `(scalar_gdof,)`, it specifies conditions 
            for specific degrees of freedom at certain nodes.

        Returns:
            TensorLike: A flattened boolean array indicating which global degrees of freedom are boundary dofs.
                        Shape is (scalar_gdof * dof_numel,).
        """
        if isinstance(threshold, tuple):
            edge_threshold = threshold[0]
            node_threshold = threshold[1] if len(threshold) > 1 else None
            direction_threshold = threshold[2] if len(threshold) > 2 else None
        else:
            edge_threshold = threshold
            node_threshold = None
            direction_threshold = None

        scalar_gdof = self.scalar_space.number_of_global_dofs()
        scalar_is_bd_dof = self.scalar_space.is_boundary_dof(edge_threshold)

        if node_threshold is not None:
            node_flags = node_threshold()
            scalar_is_bd_dof = scalar_is_bd_dof & node_flags

        if self.dof_priority:
            is_bd_dof = bm.reshape(scalar_is_bd_dof, (-1,) * self.dof_ndim + (scalar_gdof,))
            is_bd_dof = bm.broadcast_to(is_bd_dof, self.dof_shape + (scalar_gdof,))
        else:
            is_bd_dof = bm.reshape(scalar_is_bd_dof, (scalar_gdof,) + (-1,) * self.dof_ndim)
            is_bd_dof = bm.broadcast_to(is_bd_dof, (scalar_gdof,) + self.dof_shape)

        if direction_threshold is not None:
            if callable(direction_threshold):
                direction_flags = direction_threshold()
            else:
                direction_flags = bm.array(direction_threshold)

            if direction_flags.shape[0] == scalar_gdof:
                direction_flags_broadcast = bm.broadcast_to(direction_flags, is_bd_dof.shape)
                is_bd_dof = is_bd_dof & direction_flags_broadcast
            else:
                if direction_flags.dtype != bool:
                    direction_flags = direction_flags != 0

                if self.dof_priority:
                    direction_flags_broadcast = bm.reshape(direction_flags, (-1, 1))
                    direction_flags_broadcast = bm.broadcast_to(direction_flags_broadcast, is_bd_dof.shape)
                else:
                    direction_flags_broadcast = bm.broadcast_to(direction_flags, is_bd_dof.shape)

                is_bd_dof = is_bd_dof & direction_flags_broadcast

        return is_bd_dof.reshape(-1)
    
    def boundary_interpolate(self,
        gD: Union[Callable, int, float, TensorLike],
        uh: TensorLike,
        threshold: Union[Callable, TensorLike, None]=None) -> TensorLike:

        ipoints = self.interpolation_points()
        scalar_space = self.scalar_space
        # isScalarBDof = scalar_space.is_boundary_dof(threshold=threshold)

        if isinstance(threshold, tuple):
            edge_threshold = threshold[0]
            node_threshold = threshold[1] if len(threshold) > 1 else None
            direction_threshold = threshold[2] if len(threshold) > 2 else None
        else:
            edge_threshold = threshold
            node_threshold = None
            direction_threshold = None

        isScalarBDof = scalar_space.is_boundary_dof(threshold=edge_threshold)
        if node_threshold is not None:
            node_flags = node_threshold()
            isScalarBDof = isScalarBDof & node_flags

        if callable(gD):
            gD_scalar = gD(ipoints[isScalarBDof])
        else:
            gD_scalar = gD

        if direction_threshold is not None:
            direction_flags = direction_threshold()
            node_direction_flags = direction_flags[node_flags] 

        gD_vector = gD_scalar[node_direction_flags] 

        # isTensorBDof = self.is_boundary_dof(threshold=threshold)
        isTensorBDof = self.is_boundary_dof(threshold=(edge_threshold, 
                                                       node_threshold, 
                                                       direction_threshold))

        if self.dof_priority:
            uh = bm.set_at(uh, isTensorBDof, gD_vector.T.reshape(-1))
        else:
            uh = bm.set_at(uh, isTensorBDof, gD_vector.reshape(-1))

        return uh, isTensorBDof

    @barycentric
    def value(self, uh: TensorLike, bc: TensorLike, index: Index=_S) -> TensorLike:
        phi = self.basis(bc, index=index)
        c2dof = self.cell_to_dof()[index]
        val = bm.einsum('cql..., cl... -> cq...', phi, uh[c2dof, ...])
        return val
    
    @barycentric
    def grad_value(self, uh: TensorLike, bc: TensorLike, index: Index=_S) -> TensorLike:
        gphi = self.grad_basis(bc, index=index)
        cell2dof = self.cell_to_dof()[index]
        val = bm.einsum('cqlmn..., cl... -> cqmn', gphi, uh[cell2dof, ...])
        return val[...]
