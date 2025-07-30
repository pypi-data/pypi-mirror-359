from pptx.enum.text import MSO_TEXT_UNDERLINE_TYPE
from pptx.text.text import Font as PptxFont

from tppt.pptx.converter import PptxConvertible, to_pptx_length, to_tppt_length
from tppt.pptx.dml.color import ColorFormat
from tppt.types._length import Length


class Font(PptxConvertible[PptxFont]):
    @property
    def name(self) -> str | None:
        return self._pptx.name

    @name.setter
    def name(self, name: str) -> None:
        self._pptx.name = name

    @property
    def size(self) -> Length | None:
        return to_tppt_length(self._pptx.size)

    @size.setter
    def size(self, size: Length) -> None:
        self._pptx.size = to_pptx_length(size)

    @property
    def bold(self) -> bool | None:
        return self._pptx.bold

    @bold.setter
    def bold(self, bold: bool) -> None:
        self._pptx.bold = bold

    @property
    def italic(self) -> bool | None:
        return self._pptx.italic

    @italic.setter
    def italic(self, italic: bool) -> None:
        self._pptx.italic = italic

    @property
    def underline(self) -> bool | MSO_TEXT_UNDERLINE_TYPE | None:
        return self._pptx.underline

    @underline.setter
    def underline(self, underline: bool | MSO_TEXT_UNDERLINE_TYPE) -> None:
        self._pptx.underline = underline

    @property
    def color(self) -> ColorFormat:
        return ColorFormat(self._pptx.color)

    @color.setter
    def color(self, color: ColorFormat) -> None:
        self._pptx.color = color.to_pptx()
