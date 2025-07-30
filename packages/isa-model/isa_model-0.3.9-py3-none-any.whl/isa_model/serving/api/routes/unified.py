"""
Unified API Route - Single endpoint for all AI services

This is the main API that handles all types of AI requests:
- Vision tasks (image analysis, OCR, UI detection)
- Text tasks (chat, generation, translation) 
- Audio tasks (TTS, STT)
- Image generation tasks
- Embedding tasks
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union, List
import logging
import asyncio
import json
from pathlib import Path

from isa_model.client import ISAModelClient

logger = logging.getLogger(__name__)
router = APIRouter()

class UnifiedRequest(BaseModel):
    """Unified request model for all AI services"""
    input_data: Union[str, Dict[str, Any]] = Field(..., description="Input data (text, image URL, etc.)")
    task: str = Field(..., description="Task to perform (chat, analyze_image, generate_speech, etc.)")
    service_type: str = Field(..., description="Service type (text, vision, audio, image, embedding)")
    model_hint: Optional[str] = Field(None, description="Optional model preference")
    provider_hint: Optional[str] = Field(None, description="Optional provider preference")
    stream: Optional[bool] = Field(False, description="Enable streaming for text services")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional task parameters")

class UnifiedResponse(BaseModel):
    """Unified response model for all AI services"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any]

# Global ISA client instance for server-side processing
_isa_client = None

def get_isa_client():
    """Get or create ISA client for local processing"""
    global _isa_client
    if _isa_client is None:
        _isa_client = ISAModelClient(mode="local")  # Use local mode
    return _isa_client

@router.get("/")
async def unified_info():
    """API information"""
    return {
        "service": "unified_api",
        "status": "active",
        "description": "Single endpoint for all AI services",
        "supported_service_types": ["vision", "text", "audio", "image", "embedding"],
        "version": "1.0.0"
    }

@router.post("/invoke", response_model=UnifiedResponse)
async def unified_invoke(request: UnifiedRequest) -> UnifiedResponse:
    """
    **Unified API endpoint for all AI services**
    
    This single endpoint handles:
    - Vision: image analysis, OCR, UI detection
    - Text: chat, generation, translation
    - Audio: TTS, STT, transcription
    - Image: generation, img2img
    - Embedding: text embedding, similarity
    
    **Uses ISAModelClient in local mode - all the complex logic is in client.py**
    """
    try:
        # Get ISA client instance (local mode)
        client = get_isa_client()
        
        # Use client's local invoke method directly
        # This handles all the complexity: model selection, service routing, execution
        result = await client._invoke_local(
            input_data=request.input_data,
            task=request.task,
            service_type=request.service_type,
            model_hint=request.model_hint,
            provider_hint=request.provider_hint,
            **request.parameters
        )
        
        # Return the result in our API format
        return UnifiedResponse(
            success=result["success"],
            result=result.get("result"),
            error=result.get("error"),
            metadata=result["metadata"]
        )
        
    except Exception as e:
        logger.error(f"Unified invoke failed: {e}")
        return UnifiedResponse(
            success=False,
            error=str(e),
            metadata={
                "task": request.task,
                "service_type": request.service_type,
                "model_hint": request.model_hint,
                "provider_hint": request.provider_hint
            }
        )

@router.post("/stream")
async def unified_stream(request: UnifiedRequest):
    """
    **Unified streaming endpoint for text services**
    
    Returns Server-Sent Events (SSE) stream for real-time token generation.
    Only supports text service types.
    """
    try:
        # Validate streaming request
        if request.service_type != "text":
            raise HTTPException(status_code=400, detail="Streaming only supported for text services")
        
        # Get ISA client instance (local mode)
        client = get_isa_client()
        
        async def generate_stream():
            """Generator for SSE streaming"""
            try:
                # Use client's streaming method
                stream_gen = await client.invoke(
                    input_data=request.input_data,
                    task=request.task,
                    service_type=request.service_type,
                    model_hint=request.model_hint,
                    provider_hint=request.provider_hint,
                    stream=True,
                    **request.parameters
                )
                
                # Stream tokens as SSE format
                async for token in stream_gen:
                    # SSE format: "data: {json}\n\n"
                    token_data = {
                        "token": token,
                        "type": "token"
                    }
                    yield f"data: {json.dumps(token_data)}\n\n"
                
                # Send completion signal
                completion_data = {
                    "type": "completion",
                    "status": "finished"
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                error_data = {
                    "type": "error",
                    "error": str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        # Return SSE stream response
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except Exception as e:
        logger.error(f"Streaming setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invoke-file", response_model=UnifiedResponse)
async def unified_invoke_file(
    task: str = Form(...),
    service_type: str = Form(...),
    model_hint: Optional[str] = Form(None),
    provider_hint: Optional[str] = Form(None),
    file: UploadFile = File(...)
) -> UnifiedResponse:
    """
    Unified file upload endpoint
    
    For tasks that require file input (images, audio, documents)
    """
    try:
        # Read file data
        file_data = await file.read()
        
        # Get ISA client instance (local mode)
        client = get_isa_client()
        
        # Use client's local invoke method with binary data
        result = await client._invoke_local(
            input_data=file_data,  # Binary data
            task=task,
            service_type=service_type,
            model_hint=model_hint,
            provider_hint=provider_hint,
            filename=file.filename,
            content_type=file.content_type,
            file_size=len(file_data)
        )
        
        # Return the result in our API format
        return UnifiedResponse(
            success=result["success"],
            result=result.get("result"),
            error=result.get("error"),
            metadata={
                **result["metadata"],
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": len(file_data)
            }
        )
        
    except Exception as e:
        logger.error(f"File invoke failed: {e}")
        return UnifiedResponse(
            success=False,
            error=str(e),
            metadata={
                "task": task,
                "service_type": service_type,
                "filename": file.filename if file else None
            }
        )

@router.get("/models")
async def get_available_models(service_type: Optional[str] = None):
    """Get available models (optional filter by service type)"""
    try:
        client = get_isa_client()
        return await client.get_available_models(service_type)
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        # Fallback static model list
        return {
            "models": [
                {"service_type": "vision", "provider": "openai", "model_id": "gpt-4.1-mini"},
                {"service_type": "text", "provider": "openai", "model_id": "gpt-4.1-mini"},
                {"service_type": "audio", "provider": "openai", "model_id": "whisper-1"},
                {"service_type": "audio", "provider": "openai", "model_id": "tts-1"},
                {"service_type": "embedding", "provider": "openai", "model_id": "text-embedding-3-small"},
                {"service_type": "image", "provider": "replicate", "model_id": "black-forest-labs/flux-schnell"}
            ]
        }

@router.get("/health")
async def health_check():
    """Health check for unified API"""
    try:
        client = get_isa_client()
        health_result = await client.health_check()
        return {
            "api": "healthy",
            "client_health": health_result
        }
    except Exception as e:
        return {
            "api": "error",
            "error": str(e)
        }