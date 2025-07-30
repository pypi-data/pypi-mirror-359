from pptx.slide import NotesSlide as PptxNotesSlide

from tppt.pptx.converter import PptxConvertible


class NotesSlide(PptxConvertible[PptxNotesSlide]):
    """Notes slide."""
