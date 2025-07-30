# XenTokenizer

A high-performance, multilingual tokenizer based on the Qwen architecture, optimized for handling diverse languages including Indian languages and Greek.

## Features

- 🚀 **High Performance**: Processes over 900k tokens/second on CPU
- 🌍 **Multilingual**: Supports 10+ Indian languages, English, and Greek
- 🔧 **Easy Integration**: Built on top of Hugging Face's `PreTrainedTokenizerFast`
- 🛠️ **Special Tokens**: Built-in support for chat, vision, and task-specific tokens

## Installation

```bash
# Basic installation
pip install xen-tokenizer

# With Azure support for processing parquet files
pip install xen-tokenizer[azure]

# For development
pip install xen-tokenizer[dev]
```

## Quick Start

```python
from xen_tokenizer import XenTokenizerFast

# Initialize the tokenizer
tokenizer = XenTokenizerFast(tokenizer_file="tokenizer.json")

# Tokenize text
text = "Hello, world! Γειά σας! नमस्ते!"
tokens = tokenizer.encode(text)
print(tokens)

# Decode back to text
decoded = tokenizer.decode(tokens)
print(decoded)
```

## Azure Integration

Process parquet files directly from Azure Blob Storage:

```python
from xen_tokenizer.processor import AzureParquetProcessor

processor = AzureParquetProcessor(
    connection_string="your_connection_string",
    container_name="your_container",
    input_prefix="raw_data/",
    output_prefix="processed_data/"
)

# Process all parquet files
processor.process_all()
```

## License

MIT
# XenTokeniser

<div align="center">
  <h1>XenTokeniser</h1>
  <p><strong>XenArcAI's High-Performance Tokenization Library</strong></p>
  
  > **IMPORTANT**: XenTokeniser is proprietary software developed exclusively for XenArcAI's internal use. 
  > Unauthorized use, distribution, or modification is strictly prohibited.

  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  [![License](https://img.shields.io/badge/License-Proprietary-blue)](LICENSE)
</div>

## Overview

XenTokeniser is a high-performance, enterprise-grade tokenization library optimized for XenArcAI's NLP pipelines. Built on top of the Qwen architecture, it delivers fast and efficient tokenization with minimal memory overhead.

### Key Features

- **High Performance**: Multi-threaded tokenization with optimized C++ bindings
- **Enterprise Ready**: Designed for large-scale, production-grade NLP workloads
- **Memory Efficient**: Smart batching and streaming support
- **Seamless Integration**: Compatible with Hugging Face Transformers ecosystem
- **Configurable**: Fine-grained control over tokenization parameters
- **Monitoring**: Built-in metrics and progress tracking

## Installation

### Prerequisites
- Python 3.8+
- PyTorch 1.8.0+
- Hugging Face Transformers 4.18.0+

### From XenArcAI's Private Repository

```bash
pip install --extra-index-url https://pypi.xenarc.ai/simple/ xen-tokenizer
```

### From Source (Development)

```bash
# Clone the repository (XenArcAI team members only)
git clone git@github.com:XenArcAI/XenTokeniser.git
cd XenTokeniser

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Verify installation
python -c "from xen_tokenizer import XenTokenizerFast; print('XenTokeniser successfully installed!')"

## Quick Start

### Basic Usage

```python
from xen_tokenizer import XenTokenizerFast

# Initialize with default configuration
tokenizer = XenTokenizerFast(tokenizer_file="path/to/tokenizer.json")

# Tokenize text
text = "XenTokeniser delivers enterprise-grade tokenization performance"
encoded = tokenizer.encode(text)
decoded = tokenizer.decode(encoded)

print(f"Tokens: {encoded}")
print(f"Decoded: {decoded}")
```

### Batch Processing

```python
# Process multiple texts efficiently
texts = ["First document...", "Second document..."]

# Get tokenized output with attention masks and token type ids
batch_encoding = tokenizer.batch_encode_plus(
    texts,
    padding=True,
    truncation=True,
    max_length=512,
    return_tensors="pt"  # Return PyTorch tensors
)
```

## Advanced Features

### Custom Tokenization

```python
from xen_tokenizer import TokenizerConfig

# Define custom tokenization parameters
config = TokenizerConfig(
    max_length=512,
    stride=128,
    pad_token="[PAD]",
    eos_token="</s>",
    bos_token="<s>",
    unk_token="[UNK]"
)

# Initialize with custom config
tokenizer = XenTokenizerFast(
    tokenizer_file="path/to/tokenizer.json",
    config=config
)
```

### Azure Data Processing

```python
from xen_tokenizer import AzureParquetProcessor

# Process Parquet files from Azure Blob Storage
processor = AzureParquetProcessor(
    connection_string="your_connection_string",
    container_name="your_container"
)

# Process and tokenize data in chunks
for batch in processor.process_files("data/*.parquet", batch_size=1000):
    # batch contains tokenized data
    process_batch(batch)
```

## Performance Optimization

### Multi-GPU Processing

```python
import torch
from torch.utils.data import DataLoader

# Enable multi-GPU processing
if torch.cuda.device_count() > 1:
    tokenizer.parallelize()

# Use with DataLoader
loader = DataLoader(dataset, batch_size=32, num_workers=4)
for batch in loader:
    encoded = tokenizer.batch_encode_plus(
        batch,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone git@github.com:XenArcAI/XenTokeniser.git
cd XenTokeniser

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=xen_tokenizer tests/
```

### Building the Package

```bash
# Build source distribution
python setup.py sdist

# Build wheel
python setup.py bdist_wheel
```

## Deployment

### Integration with XenArcAI Services

XenTokeniser is pre-configured to work seamlessly with XenArcAI's ML infrastructure. For deployment guidelines, refer to the internal documentation.

### Versioning

XenTokeniser follows [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for added functionality
- PATCH version for backward-compatible bug fixes

## Security

- All data processed by XenTokeniser remains on-premises
- No telemetry or external calls are made
- Regular security audits are performed

## Support

For technical support or questions, please contact:
- **Engineering Team**: eng@xenarc.ai
- **Security Issues**: security@xenarc.ai

## License

Copyright © 2025 XenArcAI. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, modification, public display, or public performance is strictly prohibited.
