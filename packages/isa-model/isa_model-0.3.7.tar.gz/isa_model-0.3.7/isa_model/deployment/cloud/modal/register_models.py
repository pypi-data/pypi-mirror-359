 """
Model Registration Script for UI Analysis Pipeline

Registers the latest versions of UI analysis models in the core model registry
Prepares models for Modal deployment with proper version management
"""

import asyncio
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from isa_model.core.model_manager import ModelManager
from isa_model.core.model_repo import ModelRegistry, ModelType, ModelCapability

async def register_ui_analysis_models():
    """Register UI analysis models with latest versions"""
    
    # Initialize model manager and registry
    model_manager = ModelManager()
    
    print("🔧 Registering UI Analysis Models...")
    
    # Debug: Check available capabilities
    print("Available capabilities:")
    for cap in ModelCapability:
        print(f"  - {cap.name}: {cap.value}")
    print()
    
    # Model definitions with latest versions from HuggingFace
    models_to_register = [
        {
            "model_id": "omniparser-v2.0",
            "repo_id": "microsoft/OmniParser",
            "model_type": ModelType.VISION,
            "capabilities": [
                ModelCapability.UI_DETECTION,
                ModelCapability.IMAGE_ANALYSIS,
                ModelCapability.IMAGE_UNDERSTANDING
            ],
            "revision": "main",  # Latest version
            "metadata": {
                "description": "Microsoft OmniParser v2.0 - Advanced UI element detection",
                "provider": "microsoft",
                "model_family": "omniparser",
                "version": "2.0",
                "paper": "https://arxiv.org/abs/2408.00203",
                "huggingface_url": "https://huggingface.co/microsoft/OmniParser",
                "use_case": "UI element detection and parsing",
                "input_format": "image",
                "output_format": "structured_elements",
                "gpu_memory_mb": 8192,
                "inference_time_ms": 500
            }
        },
        {
            "model_id": "table-transformer-v1.1-detection",
            "repo_id": "microsoft/table-transformer-detection",
            "model_type": ModelType.VISION,
            "capabilities": [
                ModelCapability.TABLE_DETECTION,
                ModelCapability.IMAGE_ANALYSIS
            ],
            "revision": "main",
            "metadata": {
                "description": "Microsoft Table Transformer v1.1 - Table detection model",
                "provider": "microsoft",
                "model_family": "table-transformer",
                "version": "1.1",
                "paper": "https://arxiv.org/abs/2110.00061",
                "huggingface_url": "https://huggingface.co/microsoft/table-transformer-detection",
                "use_case": "Table detection in documents and images",
                "input_format": "image",
                "output_format": "bounding_boxes",
                "gpu_memory_mb": 4096,
                "inference_time_ms": 300
            }
        },
        {
            "model_id": "table-transformer-v1.1-structure",
            "repo_id": "microsoft/table-transformer-structure-recognition",
            "model_type": ModelType.VISION,
            "capabilities": [
                ModelCapability.TABLE_STRUCTURE_RECOGNITION,
                ModelCapability.IMAGE_ANALYSIS
            ],
            "revision": "main",
            "metadata": {
                "description": "Microsoft Table Transformer v1.1 - Table structure recognition",
                "provider": "microsoft",
                "model_family": "table-transformer",
                "version": "1.1",
                "paper": "https://arxiv.org/abs/2110.00061",
                "huggingface_url": "https://huggingface.co/microsoft/table-transformer-structure-recognition",
                "use_case": "Table structure recognition and cell extraction",
                "input_format": "image",
                "output_format": "table_structure",
                "gpu_memory_mb": 4096,
                "inference_time_ms": 400
            }
        },
        {
            "model_id": "paddleocr-v3.0",
            "repo_id": "PaddlePaddle/PaddleOCR",
            "model_type": ModelType.VISION,
            "capabilities": [
                ModelCapability.OCR,
                ModelCapability.IMAGE_ANALYSIS
            ],
            "revision": "release/2.8",
            "metadata": {
                "description": "PaddleOCR v3.0 - Multilingual OCR model",
                "provider": "paddlepaddle",
                "model_family": "paddleocr",
                "version": "3.0",
                "github_url": "https://github.com/PaddlePaddle/PaddleOCR",
                "huggingface_url": "https://huggingface.co/PaddlePaddle/PaddleOCR",
                "use_case": "Text extraction from images",
                "input_format": "image",
                "output_format": "text_with_coordinates",
                "languages": ["en", "ch", "multilingual"],
                "gpu_memory_mb": 2048,
                "inference_time_ms": 200
            }
        },
        {
            "model_id": "yolov8n-fallback",
            "repo_id": "ultralytics/yolov8",
            "model_type": ModelType.VISION,
            "capabilities": [
                ModelCapability.IMAGE_ANALYSIS,
                ModelCapability.UI_DETECTION  # As fallback
            ],
            "revision": "main",
            "metadata": {
                "description": "YOLOv8 Nano - Fallback object detection model",
                "provider": "ultralytics",
                "model_family": "yolo",
                "version": "8.0",
                "github_url": "https://github.com/ultralytics/ultralytics",
                "use_case": "General object detection (fallback for UI elements)",
                "input_format": "image",
                "output_format": "bounding_boxes",
                "gpu_memory_mb": 1024,
                "inference_time_ms": 50
            }
        }
    ]
    
    # Register each model
    registration_results = []
    
    for model_config in models_to_register:
        print(f"\n📝 Registering {model_config['model_id']}...")
        
        try:
            # Register model in registry (without downloading)
            success = model_manager.registry.register_model(
                model_id=model_config['model_id'],
                model_type=model_config['model_type'],
                capabilities=model_config['capabilities'],
                metadata={
                    **model_config['metadata'],
                    'repo_id': model_config['repo_id'],
                    'revision': model_config['revision'],
                    'registered_at': 'auto',
                    'download_status': 'not_downloaded'
                }
            )
            
            if success:
                print(f"✅ Successfully registered {model_config['model_id']}")
                registration_results.append({
                    'model_id': model_config['model_id'],
                    'status': 'success'
                })
            else:
                print(f"❌ Failed to register {model_config['model_id']}")
                registration_results.append({
                    'model_id': model_config['model_id'],
                    'status': 'failed'
                })
                
        except Exception as e:
            print(f"❌ Error registering {model_config['model_id']}: {e}")
            registration_results.append({
                'model_id': model_config['model_id'],
                'status': 'error',
                'error': str(e)
            })
    
    # Print summary
    print(f"\n📊 Registration Summary:")
    successful = [r for r in registration_results if r['status'] == 'success']
    failed = [r for r in registration_results if r['status'] != 'success']
    
    print(f"✅ Successfully registered: {len(successful)} models")
    for result in successful:
        print(f"   - {result['model_id']}")
    
    if failed:
        print(f"❌ Failed to register: {len(failed)} models")
        for result in failed:
            error_msg = f" ({result.get('error', 'unknown error')})" if 'error' in result else ""
            print(f"   - {result['model_id']}{error_msg}")
    
    return registration_results

