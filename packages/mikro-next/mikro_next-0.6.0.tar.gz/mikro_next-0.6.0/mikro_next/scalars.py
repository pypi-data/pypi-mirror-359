"""
Custom scalars for mikro_next


"""

import io
import os
from typing import Any, IO, List, Optional, TypeAlias, cast
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema
import xarray as xr
import pandas as pd
import numpy as np
import uuid
from numpy.typing import NDArray


from .utils import rechunk
from collections.abc import Iterable
import mimetypes
from pathlib import Path
from typing import Protocol
from rath.scalars import ID
from pydantic_core import core_schema


class WithId(Protocol):
    id: ID


IDCoercible = str | ID | WithId

ArrayCoercible: TypeAlias = xr.DataArray | NDArray | List[float] | List[List[float]]
""" A type alias for array-like structures that can be coerced into an xarray DataArray."""

ImageFileCoercible: TypeAlias = str | bytes | Path | io.BufferedReader
""" A type alias for image file-like structures that can be coerced into an xarray DataArray."""

ParquetCoercible: TypeAlias = pd.DataFrame
""" A type alias for parquet-like structures that can be coerced into an xarray DataArray."""

MeshCoercible: TypeAlias = str | bytes | Path | io.BufferedReader
""" A type alias for mesh-like structures that can be coerced into an xarray DataArray."""

FileCoercible: TypeAlias = str | bytes | Path | io.BufferedReader
""" A type alias for file-like structures that can be coerced into an xarray DataArray."""

FourByFourMatrixCoercible: TypeAlias = List[List[float]] | NDArray | List[List[int]]
""" A type alias for 4x4 matrix-like structures that can be coerced into an xarray DataArray."""

MillisecondsCoercible: TypeAlias = int | float
""" A type alias for millisecond-like structures that can be coerced into an xarray DataArray."""

MicrometersCoercible: TypeAlias = int | float
""" A type alias for micrometer-like structures that can be coerced into an xarray DataArray."""


def is_dask_array(v: Any) -> bool:
    """Check if the input is a dask array."""
    try:
        import dask.array.core as da

        return isinstance(v, da.Array)
    except ImportError:
        return False
    except Exception as e:
        raise ValueError(f"Error checking for dask array: {e}")


class AssignationID(str):
    """A custom scalar to represent an affine matrix."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class RGBAColor(list):
    """A custom scalar to represent an affine matrix."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class XArrayConversionException(Exception):
    """An exception that is raised when a conversion to xarray fails."""

    pass


MetricValue = Any
FeatureValue = Any


class Upload:
    """A custom scalar for ensuring an interface to files api supported by mikro_next It converts the graphql value
    (a string pointed to a zarr store) into a downloadable file. To access the file you need to call the download
    method. This is done to avoid unnecessary requests to the datalayer api.
    """

    __file__ = True

    def __init__(self, value) -> None:
        self.value = value

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        # you could also return a string here which would mean model.post_code
        # would be a string, pydantic won't care but you could end up with some
        # confusion since the value's type won't match the type annotation
        # exactly
        return cls(v)

    def __repr__(self):
        return f"Upload({self.value})"


class Micrometers(float):
    """A custom scalar to represent a micrometer."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class Microliters(float):
    """A custom scalar to represent a a microliter."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class Micrograms(float):
    """A custom scalar to represent a a microgram."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class Milliseconds(float):
    """A custom scalar to represent a micrometer."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class TwoDVector(list):
    """A custom scalar to represent a vector."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, np.ndarray):
            assert v.ndim == 1
            v = v.tolist()

        assert isinstance(v, list)
        assert len(v) == 3
        return cls(v)

    def as_vector(self):
        return np.array(self).reshape(-1)


class ThreeDVector(list):
    """A custom scalar to represent a vector."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, np.ndarray):
            assert v.ndim == 1
            v = v.tolist()

        assert isinstance(v, list)
        assert len(v) == 3
        return cls(v)

    def as_vector(self):
        return np.array(self).reshape(-1)


