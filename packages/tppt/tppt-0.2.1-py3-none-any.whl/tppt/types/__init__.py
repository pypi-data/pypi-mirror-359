"""tppt types."""

import pathlib
from typing import TypeAlias

from tppt.pptx.shape import RangeProps as _RangeProps

from ._color import Color as Color
from ._color import LiteralColor as LiteralColor
from ._color import to_color as to_color
from ._length import (
    CentiMeters as CentiMeters,
)
from ._length import (
    EnglishMetricUnits as EnglishMetricUnits,
)
from ._length import (
    Inches as Inches,
)
from ._length import (
    Length as Length,
)
from ._length import (
    LiteralLength as LiteralLength,
)
from ._length import (
    MilliMeters as MilliMeters,
)
from ._length import (
    Points as Points,
)

FilePath = str | pathlib.Path
Range: TypeAlias = _RangeProps
