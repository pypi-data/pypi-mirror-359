"""Example of creating tables from Polars dataframe."""

from pathlib import Path

import tppt


def main():
    """Run the sample."""
    import polars as pl  # type: ignore

    # Create dataframe with Polars
    df = pl.DataFrame(
        {
            "Product": ["Product A", "Product B", "Product C", "Product D"],
            "Price": ["$10.00", "$25.00", "$32.00", "$18.00"],
            "Stock": ["10 units", "5 units", "8 units", "12 units"],
            "Rating": ["★★★★☆", "★★★☆☆", "★★★★★", "★★★☆☆"],
        }
    )

    # Convert dataframe to nested list
    columns = list(df.columns)
    rows = df.rows()
    table_data = [columns]

    for row in rows:
        table_data.append([str(item) for item in row])

    # Create presentation using builder pattern
    presentation = (
        tppt.Presentation.builder()
        .slide(
            lambda slide: slide.BlankLayout()
            .builder()
            .text(
                "Polars DataFrame Example",
                left=(50, "pt"),
                top=(50, "pt"),
                width=(500, "pt"),
                height=(50, "pt"),
                size=(44, "pt"),
                bold=True,
                color="#0066CC",
            )
            .text(
                "Easily convert Polars dataframes to presentations with tppt library",
                left=(50, "pt"),
                top=(120, "pt"),
                width=(500, "pt"),
                height=(30, "pt"),
            )
            .table(
                table_data,
                left=(50, "pt"),
                top=(100, "pt"),
                width=(500, "pt"),
                height=(200, "pt"),
            )
            .text(
                "Product list and inventory status created from a Polars dataframe",
                left=(50, "pt"),
                top=(320, "pt"),
                width=(500, "pt"),
                height=(50, "pt"),
            )
        )
        .build()
    )

    # Save the presentation
    presentation.save(Path(__file__).with_suffix(".pptx"))

    print("Successfully created presentation from Polars dataframe!")


if __name__ == "__main__":
    from tppt._features import USE_POLARS

    if USE_POLARS:
        main()
    else:
        tppt.Presentation.builder().slide(
            lambda slide: slide.BlankLayout()
            .builder()
            .text(
                "Polars is not installed. Please install it to run this example.",
                left=(50, "pt"),
                top=(50, "pt"),
                width=(500, "pt"),
                height=(50, "pt"),
            )
        ).build().save(Path(__file__).with_suffix(".pptx"))
