"""Sample script to output the presentation tree structure."""

import json
from pathlib import Path

import tppt


def main() -> None:
    presentation = (
        tppt.Presentation.builder()
        .slide(
            lambda slide: slide.BlankLayout()
            .builder()
            .text(
                "Hello, world!",
                left=(100, "pt"),
                top=(100, "pt"),
                width=(100, "pt"),
                height=(100, "pt"),
            )
        )
        .build()
    )
    presentation.save(Path(__file__).with_suffix(".pptx"))

    # Get and display the tree structure
    with open(Path(__file__).with_suffix(".json"), "w") as f:
        json.dump(
            presentation.tree,
            f,
            indent=2,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
