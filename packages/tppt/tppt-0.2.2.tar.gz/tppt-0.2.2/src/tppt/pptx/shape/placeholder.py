from pptx.shapes.placeholder import LayoutPlaceholder as _PptxLayoutPlaceholder
from pptx.shapes.placeholder import MasterPlaceholder as _PptxMasterPlaceholder
from pptx.shapes.placeholder import SlidePlaceholder as _PptxSlidePlaceholder

from . import Shape


class LayoutPlaceholder(Shape[_PptxLayoutPlaceholder]): ...


class MasterPlaceholder(Shape[_PptxMasterPlaceholder]): ...


class SlidePlaceholder(Shape[_PptxSlidePlaceholder]): ...
