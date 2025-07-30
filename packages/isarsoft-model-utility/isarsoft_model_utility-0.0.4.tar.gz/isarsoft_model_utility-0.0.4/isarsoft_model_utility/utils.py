"""
Utility functions for RF-DETR export toolkit
"""

import logging
import random
import os
import zipfile
from pathlib import Path
from typing import List


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


def validate_inputs(args):
    """Validate command line arguments"""
    # Validate model path (if not using default)
    if args.model != "default" and not Path(args.model).exists():
        raise ValueError(f"Model file not found: {args.model}")
    
    # Validate class names
    if not args.classes or not args.classes.strip():
        raise ValueError("Class names are required (--classes)")
    
    class_names = [name.strip() for name in args.classes.split(',')]
    if not all(name for name in class_names):
        raise ValueError("All class names must be non-empty")
    
    # Validate class indices if provided
    if args.anonymize_classes:
        indices = [int(x.strip()) for x in args.anonymize_classes.split(',')]
        if any(i >= len(class_names) or i < 0 for i in indices):
            raise ValueError("Anonymize class indices out of range")
    
    if args.georeference_classes:
        indices = [int(x.strip()) for x in args.georeference_classes.split(',')]
        if any(i >= len(class_names) or i < 0 for i in indices):
            raise ValueError("Georeference class indices out of range")


def generate_random_color() -> str:
    """Generate a random hex color"""
    return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}".upper()


def generate_class_colors(num_classes: int, seed: int = None) -> List[str]:
    """Generate random colors for classes"""
    if seed is not None:
        random.seed(seed)
    
    colors = []
    for _ in range(num_classes):
        colors.append(generate_random_color())
    
    return colors


def create_zip_package(output_dir: str) -> str:
    """Create zip package containing exported files"""
    output_path = Path(output_dir)
    zip_path = output_path.parent / f"{output_path.name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in output_path.glob('*'):
            if file_path.is_file():
                zipf.write(file_path, file_path.name)
    
    return str(zip_path)


def ensure_directory(directory: str) -> Path:
    """Ensure directory exists, create if needed"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path