from typing import Literal, assert_never, cast

from lxml.etree import _Element
from pptx.dml.color import ColorFormat as PptxColorFormat
from pptx.dml.color import RGBColor as PptxRGBColor
from pptx.dml.color import _SRgbColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.oxml.ns import _nsmap as namespace
from pptx.oxml.xmlchemy import OxmlElement

from tppt.pptx.converter import PptxConvertible, to_pptx_rgb_color, to_tppt_rgb_color
from tppt.types import Color, LiteralColor

LiteralThemeColor = Literal[
    "accent1",
    "accent2",
    "accent3",
    "accent4",
    "accent5",
    "accent6",
    "background1",
    "background2",
    "dark1",
    "dark2",
    "followed_hyperlink",
    "hyperlink",
    "light1",
    "light2",
    "text1",
    "text2",
    "mixed",
]


def to_pptx_theme_color(
    value: LiteralThemeColor | MSO_THEME_COLOR | None,
) -> MSO_THEME_COLOR:
    match value:
        case MSO_THEME_COLOR():
            return value
        case None:
            return MSO_THEME_COLOR.NOT_THEME_COLOR
        case "accent1":
            return MSO_THEME_COLOR.ACCENT_1
        case "accent2":
            return MSO_THEME_COLOR.ACCENT_2
        case "accent3":
            return MSO_THEME_COLOR.ACCENT_3
        case "accent4":
            return MSO_THEME_COLOR.ACCENT_4
        case "accent5":
            return MSO_THEME_COLOR.ACCENT_5
        case "accent6":
            return MSO_THEME_COLOR.ACCENT_6
        case "background1":
            return MSO_THEME_COLOR.BACKGROUND_1
        case "background2":
            return MSO_THEME_COLOR.BACKGROUND_2
        case "dark1":
            return MSO_THEME_COLOR.DARK_1
        case "dark2":
            return MSO_THEME_COLOR.DARK_2
        case "followed_hyperlink":
            return MSO_THEME_COLOR.FOLLOWED_HYPERLINK
        case "hyperlink":
            return MSO_THEME_COLOR.HYPERLINK
        case "light1":
            return MSO_THEME_COLOR.LIGHT_1
        case "light2":
            return MSO_THEME_COLOR.LIGHT_2
        case "text1":
            return MSO_THEME_COLOR.TEXT_1
        case "text2":
            return MSO_THEME_COLOR.TEXT_2
        case "mixed":
            return MSO_THEME_COLOR.MIXED
        case _:
            assert_never(value)


class ColorFormat(PptxConvertible[PptxColorFormat]):
    @property
    def brightness(self) -> float:
        """
        Read/write float value between -1.0 and 1.0 indicating the brightness
        adjustment for this color, e.g. -0.25 is 25% darker and 0.4 is 40%
        lighter. 0 means no brightness adjustment.
        """
        return self._pptx.brightness

    @brightness.setter
    def brightness(self, value: float) -> None:
        self._pptx.brightness = value

    @property
    def rgb(self) -> Color:
        solid_fill = cast(
            _Element, self._pptx._xFill.solidFill.get_or_change_to_srgbClr()
        )

        if alpha := solid_fill.find("a:alpha", namespace):
            alpha = alpha.attrib["val"]
        else:
            alpha = None

        return to_tppt_rgb_color(cast(PptxRGBColor, self._pptx.rgb), alpha=alpha)

    @rgb.setter
    def rgb(self, color: Color | LiteralColor | PptxRGBColor):
        pptx_color, alpha = to_pptx_rgb_color(color)
        self._pptx.rgb = pptx_color
        srgbClr = cast(_Element, cast(_SRgbColor, self._pptx._color)._srgbClr)
        if alpha is not None:
            element = OxmlElement("a:alpha")
            element.attrib["val"] = str(int(100000 * (alpha / 255)))
            srgbClr.append(element)
        else:
            if alpha := srgbClr.find("a:alpha", namespace):
                srgbClr.remove(alpha)

    @property
    def theme_color(self) -> MSO_THEME_COLOR | None:
        """Theme color value of this color.

        Value is a member of :ref:`MsoThemeColorIndex`, e.g.
        ``MSO_THEME_COLOR.ACCENT_1``. Raises AttributeError on access if the
        color is not type ``MSO_COLOR_TYPE.SCHEME``. Assigning a member of
        :ref:`MsoThemeColorIndex` causes the color's type to change to
        ``MSO_COLOR_TYPE.SCHEME``.
        """
        return self._pptx.theme_color

    @theme_color.setter
    def theme_color(self, value: LiteralThemeColor | MSO_THEME_COLOR | None) -> None:
        self._pptx.theme_color = to_pptx_theme_color(value)
