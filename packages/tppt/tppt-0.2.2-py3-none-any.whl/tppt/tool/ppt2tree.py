"""Tool to convert PowerPoint to tree structure JSON."""

import argparse
import json
import os
from pathlib import Path
from typing import Any

from pptx import Presentation as PptxPresentation

import tppt


def save_ppt_tree(
    pptx_path: tppt.types.FilePath,
    *,
    pretty: bool = False,
    output_path: tppt.types.FilePath | None = None,
) -> None:
    """Convert PPTX file to tree structure and save as JSON.

    Args:
        pptx_path: Path to the PPTX file
        output_path: Path to save the JSON file (default: same as PPTX with .json extension)
    """
    pptx_path = Path(pptx_path)

    if not pptx_path.exists():
        raise FileNotFoundError(f"PPTX file not found: {pptx_path}")

    # Load the presentation
    presentation = tppt.Presentation.from_pptx(PptxPresentation(os.fspath(pptx_path)))

    # Get the tree structure
    tree = presentation.tree

    options: dict[str, Any] = {"ensure_ascii": False}
    if pretty:
        options["indent"] = 2
        options["separators"] = (",", ":")
    else:
        options["indent"] = None
        options["separators"] = (",", ":")

    # Save to JSON file
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            print(json.dumps(tree, **options), file=f)
    else:
        print(json.dumps(tree, **options))


if __name__ == "__main__":
    try:
        from rich_argparse import RichHelpFormatter

        formatter_class = RichHelpFormatter
    except ImportError:
        formatter_class = argparse.HelpFormatter

    parser = argparse.ArgumentParser(
        description="Convert PPTX to tree structure JSON",
        formatter_class=formatter_class,
    )
    parser.add_argument("pptx_path", help="Path to the PPTX file")
    parser.add_argument(
        "-o", "--output", default=None, help="Path to save the JSON file"
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty print the JSON")

    args = parser.parse_args()

    save_ppt_tree(args.pptx_path, pretty=args.pretty, output_path=args.output)
