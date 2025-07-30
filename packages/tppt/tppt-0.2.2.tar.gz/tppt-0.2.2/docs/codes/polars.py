import tppt
from tppt._features import USE_POLARS, PandasDataFrame

if USE_POLARS:
    df = PandasDataFrame(
        [
            {"Price": 100, "Name": "Apple", "Quantity": 10},
            {"Price": 200, "Name": "Banana", "Quantity": 20},
        ]
    )

    (
        tppt.Presentation.builder()
        .slide(
            lambda slide: slide.BlankLayout()
            .builder()
            .table(
                df,
                left=(1, "in"),
                top=(1, "in"),
                width=(5, "in"),
                height=(2, "in"),
            )
        )
        .build()
        .save("simple.pptx")
    )
