
from typing import (
    Any, Tuple, Union, Optional, Callable, TypeGuard, List,
    Literal, Dict, overload, Sequence, Iterable
)

from .base import Backend, Size, Number
from .base import TensorLike as _DT


"""
This class serves as an interface for the computation backend.
All methods in this class are static methods by default,
unless explicitly annotated otherwise.
"""

class BackendManager():
    def __init__(self, *, default_backend: Optional[str]=None): ... # instance method
    def set_backend(self, name: str) -> None: ... # instance method
    def load_backend(self, name: str) -> None: ... # instance method
    def get_current_backend(self) -> Backend: ... # instance method

    ### constants ###

    pi: float
    e: float
    nan: float
    inf: float
    newaxis: Any
    dtype: type
    device: type
    bool: Any
    uint8: Any
    uint16: Any
    uint32: Any
    uint64: Any
    int8: Any
    int16: Any
    int32: Any
    int64: Any
    float16: Any
    float32: Any
    float64: Any
    complex64: Any
    complex128: Any

    ### Backend tools ###
    def is_tensor(self, obj: Any, /) -> TypeGuard[_DT]: ...
    def context(self, tensor: _DT, /) -> Dict[str, Any]: ...
    # PyTorch
    def set_default_device(self, device: Any) -> None: ...
    def get_device(self, tensor_like: _DT, /) -> Any: ...
    def to_numpy(self, tensor_like: _DT, /) -> Any: ...
    def from_numpy(self, ndarray: Any, /) -> _DT: ...

    ### Compiler ###
    @overload
    def compile(self, fun: Callable, /, *,
                fullgraph: bool=False, dynamic: Optional[bool]=None,
                backend: str='inductor', mode: str='default',
                options: Optional[Dict[str, Any]]=None, disable=False) -> Callable: ...
    @overload
    def compile(self, fun: Callable, /, *,
                static_argnums: Union[int, Sequence[int], None]=None,
                static_argnames: Union[str, Iterable[str], None]=None,
                donate_argnums: Union[int, Sequence[int], None]=None,
                donate_argnames: Union[str, Iterable[str], None]=None,
                keep_unused: bool=False,
                device=None, backend: Optional[str]=None, inline: bool=False,
                abstracted_axes=None) -> Callable: ...

    ### Creation Functions ###
    # python array API standard v2023.12
    @overload
    def arange(self, stop: Number, /, step: Number=1, *, dtype=None, device=None) -> _DT: ...
    @overload
    def arange(self, start: Number, /, stop: Number, step: Number=1, *, dtype=None, device=None) -> _DT: ...
    def asarray(self, obj, /, *, dtype=None, device=None, copy=None) -> _DT: ...
    def empty(self, shape: Size, /, *, dtype=None, device=None) -> _DT: ...
    def empty_like(self, x: _DT, /, *, dtype=None, device=None) -> _DT: ...
    def eye(self, n_rows: int, n_cols: Optional[int]=None, /, *, k: int=0, dtype=None, device=None) -> _DT: ...
    def from_dlpack(x: Any, /) -> _DT: ...
    def full(self, shape: Size, fill_value: Number, /, *, dtype=None, device=None) -> _DT: ...
    def full_like(self, x: _DT, fill_value: Number, /, *, dtype=None, device=None) -> _DT: ...
    def linspace(self, start: Number, stop: Number, /, num: int, *, dtype=None, device=None, endpoint=True) -> _DT: ... 
    def meshgrid(self, *arrays: _DT, indexing='xy') -> Tuple[_DT, ...]: ...
    def ones(self, shape: Size, /, *, dtype=None, device=None) -> _DT: ...
    def ones_like(self, x: _DT, /, *, dtype=None, device=None) -> _DT: ...
    def tril(self, x: _DT, /, *, k: int=0) -> _DT: ...
    def triu(self, x: _DT, /, *, k: int=0) -> _DT: ...
    def zeros(self, shape: Size, /, *, dtype=None, device=None) -> _DT: ...
    def zeros_like(self, x: _DT, /, *, dtype=None, device=None) -> _DT: ...

    # non-standard
    def array(self, object, /, dtype=None, **kwargs) -> _DT: ...
    def tensor(self, data, /, dtype=None, **kwargs) -> _DT: ...

    ### Data Type Functions ###
    # python array API standard v2023.12
    def astype(self, x: _DT, dtype, /, *, copy=True, device=None) -> _DT: ...
    def can_cast(self, from_, to, /) -> _DT: ... # TODO
    def finfo(self, dtype, /) -> Any: ...
    def iinfo(self, dtype, /) -> Any: ...
    def isdtype(self, dtype, king) -> bool: ...
    def result_type(self, *arrays_and_dtypes) -> Any: ...

    ### Element-wise Functions ###
    # python array API standard v2023.12
    def abs(self, x: _DT, /) -> _DT: ...
    def acos(self, x: _DT, /) -> _DT: ...
    def acosh(self, x: _DT, /) -> _DT: ...
    def add(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def asin(self, x: _DT, /) -> _DT: ...
    def asinh(self, x: _DT, /) -> _DT: ...
    def atan(self, x: _DT, /) -> _DT: ...
    def atan2(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def atanh(self, x: _DT, /) -> _DT: ...
    def bitwise_and(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def bitwise_left_shift(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def bitwise_invert(self, x: _DT, /) -> _DT: ...
    def bitwise_or(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def bitwise_right_shift(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def bitwise_xor(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def ceil(self, x: _DT, /) -> _DT: ...
    def clip(self, x: _DT, x_min: _DT, x_max: _DT, /) -> _DT: ...
    def conj(self, x: _DT, /) -> _DT: ...
    def copysign(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def cos(self, x: _DT, /) -> _DT: ...
    def cosh(self, x: _DT, /) -> _DT: ...
    def divide(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def equal(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def exp(self, x: _DT, /) -> _DT: ...
    def expm1(self, x: _DT, /) -> _DT: ...
    def floor(self, x: _DT, /) -> _DT: ...
    def floor_divide(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def greater(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def greater_equal(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def hypot(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def imag(self, x: _DT, /) -> _DT: ...
    def isfinite(self, x: _DT, /) -> _DT: ...
    def isinf(self, x: _DT, /) -> _DT: ...
    def isnan(self, x: _DT, /) -> _DT: ...
    def less(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def less_equal(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def log(self, x: _DT, /) -> _DT: ...
    def log1p(self, x: _DT, /) -> _DT: ...
    def log2(self, x: _DT, /) -> _DT: ...
    def log10(self, x: _DT, /) -> _DT: ...
    def logaddexp(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def logical_and(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def logical_not(self, x: _DT, /) -> _DT: ...
    def logical_or(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def logical_xor(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def maximum(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def minimum(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def multiply(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def negative(self, x: _DT, /) -> _DT: ...
    def not_equal(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def positive(self, x: _DT, /) -> _DT: ...
    def pow(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def real(self, x: _DT, /) -> _DT: ...
    def remainder(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def round(self, x: _DT, /) -> _DT: ...
    def sign(self, x: _DT, /) -> _DT: ...
    def sin(self, x: _DT, /) -> _DT: ...
    def sinh(self, x: _DT, /) -> _DT: ...
    def square(self, x: _DT, /) -> _DT: ...
    def sqrt(self, x: _DT, /) -> _DT: ...
    def subtract(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def tan(self, x: _DT, /) -> _DT: ...
    def tanh(self, x: _DT, /) -> _DT: ...
    def trunc(self, x: _DT, /) -> _DT: ...

    # non-standard
    def arcsin(self, x: _DT, /) -> _DT: ...
    def arccos(self, x: _DT, /) -> _DT: ...
    def arctan(self, x: _DT, /) -> _DT: ...
    def arctan2(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def arcsinh(self, x: _DT, /) -> _DT: ...
    def arccosh(self, x: _DT, /) -> _DT: ...
    def arctanh(self, x: _DT, /) -> _DT: ...

    ### Indexing functions ###
    # python array API standard v2023.12
    def take(self, x: _DT, indices: _DT, /, *, axis: Optional[int]=None) -> _DT: ...

    ### Linear Algebra Functions ###
    # python array API standard v2023.12
    def matmul(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def matrix_transpose(x: _DT, /) -> _DT: ...
    def tensordot(self, x1: _DT, x2: _DT, /, *, axes: Union[int, Tuple]) -> _DT: ...
    def vecdot(self, x1: _DT, x2: _DT, /, *, axis: int=-1) -> _DT: ...

    # non-standard
    def cross(self, x1: _DT, x2: _DT, /, *, axis: Optional[int]=None) -> _DT: ...
    def dot(self, x1: _DT, x2: _DT, /, *, axis=-1) -> _DT: ...
    def einsum(self, subscripts: str, /, *operands: _DT, **kwargs) -> _DT: ...

    ### Manipulation Functions ###
    # python array API standard v2023.12
    def broadcast_arrays(self, *arrays: _DT) -> List[_DT]: ...
    def broadcast_to(self, x: _DT, /, shape: Size) -> _DT: ...
    def concat(self, arrays: Union[Tuple[_DT, ...], List[_DT]], /, *, axis=0) -> _DT: ...
    def expand_dims(self, x: _DT, /, *, axis: int = 0) -> _DT: ...
    def flip(self, x: _DT, /, axis: Optional[Union[int, Tuple[int, ...]]]=None) -> _DT: ...
    def moveaxis(self, x: _DT, source: Union[int, Tuple[int, ...]], destination: Union[int, Tuple[int, ...]], /) -> _DT: ...
    def permute_dims(self, x: _DT, /, axes: Tuple[int, ...]) -> _DT: ...
    def repeat(self, x: _DT, repeats: int, /, *, axis: Optional[int]=None) -> _DT: ...
    def reshape(self, x: _DT, /, shape: Size, *, copy=None) -> _DT: ...
    def roll(self, x: _DT, /, shift: Union[int, Tuple[int, ...]], *, axis: Optional[Union[int, Tuple[int, ...]]]=None) -> _DT: ...
    def squeeze(self, x: _DT, /, axis: Union[int, Tuple[int, ...]]) -> _DT: ...
    def stack(self, arrays: Union[Tuple[_DT, ...], List[_DT]], *, axis=0) -> _DT: ...
    def tile(self, x: _DT, repetitions: Tuple[int, ...], /) -> _DT: ...
    def unstack(self, x: _DT, /, *, axis: int = 0) -> Tuple[_DT, ...]: ...

    # non-standard
    def concatenate(self, arrays, /, axis=0, out=None, *, dtype=None) -> _DT: ...
    def swapaxes(self, a: _DT, axis1: int, axis2: int, /) -> _DT: ...
    def transpose(self, a: _DT, axes: Size, /) -> _DT: ...

    ### Searching Functions ###
    # python array API standard v2023.12
    def argmax(self, x: _DT, /, *, axis=None, keepdims=False) -> _DT: ...
    def argmin(self, x: _DT, /, *, axis=None, keepdims=False) -> _DT: ...
    def nonzero(self, x: _DT, /) -> Tuple[_DT, ...]: ...
    def searchsorted(self, x1: _DT, x2: _DT, /, *, side: Literal["left", "right"]="left", sorter: Optional[_DT]=None) -> _DT: ...
    def where(self, condition: _DT, x1: _DT, x2: _DT, /) -> _DT: ...

    ### Set Functions ###
    # python array API standard v2023.12
    def unique_all(self, x: _DT, /) -> Tuple[_DT, _DT, _DT, _DT]: ...

    # non-standard
    def unique(self, ar: _DT, return_index=False, return_inverse=False, return_counts=False, axis=0, **kwargs): ...

    ###Sorting Functions ###
    # python array API standard v2023.12
    def argsort(self, x: _DT, /, *, axis: int=-1, descending: bool=False, stable: bool=True) -> _DT: ...
    def sort(self, x: _DT, /, *, axis: int=-1, descending: bool=False, stable: bool=True) -> _DT: ...

    ### Statistical Functions ###
    # python array API standard v2023.12
    def cumulative_sum(x: _DT, /, *, axis: Optional[int] = None, dtype=None, include_initial: bool = False) -> _DT: ...
    def max(self, x: _DT, /, *, axis=None, keepdims=False): ...
    def mean(self, x: _DT, /, *, axis=None, keepdims: bool=False) -> _DT: ...
    def min(self, x: _DT, /, *, axis=None, keepdims=False): ...
    def prod(self, x: _DT, /, *, axis=None, dtype=None, keepdims=False, initial: Number=...) -> _DT: ...
    def std(self, x: _DT, /, *, axis=None, correction: int=0, keepdims: bool=False) -> _DT: ...
    def sum(self, x: _DT, /, *, axis=None, dtype=None, keepdims=False, initial: Number=...) -> _DT: ...
    def var(self, x: _DT, /, *, axis=None, correction: int=0, keepdims: bool=False) -> _DT: ...

    # non-standard
    def cumsum(self, x: _DT, /, *, axis: Optional[int]=None) -> _DT: ...
    def cumprod(self, x: _DT, /, *, axis: Optional[int]=None) -> _DT: ...

    ### Utility Functions ###
    # python array API standard v2023.12
    def all(self, x: _DT, /, *, axis=None, keepdims: bool=False) -> _DT: ...
    def any(self, x: _DT, /, *, axis=None, keepdims: bool=False) -> _DT: ...

    # non-standard
    def allclose(self, x1: _DT, x2: _DT, *, rtol=1e-05, atol=1e-08, equal_nan=False) -> bool: ...
    def copy(self, x: _DT, /) -> _DT: ...
    def size(self, x: _DT, /, *, axis: Optional[int]=None) -> int: ...

    ### Other Functions ###
    def add_at(self, a: _DT, indices, src: _DT, /) -> None: ...
    def index_add_(self, a: _DT, /, dim: int, index: _DT, src: _DT, *, alpha: Number=1.) -> _DT: ...

    ### Functional programming ###
    # non-standard
    def apply_along_axis(self, func1d, axis, arr: _DT, *args, **kwargs) -> _DT: ...


    ### FEALPy functionals ###
    def multi_index_matrix(self, p: int, dim: int, *, dtype=None) -> _DT: ...
    def edge_length(self, edge: _DT, node: _DT, *, out=None) -> _DT: ...
    def edge_normal(self, edge: _DT, node: _DT, unit=False, *, out=None) -> _DT: ...
    def edge_tangent(self, edge: _DT, node: _DT, unit=False, *, out=None) -> _DT: ...
    def tensorprod(self, *tensors: _DT) -> _DT: ...
    def bc_to_points(self, bcs: Union[_DT, Tuple[_DT, ...]], node: _DT, entity: _DT) -> _DT: ...
    def barycenter(self, entity: _DT, node: _DT, loc: Optional[_DT]=None) -> _DT: ...
    def simplex_ldof(self, p: int, iptype: int) -> int: ... # implement in base
    def simplex_gdof(self, p: int, nums: Tuple[int, ...]) -> int: ... # implement in base
    def simplex_measure(self, entity: _DT, node: _DT) -> _DT: ...
    def simplex_shape_function(self, bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    def simplex_grad_shape_function(self, bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    def simplex_hess_shape_function(self, bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    def tensor_ldof(self, p: int, iptype: int) -> int: ... # implement in base
    def tensor_gdof(self, p: int, nums: Tuple[int, ...]) -> int: ... # implement in base
    def tensor_measure(self, entity: _DT, node: _DT) -> _DT: ...

    def interval_grad_lambda(self, line: _DT, node: _DT) -> _DT: ...
    def triangle_area_3d(self, tri: _DT, node: _DT) -> _DT: ...
    def triangle_grad_lambda_2d(self, tri: _DT, node: _DT) -> _DT: ...
    def triangle_grad_lambda_3d(self, tri: _DT, node: _DT) -> _DT: ...
    def quadrangle_grad_lambda_2d(self, quad: _DT, node: _DT) -> _DT: ...
    def tetrahedron_grad_lambda_3d(self, tet: _DT, node: _DT, local_face: _DT) -> _DT: ...
