"""
## 📊 python-pptx wrapper implementation 📊

This module provides a wrapper for the [python-pptx](https://github.com/scanny/python-pptx) library.

In addition, the `Presentation` and `SlideLayout` classes have a `builder()` method, which allows you to create a PowerPoint declaratively.
"""

from .presentation import Presentation as Presentation
from .shape.picture import Picture as Picture
from .shape.text import Text as Text
from .slide import Slide as Slide
from .table import Table as Table
from .table import TableCellStyle as TableCellStyle
