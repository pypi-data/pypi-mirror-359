from pptx.enum.text import MSO_VERTICAL_ANCHOR
from pptx.table import _Cell as PptxCell

from tppt.pptx.converter import PptxConvertible, to_pptx_length, to_tppt_length
from tppt.pptx.dml.fill import FillFormat
from tppt.pptx.text.text_frame import TextFrame
from tppt.types._length import Length


class Cell(PptxConvertible[PptxCell]):
    """Cell data class."""

    @property
    def fill(self) -> FillFormat:
        """Fill format."""
        return FillFormat(self._pptx.fill)

    @property
    def is_merge_origin(self) -> bool:
        """True if this cell is the top-left grid cell in a merged cell."""
        return self._pptx.is_merge_origin

    @property
    def is_spanned(self) -> bool:
        """True if this cell is spanned by a merge-origin cell."""
        return self._pptx.is_spanned

    @property
    def margin_left(self) -> Length:
        """Left margin of cells."""
        return to_tppt_length(self._pptx.margin_left)

    @margin_left.setter
    def margin_left(self, value: Length) -> None:
        self._pptx.margin_left = to_pptx_length(value)

    @property
    def margin_right(self) -> Length:
        """Right margin of cell."""
        return to_tppt_length(self._pptx.margin_right)

    @margin_right.setter
    def margin_right(self, value: Length) -> None:
        self._pptx.margin_right = to_pptx_length(value)

    @property
    def margin_top(self) -> Length:
        """Top margin of cell."""
        return to_tppt_length(self._pptx.margin_top)

    @margin_top.setter
    def margin_top(self, value: Length) -> None:
        self._pptx.margin_top = to_pptx_length(value)

    @property
    def margin_bottom(self) -> Length:
        """Bottom margin of cell."""
        return to_tppt_length(self._pptx.margin_bottom)

    @margin_bottom.setter
    def margin_bottom(self, value: Length) -> None:
        self._pptx.margin_bottom = to_pptx_length(value)

    def merge(self, other_cell: "Cell") -> None:
        """Create merged cell from this cell to `other_cell`."""
        self._pptx.merge(other_cell._pptx)

    @property
    def span_height(self) -> int:
        """int count of rows spanned by this cell."""
        return self._pptx.span_height

    @property
    def span_width(self) -> int:
        """int count of columns spanned by this cell."""
        return self._pptx.span_width

    def split(self) -> None:
        """Remove merge from this (merge-origin) cell."""
        self._pptx.split()

    @property
    def text(self) -> str:
        """Textual content of cell as a single string."""
        return self._pptx.text

    @text.setter
    def text(self, value: str) -> None:
        self._pptx.text = value

    @property
    def text_frame(self) -> TextFrame:
        """Text frame of cell."""
        return TextFrame(self._pptx.text_frame)

    @property
    def vertical_anchor(self) -> MSO_VERTICAL_ANCHOR | None:
        """Vertical alignment of this cell."""
        return self._pptx.vertical_anchor

    @vertical_anchor.setter
    def vertical_anchor(self, value: MSO_VERTICAL_ANCHOR | None) -> None:
        self._pptx.vertical_anchor = value
