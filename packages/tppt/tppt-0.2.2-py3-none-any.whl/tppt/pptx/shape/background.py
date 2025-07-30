from pptx.slide import _Background as PptxBackground

from tppt.pptx.converter import PptxConvertible


class Background(PptxConvertible[PptxBackground]):
    """Background of the slide."""
