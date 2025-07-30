from pptx.dml.effect import ShadowFormat as _PptxShadowFormat

from tppt.pptx.converter import PptxConvertible


class ShadowFormat(PptxConvertible[_PptxShadowFormat]):
    @property
    def inherit(self) -> bool:
        return self._pptx.inherit

    @inherit.setter
    def inherit(self, value: bool) -> None:
        self._pptx.inherit = value
