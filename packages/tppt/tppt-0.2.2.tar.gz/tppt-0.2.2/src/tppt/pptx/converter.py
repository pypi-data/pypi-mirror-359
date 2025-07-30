"""Type definitions for pptx wrapper."""

from typing import (
    Generic,
    Self,
    TypeAlias,
    TypeVar,
    assert_never,
    overload,
)

from pptx.dml.color import RGBColor as PptxRGBColor
from pptx.util import Cm as PptxCm
from pptx.util import Emu as PptxEmu
from pptx.util import Inches as PptxInches
from pptx.util import Length as PptxLength
from pptx.util import Mm as PptxMm
from pptx.util import Pt as PptxPt

from tppt.types._angle import Angle, Degrees, LiteralAngle
from tppt.types._color import Color, LiteralColor, to_color
from tppt.types._length import (
    CentiMeters,
    EnglishMetricUnits,
    Inches,
    Length,
    LiteralLength,
    MilliMeters,
    Points,
    to_length,
)

PT = TypeVar("PT")


class PptxConvertible(Generic[PT]):
    """Protocol for objects that can be converted to and from pptx objects."""

    def __init__(self, pptx_obj: PT, /) -> None:
        self._pptx: PT = pptx_obj

    def to_pptx(self) -> PT:
        """Convert to pptx object."""
        return self._pptx

    @classmethod
    def from_pptx(cls, pptx_obj: PT) -> Self:
        """Create from pptx object."""
        return cls(pptx_obj)


@overload
def to_pptx_length(length: Length | LiteralLength | PptxLength) -> PptxLength: ...


@overload
def to_pptx_length(
    length: Length | LiteralLength | PptxLength | None,
) -> PptxLength | None: ...


def to_pptx_length(
    length: Length | LiteralLength | PptxLength | None,
) -> PptxLength | None:
    if isinstance(length, tuple):
        length = to_length(length)

    match length:
        case Inches():
            return PptxInches(length.value)
        case CentiMeters():
            return PptxCm(length.value)
        case Points():
            return PptxPt(length.value)
        case MilliMeters():
            return PptxMm(length.value)
        case EnglishMetricUnits():
            return PptxEmu(length.value)
        case PptxLength():
            return length
        case None:
            return None
        case _:
            assert_never(length)


@overload
def to_tppt_length(length: PptxLength) -> Length: ...


@overload
def to_tppt_length(length: PptxLength | None) -> Length | None: ...


def to_tppt_length(length: PptxLength | None) -> Length | None:
    return to_length((length.emu, "emu")) if length else None


@overload
def to_pptx_rgb_color(
    color: Color | LiteralColor | PptxRGBColor,
) -> tuple[PptxRGBColor, int | None]: ...


@overload
def to_pptx_rgb_color(
    color: Color | LiteralColor | PptxRGBColor | None,
) -> tuple[PptxRGBColor, int | None] | None: ...


def to_pptx_rgb_color(
    color: Color | LiteralColor | PptxRGBColor | None,
) -> (
    tuple[
        PptxRGBColor,
        int | None,
    ]
    | None
):
    if color is None:
        return None

    color = to_color(color)

    return PptxRGBColor(color.r, color.g, color.b), color.a


@overload
def to_tppt_rgb_color(color: PptxRGBColor, alpha: int | None) -> Color: ...


@overload
def to_tppt_rgb_color(
    color: PptxRGBColor | None, alpha: int | None
) -> Color | None: ...


def to_tppt_rgb_color(color: PptxRGBColor | None, alpha: int | None) -> Color | None:
    return Color(color[0], color[1], color[2], alpha) if color else None


PptxAngle: TypeAlias = float


@overload
def to_pptx_angle(angle: Angle | LiteralAngle) -> PptxAngle: ...


@overload
def to_pptx_angle(angle: Angle | LiteralAngle | None) -> PptxAngle | None: ...


def to_pptx_angle(angle: Angle | LiteralAngle | None) -> PptxAngle | None:
    match angle:
        case Degrees():
            return angle._value
        case tuple():
            return angle[0]
        case None:
            return None
        case _:
            assert_never(angle)


@overload
def to_tppt_angle(angle: PptxAngle) -> Angle: ...


@overload
def to_tppt_angle(angle: PptxAngle | None) -> Angle | None: ...


def to_tppt_angle(angle: PptxAngle | None) -> Angle | None:
    return Degrees(angle) if angle else None
