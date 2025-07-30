# Langvision: Vision LLMs with Efficient LoRA Fine-Tuning

<hr/>
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/langtrain-ai/langtrain/main/static/langvision-use-dark.png">
    <img alt="Langvision Logo" src="https://raw.githubusercontent.com/langtrain-ai/langtrain/main/static/langvision-white.png" width="full" />
  </picture>
</p>

<!-- Badges -->
<p align="center">
  <a href="https://pypi.org/project/langvision/"><img src="https://img.shields.io/pypi/v/langvision.svg" alt="PyPI version"></a>
  <a href="https://pepy.tech/project/langvision"><img src="https://pepy.tech/badge/langvision" alt="Downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <a href="https://img.shields.io/badge/coverage-90%25-brightgreen" alt="Coverage"> <img src="https://img.shields.io/badge/coverage-90%25-brightgreen"/></a>
  <a href="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python Version"> <img src="https://img.shields.io/badge/python-3.8%2B-blue"/></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
</p>

<p align="center">
  <b>Langvision provides modular components for vision models and LoRA-based fine-tuning.</b><br/>
  <span style="font-size:1.1em"><i>Adapt and fine-tune vision models for a range of tasks.</i></span>
</p>
<hr/>

## Quick Links
- [Documentation](docs/index.md)
- [Tutorials](docs/tutorials/index.md)
- [Changelog](CHANGELOG.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)

---

