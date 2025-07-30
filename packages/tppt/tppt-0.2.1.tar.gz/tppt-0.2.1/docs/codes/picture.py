import tppt

(
    tppt.Presentation.builder()
    .slide(
        lambda slide: slide.BlankLayout()
        .builder()
        .picture(
            "your_image.png",
            left=(1, "in"),
            top=(1, "in"),
            width=(5, "in"),
            height=(2, "in"),
        )
    )
    .build()
    .save("simple.pptx")
)
