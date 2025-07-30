from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from pptx.slide import SlideLayouts as PptxSlideLayouts


class TpptException(Exception):
    """Base exception for tppt."""

    @property
    @abstractmethod
    def message(self) -> str: ...

    @property
    def extra(self) -> dict[str, Any]:
        return {}

    def __str__(self) -> str:
        return self.message


class ColorInvalidFormatError(TpptException, ValueError):
    """Color format is invalid."""

    def __init__(self, color: str) -> None:
        self.color = color

    @property
    def message(self) -> str:
        return f"Invalid color format: {self.color}"


class ColorInvalidTupleSizeError(TpptException, ValueError):
    """Color tuple size is invalid."""

    def __init__(self, color: tuple[Any, ...]) -> None:
        self.color = color

    @property
    def message(self) -> str:
        return f"Invalid color tuple size: {self.color}, expected 3(RGB) or 4(RGBA) elements."


class SlideLayoutIndexError(TpptException, IndexError):
    """Slide layout index is out of range."""

    def __init__(self, index: int, slide_layouts: "PptxSlideLayouts") -> None:
        self.index = index
        self.slide_layouts = slide_layouts

    @property
    def message(self) -> str:
        return f"Slide layout index {self.index} is out of range. Available slide layouts: {[layout.name for layout in self.slide_layouts]}"


class SlideMasterAttributeMustBeSlideLayoutError(TpptException, ValueError):
    """Slide master attribute must be a slide layout."""

    def __init__(self, slide_layout_name: str) -> None:
        self.slide_layout_name = slide_layout_name

    @property
    def message(self) -> str:
        return f"The slide master attribute must be a slide layout. The {self.slide_layout_name} layout is not a slide layout."


class SlideMasterDoesNotHaveAttributesError(TpptException, AttributeError):
    """Slide master does not have an attribute."""

    @property
    def message(self) -> str:
        return "The slide master does not have an attributes"


class SlideMasterAttributeNotFoundError(TpptException, AttributeError):
    """Slide master attribute not found."""

    def __init__(self, attribute_name: str) -> None:
        self.attribute_name = attribute_name

    @property
    def message(self) -> str:
        return (
            f"The slide master does not have an attribute of the {self.attribute_name}"
        )


class InvalidSetterTypeError(TpptException, TypeError):
    """Invalid setter type."""

    def __init__(
        self, expected_type: type | tuple[type, ...], actual_type: type
    ) -> None:
        self.expected_type = expected_type
        self.actual_type = actual_type

    @property
    def message(self) -> str:
        return f"Invalid setter type. Expected type: {self.expected_type}, but got: {self.actual_type}."


class InvalidColorValueError(TpptException, ValueError):
    """Invalid color value."""

    def __init__(
        self, type: Literal["red", "green", "blue", "alpha"], value: int
    ) -> None:
        self.type = type
        self.value = value

    @property
    def message(self) -> str:
        return f"Invalid {self.type} value: {self.value}. It must be between 0 and 255."
