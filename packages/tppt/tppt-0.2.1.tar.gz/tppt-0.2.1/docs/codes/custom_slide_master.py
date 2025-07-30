import datetime

import tppt


class CustomTitleSlideLayout(tppt.SlideLayout):
    title: tppt.Placeholder[str]
    subtitle: tppt.Placeholder[str | None] = None
    date: tppt.Placeholder[datetime.date | None] = None
    footer: tppt.Placeholder[str | None] = None


class CustomTitleAndContentSlideLayout(tppt.SlideLayout):
    title: tppt.Placeholder[str]
    content: tppt.Placeholder[str]
    date: tppt.Placeholder[datetime.date | None] = None
    footer: tppt.Placeholder[str | None] = None


@tppt.slide_master("custom_slide_master_base.pptx")
class CustomSlideMaster(tppt.SlideMaster):
    TitleLayout: tppt.Layout[CustomTitleSlideLayout]
    TitleAndContentLayout: tppt.Layout[CustomTitleAndContentSlideLayout]


presentation = (
    tppt.Presentation.builder(CustomSlideMaster)
    .slide(
        lambda slide: slide.TitleLayout(
            title="Custom Master Title",
        )
    )
    .slide(
        lambda slide: slide.TitleAndContentLayout(
            title="Custom Title",
            content="Custom Content",
        )
        .builder()
        .text(
            "Custom Text",
            top=(1, "in"),
            left=(2, "in"),
            width=(3, "in"),
            height=(4, "in"),
        )
    )
    .build()
    .save("custom_slide_master.pptx")
)
