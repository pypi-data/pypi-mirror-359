# Installation

TPPT can be installed using your favorite Python package manager.

## Requirements

- Python 3.11 or higher
- One of the following package managers:
    * [pip](https://pip.pypa.io/)
    * [uv](https://docs.astral.sh/uv/)
    * [hatch](https://hatch.pypa.io/)
    * [poetry](https://python-poetry.org/)

=== "pip"
    ```bash
    pip install tppt
    ```

=== "uv"
    ```bash
    uv add tppt
    ```

=== "hatch"
    ```bash
    hatch add tppt
    ```

=== "poetry"
    ```bash
    poetry add tppt
    ```

## Optional Dependencies

TPPT provides optional dependencies for additional features:

### Data Frame Support

For working with data frames:

=== "pip"
    ```bash
    # For pandas support
    pip install "tppt[pandas]"

    # For polars support
    pip install "tppt[polars]"
    ```

=== "uv"
    ```bash
    # For pandas support
    uv add "tppt[pandas]"

    # For polars support
    uv add "tppt[polars]"
    ```

=== "hatch"
    ```bash
    # For pandas support
    hatch add "tppt[pandas]"

    # For polars support
    hatch add "tppt[polars]"
    ```

=== "poetry"
    ```bash
    # For pandas support
    poetry add "tppt[pandas]"

    # For polars support
    poetry add "tppt[polars]"
    ```

### Pydantic Support

For Pydantic integration:

=== "pip"
    ```bash
    pip install "tppt[pydantic]"
    ```

=== "uv"
    ```bash
    uv add "tppt[pydantic]"
    ```

=== "hatch"
    ```bash
    hatch add "tppt[pydantic]"
    ```

=== "poetry"
    ```bash
    poetry add "tppt[pydantic]"
    ```

### Development Tools

For development purposes:

=== "pip"
    ```bash
    pip install "tppt[dev]"
    ```

=== "uv"
    ```bash
    uv add "tppt[dev]"
    ```

=== "hatch"
    ```bash
    hatch add "tppt[dev]"
    ```

=== "poetry"
    ```bash
    poetry add "tppt[dev]"
    ```

## Verifying Installation

You can verify the installation by running:

```python
--8<-- "codes/check-version.py"
``` 