# Enhanced DICOM Generator

This tool generates sample DICOM studies with consistent patient demographics and comprehensive clinical metadata including institution information, referring physicians, laterality, and other commonly used DICOM fields.

## Features

- Generate multiple studies with multiple series and instances
- Support for various modalities (CT, MR, US, CR)
- Realistic patient demographics
- Institution and physician information
- Modality-specific configurations
- Consistent UIDs and references between files

## Requirements

- Python 3.6+
- DCMTK toolkit installed and available in PATH

## Installation

### System Requirements

First, install the DCMTK toolkit:
- **Linux**: `sudo apt-get install dcmtk`
- **macOS**: `brew install dcmtk`
- **Windows**: Download from [DCMTK website](https://dicom.offis.de/dcmtk.php.en) and add to PATH

### Install from PyPI

```bash
pip install dicom-maker
```

### Install from Source

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/dicom-maker.git
   cd dicom-maker
   ```

2. Install the package:
   ```
   pip install .
   ```

   For development mode:
   ```
   pip install -e .
   ```

## Usage

### Command Line Interface

After installation, you can use the command-line interface:

```bash
python dicom-maker.py --output-dir ./dicom-data --modality CT --body-part CHEST --num-studies 1 --num-series 3 --num-instances 5
```

### As a Python Module

```python
from dicom_maker import generate_dicom_data
from argparse import Namespace

# Create arguments
args = Namespace(
    output_dir="./dicom-data",
    modality="CT",
    body_part="CHEST",
    num_studies=1,
    num_series=3,
    num_instances=5
)

# Generate DICOM data
generate_dicom_data(args)
```

### Parameters

- `--output-dir`: Output directory for DICOM files
- `--modality`: DICOM modality (CT, MR, US, CR)
- `--body-part`: Body part examined
- `--num-studies`: Number of studies to generate (default: 1)
- `--num-series`: Number of series per study (default: 1)
- `--num-instances`: Number of instances per series (default: 1)

## Examples

Generate 2 CT studies of the chest, each with 3 series and 10 instances per series:

```bash
dicom-maker --output-dir ./chest-ct-studies --modality CT --body-part CHEST --num-studies 2 --num-series 3 --num-instances 10
```

Generate a single MR study of the brain with 5 series (potentially T1, T2, FLAIR, etc.):

```bash
dicom-maker --output-dir ./brain-mr-study --modality MR --body-part BRAIN --num-series 5
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.