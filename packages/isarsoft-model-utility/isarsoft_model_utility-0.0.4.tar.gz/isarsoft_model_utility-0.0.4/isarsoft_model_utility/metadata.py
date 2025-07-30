"""
Metadata generation for RF-DETR models
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .config import METADATA_CONFIG
from .utils import generate_class_colors


logger = logging.getLogger(__name__)


class MetadataGenerator:
    """Generate JSON metadata for exported RF-DETR models"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.config = METADATA_CONFIG
    
    def create_metadata_json(
        self,
        model_name: str,
        class_names: List[str],
        model_metadata: Dict[str, Any],
        description: str = "RF-DETR object detection model",
        company_name: str = "Generated",
        anonymize_classes: List[int] = None,
        georeference_classes: List[int] = None,
        color_seed: int = None
    ) -> str:
        """Create metadata JSON file with class names and random colors"""
        
        logger.info(f"Generating metadata for {len(class_names)} classes...")
        
        # Generate random colors for classes
        class_colors = generate_class_colors(len(class_names), seed=color_seed)
        
        # Build metadata structure
        metadata = self._build_metadata(
            model_name=model_name,
            class_names=class_names,
            class_colors=class_colors,
            model_metadata=model_metadata,
            description=description,
            company_name=company_name,
            anonymize_classes=anonymize_classes or [],
            georeference_classes=georeference_classes or []
        )
        
        # Save JSON file
        json_path = self.output_dir / "config.json"
        with open(json_path, 'w') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        
        logger.info(f"✓ Generated metadata JSON: {json_path}")
        return str(json_path)
    
    def _build_metadata(
        self,
        model_name: str,
        class_names: List[str],
        class_colors: List[str],
        model_metadata: Dict[str, Any],
        description: str,
        company_name: str,
        anonymize_classes: List[int],
        georeference_classes: List[int]
    ) -> Dict[str, Any]:
        """Build the complete metadata structure"""
        
        timestamp = datetime.now().isoformat() + "Z"
        num_classes = len(class_names)
        
        # Generate model name based on classes
        if model_name is None:
            if num_classes == 1:
                model_name = class_names[0].upper()
            else:
                model_name = "MULTI_CLASS"
        
        out = {
            "schema_version": self.config.schema_version,
            "type": self.config.model_type,
            "version": self.config.version,
            "name": model_name,
            "description": description,
            "metadata": {
                "creator": company_name,
                "release_date": timestamp,
                "architecture": model_metadata.get("architecture", "RF-DETR"),
                "precision": model_metadata.get("precision", "fp16")
            },
            "classes": [
                {
                    "name": class_names[i],
                    "color": class_colors[i],
                    "icon": self.config.default_icon
                }
                for i in range(num_classes)
            ],

            "default_detection_classes": list(range(num_classes)),
            "default_tracking_groups": [],
            "default_anonymize_classes": anonymize_classes,
            "default_georeference_classes": georeference_classes,
            "default_belonging_pairs": [],
            "default_group_detection_classes": [],
        }
        if 'yolo' in model_name.lower():
            out.update({
            "maintain_aspect_ratio": True,
            "symmetric_padding": True,
            "padding_fill_color": self.config.padding_fill_color,
            "normalize_mean": [0., 0., 0.],
            "normalize_std": [1, 1, 1],
            "detection_threshold": {
                "default": 0.25,
                "low": self.config.low_threshold,
                "medium": self.config.medium_threshold,
                "high": self.config.high_threshold
            }
            })
        else:
            out.update({
            "maintain_aspect_ratio": self.config.maintain_aspect_ratio,
            "symmetric_padding": self.config.symmetric_padding,
            "padding_fill_color": self.config.padding_fill_color,
            "normalize_mean": self.config.normalize_mean,
            "normalize_std": self.config.normalize_std,
            "detection_threshold": {
                "default": self.config.default_threshold,
                "low": self.config.low_threshold,
                "medium": self.config.medium_threshold,
                "high": self.config.high_threshold
            }
            })
        return out