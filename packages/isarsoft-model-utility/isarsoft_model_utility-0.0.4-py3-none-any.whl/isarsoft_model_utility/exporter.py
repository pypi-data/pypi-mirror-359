"""
RF-DETR model exporter with ONNX conversion and metadata generation
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import subprocess
from .metadata import MetadataGenerator
from .config import EXPORT_CONFIG
from .utils import ensure_directory, create_zip_package


logger = logging.getLogger(__name__)


class RFDETRExporter:
    """RF-DETR model exporter with metadata generation"""
    
    def __init__(
        self,
        model_path: str,
        output_dir: str,
        model_name: str,
        class_names: List[str],
        description: str = "RF-DETR object detection model",
        company_name: str = "Generated",
        anonymize_classes: Optional[List[int]] = None,
        georeference_classes: Optional[List[int]] = None,
        thumbnail: Optional[str] = None
    ):
        self.model_path = model_path
        self.output_dir = ensure_directory(output_dir)
        self.model_name = model_name
        self.class_names = class_names
        self.description = description
        self.company_name = company_name
        self.anonymize_classes = anonymize_classes or []
        self.georeference_classes = georeference_classes or []
        self.thumbnail = thumbnail if thumbnail else os.path.join(os.path.dirname(os.path.abspath(__file__)),'thumbnail.svg')
        
        self.model = None
        self.onnx_path = None
        
        logger.info(f"Initialized RF-DETR exporter for {len(class_names)} classes")
    
    def load_model(self) -> None:
        """Load RF-DETR model"""
        try:
            # Try to import RF-DETR from vendor directory first
            try:
                from rfdetr import RFDETRBase
                logger.info("Using RF-DETR from vendor directory")
            except ImportError:
                # Fallback to installed package
                logger.info("Vendor RF-DETR not found, trying installed package...")
                try:
                    from rfdetr import RFDETRBase
                    logger.info("Using installed RF-DETR package")
                except ImportError:
                    raise ImportError(
                        "RF-DETR not found. Please ensure RF-DETR code is in vendor/ directory "
                        "or install with: pip install rfdetr[onnxexport]"
                    )
            
            # Load model
            if self.model_path == "default":
                logger.info("Loading default RF-DETR pretrained model")
                self.model = RFDETRBase()
            else:
                logger.info(f"Loading RF-DETR model from {self.model_path}")
                self.model = RFDETRBase(pretrain_weights=self.model_path)
            
            logger.info("✓ RF-DETR model loaded successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load RF-DETR model: {e}")
    
    def export_to_onnx(
        self,
        imgsz: int = 640,
        half: bool = True,
    ) -> str:
        """Export RF-DETR model to ONNX format"""
        try:
            logger.info(f"Exporting RF-DETR to ONNX (imgsz={imgsz}, half={half})...")
            
            
            try:
                # Export model (RF-DETR's export method)
                
                self.model.export(output_dir=self.output_dir, simplify=True)
                
                
                # Find exported ONNX file
                onnx_files = list(self.output_dir.glob("*.onnx"))
                if not onnx_files:
                    raise RuntimeError("ONNX export completed but no .onnx file found")
                
                # Use most recent if multiple files
                if len(onnx_files) > 1:
                    onnx_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    logger.warning(f"Multiple ONNX files found, using: {onnx_files[0].name}")
                
                # Rename to standard name
                target_path = self.output_dir / "model.onnx"
                if onnx_files[0] != target_path:
                    shutil.move(str(onnx_files[0]), str(target_path))
                
                self.onnx_path = str(target_path)
                
            except Exception as e:
                raise RuntimeError(f"Failed to export RF-DETR to ONNX: {e}")
            
            logger.info(f"✓ RF-DETR exported to ONNX: {self.onnx_path}")
            return self.onnx_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to export RF-DETR to ONNX: {e}")
    
    def get_model_metadata(self) -> Dict[str, Any]:
        """Extract metadata from RF-DETR model"""
        metadata = {
            "architecture": "RF-DETR", 
            "framework": "PyTorch",
            "num_classes": len(self.class_names),
            "precision": "fp16" if EXPORT_CONFIG.default_precision == "fp16" else "fp32",
            "input_size": EXPORT_CONFIG.default_imgsz
        }
        
        # Try to extract additional metadata from model
        try:
            if hasattr(self.model, 'model'):
                if hasattr(self.model.model, 'nc'):
                    detected_classes = self.model.model.nc
                    if detected_classes != len(self.class_names):
                        logger.warning(
                            f"Model has {detected_classes} classes but {len(self.class_names)} class names provided"
                        )
        except Exception as e:
            logger.debug(f"Could not extract detailed model metadata: {e}")
        
        return metadata
    
    def generate_metadata(self) -> str:
        """Generate metadata JSON file"""
        model_metadata = self.get_model_metadata()
        
        generator = MetadataGenerator(str(self.output_dir))
        json_path = generator.create_metadata_json(
            model_name=self.model_name,
            class_names=self.class_names,
            model_metadata=model_metadata,
            description=self.description,
            company_name=self.company_name,
            anonymize_classes=self.anonymize_classes,
            georeference_classes=self.georeference_classes,
            color_seed=42  # Fixed seed for reproducible colors
        )
        
        return json_path
    
    def export(
        self,
        imgsz: int = 640,
        half: bool = True,
        create_zip: bool = True
    ) -> str:
        """Complete export workflow"""
        
        # Load model
        self.load_model()
        
        # Export to ONNX
        onnx_path = self.export_to_onnx(imgsz=imgsz, half=half)
        
        onnx_path = _export_slim(onnx_path=onnx_path)

        # Generate metadata
        json_path = self.generate_metadata()
        
        thumbnail_path = _copy_thumbnail(self.thumbnail, self.output_dir)


        logger.info(f"✓ Export completed:")
        logger.info(f"  - ONNX model: {onnx_path}")
        logger.info(f"  - Metadata: {json_path}")
        logger.info(f"  - Thumbnail: {thumbnail_path}")
        
        # Create zip package if requested
        if create_zip:
            zip_path = create_zip_package(str(self.output_dir))
            logger.info(f"  - Package: {zip_path}")
            return zip_path
        
        return str(self.output_dir)

class UltralyticsExporter:
    """Ultralytics model exporter with metadata generation"""
    
    def __init__(
        self,
        model_path: str,
        output_dir: str,
        model_name: str,
        class_names: List[str],
        description: str = "Ultralytics object detection model",
        company_name: str = "Generated",
        anonymize_classes: Optional[List[int]] = None,
        georeference_classes: Optional[List[int]] = None,
        thumbnail: Optional[str] = None,
        task: str = "detect"  # detect, segment, pose, obb
    ):
        self.model_path = model_path
        self.output_dir = ensure_directory(output_dir)
        self.model_name = model_name
        self.class_names = class_names
        self.description = description
        self.company_name = company_name
        self.anonymize_classes = anonymize_classes or []
        self.georeference_classes = georeference_classes or []
        self.thumbnail = thumbnail if thumbnail else os.path.join(os.path.dirname(os.path.abspath(__file__)),'thumbnail.svg')
        self.task = task
        
        self.model = None
        self.onnx_path = None
        
        logger.info(f"Initialized Ultralytics exporter for {len(class_names)} classes ({task} task)")
    

    def load_model(self) -> None:
        """Load Ultralytics model from Ultralytics"""
        try:
            # Try to import YOLO from ultralytics
            try:
                from tensorrt_yolo.export import ModelExporter
                logger.info("Using TensorRT-YOLO package")
            except ImportError:
                raise ImportError(
                    "TensorRT-YOLO not found."
                )
            

            self.model = ModelExporter()

            
            # Load model
            if self.model_path == "default":
                # Load default pretrained model based on task
                model_name = 'yolov11'
                model_path = 'yolov11m.pt'
                logger.info(f"Loading default Ultralytics model: {model_name}")
                self.model.load(model_path, model_name)
            else:
                logger.info(f"Loading Ultralytics model from {self.model_path}")
                self.model.load(self.model_path, self.model_name)
            
            # Validate model task matches expected task
            if hasattr(self.model, 'task') and self.model.task != self.task:
                logger.warning(f"Model task '{self.model.task}' doesn't match expected '{self.task}'")
            
            logger.info("✓ Ultralytics model loaded successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load Ultralytics model: {e}")
    
    def export_to_onnx(
        self,
        imgsz: int = 640,
        half: bool = True,
        dynamic: bool = True,
        simplify: bool = False,
        opset: int = 12,
    ) -> str:
        """Export Ultralytics model to ONNX format"""
        try:
            logger.info(f"Exporting Ultralytics to ONNX (imgsz={imgsz}, half={half}, dynamic={dynamic})...")
            
            
            try:
                # Export model using ultralytics
                batch = -1 if dynamic else False
                # batch= -1 , max_boxes = 500, iou_thres = 0.5, conf_thres = 0.25
                self.model.register(batch, 500, 0.5, 0.25)
                
                self.model.export(self.output_dir, imgsz, opset, simplify)


                # Find exported ONNX file
                onnx_files = list(self.output_dir.glob("*.onnx"))[0]
                if not onnx_files:
                    raise RuntimeError("ONNX export completed but no .onnx file found")

                # Move to output directory with standard name
                target_path = self.output_dir / "model.onnx"
                if str(onnx_files) != str(target_path):
                    shutil.move(str(onnx_files), str(target_path))
                
                self.onnx_path = str(target_path)
                
            except Exception as e:
                raise RuntimeError(f"Failed to export Ultralytics to ONNX: {e}")
            
            logger.info(f"✓ Ultralytics exported to ONNX: {self.onnx_path}")
            return self.onnx_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to export Ultralytics to ONNX: {e}")
    
    def get_model_metadata(self, imgsz: int = 640, precision: str = "fp16") -> Dict[str, Any]:
        """Extract metadata from Ultralytics model"""
        metadata = {
            "architecture": f"Ultralytics",
            "framework": "PyTorch",
            "num_classes": len(self.class_names),
            "precision": "fp16" if EXPORT_CONFIG.default_precision == "fp16" else "fp32",
            "input_size": EXPORT_CONFIG.default_imgsz
        }
        
        
        return metadata
    
    def generate_metadata(self, imgsz: int = 640, precision: str = "fp16") -> str:
        """Generate metadata JSON file"""
        model_metadata = self.get_model_metadata(imgsz=imgsz, precision=precision)
        
        generator = MetadataGenerator(str(self.output_dir))
        json_path = generator.create_metadata_json(
            model_name=self.model_name,
            class_names=self.class_names,
            model_metadata=model_metadata,
            description=self.description,
            company_name=self.company_name,
            anonymize_classes=self.anonymize_classes,
            georeference_classes=self.georeference_classes,
            color_seed=42  # Fixed seed for reproducible colors
        )
        
        return json_path
    
    def export(
        self,
        imgsz: int = 640,
        half: bool = True,
        dynamic: bool = True,
        create_zip: bool = True
    ) -> str:
        """Complete export workflow"""
        
        # Load model
        self.load_model()
        
        # Export to ONNX (primary format)
        onnx_path = self.export_to_onnx(
            imgsz=imgsz, 
            half=half, 
            dynamic=dynamic,
        )
        
        # Apply ONNX optimizations
        onnx_path = _export_slim(onnx_path=onnx_path)

        # Generate metadata
        json_path = self.generate_metadata()
        
        # Copy thumbnail
        thumbnail_path = _copy_thumbnail(self.thumbnail, self.output_dir)

        logger.info(f"✓ Ultralytics export completed:")
        logger.info(f"  - ONNX model: {onnx_path}")
        logger.info(f"  - Metadata: {json_path}")
        logger.info(f"  - Thumbnail: {thumbnail_path}")
        
        
        # Create zip package if requested
        if create_zip:
            zip_path = create_zip_package(str(self.output_dir))
            logger.info(f"  - Package: {zip_path}")
            return zip_path
        
        return str(self.output_dir)
    
def _export_slim(onnx_path: str):
    try:
        result = subprocess.run(
            ["onnxslim", onnx_path, onnx_path],
            check=True,               # Raises CalledProcessError on non-zero exit
            capture_output=True,      # Capture stdout/stderr
            text=True                 # Decode bytes to str
        )
    except Exception as e:
        raise RuntimeError(f"Failed to slim RF-DETR ONNX: {e}")


    return onnx_path
    
def _copy_thumbnail(thumbnail:str, output_path:str):
    if '.svg' in os.path.basename(thumbnail):
        output_path = os.path.join(output_path , 'thumbnail.svg')
    elif '.png' in os.path.basename(thumbnail):
        output_path = os.path.join(output_path , 'thumbnail.png')
    elif '.jpg' in os.path.basename(thumbnail):
        output_path = os.path.join(output_path , 'thumbnail.jpg')
    else:
        raise RuntimeError(f'Unsupported thumbnail file format, use jpg, svg or png')
    
    shutil.copyfile(thumbnail, output_path)
