"""Shape wrapper implementation."""

from typing import TYPE_CHECKING, Self, TypedDict

from pptx.shapes import Subshape as PptxSubshape
from pptx.shapes.autoshape import Shape as PptxShape
from pptx.shapes.base import BaseShape as PptxBaseShape
from pptx.util import Length as PptxLength
from typing_extensions import TypeVar

from tppt.pptx.converter import PptxConvertible, to_pptx_length
from tppt.types._length import Length, LiteralLength, to_length

if TYPE_CHECKING:
    from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_SHAPE_TYPE
    from pptx.oxml.shapes import ShapeElement as PptxShapeElement
    from pptx.parts.slide import BaseSlidePart as PptxBaseSlidePart
    from pptx.shapes.base import _PlaceholderFormat as PptxPlaceholderFormat

    from tppt.pptx.action import ActionSetting
    from tppt.pptx.dml.effect import ShadowFormat
    from tppt.pptx.dml.fill import FillFormat
    from tppt.pptx.dml.line import LineFormat
    from tppt.pptx.text.text_frame import TextFrame


GenericPptxBaseShape = TypeVar(
    "GenericPptxBaseShape",
    bound=PptxBaseShape,
    default=PptxBaseShape,
)

GenericPptxShape = TypeVar(
    "GenericPptxShape",
    bound=PptxShape,
    default=PptxShape,
)


class BaseShape(PptxConvertible[GenericPptxBaseShape]):
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseShape):
            return False
        return self._pptx is other._pptx

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, BaseShape):
            return True
        return self._pptx is not other._pptx

    @property
    def click_action(self) -> "ActionSetting":
        from tppt.pptx.action import ActionSetting

        return ActionSetting(self._pptx.click_action)

    @property
    def element(self) -> "PptxShapeElement":
        return self._pptx.element

    @property
    def height(self) -> Length:
        return to_length(self._pptx.height)

    @height.setter
    def height(self, value: Length | LiteralLength | PptxLength) -> None:
        self._pptx.height = to_pptx_length(value)

    def set_height(self, value: Length | LiteralLength | PptxLength) -> Self:
        """Set height value and return self for method chaining."""
        self.height = value
        return self

    @property
    def left(self) -> Length:
        return to_length(self._pptx.left)

    @left.setter
    def left(self, value: Length | LiteralLength | PptxLength) -> None:
        self._pptx.left = to_pptx_length(value)

    def set_left(self, value: Length | LiteralLength | PptxLength) -> Self:
        """Set left position value and return self for method chaining."""
        self.left = value
        return self

    @property
    def name(self) -> str:
        return self._pptx.name

    @name.setter
    def name(self, value: str) -> None:
        self._pptx.name = value

    def set_name(self, value: str) -> Self:
        """Set name value and return self for method chaining."""
        self.name = value
        return self

    @property
    def part(self) -> "PptxBaseSlidePart":
        return self._pptx.part

    @property
    def placeholder_format(self) -> "PptxPlaceholderFormat":
        return self._pptx.placeholder_format

    @property
    def rotation(self) -> float:
        return self._pptx.rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        self._pptx.rotation = value

    def set_rotation(self, value: float) -> Self:
        """Set rotation value and return self for method chaining."""
        self.rotation = value
        return self

    @property
    def shadow(self) -> "ShadowFormat":
        from tppt.pptx.dml.effect import ShadowFormat

        return ShadowFormat(self._pptx.shadow)

    @property
    def shape_id(self) -> int:
        return self._pptx.shape_id

    @property
    def shape_type(self) -> "MSO_SHAPE_TYPE":
        return self._pptx.shape_type

    @property
    def top(self) -> Length:
        return to_length(self._pptx.top)

    @top.setter
    def top(self, value: Length | LiteralLength | PptxLength) -> None:
        self._pptx.top = to_pptx_length(value)

    def set_top(self, value: Length | LiteralLength | PptxLength) -> Self:
        """Set top position value and return self for method chaining."""
        self.top = value
        return self

    @property
    def width(self) -> Length:
        return to_length(self._pptx.width)

    @width.setter
    def width(self, value: Length | LiteralLength | PptxLength) -> None:
        self._pptx.width = to_pptx_length(value)

    def set_width(self, value: Length | LiteralLength | PptxLength) -> Self:
        """Set width value and return self for method chaining."""
        self.width = value
        return self


class Shape(BaseShape[GenericPptxShape]):
    @property
    def adjustments(self) -> list[float]:
        return [self._pptx.adjustments[i] for i in range(len(self._pptx.adjustments))]

    @property
    def auto_shape_type(self) -> "MSO_AUTO_SHAPE_TYPE | None":
        return self._pptx.auto_shape_type

    @property
    def fill(self) -> "FillFormat":
        from tppt.pptx.dml.fill import FillFormat

        return FillFormat(self._pptx.fill)

    @property
    def line(self) -> "LineFormat":
        from tppt.pptx.dml.line import LineFormat

        return LineFormat(self._pptx.line)

    @property
    def text(self) -> str:
        return self._pptx.text

    @text.setter
    def text(self, text: str) -> None:
        self._pptx.text = text

    def set_text(self, text: str) -> Self:
        """Set text value and return self for method chaining."""
        self.text = text
        return self

    @property
    def text_frame(self) -> "TextFrame":
        from tppt.pptx.text.text_frame import TextFrame

        return TextFrame(self._pptx.text_frame)


_GenericPptxSubshape = TypeVar("_GenericPptxSubshape", bound=PptxSubshape)


class SubShape(PptxConvertible[_GenericPptxSubshape]):
    pass


class RangeProps(TypedDict):
    """Range properties."""

    left: Length | LiteralLength
    top: Length | LiteralLength
    width: Length | LiteralLength
    height: Length | LiteralLength
