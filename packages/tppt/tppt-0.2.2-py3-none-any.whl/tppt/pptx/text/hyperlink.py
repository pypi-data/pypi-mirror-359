from typing import Self

from pptx.text.text import _Hyperlink as PptxHyperlink

from tppt.pptx.converter import PptxConvertible


class Hyperlink(PptxConvertible[PptxHyperlink]):
    @property
    def address(self) -> str | None:
        return self._pptx.address

    @address.setter
    def address(self, address: str | None) -> None:
        self._pptx.address = address

    def set_address(self, address: str | None) -> Self:
        self._pptx.address = address
        return self
