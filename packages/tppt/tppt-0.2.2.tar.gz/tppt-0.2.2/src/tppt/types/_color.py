"""Color types for tppt."""

from dataclasses import dataclass
from typing import TypeAlias, assert_never, overload

from pptx.dml.color import RGBColor as _PptxRGBColor
from typing_extensions import Annotated, Doc

from tppt.exception import (
    ColorInvalidFormatError,
    ColorInvalidTupleSizeError,
    InvalidColorValueError,
)

LiteralRGBColor: TypeAlias = tuple[int, int, int]
LiteralRGBAColor: TypeAlias = tuple[int, int, int, int]
LiteralColor: TypeAlias = LiteralRGBColor | LiteralRGBAColor | str


@dataclass
class Color:
    r: Annotated[int, Doc("red color value")]
    g: Annotated[int, Doc("green color value")]
    b: Annotated[int, Doc("blue color value")]
    a: Annotated[int | None, Doc("alpha color value")] = None

    def __post_init__(self):
        if not 0 <= self.r <= 255:
            raise InvalidColorValueError("red", self.r)
        if not 0 <= self.g <= 255:
            raise InvalidColorValueError("green", self.g)
        if not 0 <= self.b <= 255:
            raise InvalidColorValueError("blue", self.b)
        if self.a is not None and not 0 <= self.a <= 255:
            raise InvalidColorValueError("alpha", self.a)


@overload
def to_color(color: Color | LiteralColor | _PptxRGBColor) -> Color: ...


@overload
def to_color(
    color: Color | LiteralColor | _PptxRGBColor | None,
) -> Color | None: ...


def to_color(color: Color | LiteralColor | _PptxRGBColor | None) -> Color | None:
    match color:
        case None:
            return None
        case str():
            if not color.startswith("#"):
                raise ColorInvalidFormatError(color)

            match len(color):
                case 4 | 5:
                    # Note that #123 is the same as #112233
                    r = int(color[1:2] * 2, 16)
                    g = int(color[2:3] * 2, 16)
                    b = int(color[3:4] * 2, 16)
                    a = int(color[4:5] * 2, 16) if len(color) == 5 else None
                    return Color(r, g, b, a)

                case 7 | 9:
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    a = int(color[7:9], 16) if len(color) == 9 else None
                    return Color(r, g, b, a)

                case _:
                    raise ColorInvalidFormatError(color)
        case tuple():
            match color:
                case tuple() if len(color) == 3:
                    r, g, b = color
                    return Color(r, g, b)
                case tuple() if len(color) == 4:
                    r, g, b, a = color
                    return Color(r, g, b, a)
                case _:
                    raise ColorInvalidTupleSizeError(color)
        case Color():
            return color
        case _:
            assert_never(color)
