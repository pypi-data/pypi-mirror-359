# TPPT Concept

## Why TPPT?

In today's world where generative AI is becoming ubiquitous, many organizations still require reports to be submitted in PowerPoint (pptx) format.
(Or is it just us who are being left behind?)

TPPT is a powerful wrapper for [python-pptx](https://github.com/scanny/python-pptx) that brings type safety to slide masters and more.

We've designed it to be both intuitive and easy to use,
making your PowerPoint generation process safer and more efficient.

## Minimal Imports
Let's revisit the Quick Start example:
```python
--8<-- "codes/quick_start.py"
```

Notice how this code only requires a single import of TPPT.

With just this minimal import, you can create complete PowerPoint presentations.

This design choice is intentional - by requiring only the TPPT import,
we aim to improve the success rate of AI-generated code.

We achieve this through two key techniques:

### Simplified Unit Specification with Literals

Traditionally, specifying shape dimensions in PowerPoint would look like this:
```python
--8<-- "codes/quick_start_many_import.py"
```

With TPPT, you can write the same thing more concisely: `(1, "in")` instead of `tppt.types.Inches(1)`.

This Literal-based approach significantly reduces the number of imports needed.

While writing values is simplified, reading properties still gives you proper Inches objects,
allowing you to perform arithmetic operations and comparisons as needed.

### Smart Type Extraction

You'll notice places where we use lambda expressions like `lambda slide: slide...`.
This is a form of lazy evaluation - we extract the type at initialization time
and then build the element by applying operations to it.

The beauty of this approach is that instead of importing types and passing them as function arguments,
we extract and use types directly from within the function.

This not only reduces imports but also brings another advantage:
by extracting type operations into functions, you can easily create reusable components.

```python
--8<-- "codes/apply_sample.py"
```

You can create and reuse your own formatting functions like `format_text` with ease.

### Type Safety First
TPPT is designed primarily for users who create new slides based on slide masters.

If you've worked with python-pptx before, you know the struggle of adding type safety to slide masters.

TPPT solves this by allowing you to define types for slide masters using pydantic-like declarative type hints:

```python
--8<-- "codes/custom_slide_master.py"
```

Don't want to write type definitions manually? We've got you covered with a handy tool:

```bash
python -m tppt.tool.ppt2template $YOUR_TEMPLATE.pptx -o $OUTPUT_FILE.py
```

After setting up placeholders in your slide layout constructor,
you can easily add text, pictures, tables, and other elements.

And the best part? All these operations are fully type-safe!