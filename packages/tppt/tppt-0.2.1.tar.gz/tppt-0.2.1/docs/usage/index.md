The `tppt.Presentation` class is a wrapper for the `pttx.Presentation` class and can be easily wrapped.

```python
--8<-- "codes/wrap_presentation.py"
```

However, the primary way to use tppt is through the builder.
By using the builder, you can create slides while utilizing slide masters and slide layouts in a type-safe manner.

```python
--8<-- "codes/quick_start.py"
```

Also, `tppt.Presentation` has a property called `tree`,
which is a dictionary representing the tree structure of the presentation.

```python
--8<-- "codes/pptx_tree.py"
```

It is used for automatic generation of slide master type definitions and can also be used to analyze how pptx files are structured.
