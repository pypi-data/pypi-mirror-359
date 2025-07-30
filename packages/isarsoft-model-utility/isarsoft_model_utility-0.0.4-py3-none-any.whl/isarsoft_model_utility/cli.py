#!/usr/bin/env python3
"""
Model Export Toolkit
Main entry point for exporting models to ONNX with metadata
"""

import argparse
import sys
from pathlib import Path


from .exporter import RFDETRExporter, UltralyticsExporter
from .utils import setup_logging, validate_inputs


def create_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Export RF-DETR models to ONNX with metadata generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic export with class names
  python main.py --model rf-detr-base.pt --output ./exported --classes person,car,bike --model-name rfdetr

  # Export with custom metadata
  python main.py --model model.pt --output ./exported \\
    --classes person,vehicle,animal \\
    --description "Multi-class detector" \\
    --company "MyCompany" \\
    --anonymize-classes 0 \\
    --georeference-classes 1,2 \\
    --model-name yolov11

  # Export with optimization options
  python main.py --model model.pt --output ./exported \\
    --classes person \\
    --half  --imgsz 640 \\
    --model-name yolov11
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--model', '-m',
        required=True,
        help='Path to model file (.pt) or use "default" for pretrained'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output directory for exported files'
    )
    
    parser.add_argument(
        '--classes', '-c',
        required=True,
        help='Comma-separated list of class names (e.g., "person,car,bike")'
    )
    
    parser.add_argument(
        '--model-name', '-n',
        default='yolov11',
        help='Model Name for the Frontend'
    )
    
    # Metadata options
    parser.add_argument(
        '--description', '-d',
        default='Object detection model',
        help='Model description for metadata'
    )
    
    parser.add_argument(
        '--company',
        default='Generated',
        help='Company name for metadata'
    )
    
    parser.add_argument(
        '--anonymize-classes',
        help='Comma-separated class indices to anonymize (e.g., "0,1")'
    )
    
    parser.add_argument(
        '--georeference-classes', 
        help='Comma-separated class indices to georeference (e.g., "2,3")'
    )
    
    # Export options
    parser.add_argument(
        '--imgsz',
        type=int,
        default=560,
        help='Input image size for export (default: 640)'
    )
    

    parser.add_argument(
        '--thumbnail',
        type=str,
        default=None,
        help='Location of thumbnail for Frontend'
    )

    # Output options
    parser.add_argument(
        '--no-zip',
        action='store_true',
        help='Skip creating zip package'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser


def parse_class_indices(indices_str):
    """Parse comma-separated class indices"""
    if not indices_str:
        return []
    try:
        return [int(x.strip()) for x in indices_str.split(',')]
    except ValueError:
        raise ValueError(f"Invalid class indices: {indices_str}")


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    try:
        # Validate inputs
        validate_inputs(args)
        
        # Parse class names and indices
        class_names = [name.strip() for name in args.classes.split(',')]
        anonymize_classes = parse_class_indices(args.anonymize_classes)
        georeference_classes = parse_class_indices(args.georeference_classes)
        
        print(f"🚀 Starting model export...")
        print(f"📋 Classes: {class_names}")
        print(f"📁 Output: {args.output}")
        
        if 'yolo' in args.model_name:
        # Create exporter and run export
            exporter = UltralyticsExporter(
                model_path=args.model,
                output_dir=args.output,
                model_name=args.model_name,
                class_names=class_names,
                description=args.description,
                company_name=args.company,
                anonymize_classes=anonymize_classes,
                georeference_classes=georeference_classes,
                thumbnail=args.thumbnail
            )
            
            result = exporter.export(
                imgsz=args.imgsz,
                create_zip=not args.no_zip,
            
            )
        else:
            exporter = RFDETRExporter(
                model_path=args.model,
                output_dir=args.output,
                model_name=args.model_name,
                class_names=class_names,
                description=args.description,
                company_name=args.company,
                anonymize_classes=anonymize_classes,
                georeference_classes=georeference_classes,
                thumbnail=args.thumbnail
            )
            
            result = exporter.export(
                imgsz=args.imgsz,
                create_zip=not args.no_zip,
            )
        
        print(f"\n🎉 Export completed successfully!")
        print(f"📁 Output: {result}")
        
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()