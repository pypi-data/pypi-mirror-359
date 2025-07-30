# 🎨 tppt

✨ **tppt** is a type-safe PowerPoint presentation builder that lets you create stunning presentations with Python code! 🐍

This library is a wrapper around the [python-pptx](https://github.com/scanny/python-pptx) library,
providing a more intuitive and type-safe interface for creating PowerPoint presentations.
It allows you to build presentations using a builder pattern,
making it easy to create slides with various layouts, text formatting, images, and tables.

## 🚀 Installation

```bash
pip install tppt
```

## 📚 Documentation

For detailed documentation, please visit [Documentation](https://yassun7010.github.io/tppt/).

## 🎯 Usage Examples

### 📝 Basic Presentation Creation

```python
import tppt

# Create a presentation using the builder pattern
presentation = (
    tppt.Presentation.builder()
    # Slide 1: Title and Text
    .slide(
        lambda slide: slide.TitleLayout(
            title="Amazing Presentation",
            subtitle="Example of using tppt library",
        )
    )
    # Slide 2: Text with Formatting
    .slide(
        lambda slide: slide.BlankLayout()
        .builder()
        .text(
            "Amazing Presentation",
            left=(50, "pt"),
            top=(50, "pt"),
            width=(400, "pt"),
            height=(50, "pt"),
            size=(60, "pt"),
            bold=True,
            italic=True,
            color="#0000FF",
        )
        .text(
            "Example of using tppt library",
            left=(50, "pt"),
            top=(120, "pt"),
            width=(400, "pt"),
            height=(30, "pt"),
        )
    )
    # Slide 3: Image
    .slide(
        lambda slide: slide.BlankLayout()
        .builder()
        .text(
            "Python Logo Example",
            left=(50, "pt"),
            top=(50, "pt"),
            width=(300, "pt"),
            height=(40, "pt"),
        )
        .picture(
            "python-logo.png",
            left=(50, "pt"),
            top=(100, "pt"),
            width=(300, "pt"),
            height=(80, "pt"),
        )
    )
    # Slide 4: Table
    .slide(
        lambda slide: slide.BlankLayout()
        .builder()
        .text(
            "Table Example",
            left=(50, "pt"),
            top=(50, "pt"),
            width=(300, "pt"),
            height=(40, "pt"),
        )
        .table(
            [
                ["Product", "Price", "Stock"],
                ["Product A", "$10.00", "10 units"],
                ["Product B", "$25.00", "5 units"],
            ],
            left=(50, "pt"),
            top=(100, "pt"),
            width=(400, "pt"),
            height=(200, "pt"),
        )
    )
    .build()
)

# Save the presentation
presentation.save("output.pptx")
```

## ✨ Features

- 🛡️ Type-safe interface with comprehensive type hints
- 🏗️ Intuitive API using the builder pattern
- 🎨 Flexible slide layouts (Title, Title and Content, Blank)
- 📝 Rich text formatting capabilities:
  - 🅰️ Font size, bold, italic
  - 🎨 Custom colors
  - 🎯 Advanced text formatting through custom functions
- 🖼️ Image support with precise positioning
- 📊 Table creation with customizable dimensions
- 📏 Fine-grained control over element positioning and sizing
- 🎭 Support for custom slide masters

## 📜 License

MIT
