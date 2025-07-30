
# Micro Kolmogorov–Arnold Network (MicroKAN)

This repository contains a minimal Python implementation of the Kolmogorov–Arnold Network (KAN) architecture, adapted for edge devices such as the Raspberry Pi. It eliminates non-essential dependencies of the original KAN implementations and targets constrained systems.

## Features

* Streamlined implementation requiring only PyTorch, NumPy, PyYAML, and tqdm.
* Verified on Raspberry Pi 3 Model B with Python 3.10.
* Removes heavy dependencies such as scikit-learn, pandas, matplotlib, and sympy.

## Test Setup

* Raspberry Pi 3 Model B (ARMv7)
* Bullseye OS
* Python 3.10
* PyTorch 1.13
* NumPy 1.23

## Installation

### System packages

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends \
    python3 python3-pip libblas3 libgomp1 libopenblas0 python3-typing-extensions libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libgdbm-dev lzma lzma-dev tcl-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev wget curl make build-essential openssl
```

### Python setup
See full tutorial at [samwestby](https://www.samwestby.com/tutorials/rpi-pyenv)

```bash
curl https://pyenv.run | bash
# ...
pyenv install 3.10.12
pyenv shell 3.10.12
```

### Python packages

```bash
python3.10 -m pip install \
    https://github.com/maxisoft/pytorch-arm/releases/download/v1.0.0/numpy-1.23.5-cp310-cp310-linux_armv7l.whl \
    https://github.com/maxisoft/pytorch-arm/releases/download/v1.0.0/torch-1.13.0a0+git7c98e70-cp310-cp310-linux_armv7l.whl \
    https://github.com/maxisoft/pytorch-arm/releases/download/v1.0.0/PyYAML-6.0-cp310-cp310-linux_armv7l.whl
python3.10 -m pip install tqdm
```

### MicroKAN

```bash
python3.10 -m pip install microkan
```

## Example Usage

The API is nearly identical to the original [pykan](https://github.com/KindXiaoming/pykan), except that auxiliary arguments related to file saving and verbose outputs have been removed. Refer to the original KAN documentation for detailed parameter options. Here is a working example of `microkan`:

```python
from microkan import *
import os

set_seed(0)

model = KAN(width=[2, 1, 1], grid=3, k=3, seed=1).speed(compile=False)

f = lambda x: torch.exp(torch.sin(torch.pi * x[:, [0]]) + x[:, [1]] ** 2)
dataset = create_dataset(f, n_var=2, train_num=10, test_num=5)

model.fit(dataset, opt="LBFGS", steps=10)

print(model(dataset["test_input"]))

os.makedirs("microkan", exist_ok=True)
model.saveckpt("microkan/example_model")

# Loading example
loaded = KAN.loadckpt("microkan/example_model")
print(loaded(dataset["test_input"]))
```

## Performance Timing

The table below reports mean inference times (± standard deviation) on a Raspberry Pi 3 Model B and an Intel Core i5-1235U, illustrating typical speed differences across varying KAN architectures.

Architecture            | Grid | k | RPI3 Time (ms)      | PC Time (ms) |
------------------------|------|---|---------------------|--------------|
[6, 80, 3]              | 9    | 1 | 19.5 ± 2.6          | 1.4 ± 0.4    |
[6, 40, 55, 75, 3]      | 5    | 2 | 98.6 ± 14.9         | 3.6 ± 1.0    |
[6, 55, 65, 3]          | 5    | 4 | 110.1 ± 13.2        | 3.6 ± 1.1    |
[6, 45, 3]              | 3    | 2 | 31.4 ± 4.4          | 1.2 ± 0.7    |
[6, 80, 75, 3]          | 3    | 4 | 116.1 ± 12.7        | 3.7 ± 1.0    |
[6, 100, 65, 90, 3]     | 3    | 2 | 113.6 ± 13.3        | 3.9 ± 1.1    |

## Other Platforms

This implementation may also operate on platforms beyond ARMv7, provided that compatible PyTorch builds are available for the target architecture. However, these configurations have not been tested, and functionality or performance is not verified outside the specified ARMv7 environment.


## Acknowledgments

* Based on [PyEnv](https://github.com/pyenv/pyenv) Python Version Manager.
* Original Kolmogorov–Arnold Network concept implemented in [pykan](https://github.com/KindXiaoming/pykan).
* ARM builds of PyTorch and dependencies courtesy of [maxisoft/pytorch-arm](https://github.com/maxisoft/pytorch-arm).
