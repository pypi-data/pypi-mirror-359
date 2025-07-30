"""Simple example of using tppt."""

from pathlib import Path

import tppt

EXAMPLE_DIR = Path(__file__).parent


def main():
    """Run the example."""
    # Create a presentation using the builder pattern
    presentation = (
        tppt.Presentation.builder()
        # Slide 1: Title and Text
        .slide(
            lambda slide: slide.TitleLayout(
                title="Amazing Presentation",
                subtitle="Example of using tppt library",
            )
        )
        .slide(
            lambda slide: slide.BlankLayout()
            .builder()
            .text(
                "Amazing Presentation",  # Title
                left=(50, "pt"),
                top=(50, "pt"),
                width=(400, "pt"),
                height=(50, "pt"),
                size=(60, "pt"),
                bold=True,
                italic=True,
                color="#0000FF",
            )
            .text(
                "Example of using tppt library",  # Subtitle
                left=(50, "pt"),
                top=(120, "pt"),
                width=(400, "pt"),
                height=(30, "pt"),
            )
            .text(
                "• Example of text boxes\n• Multiple text elements can be added\n• Position and size can be specified",
                left=(50, "pt"),
                top=(180, "pt"),
                width=(400, "pt"),
                height=(150, "pt"),
            )
        )
        # Slide 2: Python Logo Image
        .slide(
            lambda slide: slide.BlankLayout()
            .builder()
            .text(
                "Python Logo Example",
                left=(50, "pt"),
                top=(50, "pt"),
                width=(300, "pt"),
                height=(40, "pt"),
            )
            .picture(
                EXAMPLE_DIR / "images" / "python-logo.png",
                left=(50, "pt"),
                top=(100, "pt"),
            )
            .text(
                "The Python logo",
                left=(50, "pt"),
                top=(190, "pt"),
                width=(300, "pt"),
                height=(30, "pt"),
            )
            .picture(
                EXAMPLE_DIR / "images" / "python-powered-w.png",
                left=(50, "pt"),
                top=(240, "pt"),
                width=(200, "pt"),
                height=(80, "pt"),
            )
            .text(
                "Python Powered logo",
                left=(50, "pt"),
                top=(330, "pt"),
                width=(300, "pt"),
                height=(30, "pt"),
            )
        )
        # Slide 3: Table example
        .slide(
            lambda slide: slide.BlankLayout()
            .builder()
            .text(
                "Table Example",
                left=(50, "pt"),
                top=(50, "pt"),
                width=(300, "pt"),
                height=(40, "pt"),
            )
            .table(
                [
                    ["Product", "Price", "Stock"],
                    ["Product A", "$10.00", "10 units"],
                    ["Product B", "$25.00", "5 units"],
                    ["Product C", "$32.00", "8 units"],
                    ["Product D", "$18.00", "12 units"],
                ],
                left=(50, "pt"),
                top=(100, "pt"),
                width=(400, "pt"),
                height=(200, "pt"),
            )
            .text(
                "This table shows a list of products and their inventory status.",
                left=(50, "pt"),
                top=(320, "pt"),
                width=(400, "pt"),
                height=(50, "pt"),
            )
        )
        .build()
    )

    # Save the presentation
    presentation.save(Path(__file__).with_suffix(".pptx"))

    print("Rich presentation created successfully!")


if __name__ == "__main__":
    main()