## Table of Contents
- [Features](#features)
- [Showcase](#showcase)
- [Getting Started](#getting-started)
- [Supported Python Versions](#supported-python-versions)
- [Why langvision?](#why-langvision)
- [Architecture Overview](#architecture-overview)
- [Core Modules](#core-modules)
- [Performance & Efficiency](#performance--efficiency)
- [Advanced Configuration](#advanced-configuration)
- [Documentation & Resources](#documentation--resources)
- [Testing & Quality](#testing--quality)
- [Examples & Use Cases](#examples--use-cases)
- [Extending the Framework](#extending-the-framework)
- [Contributing](#contributing)
- [FAQ](#faq)
- [Citation](#citation)
- [Acknowledgements](#acknowledgements)
- [License](#license)

---

## Features
- LoRA adapters for parameter-efficient fine-tuning
- Modular Vision Transformer (ViT) backbone
- Model zoo for open-source visual models
- Configurable and extensible codebase
- Checkpointing and resume support
- Mixed precision and distributed training
- Built-in metrics and visualization tools
- CLI for fine-tuning and evaluation
- Extensible callbacks (early stopping, logging, etc.)

---

## Showcase

Langvision is a framework for building and fine-tuning vision models with LoRA support. It is suitable for tasks such as image classification, visual question answering, and custom vision applications.

---

## Getting Started

Install with pip:

```bash
pip install langvision
```

Minimal example:

```python
import torch
from langvision.models.vision_transformer import VisionTransformer
from langvision.utils.config import default_config

x = torch.randn(2, 3, 224, 224)
model = VisionTransformer(
    img_size=default_config['img_size'],
    patch_size=default_config['patch_size'],
    in_chans=default_config['in_chans'],
    num_classes=default_config['num_classes'],
    embed_dim=default_config['embed_dim'],
    depth=default_config['depth'],
    num_heads=default_config['num_heads'],
    mlp_ratio=default_config['mlp_ratio'],
    lora_config=default_config['lora'],
)

with torch.no_grad():
    out = model(x)
    print('Output shape:', out.shape)
```

For more details, see the [Documentation](docs/index.md) and [src/langvision/cli/finetune.py](src/langvision/cli/finetune.py).

---

## Supported Python Versions
- Python 3.8+

---

## Why langvision?

- Parameter-efficient fine-tuning with LoRA adapters
- Modular ViT backbone for flexible model design
- Unified interface for open-source vision models
- Designed for both research and production
- Efficient memory usage for large models

---

## Architecture Overview

Langvision uses a modular Vision Transformer backbone with LoRA adapters in attention and MLP layers. This allows adaptation of pre-trained models with fewer trainable parameters.

### Model Data Flow

```mermaid
---
config:
  layout: dagre
---
flowchart TD
 subgraph LoRA_Adapters["LoRA Adapters in Attention and MLP"]
        LA1(["LoRA Adapter 1"])
        LA2(["LoRA Adapter 2"])
        LA3(["LoRA Adapter N"])
  end
    A(["Input Image"]) --> B(["Patch Embedding"])
    B --> C(["CLS Token & Positional Encoding"])
    C --> D1(["Encoder Layer 1"])
    D1 --> D2(["Encoder Layer 2"])
    D2 --> D3(["Encoder Layer N"])
    D3 --> E(["LayerNorm"])
    E --> F(["MLP Head"])
    F --> G(["Output Class Logits"])
    LA1 -.-> D1
    LA2 -.-> D2
    LA3 -.-> D3
     LA1:::loraStyle
     LA2:::loraStyle
     LA3:::loraStyle
    classDef loraStyle fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
```

---

## Core Modules

| Module | Description | Key Features |
|--------|-------------|--------------|
| PatchEmbedding | Image-to-patch conversion and embedding | Configurable patch sizes, position embeddings |
| TransformerEncoder | Multi-layer transformer backbone | Self-attention, LoRA integration, checkpointing |
| LoRALinear | Low-rank adaptation layers | Configurable rank, memory-efficient updates |
| MLPHead | Output projection layer | Classification, regression, dropout |
| Config System | Centralized configuration | YAML/JSON config, CLI overrides |
| Data Utils | Preprocessing and augmentation | Built-in transforms, custom loaders |

---

## Performance & Efficiency

| Metric | Full Fine-tuning | LoRA Fine-tuning | Improvement |
|--------|------------------|------------------|-------------|
| Trainable Parameters | 86M | 2.4M | 97% reduction |
| Memory Usage | 12GB | 4GB | 67% reduction |
| Training Time | 4h | 1.5h | 62% faster |
| Storage per Task | 344MB | 9.6MB | 97% smaller |

*Benchmarks: ViT-Base, CIFAR-100, RTX 3090*

Supported model sizes: ViT-Tiny, ViT-Small, ViT-Base, ViT-Large

---

## Advanced Configuration

Example LoRA config:

```python
lora_config = {
    "rank": 16,
    "alpha": 32,
    "dropout": 0.1,
    "target_modules": ["attention.qkv", "attention.proj", "mlp.fc1", "mlp.fc2"],
    "merge_weights": False
}
```

Example training config:

```yaml
model:
  name: "vit_base"
  img_size: 224
  patch_size: 16
  num_classes: 1000
training:
  epochs: 10
  batch_size: 32
  learning_rate: 1e-4
  weight_decay: 0.01
  warmup_steps: 1000
lora:
  rank: 16
  alpha: 32
  dropout: 0.1
```

---

## Documentation & Resources
- [API Reference](docs/api/index.md)
- [Tutorials and Examples](docs/tutorials/index.md)
- [Research Papers](#research-papers)
- [Best Practices Guide](docs/best_practices.md)
- [Troubleshooting](docs/troubleshooting.md)

### Research Papers
- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929)
- [Vision Transformer for Fine-Grained Image Classification](https://arxiv.org/abs/2103.07579)

---

## Testing & Quality

Run tests:

```bash
pytest tests/
```

Code quality tools:

```bash
flake8 src/
black src/ --check
mypy src/
bandit -r src/
```

---

## Examples & Use Cases

Image classification:

```python
from langvision import VisionTransformer
from langvision.datasets import CIFAR10Dataset

model = VisionTransformer.from_pretrained("vit_base_patch16_224")
dataset = CIFAR10Dataset(train=True, transform=model.default_transform)
model.finetune(dataset, epochs=10, lora_rank=16)
```

Custom dataset:

```python
from langvision.datasets import ImageFolderDataset

dataset = ImageFolderDataset(
    root="/path/to/dataset",
    split="train",
    transform=model.default_transform
)
model.finetune(dataset, config_path="configs/custom_config.yaml")
```

---

## Extending the Framework
- Add datasets in `src/langvision/data/datasets.py`
- Add callbacks in `src/langvision/callbacks/`
- Add models in `src/langvision/models/`
- Add CLI tools in `src/langvision/cli/`

## Documentation
- See code comments and docstrings for details.
- For advanced usage, see `src/langvision/cli/finetune.py`.

## Contributing
We welcome contributions. See the [Contributing Guide](CONTRIBUTING.md) for details.

## License & Citation

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

If you use langvision in your research, please cite:

```bibtex
@software{langtrain2025,
  author = {Pritesh Raj},
  title = {langtrain: Vision LLMs with Efficient LoRA Fine-Tuning},
  url = {https://github.com/langtrain-ai/langvision},
  year = {2025},
  version = {1.0.0}
}
```

## Acknowledgements

We thank the following projects and communities:
- [PyTorch](https://pytorch.org/)
- [HuggingFace](https://huggingface.co/)
- [timm](https://github.com/rwightman/pytorch-image-models)
- [PEFT](https://github.com/huggingface/peft)

<p align="center">
  <b>Made in India 🇮🇳 with ❤️ by the langtrain team</b><br/>
  <i>Star ⭐ this repo if you find it useful!</i>
</p>