# Enhanced DICOM Generator

This tool generates high-quality sample DICOM studies with realistic patient demographics, institution metadata, and consistent references for various modalities. It supports features to simulate clinical environments for testing and development purposes.

## Updated Features

- **Improved Study Generation**: Create multiple studies with interlinked series and instances.
- **Expanded Modality Support**: Includes CT, MR, US, CR, and new modalities as needed.
- **Realistic Metadata**: Utilize generated patient demographics, institution details, and physician information.
- **Modality-Specific Configurations**: Tailor configurations for modality-specific needs.
- **UID Management**: Consistent and reproducible DICOM UIDs across instances.

## Requirements

- Python 3.6+
- DCMTK toolkit installed and available in PATH

## Installation

### System Requirements for DCMTK

**Linux**:
```bash
sudo apt-get install dcmtk
```

**macOS**:
```bash
brew install dcmtk
```

**Windows**:
Download DCMTK from the [official website](https://dicom.offis.de/dcmtk.php.en) and add it to your system PATH.

### Install from PyPI

```bash
pip install dicom-maker
```

### Install from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/dicom-maker.git
   cd dicom-maker
   ```

2. Install the package:
   ```bash
   pip install .
   ```

   Install in development mode:
   ```bash
   pip install -e .
   ```

## Usage

### Command Line Interface

Run the following command to generate DICOM studies:

```bash
dicom-maker --output-dir ./dicom-data --modality CT --body-part CHEST --num-studies 1 --num-series 3 --num-instances 5
```

### Usage as a Python Module

You can import the package and use it as part of your Python code:

```python
from make_dicom.dicom_maker import generate_dicom_data
from argparse import Namespace

# Define arguments
args = Namespace(
    output_dir="./dicom-data",
    modality="CT",
    body_part="CHEST",
    num_studies=1,
    num_series=3,
    num_instances=5
)

# Generate DICOM datasets
generate_dicom_data(args)
```

### Accepted Parameters

| Parameter         | Description                                   | Default |
|--------------------|-----------------------------------------------|---------|
| `--output-dir`     | Directory where generated DICOM files go     | `./dicom-data` |
| `--modality`       | Modality for the DICOM files (e.g., CT, MR)  | `CT`    |
| `--body-part`      | Body part being examined                     | `CHEST` |
| `--num-studies`    | Number of studies to generate                | `1`     |
| `--num-series`     | Number of series per study                   | `1`     |
| `--num-instances`  | Number of instances per series               | `1`     |

---

## Examples

### Generate Multiple Studies

Generate 2 CT studies of the chest, each having 3 series and 10 instances:

```bash
dicom-maker --output-dir ./chest-ct-studies --modality CT --body-part CHEST --num-studies 2 --num-series 3 --num-instances 10
```

### Generate a Brain MR Study

Generate a single MR study of the brain with 5 series (e.g., T1, T2, FLAIR, etc.):

```bash
dicom-maker --output-dir ./brain-mr-study --modality MR --body-part BRAIN --num-series 5
```

---

## License

This project is released under the MIT License. See the `LICENSE` file for additional details.