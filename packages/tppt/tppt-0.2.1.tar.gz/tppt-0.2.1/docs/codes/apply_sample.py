import tppt


def format_text(
    text_obj: tppt.pptx.Text, text: str, *, bold: bool = False, italic: bool = False
) -> tppt.pptx.Text:
    paragraph = text_obj.text_frame.add_paragraph()
    run = paragraph.add_run()
    run.text = text
    font = run.font
    if bold:
        font.bold = True
    if italic:
        font.italic = True

    return text_obj


(
    tppt.Presentation.builder()
    .slide(
        lambda slide: slide.BlankLayout()
        .builder()
        .text(
            tppt.apply(format_text, "Hello, World!", bold=True, italic=True),
            left=(1, "in"),
            top=(1, "in"),
            width=(5, "in"),
            height=(2, "in"),
        )
    )
    .build()
    .save("simple.pptx")
)
