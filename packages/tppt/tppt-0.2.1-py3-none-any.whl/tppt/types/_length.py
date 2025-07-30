"""Length types for tppt."""

from typing import Literal, assert_never

from pptx.util import Length as _PptxLength

# Constants for unit conversion
INCHES_PER_POINT = 1 / 72  # 1 point = 1/72 inches
POINTS_PER_INCH = 72  # 1 inch = 72 points
CM_PER_INCH = 2.54  # 1 inch = 2.54 cm
MM_PER_INCH = 25.4  # 1 inch = 25.4 mm
MM_PER_CM = 10  # 1 cm = 10 mm
EMUS_PER_INCH = 914400  # 1 inch = 914400 EMU
EMUS_PER_CM = 360000  # 1 cm = 360000 EMU
EMUS_PER_MM = 36000  # 1 mm = 36000 EMU
EMUS_PER_PT = 12700  # 1 pt = 12700 EMU

LiteralPoints = tuple[int, Literal["pt"]]
LiteralCentimeters = tuple[float, Literal["cm"]]
LiteralInches = tuple[float, Literal["in"]]
LiteralMillimeters = tuple[float, Literal["mm"]]
LiteralEnglishMetricUnits = tuple[int, Literal["emu"]]

LiteralLength = (
    LiteralPoints
    | LiteralCentimeters
    | LiteralInches
    | LiteralMillimeters
    | LiteralEnglishMetricUnits
)


class Inches:
    """Class representing inches"""

    def __init__(self, value: float):
        self.value = value

    def __add__(self, other: "Length | LiteralLength") -> "Inches":
        if isinstance(other, tuple):
            other = to_length(other)
        return Inches(self.value + to_inches(other).value)

    def __sub__(self, other: "Length | LiteralLength") -> "Inches":
        if isinstance(other, tuple):
            other = to_length(other)
        return Inches(self.value - to_inches(other).value)

    def __iadd__(self, other: "Length | LiteralLength") -> "Inches":
        if isinstance(other, tuple):
            other = to_length(other)
        self.value += to_inches(other).value
        return self

    def __isub__(self, other: "Length | LiteralLength") -> "Inches":
        if isinstance(other, tuple):
            other = to_length(other)
        self.value -= to_inches(other).value
        return self

    def __mul__(self, other: int | float) -> "Inches":
        return Inches(self.value * other)

    def __truediv__(self, other: int | float) -> "Inches":
        return Inches(self.value / other)

    def __eq__(self, other: object) -> bool:
        match other:
            case Inches():
                return self.value == other.value
            case (
                CentiMeters()
                | Points()
                | MilliMeters()
                | EnglishMetricUnits()
                | tuple()
            ):
                return self == to_inches(other)
            case _:
                raise NotImplementedError(
                    f"Cannot compare {type(self)} with {type(other)}"
                )

    def __repr__(self) -> str:
        return f"Inchs({self.value})"


class Points:
    """Class representing points"""

    def __init__(self, value: int):
        self.value = value

    def __add__(self, other: "Length | LiteralLength") -> "Points":
        if isinstance(other, tuple):
            other = to_length(other)
        return Points(self.value + to_points(other).value)

    def __sub__(self, other: "Length | LiteralLength") -> "Points":
        if isinstance(other, tuple):
            other = to_length(other)
        return Points(self.value - to_points(other).value)

    def __iadd__(self, other: "Length | LiteralLength") -> "Points":
        if isinstance(other, tuple):
            other = to_length(other)
        self.value += to_points(other).value
        return self

    def __isub__(self, other: "Length | LiteralLength") -> "Points":
        if isinstance(other, tuple):
            other = to_length(other)
        self.value -= to_points(other).value
        return self

    def __mul__(self, other: int | float) -> "Points":
        return Points(int(self.value * other))

    def __truediv__(self, other: int | float) -> "Points":
        return Points(int(self.value / other))

    def __eq__(self, other: object) -> bool:
        match other:
            case Points():
                return self.value == other.value
            case (
                CentiMeters()
                | Inches()
                | MilliMeters()
                | EnglishMetricUnits()
                | tuple()
            ):
                return self == to_points(other)
            case _:
                raise NotImplementedError(
                    f"Cannot compare {type(self)} with {type(other)}"
                )

    def __repr__(self) -> str:
        return f"Points({self.value})"


