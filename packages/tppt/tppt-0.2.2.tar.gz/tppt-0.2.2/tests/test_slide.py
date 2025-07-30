"""Tests for slide module."""

import pytest

import tppt
import tppt.pptx.slide
from tppt.pptx.shape.placeholder import LayoutPlaceholder, SlidePlaceholder
from tppt.pptx.slide_layout import SlideLayout as PptxSlideLayout


@pytest.mark.skip(reason="This test is not implemented yet.")
def test_slide_placeholders() -> None:
    """Test getting placeholders from a slide."""
    # Create a presentation with a slide
    presentation = (
        tppt.Presentation.builder().slide(lambda slide: slide.BlankLayout()).build()
    )

    # Get the slide from the presentation's pptx object
    pptx_presentation = presentation.to_pptx()
    if not pptx_presentation.slides:
        pytest.skip("No slides in presentation")

    slide = tppt.pptx.slide.Slide(pptx_presentation.slides[0])

    # Test that we can get placeholders
    placeholders = slide.placeholders

    # Check that placeholders is a list
    assert isinstance(placeholders, list)
    assert len(placeholders) != 0

    # Verify each placeholder is a SlidePlaceholder instance
    for placeholder in placeholders:
        assert isinstance(placeholder, SlidePlaceholder)

        # Check that we can convert it to pptx object
        pptx_placeholder = placeholder.to_pptx()
        assert pptx_placeholder is not None


def test_slide_layout_placeholders() -> None:
    """Test getting placeholders from a slide layout."""
    # Create a presentation
    presentation = tppt.Presentation.builder().build()

    # Get the slide layout from the presentation's pptx object
    pptx_presentation = presentation.to_pptx()
    if not pptx_presentation.slide_layouts:
        pytest.skip("No slide layouts in presentation")

    # Get the first slide layout
    slide_layout = PptxSlideLayout(pptx_presentation.slide_layouts[0])

    # Test that we can get placeholders
    placeholders = slide_layout.placeholders

    # Check that placeholders is a list
    assert isinstance(placeholders, list)
    assert len(placeholders) != 0

    # Verify each placeholder is a LayoutPlaceholder instance
    for placeholder in placeholders:
        assert isinstance(placeholder, LayoutPlaceholder)

        # Check that we can convert it to pptx object
        pptx_placeholder = placeholder.to_pptx()
        assert pptx_placeholder is not None
