# EPINF-NeuFlow

The pytorch implementation of the paper "EPINF: Efficient Physics Informed Fluid Flow Reconstruction With Spatial and
Temporal Priors"

## Environment Setup

### System Requirements

- System
  - Windows 11 + MSVC 2022 (Fully Tested)
  - Ubuntu 24.04.2 (Fully Tested)
- Python: 3.13
- PyTorch: 2.7.1 + CUDA 12.8

### Pip Packages

```shell
python -m pip install --upgrade pip setuptools wheel
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
python -m pip install lightning lightning[extra] dearpygui tyro matplotlib av huggingface_hub opencv-python phiflow
```

### Fully Fused-NNs - [tiny-cuda-nn](https://github.com/NVlabs/tiny-cuda-nn)

```shell
set TCNN_CUDA_ARCHITECTURES=86
python -m pip install git+https://github.com/NVlabs/tiny-cuda-nn/#subdirectory=bindings/torch
```

For Windows deployment, open `X64 Native Tools Command Prompt for VS 2022` then activate your python venv if any, and set `TCNN_CUDA_ARCHITECTURES` to your GPU architecture.

| GPU             | CUDA arch |
|-----------------|-----------|
| H100            | 90        |
| 40X0            | 89        |
| 30X0            | 86        |
| A100            | 80        |
| 20X0            | 75        |
| TITAN V / V100  | 70        |
| 10X0 / TITAN Xp | 61        |
| 9X0             | 52        |
| K80             | 37        |

### Native CUDA Extensions

#### freqencoder, gridencoder, raymarching, shencoder

```shell
python -m pip install ./cuda_extensions/freqencoder ./cuda_extensions/gridencoder ./cuda_extensions/raymarching ./cuda_extensions/shencoder
```

### Optional Packages

#### [triton-windows](https://github.com/woct0rdho/triton-windows) - Activate `torch.compile` for Windows

```shell
python -m pip install -U "triton-windows<3.3"
```

## Datasets

We provide two datasets for training and testing the model:

- the NeRF-Synthetic is available
  at [Hugging Face - nerf_synthetic](https://huggingface.co/datasets/XayahHina/nerf_synthetic).
- The PI-Neuflow dataset is available
  at [Hugging Face - PI-NeuFlow](https://huggingface.co/datasets/XayahHina/PI-NeuFlow).

ALL datasets are downloaded **_AUTOMATICALLY_** when running the training script.
