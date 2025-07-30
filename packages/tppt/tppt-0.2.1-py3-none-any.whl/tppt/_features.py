from typing import ClassVar, Protocol, TypeVar

from typing_extensions import TypeAlias

T = TypeVar("T")


class _NotSupportFeature:
    pass


class Dataclass(Protocol):
    """Protocol for dataclass type."""

    __dataclass_fields__: ClassVar[dict]


try:
    import pydantic  # type: ignore[import]  # noqa: F401

    USE_PYDANTIC = True
    PydanticModel: TypeAlias = pydantic.BaseModel  # type: ignore

except ImportError:
    USE_PYDANTIC = False
    PydanticModel: TypeAlias = _NotSupportFeature  # type: ignore


try:
    import pandas  # type: ignore[import]  # noqa: F401

    USE_PANDAS = True
    PandasDataFrame: TypeAlias = pandas.DataFrame  # type: ignore


except ImportError:
    USE_PANDAS = False
    PandasDataFrame: TypeAlias = _NotSupportFeature  # type: ignore


try:
    import polars  # type: ignore[import]  # noqa: F401

    USE_POLARS = True
    PolarsDataFrame: TypeAlias = polars.DataFrame  # type: ignore
    PolarsLazyFrame: TypeAlias = polars.LazyFrame  # type: ignore


except ImportError:
    USE_POLARS = False
    PolarsDataFrame: TypeAlias = _NotSupportFeature  # type: ignore
    PolarsLazyFrame: TypeAlias = _NotSupportFeature  # type: ignore
