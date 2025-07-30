from pptx.slide import SlideLayout as PptxSlideLayout

from .converter import PptxConvertible
from .shape import BaseShape
from .shape.background import Background
from .shape.placeholder import LayoutPlaceholder


class SlideLayout(PptxConvertible[PptxSlideLayout]):
    """Slide layout data class."""

    @property
    def name(self) -> str | None:
        """String representing the internal name of this slide.

        Returns an empty string if no name is assigned.
        """
        if name := self._pptx.name:
            return name

        return None

    @property
    def background(self) -> Background:
        """Get the background."""
        return Background.from_pptx(self._pptx.background)

    @property
    def placeholders(self) -> list[LayoutPlaceholder]:
        """Get the placeholders."""
        return [
            LayoutPlaceholder.from_pptx(placeholder)
            for placeholder in self._pptx.placeholders.__iter__()
        ]

    @property
    def shapes(self) -> list[BaseShape]:
        """Get the shapes."""
        return [BaseShape.from_pptx(shape) for shape in self._pptx.shapes]
