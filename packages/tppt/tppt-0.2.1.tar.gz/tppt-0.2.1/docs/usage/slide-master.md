# Slide Master

## Custom Slide Master

You can create custom slide masters by defining your own layout classes. Here's an example of how to create and use a custom slide master:

```python
--8<-- "codes/custom_slide_master.py"
```

## Automatic Template Generation

You can automatically generate slide master and layout definitions from an existing PowerPoint file using the `ppt2template` tool:

```bash
python -m tppt.tool.ppt2template $YOUR_TEMPLATE.pptx -o $OUTPUT_FILE.py
```

This will analyze your PowerPoint file and generate:
- Custom layout classes for each slide layout
- A slide master class that uses these layouts
- Proper type hints for all placeholders

The generated code can be used directly in your project, saving you the effort of manually defining layouts and placeholders.

### Features of Generated Templates

- Automatically detects placeholder types (title, content, date, footer, etc.)
- Generates appropriate field names and types
- Handles special cases like multiple content placeholders
- Maintains the original layout structure
- Provides type safety through proper type hints
