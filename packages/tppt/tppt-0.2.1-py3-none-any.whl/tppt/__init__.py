"""
## 🐍 🛡️ Typed Python PowerPoint Tool 🛡️ 🐍

>>> import tppt
>>> (
...     tppt.Presentation.builder()
...     .slide(
...         lambda slide: slide.BlankLayout()
...         .builder()
...         .text(
...             "Hello, World!",
...             left=(1, "in"),
...             top=(1, "in"),
...             width=(5, "in"),
...             height=(2, "in"),
...         )
...     )
...     .build()
...     .save("simple.pptx")
... )

"""

import importlib.metadata
from typing import Callable, Concatenate, ParamSpec, TypeVar

from . import pptx as pptx
from . import types as types
from .pptx import Presentation as Presentation
from .template.slide_layout import Placeholder as Placeholder
from .template.slide_layout import SlideLayout as SlideLayout
from .template.slide_master import Layout as Layout
from .template.slide_master import SlideMaster as SlideMaster
from .template.slide_master import slide_master as slide_master

__version__ = importlib.metadata.version("tppt")

T = TypeVar("T")
P = ParamSpec("P")


def apply(
    func: Callable[Concatenate[T, P], T], *args: P.args, **kwargs: P.kwargs
) -> Callable[[T], T]:
    """
    Partially applies the given function `func` with arguments `args` and keyword arguments `kwargs`,
    returning a new function that takes only the first argument.

    Args:
        func: A function that takes a first argument of type `T` and variable arguments `P`, returning `T`
        *args: Variable positional arguments to partially apply to `func`
        **kwargs: Variable keyword arguments to partially apply to `func`

    Returns:
        A function that takes a single argument `x` and calls `func(x, *args, **kwargs)`
    """

    def wrapper(x: T) -> T:
        return func(x, *args, **kwargs)

    return wrapper