class FourDVector(list):
    """A custom scalar to represent a vector."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, np.ndarray):
            assert v.ndim == 1
            v = v.tolist()

        assert isinstance(v, list)
        assert len(v) == 4
        return cls(v)

    def as_vector(self):
        return np.array(self).reshape(-1)


class FiveDVector(list):
    """A custom scalar to represent a vector."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *info):
        """Validate the input array and convert it to a xr.DataArray."""

        if isinstance(v, np.ndarray):
            if not v.ndim == 1:
                raise ValueError("The input array must be a 1D array")
            v = v.tolist()

        if not isinstance(v, Iterable):
            raise ValueError("The input must be a list or a 1-D numpy array.")

        if not isinstance(v, list):
            v = list(v)

        for i in v:
            if not isinstance(i, (int, float)):
                raise ValueError(
                    f"The input must be a list of integers or floats. You provided a list of {type(i)}"
                )

        if len(v) < 2 or len(v) > 5:
            raise ValueError(
                f"The input must be a list or at least 2 elements (x, y) but not more than 5e lements (c, t, z, x, y). Every additional element is a z value (c, t, z, x, y). You provided a list o {len(v)} elements"
            )

        # prepend list with zeros
        if len(v) < 5:
            v = [0] * (5 - len(v)) + v

        return v

    @classmethod
    def list_from_numpyarray(
        cls,
        x: np.ndarray,
        t: Optional[int] = None,
        c: Optional[int] = None,
        z: Optional[int] = None,
    ) -> List["FiveDVector"]:
        """Creates a list of FiveDVectors from a numpy array

        Args:
            vector_list (List[List[float]]): A list of lists of floats

        Returns:
            List[Vectorizable]: A list of InputVector
        """
        assert x.ndim == 2, "Needs to be a List array of vectors"
        if x.shape[1] == 4:
            return [FiveDVector([c] + i) for i in x.tolist()]
        elif x.shape[1] == 3:
            return [FiveDVector([c, t] + i) for i in x.tolist()]
        elif x.shape[1] == 2:
            return [FiveDVector([c, t, z] + i) for i in x.tolist()]
        else:
            raise NotImplementedError(
                f"Incompatible shape {x.shape} of {x}. List dimension needs to either be of size 2 or 3"
            )

    def as_vector(self):
        return np.array(self).reshape(-1)


class Matrix(list):
    """A custom scalar to represent an affine matrix."""

    def __get__(self, instance, owner) -> "Matrix": ...

    def __set__(self, instance, value: FourByFourMatrixCoercible): ...

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_before_validator_function(
            cls.validate, handler(list)
        )

    @classmethod
    def validate(cls, v: FourByFourMatrixCoercible) -> "Matrix":
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, np.ndarray):
            assert v.ndim == 2
            assert v.shape[0] == v.shape[1]
            assert v.shape == (3, 3)
            v = v.tolist()

        assert isinstance(v, list)
        return cls(v)

    def as_matrix(self):
        return np.array(self).reshape(3, 3)


class FourByFourMatrix(list):
    """A custom scalar to represent a four by four matrix (e.g 3D affine matrix.)"""

    def __get__(self, instance, owner) -> "FourByFourMatrix": ...

    def __set__(self, instance, value: FourByFourMatrixCoercible): ...

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_before_validator_function(
            cls.validate, handler(list)
        )

    @classmethod
    def validate(cls, v: np.ndarray) -> "FourByFourMatrix":
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, np.ndarray):
            if not v.ndim == 2:
                raise ValueError("The input array must be a 2D array")
            if not v.shape[0] == v.shape[1]:
                raise ValueError("The input array must be a square matrix")
            if not v.shape == (4, 4):
                raise ValueError("The input array must be a 4x4 matrix")
            clean = [[float(v[i, j]) for j in range(4)] for i in range(4)]
        else:
            clean = v

        if not isinstance(clean, list):
            raise ValueError(
                f"Expected a list or numpy array, got {type(clean)}. Please provide a 4x4 matrix."
            )

        if len(clean) != 4 or any(len(row) != 4 for row in clean):
            raise ValueError(
                f"Expected a 4x4 matrix, got {len(clean)} rows and {[len(row) for row in clean]} columns."
            )

        for row in clean:
            if not all(isinstance(x, (int, float)) for x in row):
                raise ValueError(
                    "All elements of the 4x4 matrix must be integers or floats."
                )

        print(f"Validating FourByFourMatrix: {clean}")
        return cls(clean)

    def as_matrix(self):
        return np.array(self).reshape(3, 3)

    @classmethod
    def from_np(cls, v: np.ndarray):
        """Validate the input array and convert it to a xr.DataArray."""
        assert v.ndim == 2
        assert v.shape[0] == v.shape[1]
        assert v.shape == (4, 4)
        v = v.tolist()
        return cls(v)


