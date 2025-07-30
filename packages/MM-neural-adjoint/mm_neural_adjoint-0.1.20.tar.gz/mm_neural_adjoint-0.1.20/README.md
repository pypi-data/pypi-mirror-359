# MM-Neural-Adjoint

[![PyPI version](https://badge.fury.io/py/MM-neural-adjoint.svg)](https://badge.fury.io/py/MM-neural-adjoint)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A Python package implementing neural adjoint methods for inverse design of metamaterials. This implementation is based on the work from [BDIMNNA (Benchmarking Deep Inverse Models over time, and the Neural-Adjoint method)](https://github.com/BensonRen/BDIMNNA), published in NeurIPS 2020 by Simiao Ren, Willie J. Padilla and Jordan Malof.

## Overview

MM-Neural-Adjoint provides a streamlined implementation of the Neural Adjoint (NA) method specifically optimized for metamaterial geometry prediction tasks. The package enables researchers and engineers to perform inverse design of metamaterials by predicting optimal geometric parameters from desired spectral responses.

## Key Features

- **Neural Adjoint Implementation**: Complete implementation of the NA method for inverse design
- **Multiple Model Architectures**: Support for both linear and convolutional neural network models
- **MLflow Integration**: Built-in experiment tracking and model management
- **Boundary Constraint Handling**: Automatic handling of geometric boundary constraints
- **GPU/CPU Support**: Compatible with CPU, Apple Silicon (M1/M2), and NVIDIA GPUs
- **Comprehensive Evaluation**: Tools for both forward prediction and inverse design evaluation

## Installation

### Basic Installation (CPU/Apple Silicon)
```bash
pip install MM-neural-adjoint
```

### Development Installation
```bash
git clone https://github.com/your-username/mm-neural-adjoint.git
cd mm-neural-adjoint
pip install -e .
```

## Core Classes

### NANetwork

The main class that implements the Neural Adjoint method for training and inference.

**Key Methods:**
- `train(epochs, train_loader, val_loader, save=False, progress_bar=None)`: Trains the neural network using the provided data loaders
- `evaluate_geometry(val_loader, save_dir='val_results/', back_prop_steps=300, show_progress=True)`: Evaluates inverse design performance on validation data
- `evaluate_one(target_spectra, back_prop_steps=300, num_geometry_eval=2048, save_top=None, show_inner_progress=True)`: Performs inverse design for a single target spectrum
- `predict_spectra(geometry, file_name=None)`: Forward prediction of spectra from geometry parameters
- `predict_geometry(spectra, file_name=None, save_top=1)`: Inverse prediction of geometry from spectrum parameters
- `save()`: Saves model parameters and training metadata
- `load(filepath)`: Loads a previously saved model

**Key Attributes:**
- `model`: The underlying neural network model
- `device`: Computation device (CPU/GPU)
- `best_validation_loss`: Best validation loss achieved during training
- `geometry_mean`, `geometry_lower_bound`, `geometry_upper_bound`: Geometry normalization parameters

### ConvModel

A convolutional neural network architecture for metamaterial design.

**Constructor Parameters:**
- `geometry`: Input geometry dimension
- `spectrum`: Output spectrum dimension
- `num_linear_layers`: Number of linear layers (default: 4)
- `num_conv_layers`: Number of convolutional layers (default: 3)
- `num_linear_neurons`: Number of neurons in linear layers (default: 1000)
- `num_conv_out_channel`: Number of output channels in conv layers (default: 4)

**Architecture:**
- Initial linear layers with batch normalization and ReLU activation
- Transposed convolutional layers for spectrum generation
- Final convolutional layer for output refinement

### LinModel

A fully connected neural network architecture for metamaterial design.

**Constructor Parameters:**
- `geometry`: Input geometry dimension
- `spectrum`: Output spectrum dimension
- `hidden_layers`: List of hidden layer sizes (default: [1000, 1000, 1000, 1000, 1000, 1000, 1000])

**Architecture:**
- Multiple fully connected layers with batch normalization
- ReLU activation functions
- Configurable hidden layer sizes

## MLflow Integration

The package includes comprehensive MLflow integration for experiment tracking:

### Features
- **Automatic Logging**: Training metrics, model parameters, and checkpoints
- **Experiment Organization**: Timestamped runs with custom experiment names
- **Model Checkpoints**: Automatic saving of best models
- **Custom Metrics**: Support for additional metric logging

### Usage
```bash
# Start MLflow UI
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

## Examples

For detailed usage examples and tutorials, see the [example notebook](examples/example.ipynb) in the `examples/` directory. The notebook demonstrates:

- Basic model initialization and training
- Inverse design evaluation
- MLflow experiment tracking
- Model saving and loading
- Performance analysis

## Requirements

- Python >= 3.10
- PyTorch >= 2.6.0
- NumPy >= 2.2.4
- Pandas >= 2.2.3
- tqdm >= 4.67.1
- MLflow >= 2.21.3
- scikit-learn >= 1.4.0

## Citation

If you use this package in your research, please cite the original BDIMNNA work:

```bibtex
@inproceedings{ren2020benchmarking,
  title={Benchmarking Deep Inverse Models over time, and the Neural-Adjoint method},
  author={Ren, Simiao and Padilla, Willie J and Malof, Jordan},
  booktitle={Advances in Neural Information Processing Systems},
  year={2020}
}
```

## Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This package is based on the Neural Adjoint implementation from the [BDIMNNA repository](https://github.com/BensonRen/BDIMNNA) by Benson Ren et al. We thank the original authors for their foundational work in developing and benchmarking the Neural Adjoint method.


