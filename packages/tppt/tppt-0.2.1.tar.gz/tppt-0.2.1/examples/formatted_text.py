"""Simple example of using tppt."""

from pathlib import Path

import tppt

EXAMPLE_DIR = Path(__file__).parent


def main():
    def formatted_text(text: tppt.pptx.Text, /) -> tppt.pptx.Text:
        run = text.text_frame.add_paragraph().add_run()
        run.text = "Hello, world!"
        font = run.font
        font.color.rgb = "#00FFFF"
        font.italic = True

        return text

    def functional_text(
        text_obj: tppt.pptx.Text,
        /,
        *,
        text: str,
        bold: bool = False,
        italic: bool = False,
        color: tppt.types.Color | tppt.types.LiteralColor | None = None,
    ) -> tppt.pptx.Text:
        run = text_obj.text_frame.add_paragraph().add_run()
        run.text = text
        font = run.font

        if color is not None:
            font.color.rgb = color
        if bold:
            font.bold = True
        if italic:
            font.italic = True

        return text_obj

    """Run the example."""
    # Create a presentation using the builder pattern
    presentation = (
        tppt.Presentation.builder()
        .slide(
            lambda slide: slide.BlankLayout()
            .builder()
            .text(
                # Pattern build-in options
                "This is a text",
                left=(50, "pt"),
                top=(50, "pt"),
                width=(400, "pt"),
                height=(50, "pt"),
                bold=True,
                italic=True,
                color="#0000FF",
            )
            .text(
                # Pattern custom function
                formatted_text,
                left=(50, "pt"),
                top=(100, "pt"),
                width=(400, "pt"),
                height=(50, "pt"),
            )
            .text(
                # Pattern use partial apply function
                tppt.apply(
                    functional_text,
                    text="Hello, world!",
                    bold=True,
                    italic=True,
                    color="#00FF00",
                ),
                left=(50, "pt"),
                top=(150, "pt"),
                width=(400, "pt"),
                height=(50, "pt"),
            )
        )
        .build()
    )

    # Save the presentation
    presentation.save(Path(__file__).with_suffix(".pptx"))

    print("Rich Text presentation created successfully!")


if __name__ == "__main__":
    main()
