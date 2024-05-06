
import torch
from torch import Tensor
import torch.utils

from .integrator import DomainIntegrator, _FS, _S, Index, CoefLike
from ..mesh import HomoMesh
from ..utils import process_coef_func, is_scalar


class DiffusionIntegrator(DomainIntegrator[_FS]):
    r"""The diffusion integrator for function spaces based on homogeneous meshes."""
    def __init__(self, c: CoefLike, q: int=3) -> None:
        self.coef = c
        self.q = q

    def assembly_cell_matrix(self, space: _FS, index: Index=_S) -> Tensor:
        coef = self.coef
        q = self.q
        mesh = getattr(space, 'mesh', None)

        if not isinstance(mesh, HomoMesh):
            raise RuntimeError("The DiffusionIntegrator only support spaces on"
                               f"homogeneous meshes, but {type(mesh).__name__} is"
                               "not a subclass of HomoMesh.")

        cm = mesh.entity_measure('cell', index)
        NC = cm.size(0)
        qf = mesh.integrator(q, 'cell')
        bcs, ws = qf.get_quadrature_points_and_weights()
        NQ = ws.size(0)

        gphi = space.grad_basis(bcs, index)

        if coef is None:
            return torch.einsum('q, qci..., qcj..., c -> cij', ws, gphi, gphi, cm)
        else:
            coef = process_coef_func(coef, mesh=mesh, index=index)
            if is_scalar(coef):
                return torch.einsum('q, qci..., qcj..., c -> cij', ws, gphi, gphi, cm) * coef
            else:
                if coef.shape == (NC, ):
                    return torch.einsum('q, qci..., qcj..., c -> cij', ws, gphi, gphi, cm*coef)
                elif coef.shape == (NQ, NC):
                    return torch.einsum('q, qci..., qcj..., c, qc -> cij', ws, gphi, gphi, cm, coef)
                else:
                    RuntimeError(f'coef.shape = {coef.shape} is not supported.')
