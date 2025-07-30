# Isarsoft Model Utility

A command-line utility for exporting object detection models to ONNX format for Isarsoft Perception, complete with metadata generation and optional packaging.

## Features

* Convert PyTorch `.pt` models (including pretrained defaults) to ONNX
* Embed metadata: class labels, model description, company attribution
* Options to anonymize or georeference specific classes
* Support for custom input image sizes
* Generate a thumbnail for frontend display (optional)
* Package outputs into a ZIP archive (optional)
* Verbose logging for debugging and audit trails

## Requirements

* Python 3.8 or later

## Installation

```bash
# Clone the repository
git clone https://gitlab.com/isarsoft/isarsoft-model-utility.git
cd isarsoft-model-utility

# Create a conda environment (recommended)
conda create -n isarsoft-export python=3.10 -y
conda activate isarsoft-export

# Install the package
pip install -e .
```

## Usage

```bash
isarsoft-export --model <MODEL_PATH> \
                --output <OUTPUT_DIR> \
                --classes <CLASS_LIST> 
                --model-name <YOLO11 | RFDETR >[options]
```

All flags and options are described below.

### Required Arguments

| Flag        | Shortcut | Description                                                   |
| ----------- | -------- | ------------------------------------------------------------- |
| `--model`   | `-m`     | Path to model file (`.pt`) or use `default` for pretrained   |
| `--output`  | `-o`     | Directory where exported files will be saved                  |
| `--classes` | `-c`     | Comma-separated list of class names (e.g., `person,car,bike`) |

### Optional Arguments

| Flag                     | Shortcut | Type    | Default                          | Description                                                 |
| ------------------------ | -------- | ------- | -------------------------------- | ----------------------------------------------------------- |
| `--model-name`           | `-n`     | String  | `rfdetr`                         | Model Name for the Frontend                                 |
| `--description`          | `-d`     | String  | `Object detection model` | Model description for metadata                              |
| `--company`              |          | String  | `Generated`                      | Company name for metadata                                   |
| `--anonymize-classes`    |          | String  | None                             | Comma-separated class indices to anonymize (e.g., `0,1`)    |
| `--georeference-classes` |          | String  | None                             | Comma-separated class indices to georeference (e.g., `2,3`) |
| `--imgsz`                |          | Integer | `560`                            | Input image size for export                                 |
| `--thumbnail`            |          | String  | None                             | Location of thumbnail for Frontend                          |
| `--no-zip`               |          | Flag    | Disabled                         | Skip creating zip package                                   |
| `--verbose`              | `-v`     | Flag    | Disabled                         | Enable verbose logging                                      |

### Examples

Basic export with class names:

```bash
isarsoft-export \
  --model model.pt \
  --output ./exported \
  --classes person,car,bike
  --model-name yolo11
```

Export with custom metadata and class options:

```bash
isarsoft-export \
  --model model.pt \
  --output ./exported \
  --classes person,vehicle,animal \
  --description "Multi-class detector" \
  --company "MyCompany" \
  --anonymize-classes 0 \
  --georeference-classes 1,2
  --model-name yolo11
```

Export with custom image size and thumbnail:

```bash
isarsoft-export \
  --model model.pt \
  --output ./exported \
  --classes person \
  --imgsz 640 \
  --thumbnail ./thumbnail.jpg
  --model-name yolo11
```

## Exit Codes

* `0` on successful export
* `1` on failure (errors are printed; use `--verbose` for traceback)

## Logging

Verbose mode (`--verbose`) outputs detailed logs to the console, including validation steps and stack traces on error.
