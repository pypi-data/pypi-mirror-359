from typing import Literal, NotRequired

from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.shapes.autoshape import Shape as PptxShape

from tppt.pptx.text.text_frame import TextFrame
from tppt.types._color import Color, LiteralColor, to_color
from tppt.types._length import Length, LiteralLength, to_length

from . import RangeProps, Shape


class TextProps(RangeProps):
    """Text properties."""

    size: NotRequired[Length | LiteralLength]
    bold: NotRequired[bool]
    italic: NotRequired[bool]
    color: NotRequired[Color | LiteralColor]
    margin_bottom: NotRequired[Length | LiteralLength]
    margin_left: NotRequired[Length | LiteralLength]
    vertical_anchor: NotRequired[MSO_ANCHOR]
    word_wrap: NotRequired[bool]
    auto_size: NotRequired[MSO_AUTO_SIZE]
    alignment: NotRequired[PP_ALIGN]
    level: NotRequired[int]


class TextData(TextProps):
    """Text data."""

    type: Literal["text"]

    text: str


class Text(Shape):
    """Text data class."""

    def __init__(self, pptx_obj: PptxShape, data: TextData | None = None, /) -> None:
        if data and data["text"] != "":
            text_frame = TextFrame(pptx_obj.text_frame)
            p = text_frame.paragraphs[0]
            run = p.add_run()
            run.text = data["text"]
            font = run.font
            if size := data.get("size"):
                font.size = to_length(size)
            if (bold := data.get("bold")) is not None:
                font.bold = bold
            if (italic := data.get("italic")) is not None:
                font.italic = italic
            if (color := data.get("color")) is not None:
                font.color.rgb = to_color(color)
            if (margin_bottom := data.get("margin_bottom")) is not None:
                p.space_after = to_length(margin_bottom)
            if (margin_left := data.get("margin_left")) is not None:
                p.space_before = to_length(margin_left)
            if (vertical_anchor := data.get("vertical_anchor")) is not None:
                text_frame.vertical_anchor = vertical_anchor
            if (word_wrap := data.get("word_wrap")) is not None:
                text_frame.word_wrap = word_wrap
            if (auto_size := data.get("auto_size")) is not None:
                text_frame.auto_size = auto_size
            if (alignment := data.get("alignment")) is not None:
                p.alignment = alignment
            if (level := data.get("level")) is not None:
                p.level = level

        self._pptx = pptx_obj

    @property
    def text_frame(self) -> TextFrame:
        return TextFrame(self._pptx.text_frame)