class ArrayLike:
    """A custom scalar for wrapping of every supported array like structure on
    the mikro platform. This scalar enables validation of various array formats
    into a mikro api compliant xr.DataArray.."""

    def __init__(self, value: xr.DataArray) -> None:
        self.value = value
        self.key = str(uuid.uuid4())

    def __get__(self, instance, owner) -> float: ...

    def __set__(self, instance, value: ArrayCoercible): ...

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_after_validator_function(
            cls.validate, handler(object)
        )

    @classmethod
    def validate(cls, v: ArrayCoercible) -> "ArrayLike":
        """Validate the input array and convert it to a xr.DataArray."""
        was_labeled = True
        # initial coercion checks, if a numpy array is passed, we need to convert it to a xarray
        # but that means the user didnt pass the dimensions explicitly so we need to add them
        # but error if they do not make sense

        if isinstance(v, np.ndarray) or is_dask_array(v):
            v = cast(np.ndarray, v)
            dims = ["c", "t", "z", "y", "x"]
            v = xr.DataArray(v, dims=dims[5 - v.ndim :])
            was_labeled = False

        if not isinstance(v, xr.DataArray):
            raise ValueError("This needs to be a instance of xarray.DataArray")

        if "x" not in v.dims:
            raise ValueError("Representations must always have a 'x' Dimension")

        if "y" not in v.dims:
            raise ValueError("Representations must always have a 'y' Dimension")

        if "t" not in v.dims:
            v = v.expand_dims("t")
        if "c" not in v.dims:
            v = v.expand_dims("c")
        if "z" not in v.dims:
            v = v.expand_dims("z")

        chunks = rechunk(
            v.sizes, itemsize=v.data.itemsize, chunksize_in_bytes=20_000_000
        )
        if not was_labeled:
            if v.sizes["t"] > v.sizes["x"] or v.sizes["t"] > v.sizes["y"]:
                raise ValueError(
                    f"Probably Non sensical dimensions. T is bigger than x or y: Sizes {v.sizes}"
                )
            if v.sizes["z"] > v.sizes["x"] or v.sizes["z"] > v.sizes["y"]:
                raise ValueError(
                    f"Probably Non sensical dimensions. Z is bigger than x or y: Sizes {v.sizes}"
                )
            if v.sizes["c"] > v.sizes["x"] or v.sizes["c"] > v.sizes["y"]:
                raise ValueError(
                    f"Probably Non sensical dimensions. C is bigger than x or y: Sizes {v.sizes}"
                )

        v = v.chunk(
            {key: chunksize for key, chunksize in chunks.items() if key in v.dims}
        )

        v = v.transpose(*"ctzyx")

        if is_dask_array(v.data):
            v = v.compute()

        return cls(v)

    def __repr__(self):
        return f"InputArray({self.value})"


class BigFile:
    """A custom scalar for wrapping of every supported array like structure on
    the mikro platform. This scalar enables validation of various array formats
    into a mikro api compliant xr.DataArray.."""

    def __init__(self, value: IO) -> None:
        self.value = value
        self.key = str(value.name)

    def __get__(self, instance, owner) -> "BigFile": ...

    def __set__(self, instance, value: FileCoercible): ...

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_after_validator_function(
            cls.validate, handler(object)
        )

    @classmethod
    def validate(cls, v: FileCoercible) -> "BigFile":
        """Validate the input array and convert it to a xr.DataArray."""

        if isinstance(v, str):
            v = open(v, "rb")

        if not isinstance(v, io.IOBase):
            raise ValueError("This needs to be a instance of a file")

        return cls(v)

    def __repr__(self):
        return f"BigFile({self.value})"


