"""
Configuration settings for RF-DETR export toolkit
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ExportConfig:
    """Configuration for model export"""
    default_imgsz: int = 560
    default_precision: str = "fp16"
    onnx_opset: int = 17
    simplify_onnx: bool = True


@dataclass
class MetadataConfig:
    """Configuration for metadata generation"""
    schema_version: int = 1
    model_type: str = "DetectionModel"
    version: int = 1
    default_icon: str = "Pending"
    
    # Preprocessing defaults
    maintain_aspect_ratio: bool = False
    symmetric_padding: bool = False
    padding_fill_color: List[int] = None
    normalize_mean: List[float] = None
    normalize_std: List[float] = None
    
    # Detection thresholds
    default_threshold: float = 0.5
    low_threshold: float = 0.25
    medium_threshold: float = 0.5
    high_threshold: float = 0.75
    
    def __post_init__(self):
        if self.padding_fill_color is None:
            self.padding_fill_color = [114, 114, 114]
        if self.normalize_mean is None:
            self.normalize_mean = [0.485, 0.456, 0.406]
        if self.normalize_std is None:
            self.normalize_std = [0.229, 0.224, 0.225]


# Global configuration instances
EXPORT_CONFIG = ExportConfig()
METADATA_CONFIG = MetadataConfig()