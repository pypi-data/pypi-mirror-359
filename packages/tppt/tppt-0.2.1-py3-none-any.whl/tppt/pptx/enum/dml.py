from typing import Literal, assert_never, overload

from pptx.enum.dml import MSO_LINE_DASH_STYLE, MSO_PATTERN_TYPE

LiteralLineDashStyle = Literal[
    "dash",
    "dash_dot",
    "dash_dot_dot",
    "long_dash",
    "long_dash_dot",
    "round_dot",
    "solid",
    "square_dot",
    "mixed",
]

LiteralPatternType = Literal[
    "cross",
    "dark_downward_diagonal",
    "dark_horizontal",
    "dark_upward_diagonal",
    "dark_vertical",
    "dashed_downward_diagonal",
    "dashed_horizontal",
    "dashed_upward_diagonal",
    "dashed_vertical",
    "diagonal_brick",
    "diagonal_cross",
    "divot",
    "dotted_grid",
    "downward_diagonal",
    "horizontal",
    "horizontal_brick",
    "large_checker_board",
    "large_confetti",
    "large_grid",
    "light_downward_diagonal",
    "light_horizontal",
    "light_upward_diagonal",
    "light_vertical",
    "narrow_horizontal",
    "narrow_vertical",
    "outlined_diamond",
    "5%_of_the_foreground_color",
    "10%_of_the_foreground_color",
    "20%_of_the_foreground_color",
    "25%_of_the_foreground_color",
    "30%_of_the_foreground_color",
    "40%_of_the_foreground_color",
    "50%_of_the_foreground_color",
    "60%_of_the_foreground_color",
    "70%_of_the_foreground_color",
    "75%_of_the_foreground_color",
    "80%_of_the_foreground_color",
    "90%_of_the_foreground_color",
    "plaid",
    "shingle",
    "small_checker_board",
    "small_confetti",
    "small_grid",
    "solid_diamond",
    "sphere",
    "trellis",
    "upward_diagonal",
    "vertical",
    "wave",
    "weave",
    "wide_downward_diagonal",
    "wide_upward_diagonal",
    "zig_zag",
    "mixed",
]


@overload
def to_pptx_line_dash_style(
    dash_style: LiteralLineDashStyle | MSO_LINE_DASH_STYLE,
) -> MSO_LINE_DASH_STYLE: ...


@overload
def to_pptx_line_dash_style(
    dash_style: LiteralLineDashStyle | MSO_LINE_DASH_STYLE | None,
) -> MSO_LINE_DASH_STYLE | None: ...


def to_pptx_line_dash_style(
    dash_style: LiteralLineDashStyle | MSO_LINE_DASH_STYLE | None,
) -> MSO_LINE_DASH_STYLE | None:
    match dash_style:
        case None:
            return None
        case MSO_LINE_DASH_STYLE():
            return dash_style
        case "dash":
            return MSO_LINE_DASH_STYLE.DASH
        case "dash_dot":
            return MSO_LINE_DASH_STYLE.DASH_DOT
        case "dash_dot_dot":
            return MSO_LINE_DASH_STYLE.DASH_DOT_DOT
        case "long_dash":
            return MSO_LINE_DASH_STYLE.LONG_DASH
        case "long_dash_dot":
            return MSO_LINE_DASH_STYLE.LONG_DASH_DOT
        case "round_dot":
            return MSO_LINE_DASH_STYLE.ROUND_DOT
        case "solid":
            return MSO_LINE_DASH_STYLE.SOLID
        case "square_dot":
            return MSO_LINE_DASH_STYLE.SQUARE_DOT
        case "mixed":
            return MSO_LINE_DASH_STYLE.DASH_STYLE_MIXED
        case _:
            assert_never(dash_style)


