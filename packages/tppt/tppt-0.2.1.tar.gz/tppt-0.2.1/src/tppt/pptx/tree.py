from typing import Any, cast

from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.presentation import Presentation as PptxPresentation
from pptx.shapes.autoshape import Shape
from pptx.shapes.base import BaseShape
from pptx.shapes.graphfrm import GraphicFrame
from pptx.shapes.group import GroupShape
from pptx.slide import Slide


def color_format_to_dict(color_format: Any) -> dict[str, Any]:
    """Convert color format to dictionary"""
    data = {}

    try:
        if rgb := getattr(color_format, "rgb", None):
            data["rgb"] = str(rgb)

        if theme_color := getattr(color_format, "theme_color", None):
            data["theme_color"] = str(theme_color)

        if brightness := getattr(color_format, "brightness", None):
            data["brightness"] = brightness
    except Exception:
        pass

    return data


def text_frame_to_dict(text_frame: Any) -> dict[str, Any]:
    """Convert text frame to dictionary"""
    if not hasattr(text_frame, "paragraphs"):
        return {"text": str(text_frame) if text_frame else ""}

    result = {"text": text_frame.text, "paragraphs": []}

    for p in text_frame.paragraphs:
        paragraph = {"text": p.text, "level": p.level, "runs": []}

        for run in p.runs:
            run_data = {"text": run.text}

            if font := getattr(run, "font", None):
                font_data = {}
                if name := getattr(font, "name", None):
                    font_data["name"] = name
                if size := getattr(font, "size", None):
                    font_data["size"] = size.pt if hasattr(size, "pt") else size
                if bold := getattr(font, "bold", None):
                    font_data["bold"] = bold
                if italic := getattr(font, "italic", None):
                    font_data["italic"] = italic
                if underline := getattr(font, "underline", None):
                    font_data["underline"] = underline

                if color := getattr(font, "color", None):
                    font_data["color"] = color_format_to_dict(color)

                run_data["font"] = font_data

            paragraph["runs"].append(run_data)

        result["paragraphs"].append(paragraph)

    return result


def shape_to_dict(shape: BaseShape) -> dict[str, Any]:
    """Convert Shape object to dictionary"""
    shape_data = {
        "name": shape.name,
        "shape_id": shape.shape_id,
        "shape_type": str(shape.shape_type),
        "has_text_frame": shape.has_text_frame,
        "has_table": shape.has_table,
        "has_chart": shape.has_chart,
        "width": shape.width.pt if hasattr(shape.width, "pt") else shape.width,
        "height": shape.height.pt if hasattr(shape.height, "pt") else shape.height,
        "rotation": shape.rotation,
        "left": shape.left.pt if hasattr(shape.left, "pt") else shape.left,
        "top": shape.top.pt if hasattr(shape.top, "pt") else shape.top,
    }

    # In case of a placeholder
    if shape.shape_type == MSO_SHAPE_TYPE.PLACEHOLDER:
        try:
            shape_data["placeholder_type"] = (
                shape.placeholder_format.type
                if hasattr(shape.placeholder_format, "type")
                else None
            )
            shape_data["placeholder_idx"] = (
                shape.placeholder_format.idx
                if hasattr(shape.placeholder_format, "idx")
                else None
            )
        except Exception:
            pass

    # If there is a text frame
    if shape.has_text_frame:
        shape = cast(Shape, shape)
        shape_data["text_frame"] = text_frame_to_dict(shape.text_frame)

    # If there is a table
    if shape.has_table:
        shape = cast(GraphicFrame, shape)
        table_data = {
            "rows": len(shape.table.rows),
            "columns": len(shape.table.columns),
            "cells": [],
        }

        for row_idx in range(len(shape.table.rows)):
            for col_idx in range(len(shape.table.columns)):
                cell = shape.table.cell(row_idx, col_idx)
                cell_data = {
                    "row": row_idx,
                    "column": col_idx,
                    "text_frame": text_frame_to_dict(cell.text_frame),
                }
                table_data["cells"].append(cell_data)

        shape_data["table"] = table_data

    # In case of a group shape
    if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        shape = cast(GroupShape, shape)
        shape_data["shapes"] = [shape_to_dict(subshape) for subshape in shape.shapes]

    return shape_data


