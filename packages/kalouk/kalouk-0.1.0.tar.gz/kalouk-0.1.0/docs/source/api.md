# API Reference

This page contains the complete API reference for the Kalouk Python package.

## kalouk module

```{eval-rst}
.. automodule:: kalouk
   :members:
   :undoc-members:
   :show-inheritance:
```

## kalouk.dataset module

The main Dataset class for creating and managing dataset metadata.

```{eval-rst}
.. automodule:: kalouk.dataset
   :members:
   :undoc-members:
   :show-inheritance:
```

## Dataset Class Details

The `Dataset` class is the core component of the Kalouk package. It provides:

- **Metadata Management**: Store and organize dataset metadata using Schema.org properties
- **API Integration**: Send metadata directly to Kalouk's API endpoint
- **Type Safety**: Full type hints for better development experience

### Schema.org Properties

The Dataset class can store any metadata following the [Schema.org Dataset](https://schema.org/Dataset) specification. Common properties include:

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | The name of the dataset |
| `description` | string | A description of the dataset |
| `creator` | string/Person | The creator of the dataset |
| `dateCreated` | string/Date | When the dataset was created |
| `license` | string/URL | The license under which the dataset is distributed |
| `keywords` | string/array | Keywords or tags describing the dataset |
| `url` | string/URL | The URL where the dataset can be found |
| `distribution` | DataDownload | Information about how to download the dataset |

### Example Usage

```python
from kalouk import Dataset

# Create a comprehensive dataset
dataset = Dataset()

# Basic metadata
dataset.set_metadata("name", "Climate Data 2024")
dataset.set_metadata("description", "Daily temperature and precipitation data")

# Creator information
dataset.set_metadata("creator", "Research Institute")
dataset.set_metadata("dateCreated", "2024-12-01")

# Licensing and access
dataset.set_metadata("license", "https://creativecommons.org/licenses/by/4.0/")
dataset.set_metadata("keywords", ["climate", "temperature", "precipitation"])

# Send to Kalouk
response = dataset.send_to_kalouk()
if response.status_code == 200:
    print("Dataset metadata successfully sent!")
else:
    print(f"Error: {response.status_code}")
```
