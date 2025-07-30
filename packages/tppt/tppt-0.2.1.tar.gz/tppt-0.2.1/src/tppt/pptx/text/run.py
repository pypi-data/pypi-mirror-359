from pptx.text.text import _Run as PptxRun

from tppt.pptx.converter import PptxConvertible
from tppt.pptx.text.font import Font
from tppt.pptx.text.hyperlink import Hyperlink


class Run(PptxConvertible[PptxRun]):
    @property
    def font(self) -> Font:
        return Font(self._pptx.font)

    @property
    def hyperlink(self) -> Hyperlink:
        return Hyperlink(self._pptx.hyperlink)

    @property
    def text(self) -> str:
        return self._pptx.text

    @text.setter
    def text(self, text: str) -> None:
        self._pptx.text = text
