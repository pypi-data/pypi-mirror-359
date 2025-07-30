import tppt

(
    tppt.Presentation.builder()
    .slide(
        lambda slide: slide.BlankLayout()
        .builder()
        .table(
            [
                ["Price", "Name", "Quantity"],
                ["100", "Apple", "10"],
                ["200", "Banana", "20"],
            ],
            left=(1, "in"),
            top=(1, "in"),
            width=(5, "in"),
            height=(2, "in"),
        )
    )
    .build()
    .save("simple.pptx")
)
