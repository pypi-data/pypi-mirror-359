"""Example of adding shapes with background and text."""

from pathlib import Path

from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE

import tppt


def main():
    """Create a PowerPoint with box shapes that have background color and text."""
    tppt.Presentation.builder().slide(
        lambda slide: slide.BlankLayout()
        .builder()
        .add_shape(
            MSO_AUTO_SHAPE_TYPE.RECTANGLE,
            lambda shape: (
                shape.fill.solid().fore_color.set_rgb("#0066ff"),
                shape.set_text("Sample Box with Text"),
            )[-1],
            left=(1, "in"),
            top=(1, "in"),
            width=(4, "in"),
            height=(2, "in"),
        )
        .add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
            lambda shape: (
                shape.fill.solid().fore_color.set_rgb("#ff6600"),
                shape.set_text("Rounded Box"),
            )[-1],
            left=(6, "in"),
            top=(1, "in"),
            width=(3, "in"),
            height=(1.5, "in"),
        )
        .add_shape(
            MSO_AUTO_SHAPE_TYPE.OVAL,
            lambda shape: (
                shape.fill.solid().fore_color.set_rgb("#00ff00"),
                shape.set_text("Circle"),
            )[-1],
            left=(1, "in"),
            top=(4, "in"),
            width=(2, "in"),
            height=(2, "in"),
        )
    ).save(Path(__file__).with_suffix(".pptx"))


if __name__ == "__main__":
    main()
