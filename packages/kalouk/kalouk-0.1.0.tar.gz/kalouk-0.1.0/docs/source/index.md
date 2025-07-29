# Kalouk Python Package

Welcome to the Kalouk Python package documentation!

```{note}
Kalouk is a Python package that helps in creating metadata for datasets using Schema.org's Dataset type and sending it to Kalouk's API.
```

## Installation

Install Kalouk using your preferred package manager:

````{tab-set}

```{tab-item} uv
```bash
uv add kalouk
```

```{tab-item} pip
```bash
pip install kalouk
```

```{tab-item} conda
```bash
conda install -c conda-forge kalouk
```
````

## Quick Start

Here's how to get started with Kalouk:

```python
from kalouk import Dataset

# Create a new dataset
dataset = Dataset()

# Set metadata using Schema.org Dataset properties
dataset.set_metadata("name", "My Dataset")
dataset.set_metadata("description", "A sample dataset")
dataset.set_metadata("creator", "John Doe")
dataset.set_metadata("dateCreated", "2025-01-01")
dataset.set_metadata("license", "https://creativecommons.org/licenses/by/4.0/")

# Send to Kalouk's API
response = dataset.send_to_kalouk()
print(f"Status: {response.status_code}")
```

## Features

✅ **Schema.org Compliant**: Uses Schema.org's Dataset specification for metadata  
✅ **API Integration**: Direct integration with Kalouk's API  
✅ **Type Safety**: Full type hints and NumPy-style docstrings  
✅ **Well Documented**: Comprehensive documentation with examples  

## Table of Contents

```{toctree}
:maxdepth: 2
:caption: Documentation

api
```

## API Reference

For detailed API documentation, see the {doc}`api` page.

---

```{admonition} Need Help?
:class: tip

If you encounter any issues or have questions, please check our documentation or reach out to the community.
```
