"""
Qwen2.5-VL-32B Table Data Extraction Service

Specialized service for table data extraction using Qwen2.5-VL-32B-Instruct-AWQ
"""

import modal
import torch
import base64
import io
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Any
import time
import json
import os
import logging

# Define Modal application
app = modal.App("qwen-vision-table")

# Download Qwen2.5-VL model
def download_qwen_model():
    """Download Qwen2.5-VL-32B-Instruct-AWQ model"""
    from huggingface_hub import snapshot_download
    
    print("📦 Downloading Qwen2.5-VL-32B-Instruct-AWQ...")
    os.makedirs("/models", exist_ok=True)
    
    try:
        snapshot_download(
            repo_id="Qwen/Qwen2.5-VL-32B-Instruct-AWQ",
            local_dir="/models/qwen2.5-vl-32b-awq",
            allow_patterns=["**/*.safetensors", "**/*.json", "**/*.py", "**/*.txt"],
            # Use auth token if needed for gated models
            # token=os.getenv("HF_TOKEN")
        )
        print("✅ Qwen2.5-VL-32B-Instruct-AWQ downloaded")
    except Exception as e:
        print(f"⚠️ Model download failed: {e}")
        raise
    
    print("📦 Model download completed")

# Define Modal container image with AWQ support
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        # Core AI libraries with AWQ support
        "torch>=2.1.0",
        "torchvision",
        "transformers>=4.37.0",
        "accelerate>=0.26.0",
        "autoawq>=0.2.0",  # AWQ quantization support
        "huggingface_hub",
        
        # Qwen-VL specific dependencies
        "qwen-vl-utils",  # If available
        "tiktoken",
        "einops",
        "timm",
        
        # Image processing
        "pillow>=10.0.1",
        "opencv-python-headless",
        "numpy>=1.24.3",
        
        # HTTP libraries
        "httpx>=0.26.0",
        "requests",
        
        # Utilities
        "pydantic>=2.0.0",
        "python-dotenv",
    ])
    .run_function(download_qwen_model)
    .env({
        "TRANSFORMERS_CACHE": "/models",
        "HF_HOME": "/models",
        "TORCH_HOME": "/models",
    })
)