class CentiMeters:
    """Class representing centimeters"""

    def __init__(self, value: float):
        self.value = value

    def __add__(self, other: "Length | LiteralLength") -> "CentiMeters":
        if isinstance(other, tuple):
            other = to_length(other)
        return CentiMeters(self.value + to_centi_meters(other).value)

    def __sub__(self, other: "Length | LiteralLength") -> "CentiMeters":
        if isinstance(other, tuple):
            other = to_length(other)
        return CentiMeters(self.value - to_centi_meters(other).value)

    def __iadd__(self, other: "Length | LiteralLength") -> "CentiMeters":
        if isinstance(other, tuple):
            other = to_length(other)
        self.value += to_centi_meters(other).value
        return self

    def __isub__(self, other: "Length | LiteralLength") -> "CentiMeters":
        if isinstance(other, tuple):
            other = to_length(other)
        self.value -= to_centi_meters(other).value
        return self

    def __mul__(self, other: int | float) -> "CentiMeters":
        return CentiMeters(self.value * other)

    def __truediv__(self, other: int | float) -> "CentiMeters":
        return CentiMeters(self.value / other)

    def __eq__(self, other: object) -> bool:
        match other:
            case CentiMeters():
                return self.value == other.value
            case Inches() | Points() | MilliMeters() | EnglishMetricUnits() | tuple():
                return self == to_centi_meters(other)
            case _:
                raise NotImplementedError(
                    f"Cannot compare {type(self)} with {type(other)}"
                )

    def __repr__(self) -> str:
        return f"CentiMeters({self.value})"


class MilliMeters:
    """Class representing millimeters"""

    def __init__(self, value: float):
        self.value = value

    def __add__(self, other: "Length | LiteralLength") -> "MilliMeters":
        if isinstance(other, tuple):
            other = to_length(other)
        return MilliMeters(self.value + to_milli_meters(other).value)

    def __sub__(self, other: "Length | LiteralLength") -> "MilliMeters":
        if isinstance(other, tuple):
            other = to_length(other)
        return MilliMeters(self.value - to_milli_meters(other).value)

    def __iadd__(self, other: "Length | LiteralLength") -> "MilliMeters":
        if isinstance(other, tuple):
            other = to_length(other)
        self.value += to_milli_meters(other).value
        return self

    def __isub__(self, other: "Length | LiteralLength") -> "MilliMeters":
        if isinstance(other, tuple):
            other = to_length(other)
        self.value -= to_milli_meters(other).value
        return self

    def __mul__(self, other: int | float) -> "MilliMeters":
        return MilliMeters(self.value * other)

    def __truediv__(self, other: int | float) -> "MilliMeters":
        return MilliMeters(self.value / other)

    def __eq__(self, other: object) -> bool:
        match other:
            case MilliMeters():
                return self.value == other.value
            case CentiMeters() | Inches() | Points() | EnglishMetricUnits() | tuple():
                return self == to_milli_meters(other)
            case _:
                raise NotImplementedError(
                    f"Cannot compare {type(self)} with {type(other)}"
                )

    def __repr__(self) -> str:
        return f"MilliMeters({self.value})"


class EnglishMetricUnits:
    """
    Class representing English Metric Units (EMU)

    This is not a physical unit system, but is written as a Microsoft-specific definition
    in the ISO/IEC 29500 specification as "1 inch = 360,000 EMU".
    """

    def __init__(self, value: int):
        self.value = value

    def __add__(self, other: "Length | LiteralLength") -> "EnglishMetricUnits":
        if isinstance(other, tuple):
            other = to_length(other)
        return EnglishMetricUnits(self.value + to_english_metric_units(other).value)

    def __sub__(self, other: "Length | LiteralLength") -> "EnglishMetricUnits":
        if isinstance(other, tuple):
            other = to_length(other)
        return EnglishMetricUnits(self.value - to_english_metric_units(other).value)

    def __iadd__(self, other: "Length | LiteralLength") -> "EnglishMetricUnits":
        if isinstance(other, tuple):
            other = to_length(other)
        self.value += to_english_metric_units(other).value
        return self

    def __isub__(self, other: "Length | LiteralLength") -> "EnglishMetricUnits":
        if isinstance(other, tuple):
            other = to_length(other)
        self.value -= to_english_metric_units(other).value
        return self

    def __mul__(self, other: int | float) -> "EnglishMetricUnits":
        return EnglishMetricUnits(int(self.value * other))

    def __truediv__(self, other: int | float) -> "EnglishMetricUnits":
        return EnglishMetricUnits(int(self.value / other))

    def __eq__(self, other: object) -> bool:
        match other:
            case EnglishMetricUnits():
                return self.value == other.value
            case CentiMeters() | Inches() | Points() | MilliMeters() | tuple():
                return self == to_english_metric_units(other)
            case _:
                raise NotImplementedError(
                    f"Cannot compare {type(self)} with {type(other)}"
                )

    def __repr__(self) -> str:
        return f"EnglishMetricUnits({self.value})"


Length = Inches | Points | CentiMeters | MilliMeters | EnglishMetricUnits


def to_length(length: LiteralLength | Length | _PptxLength) -> Length:
    """Convert public length representation to internal length representation

    Args:
        length (Length): Public length representation

    Returns:
        _Length: Internal length representation
    """

    match length:
        case tuple():
            value, unit = length
            match unit:
                case "in":
                    return Inches(value)
                case "cm":
                    return CentiMeters(value)
                case "pt":
                    return Points(int(value))
                case "mm":
                    return MilliMeters(value)
                case "emu":
                    return EnglishMetricUnits(int(value))
                case _:
                    assert_never(unit)
        case _PptxLength():
            return EnglishMetricUnits(length)
        case _:
            return length