def placeholder_to_dict(placeholder: Any) -> dict[str, Any]:
    """Convert placeholder to dictionary"""
    placeholder_data = shape_to_dict(placeholder)

    # Add placeholder-specific information
    try:
        placeholder_data["placeholder_type"] = getattr(
            placeholder.placeholder_format, "type", None
        )
        placeholder_data["placeholder_idx"] = getattr(
            placeholder.placeholder_format, "idx", None
        )
    except Exception:
        pass

    return placeholder_data


def slide_layout_to_dict(slide_layout: Any) -> dict[str, Any]:
    """Convert slide layout to dictionary"""
    layout_data = {
        "name": slide_layout.name,
        "shapes": [shape_to_dict(shape) for shape in slide_layout.shapes],
        "placeholders": [
            placeholder_to_dict(placeholder)
            for placeholder in slide_layout.placeholders
        ],
    }

    return layout_data


def slide_master_to_dict(slide_master: Any) -> dict[str, Any]:
    """Convert slide master to dictionary"""
    master_data = {
        "shapes": [shape_to_dict(shape) for shape in slide_master.shapes],
        "placeholders": [
            placeholder_to_dict(placeholder)
            for placeholder in slide_master.placeholders
        ],
        "slide_layouts": [],
    }

    # Add slide layout information
    for layout in slide_master.slide_layouts:
        layout_dict = slide_layout_to_dict(layout)
        master_data["slide_layouts"].append(layout_dict)

    return master_data


def slide_to_dict(slide: Slide) -> dict[str, Any]:
    """Convert slide to dictionary"""
    slide_data = {
        "slide_id": slide.slide_id,
        "slide_layout_name": slide.slide_layout.name
        if hasattr(slide.slide_layout, "name")
        else None,
        "shapes": [shape_to_dict(shape) for shape in slide.shapes],
        "placeholders": [],
    }

    # Add placeholder information
    if placeholders := getattr(slide, "placeholders", None):
        slide_data["placeholders"] = [
            placeholder_to_dict(placeholder) for placeholder in placeholders
        ]

    # Add notes information
    if notes_slide := getattr(slide, "notes_slide", None):
        notes_placeholders = []
        if placeholders := getattr(notes_slide, "placeholders", None):
            notes_placeholders = [
                placeholder_to_dict(placeholder) for placeholder in placeholders
            ]

        slide_data["notes_slide"] = {
            "shapes": [shape_to_dict(shape) for shape in slide.notes_slide.shapes],
            "placeholders": notes_placeholders,
        }

    return slide_data


def ppt2tree(ppt: PptxPresentation) -> dict[str, Any]:
    """Convert presentation information to dictionary"""

    # Safely get the slide size
    slide_width = None
    slide_height = None

    if slide_width := ppt.slide_width:
        slide_width = slide_width.pt
    else:
        slide_width = None

    if slide_height := ppt.slide_height:
        slide_height = slide_height.pt
    else:
        slide_height = None

    prs_data = {
        "slides_count": len(ppt.slides),
        "slide_masters_count": len(ppt.slide_masters),
        "slide_layouts_count": len(ppt.slide_layouts),
        "slide_width": slide_width,
        "slide_height": slide_height,
        "slides": [slide_to_dict(slide) for slide in ppt.slides],
        "slide_masters": [slide_master_to_dict(master) for master in ppt.slide_masters],
    }

    # Add note master information
    if notes_master := getattr(ppt, "notes_master", None):
        notes_placeholders = []
        if placeholders := getattr(notes_master, "placeholders", None):
            notes_placeholders = [
                placeholder_to_dict(placeholder) for placeholder in placeholders
            ]

        prs_data["notes_master"] = {
            "shapes": [shape_to_dict(shape) for shape in ppt.notes_master.shapes],
            "placeholders": notes_placeholders,
        }

    return prs_data
