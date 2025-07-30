# Examples

Here are some examples of how to use TPPT in various scenarios. For detailed API reference, see [API Reference](api/tppt.md).

## Basic Presentation

```python
from tppt import Presentation

# Create a new presentation
presentation = Presentation()

# Add a title slide
slide = presentation.add_slide()
slide.add_title("My First Presentation")
slide.add_text("Created with TPPT")

# Add a content slide
slide = presentation.add_slide()
slide.add_title("Key Points")
slide.add_text("""
• Point 1
• Point 2
• Point 3
""")

# Save the presentation
presentation.save("basic_presentation.pptx")
```

## Working with Data

```python
import pandas as pd
from tppt import Presentation

# Create sample data
data = {
    "Month": ["Jan", "Feb", "Mar"],
    "Sales": [1000, 1200, 1500],
    "Growth": ["10%", "20%", "25%"]
}
df = pd.DataFrame(data)

# Create presentation
presentation = Presentation()

# Add title slide
slide = presentation.add_slide()
slide.add_title("Sales Report")
slide.add_text("Q1 2024")

# Add data slide
slide = presentation.add_slide()
slide.add_title("Sales Data")
slide.add_dataframe(df)

# Save the presentation
presentation.save("sales_report.pptx")
```

## Using Templates

```python
from tppt import Presentation

# Create presentation from template
presentation = Presentation.from_template("corporate_template.pptx")

# Add content to template slides
slide = presentation.add_slide()
slide.add_title("Project Overview")
slide.add_text("Project details go here")

# Add an image
slide = presentation.add_slide()
slide.add_title("Project Timeline")
slide.add_image("timeline.png")

# Save with template styling
presentation.save("project_presentation.pptx")
```

## Advanced Formatting

```python
from tppt import Presentation

presentation = Presentation()

# Create a slide with custom shapes
slide = presentation.add_slide()
slide.add_title("Custom Design")

# Add and style shapes
rect = slide.add_shape("rectangle", x=100, y=100, width=200, height=100)
rect.fill_color = "#FF0000"
rect.line_color = "#000000"
rect.line_width = 2

oval = slide.add_shape("oval", x=350, y=100, width=100, height=100)
oval.fill_color = "#0000FF"
oval.line_color = "#000000"
oval.line_width = 2

# Add text with custom formatting
text = slide.add_text("Custom Formatted Text")
text.font_name = "Arial"
text.font_size = 24
text.font_bold = True

presentation.save("advanced_formatting.pptx")
```

## Working with Tables

```python
from tppt import Presentation

presentation = Presentation()

# Create a slide with a table
slide = presentation.add_slide()
slide.add_title("Project Status")

# Define table data
data = [
    ["Project", "Status", "Completion"],
    ["Project A", "In Progress", "60%"],
    ["Project B", "Completed", "100%"],
    ["Project C", "Planning", "0%"]
]

# Add and format table
table = slide.add_table(data)

presentation.save("project_status.pptx")
```

These examples demonstrate some common use cases for TPPT. For more detailed information about specific features, please refer to the [API Reference](api/tppt.md). 