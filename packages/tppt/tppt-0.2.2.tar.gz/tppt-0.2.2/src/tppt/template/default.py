import datetime
from typing import Literal

from tppt.types import FilePath

from .slide_layout import Placeholder, SlideLayout
from .slide_master import Layout, SlideMaster, slide_master


class DefaultTitleSlideLayout(SlideLayout):
    """Title slide layout."""

    title: Placeholder[str]
    subtitle: Placeholder[str | None] = None
    date: Placeholder[datetime.date | None] = None
    footer: Placeholder[str | None] = None
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


class DefaultTitleAndContentSlideLayout(SlideLayout):
    """Title and content slide layout."""

    title: Placeholder[str]
    content: Placeholder[str]
    date: Placeholder[datetime.date | None] = None
    footer: Placeholder[str | None] = None
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


class DefaultSectionHeaderSlideLayout(SlideLayout):
    """Section header slide layout."""

    title: Placeholder[str]
    text: Placeholder[str]
    date: Placeholder[datetime.date | None] = None
    footer: Placeholder[str | None] = None
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


class DefaultTwoContentSlideLayout(SlideLayout):
    """Two content slide layout."""

    title: Placeholder[str]
    left_content: Placeholder[str]
    right_content: Placeholder[str]
    date: Placeholder[datetime.date | None] = None
    footer: Placeholder[str | None] = None
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


class DefaultComparisonSlideLayout(SlideLayout):
    """Comparison slide layout."""

    title: Placeholder[str]
    left_title: Placeholder[str]
    left_content: Placeholder[str]
    right_title: Placeholder[str]
    right_content: Placeholder[str]
    date: Placeholder[datetime.date | None] = None
    footer: Placeholder[str | None] = None
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


class DefaultTitleOnlySlideLayout(SlideLayout):
    """Title only slide layout."""

    title: Placeholder[str]
    date: Placeholder[datetime.date | None] = None
    footer: Placeholder[str | None] = None
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


class DefaultBlankSlideLayout(SlideLayout):
    """Blank slide layout."""

    date: Placeholder[datetime.date | None] = None
    footer: Placeholder[str | None] = None
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


class DefaultContentWithCaptionSlideLayout(SlideLayout):
    """Content with caption slide layout."""

    title: Placeholder[str]
    content: Placeholder[str]
    date: Placeholder[datetime.date | None] = None
    footer: Placeholder[str | None] = None
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


class DefaultPictureWithCaptionSlideLayout(SlideLayout):
    """Picture with caption slide layout."""

    title: Placeholder[str]
    picture_path: Placeholder[FilePath]
    date: Placeholder[datetime.date | None] = None
    footer: Placeholder[str | None] = None
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


class DefaultTitleAndVerticalTextSlideLayout(SlideLayout):
    """Title and vertical text slide layout."""

    title: Placeholder[str]
    vertical_text: Placeholder[str]
    date: Placeholder[datetime.date | None] = None
    footer: Placeholder[str | None] = None
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


class DefaultVerticalTitleAndTextSlideLayout(SlideLayout):
    """Vertical title and text slide layout."""

    vertical_title: Placeholder[str]
    text: Placeholder[str]
    date: Placeholder[datetime.date | None]
    footer: Placeholder[str | None]
    slide_number: Placeholder[Literal["‹#›"] | int | None] = None


@slide_master("default")
class DefaultSlideMaster(SlideMaster):
    TitleLayout: Layout[DefaultTitleSlideLayout]
    TitleAndContentLayout: Layout[DefaultTitleAndContentSlideLayout]
    SectionHeaderLayout: Layout[DefaultSectionHeaderSlideLayout]
    TwoContentLayout: Layout[DefaultTwoContentSlideLayout]
    ComparisonLayout: Layout[DefaultComparisonSlideLayout]
    TitleOnlyLayout: Layout[DefaultTitleOnlySlideLayout]
    BlankLayout: Layout[DefaultBlankSlideLayout]
    ContentWithCaptionLayout: Layout[DefaultContentWithCaptionSlideLayout]
    PictureWithCaptionLayout: Layout[DefaultPictureWithCaptionSlideLayout]
    TitleAndVerticalTextLayout: Layout[DefaultTitleAndVerticalTextSlideLayout]
    VerticalTitleAndTextLayout: Layout[DefaultVerticalTitleAndTextSlideLayout]
