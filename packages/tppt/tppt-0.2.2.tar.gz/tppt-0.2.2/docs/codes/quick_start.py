import tppt

(
    tppt.Presentation.builder()
    .slide(
        lambda slide: slide.BlankLayout()
        .builder()
        .text(
            "Hello, World!",
            left=(1, "in"),
            top=(1, "in"),
            width=(5, "in"),
            height=(2, "in"),
        )
    )
    .build()
    .save("simple.pptx")
)