class ParquetLike:
    """A custom scalar for ensuring a common format to support write to the
    parquet api supported by mikro_next It converts the passed value into
    a compliant format.."""

    def __init__(self, value: pd.DataFrame) -> None:
        self.value = value
        self.key = str(uuid.uuid4())

    def __get__(self, instance, owner) -> "ParquetLike": ...

    def __set__(self, instance, value: ParquetCoercible): ...

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_after_validator_function(
            cls.validate, handler(object)
        )

    @classmethod
    def validate(cls, v: str) -> "ParquetLike":
        """Validate the validator function"""

        if not isinstance(v, pd.DataFrame):
            raise ValueError("This needs to be a instance of pandas DataFrame")

        return cls(v)

    def __repr__(self):
        return f"ParquetLike({self.value})"


class ImageFileLike:
    """A custom scalar for ensuring a common format to support write to the
    parquet api supported by mikro_next It converts the passed value into
    a compliant format.."""

    def __init__(self, value: io.BufferedReader, name="") -> None:
        self.value = value
        self.file_name = os.path.basename(name)
        self.mime_type = mimetypes.guess_type(self.file_name)[0]

    def __get__(self, instance, owner) -> "FileLike": ...

    def __set__(self, instance, value: FileCoercible): ...

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_after_validator_function(
            cls.validate, handler(object)
        )

    @classmethod
    def validate(cls, v: FileCoercible) -> "ImageFileLike":
        """Validate the validator function"""

        if isinstance(v, str):
            file = open(v, "rb")
            name = v
        elif isinstance(v, io.IOBase):
            file = v
            name = v.name
        elif isinstance(v, Path):
            file = open(v, "rb")
            name = str(v)
        else:
            raise ValueError(
                f"Unsupported type {type(v)}. Please provide a string or a Path object. Or a file object that is opened in binary mode."
            )

        if not isinstance(file, io.BufferedReader):
            raise ValueError("This needs to be a instance of a file")

        return cls(file, name=name)

    def __repr__(self):
        return f"FileLike({self.value})"


class FileLike:
    """A custom scalar for ensuring a common format to support write to the
    parquet api supported by mikro_next It converts the passed value into
    a compliant format.."""

    def __init__(self, value: IO, name="") -> None:
        self.value = value
        self.file_name = os.path.basename(name)
        self.mime_type = mimetypes.guess_type(self.file_name)[0]

    def __get__(self, instance, owner) -> "FileLike": ...

    def __set__(self, instance, value: FileCoercible): ...

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_after_validator_function(
            cls.validate, handler(object)
        )

    @classmethod
    def validate(cls, v: FileCoercible) -> "FileLike":
        """Validate the validator function"""

        if isinstance(v, str):
            file = open(v, "rb")
            name = v
        elif isinstance(v, io.IOBase):
            file = v
            name = v.name
        elif isinstance(v, Path):
            file = open(v, "rb")
            name = str(v)
        else:
            raise ValueError(
                f"Unsupported type {type(v)}. Please provide a string or a Path object. Or a file object that is opened in binary mode."
            )

        if not isinstance(file, io.IOBase):
            raise ValueError("This needs to be a instance of a file")

        return cls(file, name=name)

    def __repr__(self):
        return f"FileLike({self.value})"


class MeshLike:
    """A custom scalar for ensuring a common format to support write to the
    mesh api supported by mikro_next It converts the passed value into
    a compliant format.."""

    def __init__(self, value: IO[bytes], name: str = "") -> None:
        self.value = value
        self.key = str(name)

    def __get__(self, instance, owner) -> "MeshLike": ...

    def __set__(self, instance, value: MeshCoercible): ...

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function"""
        return core_schema.no_info_after_validator_function(
            cls.validate, handler(object)
        )

    @classmethod
    def validate(cls, v: MeshCoercible) -> "MeshLike":
        """Validate the input array and convert it to a xr.DataArray."""

        if isinstance(v, str):
            file = open(v, "rb")
            name = v
        elif isinstance(v, io.IOBase):
            file = v
            name = "Random Name"
        else:
            file = v
            name = str(v)

        if not isinstance(file, io.BufferedReader):
            raise ValueError("This needs to be a instance of a file")

        return cls(file, name=name)

    def __repr__(self):
        return f"MeshLike({self.value})"
