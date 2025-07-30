import tppt
from tppt.types import Inches

(
    tppt.Presentation.builder()
    .slide(
        lambda slide: slide.BlankLayout()
        .builder()
        .text(
            "Hello, World!",
            left=Inches(1),
            top=Inches(1),
            width=Inches(5),
            height=Inches(2),
        )
    )
    .build()
    .save("simple.pptx")
)
