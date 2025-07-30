from typing import TypeVar, cast

from pptx.dml.fill import FillFormat as PptxFillFormat
from pptx.dml.fill import _Fill as PptxFill
from pptx.dml.fill import _GradFill as PptxGradFill
from pptx.dml.fill import _GradientStop as PptxGradientStop
from pptx.dml.fill import _GradientStops as PptxGradientStops
from pptx.dml.fill import _NoFill as PptxNoFill
from pptx.dml.fill import _PattFill as PptxPattFill
from pptx.dml.fill import _SolidFill as PptxSolidFill
from pptx.enum.dml import MSO_PATTERN_TYPE

from tppt.pptx.converter import PptxConvertible, to_pptx_angle, to_tppt_angle
from tppt.pptx.dml.color import ColorFormat
from tppt.pptx.enum.dml import LiteralPatternType, to_pptx_pattern_type
from tppt.types._angle import Angle


class FillFormat(PptxConvertible[PptxFillFormat]):
    """Fill format."""

    @property
    def fore_color(self) -> ColorFormat:
        """Fore color."""
        return ColorFormat(self._pptx.fore_color)

    @property
    def back_color(self) -> ColorFormat:
        """Back color."""
        return ColorFormat(self._pptx.back_color)

    @property
    def pattern(self) -> MSO_PATTERN_TYPE:
        """Pattern."""
        return self._pptx.pattern

    @pattern.setter
    def pattern(self, value: MSO_PATTERN_TYPE) -> None:
        self._pptx.pattern = value

    def set_pattern(self, value: MSO_PATTERN_TYPE) -> "FillFormat":
        """Set pattern."""
        self.pattern = value
        return self

    def patterned(self) -> "PattFill":
        """Set the fill type to patterned."""
        self._pptx.patterned()
        return PattFill(cast(PptxPattFill, self._pptx._fill))

    def background(self) -> "NoFill":
        """Set the fill type to noFill, i.e. transparent."""
        self._pptx.background()
        return NoFill(cast(PptxNoFill, self._pptx._fill))

    def solid(self) -> "SolidFill":
        """Set the fill type to solid."""
        self._pptx.solid()
        return SolidFill(cast(PptxSolidFill, self._pptx._fill))

    def gradient(self) -> "GradFill":
        """Sets the fill type to gradient."""
        self._pptx.gradient()
        return GradFill(cast(PptxGradFill, self._pptx._fill))


_GenericPptxFill = TypeVar("_GenericPptxFill", bound=PptxFill)


class Fill(PptxConvertible[_GenericPptxFill]):
    pass


class GradFill(Fill[PptxGradFill]):
    """Gradient fill."""

    @property
    def gradient_angle(self) -> Angle | None:
        """Angle in float degrees of line of a linear gradient."""
        return to_tppt_angle(cast(float | None, self._pptx.gradient_angle))

    @gradient_angle.setter
    def gradient_angle(self, value: Angle) -> None:
        self._pptx.gradient_angle = to_pptx_angle(value)

    def set_gradient_angle(self, value: Angle) -> "GradFill":
        """Set gradient angle."""
        self.gradient_angle = value
        return self

    @property
    def gradient_stops(self) -> "GradientStops":
        """Gradient stops."""
        return GradientStops(self._pptx.gradient_stops)


class NoFill(Fill[PptxNoFill]):
    """No fill."""


class PattFill(Fill[PptxPattFill]):
    """Pattern fill."""

    @property
    def back_color(self) -> ColorFormat:
        """Back color."""
        return ColorFormat(self._pptx.back_color)

    @property
    def fore_color(self) -> ColorFormat:
        """Fore color."""
        return ColorFormat(self._pptx.fore_color)

    @property
    def pattern(self) -> MSO_PATTERN_TYPE:
        """Pattern."""
        return self._pptx.pattern

    @pattern.setter
    def pattern(self, value: LiteralPatternType | MSO_PATTERN_TYPE) -> None:
        self._pptx.pattern = to_pptx_pattern_type(value)

    def set_pattern(self, value: LiteralPatternType | MSO_PATTERN_TYPE) -> "PattFill":
        """Set pattern."""
        self.pattern = value
        return self


class SolidFill(Fill[PptxSolidFill]):
    """Solid fill."""

    @property
    def fore_color(self) -> ColorFormat:
        """Fore color."""
        return ColorFormat(self._pptx.fore_color)


class GradientStops(PptxConvertible[PptxGradientStops]):
    """Gradient stops."""

    def __getitem__(self, idx: int) -> "GradientStop":
        return GradientStop(self._pptx[idx])

    def __len__(self) -> int:
        return len(self._pptx)


class GradientStop(PptxConvertible[PptxGradientStop]):
    """Gradient stop."""

    @property
    def color(self) -> ColorFormat:
        """Color."""
        return ColorFormat(self._pptx.color)

    @property
    def position(self) -> float:
        """Location of stop in gradient path as float between 0.0 and 1.0.

        The value represents a percentage, where 0.0 (0%) represents the
        start of the path and 1.0 (100%) represents the end of the path. For
        a linear gradient, these would represent opposing extents of the
        filled area.
        """
        return self._pptx.position

    @position.setter
    def position(self, value: float) -> None:
        self._pptx.position = value

    def set_position(self, value: float) -> "GradientStop":
        """Set position."""
        self.position = value
        return self