# Table Extraction Service
@app.cls(
    gpu="A100",  # A100 recommended for 32B model, H100 if available
    image=image,
    memory=32768,  # 32GB RAM for 32B model
    timeout=3600,  # 1 hour timeout
    scaledown_window=60,   # 1 minute idle timeout
    min_containers=0,  # Scale to zero to save costs
    # secrets=[modal.Secret.from_name("huggingface-token")]  # If needed
)
class QwenTableExtractionService:
    """
    Table Data Extraction Service using Qwen2.5-VL-32B-Instruct-AWQ
    
    Provides high-accuracy table extraction from images
    """
        
    @modal.enter()
    def load_model(self):
        """Load Qwen2.5-VL model on container startup"""
        print("🚀 Loading Qwen2.5-VL-32B-Instruct-AWQ...")
        start_time = time.time()
        
        # Initialize attributes
        self.model = None
        self.processor = None
        self.logger = logging.getLogger(__name__)
        
        try:
            from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
            
            model_path = "Qwen/Qwen2.5-VL-32B-Instruct-AWQ"
            
            # Load processor
            print("📱 Loading processor...")
            self.processor = AutoProcessor.from_pretrained(
                model_path,
                trust_remote_code=True
            )
            
            # Load model with AWQ quantization
            print("🧠 Loading AWQ quantized model...")
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
                # AWQ specific settings
                use_safetensors=True,
            )
            
            # Try to import qwen-vl-utils
            try:
                from qwen_vl_utils import process_vision_info as qwen_process_vision_info
                print("✅ qwen-vl-utils imported successfully")
                # Use the official process_vision_info if available
                globals()['process_vision_info'] = qwen_process_vision_info
            except ImportError:
                print("⚠️ qwen-vl-utils not found, using custom implementation")
            
            # Set to evaluation mode
            self.model.eval()
            
            load_time = time.time() - start_time
            print(f"✅ Qwen2.5-VL model loaded in {load_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            raise
    
    @modal.method()
    def extract_table_data(
        self, 
        image_b64: str, 
        extraction_format: str = "markdown",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract table data from image
        
        Args:
            image_b64: Base64 encoded image
            extraction_format: Output format ("markdown", "json", "csv", "html")
            custom_prompt: Custom extraction prompt
            
        Returns:
            Extracted table data and metadata
        """
        start_time = time.time()
        
        try:
            # Decode image
            image = self._decode_image(image_b64)
            
            # Prepare prompt based on format
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = self._get_extraction_prompt(extraction_format)
            
            # Process inputs
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Prepare inputs for the model
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            inputs = inputs.to("cuda")
            
            # Generate response
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=2048,
                    do_sample=False,
                    temperature=0.0,  # Deterministic for table extraction
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # Decode response
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]
            
            processing_time = time.time() - start_time
            
            # Post-process extracted data
            processed_data = self._post_process_extraction(output_text, extraction_format)
            
            return {
                'success': True,
                'service': 'qwen-vision-table',
                'extracted_data': processed_data,
                'raw_output': output_text,
                'format': extraction_format,
                'processing_time': processing_time,
                'model_info': {
                    'model': 'Qwen2.5-VL-32B-Instruct-AWQ',
                    'gpu': 'A100',
                    'quantization': 'AWQ',
                    'container_id': os.environ.get('MODAL_TASK_ID', 'unknown')
                }
            }
            
        except Exception as e:
            self.logger.error(f"Table extraction failed: {e}")
            return {
                'success': False,
                'service': 'qwen-vision-table',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _get_extraction_prompt(self, format_type: str) -> str:
        """Get extraction prompt based on desired format"""
        base_prompt = "Please extract all the data from this table accurately."
        
        format_prompts = {
            "markdown": f"{base_prompt} Format the output as a markdown table with proper alignment.",
            "json": f"{base_prompt} Format the output as a JSON array where each row is an object with column headers as keys.",
            "csv": f"{base_prompt} Format the output as CSV with comma-separated values. Include headers in the first row.",
            "html": f"{base_prompt} Format the output as an HTML table with proper <table>, <tr>, <td>, and <th> tags.",
        }
        
        return format_prompts.get(format_type, base_prompt)
    
    def _post_process_extraction(self, raw_output: str, format_type: str) -> Dict[str, Any]:
        """Post-process extracted table data"""
        try:
            if format_type == "json":
                # Try to parse JSON
                import json
                try:
                    # Extract JSON from the output if it's wrapped in text
                    start_idx = raw_output.find('[')
                    end_idx = raw_output.rfind(']') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = raw_output[start_idx:end_idx]
                        parsed_data = json.loads(json_str)
                        return {"structured_data": parsed_data, "raw_text": raw_output}
                except json.JSONDecodeError:
                    pass
            
            elif format_type == "csv":
                # Parse CSV-like output
                lines = raw_output.strip().split('\n')
                csv_data = [line.split(',') for line in lines if line.strip()]
                return {"structured_data": csv_data, "raw_text": raw_output}
            
            # For markdown, html, or unparseable formats, return as text
            return {"structured_data": raw_output, "raw_text": raw_output}
            
        except Exception as e:
            self.logger.warning(f"Post-processing failed: {e}")
            return {"structured_data": raw_output, "raw_text": raw_output}
    
    @modal.method()
    def batch_extract_tables(self, images_b64: List[str], extraction_format: str = "markdown") -> Dict[str, Any]:
        """
        Extract tables from multiple images
        
        Args:
            images_b64: List of base64 encoded images
            extraction_format: Output format for all extractions
            
        Returns:
            Batch extraction results
        """
        start_time = time.time()
        results = []
        
        for i, image_b64 in enumerate(images_b64):
            try:
                result = self.extract_table_data(image_b64, extraction_format)
                result['image_index'] = i
                results.append(result)
            except Exception as e:
                results.append({
                    'success': False,
                    'image_index': i,
                    'error': str(e)
                })
        
        return {
            'success': True,
            'service': 'qwen-vision-table',
            'batch_results': results,
            'total_images': len(images_b64),
            'successful_extractions': sum(1 for r in results if r.get('success', False)),
            'total_processing_time': time.time() - start_time
        }
    
    @modal.method()
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'qwen-vision-table',
            'model': 'Qwen2.5-VL-32B-Instruct-AWQ',
            'model_loaded': self.model is not None,
            'processor_loaded': self.processor is not None,
            'timestamp': time.time(),
            'gpu': 'A100'
        }
    
    def _decode_image(self, image_b64: str) -> Image.Image:
        """Decode base64 image"""
        try:
            if image_b64.startswith('data:image'):
                image_b64 = image_b64.split(',')[1]
            
            image_data = base64.b64decode(image_b64)
            return Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception as e:
            raise ValueError(f"Failed to decode image: {e}")

# Helper function for vision processing
def process_vision_info(messages):
    """Process vision information from messages"""
    image_inputs = []
    video_inputs = []
    
    for message in messages:
        if isinstance(message.get("content"), list):
            for content in message["content"]:
                if content.get("type") == "image":
                    image_inputs.append(content["image"])
                elif content.get("type") == "video":
                    video_inputs.append(content["video"])
    
    return image_inputs, video_inputs

# Deployment script
@app.function()
def deploy_info():
    """Deployment information"""
    return {
        "service": "Qwen2.5-VL-32B Table Extraction",
        "model": "Qwen/Qwen2.5-VL-32B-Instruct-AWQ",
        "gpu_requirement": "A100 (minimum), H100 (recommended)",
        "memory_requirement": "32GB+",
        "deploy_command": "modal deploy qwen_table_extraction.py"
    }

# Auto-registration function
@app.function() 
async def register_service():
    """Auto-register this service in the model registry"""
    try:
        import sys
        from pathlib import Path
        
        # Add project root to path for imports
        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        try:
            from isa_model.core.model_manager import ModelManager
            from isa_model.core.model_repo import ModelType, ModelCapability
            from isa_model.core.service_registry import ServiceRegistry
            from isa_model.core.types import ServiceType, DeploymentPlatform, ServiceStatus, ResourceRequirements
            from isa_model.core.model_service import ModelService
        except ImportError:
            # Fallback if import fails in Modal environment
            print("⚠️ Could not import required modules - registration skipped")
            return {"success": False, "error": "Required modules not available"}
        
        # Use ModelManager to register this service
        model_manager = ModelManager()
        
        # 1. First register the underlying model (backward compatibility)
        model_success = model_manager.registry.register_model(
            model_id="qwen2.5-vl-32b-table-service",
            model_type=ModelType.VISION,
            capabilities=[
                ModelCapability.TABLE_DETECTION,
                ModelCapability.TABLE_STRUCTURE_RECOGNITION,
                ModelCapability.OCR,
                ModelCapability.IMAGE_ANALYSIS
            ],
            metadata={
                "description": "Qwen2.5-VL-32B table extraction service",
                "service_name": "qwen-vision-table",
                "service_type": "modal",
                "deployment_type": "modal",
                "endpoint": "https://qwen-vision-table.modal.run",
                "underlying_model": "Qwen/Qwen2.5-VL-32B-Instruct-AWQ",
                "gpu_requirement": "A100",
                "memory_mb": 32768,
                "auto_registered": True,
                "registered_by": "isa_vision_table_service.py",
                "is_service": True  # Mark this as a service, not a raw model
            }
        )
        
        # 2. Register as a deployed service in the ServiceRegistry (MaaS platform)
        service_success = False
        try:
            service_registry = ServiceRegistry(model_manager.registry)
            
            # Create ModelService instance
            service = ModelService(
                service_id="qwen-table-modal-001",
                service_name="isa_vision_table",
                model_id="qwen2.5-vl-32b-table-service",
                deployment_platform=DeploymentPlatform.MODAL,
                service_type=ServiceType.VISION,
                status=ServiceStatus.HEALTHY,
                inference_endpoint="https://qwen-vision-table.modal.run/extract_table_data",
                health_endpoint="https://qwen-vision-table.modal.run/health_check",
                capabilities=["table_detection", "table_structure_recognition", "ocr", "image_analysis"],
                resource_requirements=ResourceRequirements(
                    gpu_type="A100",
                    memory_mb=32768,
                    cpu_cores=8,
                    min_replicas=0,
                    max_replicas=3
                ),
                metadata={
                    "description": "Qwen2.5-VL-32B table extraction service",
                    "underlying_model": "Qwen/Qwen2.5-VL-32B-Instruct-AWQ",
                    "auto_scaling": True,
                    "scale_to_zero": True,
                    "platform": "modal",
                    "registered_by": "isa_vision_table_service.py"
                }
            )
            
            # Register in ServiceRegistry
            service_success = await service_registry.register_service(service)
            
            if service_success:
                print("✅ Service registered in MaaS platform ServiceRegistry")
            else:
                print("⚠️ ServiceRegistry registration failed")
                
        except Exception as e:
            print(f"⚠️ ServiceRegistry registration error: {e}")
        
        if model_success:
            print("✅ Model registry registration successful")
        else:
            print("⚠️ Model registry registration failed")
            
        overall_success = model_success and service_success
        return {
            "success": overall_success, 
            "model_registry": model_success,
            "service_registry": service_success
        }
        
    except Exception as e:
        print(f"❌ Auto-registration error: {e}")
        return {"success": False, "error": str(e)}

# Quick deployment function
@app.function()
def deploy_service():
    """Deploy this service instantly"""
    import subprocess
    
    print("🚀 Deploying Qwen2.5-VL Table Extraction Service...")
    try:
        # Get the current file path
        current_file = __file__
        
        # Run modal deploy command
        result = subprocess.run(
            ["modal", "deploy", current_file],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Deployment completed successfully!")
        print(f"📝 Output: {result.stdout}")
        return {"success": True, "output": result.stdout}
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print(f"📝 Error: {e.stderr}")
        return {"success": False, "error": str(e), "stderr": e.stderr}

if __name__ == "__main__":
    print("🚀 Qwen2.5-VL Table Extraction Service - Modal Deployment")
    print("Deploy with: modal deploy isa_vision_table_service.py")
    print("Or call: modal run isa_vision_table_service.py::deploy_service")
    print("Note: Requires A100 GPU and 32GB+ RAM for optimal performance")
    print("\n📝 Service will auto-register in model registry upon deployment")