async def verify_model_registry():
    """Verify registered models and their capabilities"""
    
    model_manager = ModelManager()
    
    print(f"\n🔍 Verifying Model Registry...")
    
    # Check models by capability
    capabilities_to_check = [
        ModelCapability.UI_DETECTION,
        ModelCapability.OCR,
        ModelCapability.TABLE_DETECTION,
        ModelCapability.TABLE_STRUCTURE_RECOGNITION
    ]
    
    for capability in capabilities_to_check:
        models = model_manager.registry.get_models_by_capability(capability)
        print(f"\n📋 Models with {capability.value} capability:")
        
        if models:
            for model_id, model_info in models.items():
                metadata = model_info.get('metadata', {})
                version = metadata.get('version', 'unknown')
                provider = metadata.get('provider', 'unknown')
                print(f"   ✅ {model_id} (v{version}, {provider})")
        else:
            print(f"   ❌ No models found for {capability.value}")
    
    # Print overall stats
    stats = model_manager.registry.get_stats()
    print(f"\n📈 Registry Statistics:")
    print(f"   Total models: {stats['total_models']}")
    print(f"   Models by type: {stats['models_by_type']}")
    print(f"   Models by capability: {stats['models_by_capability']}")

def get_model_for_capability(capability: ModelCapability) -> str:
    """Get the best model for a specific capability"""
    
    model_manager = ModelManager()
    models = model_manager.registry.get_models_by_capability(capability)
    
    if not models:
        return None
    
    # Priority order for UI analysis models
    priority_order = {
        ModelCapability.UI_DETECTION: [
            "omniparser-v2.0",
            "yolov8n-fallback"
        ],
        ModelCapability.OCR: [
            "paddleocr-v3.0"
        ],
        ModelCapability.TABLE_DETECTION: [
            "table-transformer-v1.1-detection"
        ],
        ModelCapability.TABLE_STRUCTURE_RECOGNITION: [
            "table-transformer-v1.1-structure"
        ]
    }
    
    preferred_models = priority_order.get(capability, [])
    
    # Return the first available preferred model
    for model_id in preferred_models:
        if model_id in models:
            return model_id
    
    # Fallback to first available model
    return list(models.keys())[0] if models else None

async def main():
    """Main registration workflow"""
    
    print("🚀 ISA Model Registry - UI Analysis Models Registration")
    print("=" * 60)
    
    try:
        # Register models
        results = await register_ui_analysis_models()
        
        # Verify registration
        await verify_model_registry()
        
        print(f"\n🎉 Model registration completed!")
        print(f"   Use ModelManager.get_model() to download and use models")
        print(f"   Use get_model_for_capability() to get recommended models")
        
        # Show usage example
        print(f"\n💡 Usage Example:")
        print(f"   from isa_model.core.model_manager import ModelManager")
        print(f"   from isa_model.core.model_repo import ModelCapability")
        print(f"   ")
        print(f"   manager = ModelManager()")
        print(f"   ui_model_path = await manager.get_model(")
        print(f"       model_id='omniparser-v2.0',")
        print(f"       repo_id='microsoft/OmniParser',")
        print(f"       model_type=ModelType.VISION,")
        print(f"       capabilities=[ModelCapability.UI_DETECTION]")
        print(f"   )")
        
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())