def to_literal_length(
    length: LiteralLength | Length, unit: Literal["in", "cm", "pt", "mm", "emu"]
) -> LiteralLength:
    """Convert internal length representation to public length representation

    Args:
        length (_Length): Internal length representation
        unit (Literal["in", "cm", "pt", "mm", "emu"]): Desired unit

    Returns:
        Length: Public length representation
    """
    if isinstance(length, tuple):
        return length

    match unit:
        case "in":
            return (to_inches(length).value, "in")
        case "cm":
            return (to_centi_meters(length).value, "cm")
        case "pt":
            return (to_points(length).value, "pt")
        case "mm":
            return (to_milli_meters(length).value, "mm")
        case "emu":
            return (to_english_metric_units(length).value, "emu")
        case _:
            assert_never(unit)


def to_centi_meters(length: Length | LiteralLength | _PptxLength) -> CentiMeters:
    """Convert any length to centimeters

    Args:
        length (_Length | Length): Length in any unit

    Returns:
        _Centimeter: Length in centimeters
    """
    if isinstance(length, tuple):
        return to_centi_meters(to_length(length))

    match length:
        case Inches():
            return CentiMeters(length.value * CM_PER_INCH)
        case Points():
            return CentiMeters(length.value * INCHES_PER_POINT * CM_PER_INCH)
        case CentiMeters():
            return length
        case MilliMeters():
            return CentiMeters(length.value / MM_PER_CM)
        case EnglishMetricUnits():
            return CentiMeters(length.value / EMUS_PER_CM)
        case _PptxLength():
            return CentiMeters(length.cm)
        case _:
            assert_never(length)


def to_inches(length: Length | LiteralLength | _PptxLength) -> Inches:
    """Convert any length to inches

    Args:
        length (_Length | Length): Length in any unit

    Returns:
        _Inch: Length in inches
    """
    if isinstance(length, tuple):
        return to_inches(to_length(length))

    match length:
        case Inches():
            return length
        case Points():
            return Inches(float(length.value) * INCHES_PER_POINT)
        case CentiMeters():
            return Inches(length.value / CM_PER_INCH)
        case MilliMeters():
            return Inches(length.value / MM_PER_INCH)
        case EnglishMetricUnits():
            return Inches(length.value / EMUS_PER_INCH)
        case _PptxLength():
            return Inches(length.inches)
        case _:
            assert_never(length)


def to_points(length: Length | LiteralLength | _PptxLength) -> Points:
    """Convert any length to points

    Args:
        length (_Length | Length): Length in any unit

    Returns:
        _Point: Length in points
    """
    if isinstance(length, tuple):
        return to_points(to_length(length))

    match length:
        case Inches():
            return Points(int(length.value * POINTS_PER_INCH))
        case Points():
            return length
        case CentiMeters():
            return Points(int(length.value / CM_PER_INCH * POINTS_PER_INCH))
        case MilliMeters():
            return Points(int(length.value / MM_PER_INCH * POINTS_PER_INCH))
        case EnglishMetricUnits():
            return Points(int(length.value / EMUS_PER_PT))
        case _PptxLength():
            return Points(int(length.pt))
        case _:
            assert_never(length)


def to_milli_meters(length: Length | LiteralLength | _PptxLength) -> MilliMeters:
    """Convert any length to millimeters

    Args:
        length (_Length | Length): Length in any unit

    Returns:
        _Millimeter: Length in millimeters
    """
    if isinstance(length, tuple):
        return to_milli_meters(to_length(length))

    match length:
        case Inches():
            return MilliMeters(length.value * MM_PER_INCH)
        case Points():
            return MilliMeters(length.value * INCHES_PER_POINT * MM_PER_INCH)
        case CentiMeters():
            return MilliMeters(length.value * MM_PER_CM)
        case MilliMeters():
            return length
        case EnglishMetricUnits():
            return MilliMeters(length.value / EMUS_PER_MM)
        case _PptxLength():
            return MilliMeters(length.mm)
        case _:
            assert_never(length)


def to_english_metric_units(
    length: Length | LiteralLength | _PptxLength,
) -> EnglishMetricUnits:
    """Convert any length to English Metric Units (EMU)

    Args:
        length (_Length | Length): Length in any unit

    Returns:
        _Emu: Length in EMU
    """
    if isinstance(length, tuple):
        return to_english_metric_units(to_length(length))

    match length:
        case Inches():
            return EnglishMetricUnits(int(length.value * EMUS_PER_INCH))
        case Points():
            return EnglishMetricUnits(int(length.value * EMUS_PER_PT))
        case CentiMeters():
            return EnglishMetricUnits(int(length.value * EMUS_PER_CM))
        case MilliMeters():
            return EnglishMetricUnits(int(length.value * EMUS_PER_MM))
        case EnglishMetricUnits():
            return length
        case _PptxLength():
            return EnglishMetricUnits(length.emu)
        case _:
            assert_never(length)
