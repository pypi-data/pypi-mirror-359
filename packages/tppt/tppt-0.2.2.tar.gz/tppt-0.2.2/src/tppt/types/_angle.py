from typing import Literal, TypeAlias

LiteralDegree: TypeAlias = tuple[float, Literal["deg"]]
LiteralAngle: TypeAlias = LiteralDegree


class Degrees(float):
    """Degrees."""

    def __init__(self, value: float) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"Degrees({self._value})"


Angle: TypeAlias = Degrees


def to_angle(angle: LiteralAngle | Angle) -> Angle:
    """Convert any angle to Degrees."""
    if isinstance(angle, tuple):
        return Degrees(angle[0])
    return angle
