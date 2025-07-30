import datetime
from pathlib import Path

import tppt


def main():
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
        .slide(lambda slide: slide.TitleLayout(title="Custom Master Title"))
        .slide(
            lambda slide: slide.TitleAndContentLayout(
                title="Custom Title",
                content="Custom Content",
            )
        )
        .build()
    )

    presentation.save(Path(__file__).with_suffix(".pptx"))


if __name__ == "__main__":
    main()
