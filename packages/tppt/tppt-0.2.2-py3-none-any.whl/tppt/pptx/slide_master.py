from pptx.slide import SlideMaster as PptxSlideMaster

from tppt.pptx.converter import PptxConvertible

from .slide_layout import SlideLayout


class SlideMaster(PptxConvertible[PptxSlideMaster]):
    """Slide master data class."""

    @property
    def slide_layouts(self) -> list[SlideLayout]:
        return [SlideLayout.from_pptx(layout) for layout in self._pptx.slide_layouts]
