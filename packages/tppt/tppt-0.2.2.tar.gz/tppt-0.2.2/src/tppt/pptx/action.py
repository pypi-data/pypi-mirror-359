from typing import Self

from pptx.action import ActionSetting as _PptxActionSetting
from pptx.action import Hyperlink as _PptxHyperlink
from pptx.enum.action import PP_ACTION_TYPE

from tppt.pptx.converter import PptxConvertible
from tppt.pptx.shape import SubShape
from tppt.pptx.slide import Slide


class Hyperlink(SubShape[_PptxHyperlink]):
    @property
    def address(self) -> str | None:
        return self._pptx.address

    @address.setter
    def address(self, value: str | None):
        self._pptx.address = value

    def set_address(self, value: str | None) -> Self:
        self.address = value
        return self


class ActionSetting(PptxConvertible[_PptxActionSetting]):
    @property
    def action(self) -> PP_ACTION_TYPE:
        return self._pptx.action

    @property
    def hyperlink(self) -> Hyperlink:
        return Hyperlink(self._pptx.hyperlink)

    @property
    def target_slide(self) -> Slide | None:
        if target_slide := self._pptx.target_slide:
            return Slide(target_slide)
        return None

    @target_slide.setter
    def target_slide(self, value: Slide | None):
        if value is None:
            self._pptx.target_slide = None
        else:
            self._pptx.target_slide = value._pptx

    def set_target_slide(self, value: Slide | None) -> Self:
        self.target_slide = value
        return self