def to_pptx_pattern_type(
    pattern_type: LiteralPatternType | MSO_PATTERN_TYPE,
) -> MSO_PATTERN_TYPE:
    match pattern_type:
        case MSO_PATTERN_TYPE():
            return pattern_type
        case "cross":
            return MSO_PATTERN_TYPE.CROSS
        case "dark_downward_diagonal":
            return MSO_PATTERN_TYPE.DARK_DOWNWARD_DIAGONAL
        case "dark_horizontal":
            return MSO_PATTERN_TYPE.DARK_HORIZONTAL
        case "dark_upward_diagonal":
            return MSO_PATTERN_TYPE.DARK_UPWARD_DIAGONAL
        case "dark_vertical":
            return MSO_PATTERN_TYPE.DARK_VERTICAL
        case "dashed_downward_diagonal":
            return MSO_PATTERN_TYPE.DASHED_DOWNWARD_DIAGONAL
        case "dashed_horizontal":
            return MSO_PATTERN_TYPE.DASHED_HORIZONTAL
        case "dashed_upward_diagonal":
            return MSO_PATTERN_TYPE.DASHED_UPWARD_DIAGONAL
        case "dashed_vertical":
            return MSO_PATTERN_TYPE.DASHED_VERTICAL
        case "diagonal_brick":
            return MSO_PATTERN_TYPE.DIAGONAL_BRICK
        case "diagonal_cross":
            return MSO_PATTERN_TYPE.DIAGONAL_CROSS
        case "divot":
            return MSO_PATTERN_TYPE.DIVOT
        case "dotted_grid":
            return MSO_PATTERN_TYPE.DOTTED_GRID
        case "downward_diagonal":
            return MSO_PATTERN_TYPE.DOWNWARD_DIAGONAL
        case "horizontal":
            return MSO_PATTERN_TYPE.HORIZONTAL
        case "horizontal_brick":
            return MSO_PATTERN_TYPE.HORIZONTAL_BRICK
        case "large_checker_board":
            return MSO_PATTERN_TYPE.LARGE_CHECKER_BOARD
        case "large_confetti":
            return MSO_PATTERN_TYPE.LARGE_CONFETTI
        case "large_grid":
            return MSO_PATTERN_TYPE.LARGE_GRID
        case "light_downward_diagonal":
            return MSO_PATTERN_TYPE.LIGHT_DOWNWARD_DIAGONAL
        case "light_horizontal":
            return MSO_PATTERN_TYPE.LIGHT_HORIZONTAL
        case "light_upward_diagonal":
            return MSO_PATTERN_TYPE.LIGHT_UPWARD_DIAGONAL
        case "light_vertical":
            return MSO_PATTERN_TYPE.LIGHT_VERTICAL
        case "narrow_horizontal":
            return MSO_PATTERN_TYPE.NARROW_HORIZONTAL
        case "narrow_vertical":
            return MSO_PATTERN_TYPE.NARROW_VERTICAL
        case "outlined_diamond":
            return MSO_PATTERN_TYPE.OUTLINED_DIAMOND
        case "5%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_5
        case "10%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_10
        case "20%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_20
        case "25%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_25
        case "30%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_30
        case "40%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.ERCENT_40
        case "50%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_50
        case "60%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_60
        case "70%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_70
        case "75%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_75
        case "80%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_80
        case "90%_of_the_foreground_color":
            return MSO_PATTERN_TYPE.PERCENT_90
        case "plaid":
            return MSO_PATTERN_TYPE.PLAID
        case "shingle":
            return MSO_PATTERN_TYPE.SHINGLE
        case "small_checker_board":
            return MSO_PATTERN_TYPE.SMALL_CHECKER_BOARD
        case "small_confetti":
            return MSO_PATTERN_TYPE.SMALL_CONFETTI
        case "small_grid":
            return MSO_PATTERN_TYPE.SMALL_GRID
        case "solid_diamond":
            return MSO_PATTERN_TYPE.SOLID_DIAMOND
        case "sphere":
            return MSO_PATTERN_TYPE.SPHERE
        case "trellis":
            return MSO_PATTERN_TYPE.TRELLIS
        case "upward_diagonal":
            return MSO_PATTERN_TYPE.UPWARD_DIAGONAL
        case "vertical":
            return MSO_PATTERN_TYPE.VERTICAL
        case "wave":
            return MSO_PATTERN_TYPE.WAVE
        case "weave":
            return MSO_PATTERN_TYPE.WEAVE
        case "wide_downward_diagonal":
            return MSO_PATTERN_TYPE.WIDE_DOWNWARD_DIAGONAL
        case "wide_upward_diagonal":
            return MSO_PATTERN_TYPE.WIDE_UPWARD_DIAGONAL
        case "zig_zag":
            return MSO_PATTERN_TYPE.ZIG_ZAG
        case "mixed":
            return MSO_PATTERN_TYPE.MIXED
        case _:
            assert_never(pattern_type)
