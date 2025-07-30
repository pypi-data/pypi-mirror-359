#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ISA Model Client - Unified interface for all AI services
Provides intelligent model selection and simplified API
"""

import logging
import asyncio
from typing import Any, Dict, Optional, List, Union
from pathlib import Path
import aiohttp

from isa_model.inference.ai_factory import AIFactory

try:
    from isa_model.core.services.intelligent_model_selector import IntelligentModelSelector, get_model_selector
    INTELLIGENT_SELECTOR_AVAILABLE = True
except ImportError:
    IntelligentModelSelector = None
    get_model_selector = None
    INTELLIGENT_SELECTOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class ISAModelClient:
    """
    Unified ISA Model Client with intelligent model selection
    
    Usage:
        client = ISAModelClient()
        response = await client.invoke("image.jpg", "analyze_image", "vision")
        response = await client.invoke("Hello world", "generate_speech", "audio")
        response = await client.invoke("audio.mp3", "transcribe", "audio") 
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 mode: str = "local",
                 api_url: Optional[str] = None,
                 api_key: Optional[str] = None):
        """Initialize ISA Model Client
        
        Args:
            config: Optional configuration override
            mode: "local" for direct AI Factory, "api" for HTTP API calls
            api_url: API base URL (required if mode="api")
            api_key: API key for authentication (optional)
        """
        self.config = config or {}
        self.mode = mode
        self.api_url = api_url.rstrip('/') if api_url else None
        self.api_key = api_key
        
        # Setup HTTP headers for API mode
        if self.mode == "api":
            if not self.api_url:
                raise ValueError("api_url is required when mode='api'")
            
            self.headers = {
                "Content-Type": "application/json",
                "User-Agent": "ISA-Model-Client/1.0.0"
            }
            if self.api_key:
                self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Initialize AI Factory for local mode
        if self.mode == "local":
            self.ai_factory = AIFactory.get_instance()
        else:
            self.ai_factory = None
        
        # Initialize intelligent model selector
        self.model_selector = None
        if INTELLIGENT_SELECTOR_AVAILABLE:
            try:
                # Initialize asynchronously later
                self._model_selector_task = None
                logger.info("Intelligent model selector will be initialized on first use")
            except Exception as e:
                logger.warning(f"Failed to setup model selector: {e}")
        else:
            logger.info("Intelligent model selector not available, using default selection")
        
        # Cache for frequently used services
        self._service_cache: Dict[str, Any] = {}
        
        logger.info("ISA Model Client initialized")
    
    async def stream(
        self,
        input_data: Union[str, bytes, Path, Dict[str, Any]], 
        task: str, 
        service_type: str,
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None,
        **kwargs
    ):
        """
        Streaming invoke method that yields tokens in real-time
        
        Args:
            input_data: Input data (text for LLM streaming)
            task: Task to perform 
            service_type: Type of service (only "text" supports streaming)
            model_hint: Optional model preference
            provider_hint: Optional provider preference
            **kwargs: Additional parameters
            
        Yields:
            Individual tokens as they arrive from the model
            
        Example:
            async for token in client.stream("Hello world", "chat", "text"):
                print(token, end="", flush=True)
        """
        if service_type != "text":
            raise ValueError("Streaming is only supported for text/LLM services")
            
        try:
            if self.mode == "api":
                async for token in self._stream_api(input_data, task, service_type, model_hint, provider_hint, **kwargs):
                    yield token
            else:
                async for token in self._stream_local(input_data, task, service_type, model_hint, provider_hint, **kwargs):
                    yield token
        except Exception as e:
            logger.error(f"Failed to stream {task} on {service_type}: {e}")
            raise

    async def invoke(
        self, 
        input_data: Union[str, bytes, Path, Dict[str, Any]], 
        task: str, 
        service_type: str,
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None,
        stream: bool = False,
        tools: Optional[List[Any]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], object]:
        """
        Unified invoke method with intelligent model selection
        
        Args:
            input_data: Input data (image path, text, audio, etc.)
            task: Task to perform (analyze_image, generate_speech, transcribe, etc.)
            service_type: Type of service (vision, audio, text, image, embedding)
            model_hint: Optional model preference
            provider_hint: Optional provider preference
            stream: Enable streaming for text services (returns AsyncGenerator)
            tools: Optional list of tools for function calling (only for text services)
            **kwargs: Additional task-specific parameters
            
        Returns:
            If stream=False: Unified response dictionary with result and metadata
            If stream=True: AsyncGenerator yielding tokens (only for text services)
            
        Examples:
            # Vision tasks
            await client.invoke("image.jpg", "analyze_image", "vision")
            await client.invoke("screenshot.png", "detect_ui_elements", "vision")
            await client.invoke("document.pdf", "extract_table", "vision")
            
            # Audio tasks  
            await client.invoke("Hello world", "generate_speech", "audio")
            await client.invoke("audio.mp3", "transcribe", "audio")
            
            # Text tasks
            await client.invoke("Translate this text", "translate", "text")
            await client.invoke("What is AI?", "chat", "text")
            
            # Streaming text
            async for token in await client.invoke("Hello", "chat", "text", stream=True):
                print(token, end="", flush=True)
            
            # Text with tools
            await client.invoke("What's 5+3?", "chat", "text", tools=[calculator_function])
            
            # Streaming with tools
            async for token in await client.invoke("What's 5+3?", "chat", "text", stream=True, tools=[calculator_function]):
                print(token, end="")
            
            # Image generation
            await client.invoke("A beautiful sunset", "generate_image", "image")
            
            # Embedding
            await client.invoke("Text to embed", "create_embedding", "embedding")
        """
        try:
            # Handle streaming case
            if stream:
                if service_type != "text":
                    raise ValueError("Streaming is only supported for text services")
                
                if self.mode == "api":
                    return self._stream_api(
                        input_data=input_data,
                        task=task,
                        service_type=service_type,
                        model_hint=model_hint,
                        provider_hint=provider_hint,
                        tools=tools,
                        **kwargs
                    )
                else:
                    return self._stream_local(
                        input_data=input_data,
                        task=task,
                        service_type=service_type,
                        model_hint=model_hint,
                        provider_hint=provider_hint,
                        tools=tools,
                        **kwargs
                    )
            
            # Route to appropriate mode for non-streaming
            if self.mode == "api":
                return await self._invoke_api(
                    input_data=input_data,
                    task=task,
                    service_type=service_type,
                    model_hint=model_hint,
                    provider_hint=provider_hint,
                    tools=tools,
                    **kwargs
                )
            else:
                return await self._invoke_local(
                    input_data=input_data,
                    task=task,
                    service_type=service_type,
                    model_hint=model_hint,
                    provider_hint=provider_hint,
                    tools=tools,
                    **kwargs
                )
                
        except Exception as e:
            logger.error(f"Failed to invoke {task} on {service_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "task": task,
                    "service_type": service_type,
                    "input_type": type(input_data).__name__
                }
            }
    
    async def _select_model(
        self,
        input_data: Any,
        task: str,
        service_type: str, 
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Select the best model for the given task"""
        
        # If explicit hints provided, use them
        if model_hint and provider_hint:
            return {
                "model_id": model_hint,
                "provider": provider_hint, 
                "reason": "User specified"
            }
        
        # Use intelligent model selector if available
        if INTELLIGENT_SELECTOR_AVAILABLE:
            try:
                # Initialize model selector if not already done
                if self.model_selector is None:
                    self.model_selector = await get_model_selector(self.config)
                
                # Create selection request
                request = f"{task} for {service_type}"
                if isinstance(input_data, (str, Path)):
                    request += f" with input: {str(input_data)[:100]}"
                
                selection = await self.model_selector.select_model(
                    request=request,
                    service_type=service_type,
                    context={
                        "task": task,
                        "input_type": type(input_data).__name__,
                        "provider_hint": provider_hint,
                        "model_hint": model_hint
                    }
                )
                
                if selection["success"]:
                    return {
                        "model_id": selection["selected_model"]["model_id"],
                        "provider": selection["selected_model"]["provider"],
                        "reason": selection["selection_reason"]
                    }
                
            except Exception as e:
                logger.warning(f"Intelligent selection failed: {e}, using defaults")
        
        # Fallback to default model selection
        return self._get_default_model(service_type, task, provider_hint)
    
    def _get_default_model(
        self, 
        service_type: str, 
        task: str,
        provider_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get default model for service type and task"""
        
        defaults = {
            "vision": {
                "model_id": "gpt-4o-mini",
                "provider": "openai"
            },
            "audio": {
                "tts": {"model_id": "tts-1", "provider": "openai"},
                "stt": {"model_id": "whisper-1", "provider": "openai"},
                "default": {"model_id": "whisper-1", "provider": "openai"}
            },
            "text": {
                "model_id": "gpt-4.1-mini", 
                "provider": "openai"
            },
            "image": {
                "model_id": "black-forest-labs/flux-schnell",
                "provider": "replicate"
            },
            "embedding": {
                "model_id": "text-embedding-3-small",
                "provider": "openai"
            }
        }
        
        # Handle audio service type with task-specific models
        if service_type == "audio":
            if "speech" in task or "tts" in task:
                default = defaults["audio"]["tts"]
            elif "transcribe" in task or "stt" in task:
                default = defaults["audio"]["stt"] 
            else:
                default = defaults["audio"]["default"]
        else:
            default = defaults.get(service_type, defaults["vision"])
        
        # Apply provider hint if provided
        if provider_hint:
            default = dict(default)
            default["provider"] = provider_hint
        
        return {
            **default,
            "reason": "Default selection"
        }
    
    async def _get_service(
        self,
        service_type: str,
        model_name: str,
        provider: str,
        task: str,
        tools: Optional[List[Any]] = None
    ) -> Any:
        """Get appropriate service instance"""
        
        cache_key = f"{service_type}_{provider}_{model_name}"
        
        # Check cache first
        if cache_key in self._service_cache:
            service = self._service_cache[cache_key]
            # If tools are needed, bind them to the service
            if tools and service_type == "text":
                return service.bind_tools(tools)
            return service
        
        try:
            # Route to appropriate AIFactory method
            if service_type == "vision":
                service = self.ai_factory.get_vision(model_name, provider)
            
            elif service_type == "audio":
                if "speech" in task or "tts" in task:
                    service = self.ai_factory.get_tts(model_name, provider)
                elif "transcribe" in task or "stt" in task:
                    service = self.ai_factory.get_stt(model_name, provider)
                else:
                    # Default to STT for unknown audio tasks
                    service = self.ai_factory.get_stt(model_name, provider)
            
            elif service_type == "text":
                service = self.ai_factory.get_llm(model_name, provider)
            
            elif service_type == "image":
                service = self.ai_factory.get_img("t2i", model_name, provider)
            
            elif service_type == "embedding":
                service = self.ai_factory.get_embed(model_name, provider)
            
            else:
                raise ValueError(f"Unsupported service type: {service_type}")
            
            # Cache the service
            self._service_cache[cache_key] = service
            
            # If tools are needed, bind them to the service
            if tools and service_type == "text":
                return service.bind_tools(tools)
            
            return service
            
        except Exception as e:
            logger.error(f"Failed to get service {service_type}/{provider}/{model_name}: {e}")
            raise
    
    async def _execute_task(
        self,
        service: Any,
        input_data: Any,
        task: str,
        service_type: str,
        **kwargs
    ) -> Any:
        """Execute the task using the appropriate service"""
        
        try:
            if service_type == "vision":
                return await self._execute_vision_task(service, input_data, task, **kwargs)
            
            elif service_type == "audio":
                return await self._execute_audio_task(service, input_data, task, **kwargs)
            
            elif service_type == "text":
                return await self._execute_text_task(service, input_data, task, **kwargs)
            
            elif service_type == "image":
                return await self._execute_image_task(service, input_data, task, **kwargs)
            
            elif service_type == "embedding":
                return await self._execute_embedding_task(service, input_data, task, **kwargs)
            
            else:
                raise ValueError(f"Unsupported service type: {service_type}")
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise
    
    async def _execute_vision_task(self, service, input_data, task, **kwargs):
        """Execute vision-related tasks using unified invoke method"""
        
        # Map common task names to unified task names
        task_mapping = {
            "analyze_image": "analyze_image",
            "detect_ui_elements": "detect_ui", 
            "extract_table": "extract_table",
            "extract_text": "extract_text",
            "ocr": "extract_text",
            "describe": "analyze_image"
        }
        
        unified_task = task_mapping.get(task, task)
        
        # Use unified invoke method with proper parameters  
        return await service.invoke(
            image=input_data,
            task=unified_task,
            **kwargs
        )
    
    async def _execute_audio_task(self, service, input_data, task, **kwargs):
        """Execute audio-related tasks using unified invoke method"""
        
        # Map common task names to unified task names
        task_mapping = {
            "generate_speech": "synthesize",
            "text_to_speech": "synthesize", 
            "tts": "synthesize",
            "transcribe": "transcribe",
            "speech_to_text": "transcribe",
            "stt": "transcribe",
            "translate": "translate",
            "detect_language": "detect_language"
        }
        
        unified_task = task_mapping.get(task, task)
        
        # Use unified invoke method with correct parameter name based on task type
        if unified_task in ["synthesize", "text_to_speech", "tts"]:
            # TTS services expect 'text' parameter
            return await service.invoke(
                text=input_data,
                task=unified_task,
                **kwargs
            )
        else:
            # STT services expect 'audio_input' parameter
            return await service.invoke(
                audio_input=input_data,
                task=unified_task,
                **kwargs
            )
    
    async def _execute_text_task(self, service, input_data, task, **kwargs):
        """Execute text-related tasks using unified invoke method"""
        
        # Map common task names to unified task names
        task_mapping = {
            "chat": "chat",
            "generate": "generate",
            "complete": "complete",
            "translate": "translate",
            "summarize": "summarize",
            "analyze": "analyze",
            "extract": "extract",
            "classify": "classify"
        }
        
        unified_task = task_mapping.get(task, task)
        
        # Use unified invoke method
        result = await service.invoke(
            input_data=input_data,
            task=unified_task,
            **kwargs
        )
        
        # Handle the new response format from LLM services
        # LLM services now return {"message": ..., "success": ..., "metadata": ...}
        if isinstance(result, dict) and "message" in result:
            # Extract the message content (convert AIMessage to string)
            message = result["message"]
            if hasattr(message, 'content'):
                # Handle langchain AIMessage objects
                return message.content
            elif isinstance(message, str):
                return message
            else:
                # Fallback: convert to string
                return str(message)
        
        # Fallback for other service types or legacy format
        return result
    
    async def _execute_image_task(self, service, input_data, task, **kwargs):
        """Execute image generation tasks using unified invoke method"""
        
        # Map common task names to unified task names
        task_mapping = {
            "generate_image": "generate",
            "generate": "generate",
            "img2img": "img2img", 
            "image_to_image": "img2img",
            "generate_batch": "generate_batch"
        }
        
        unified_task = task_mapping.get(task, task)
        
        # Use unified invoke method
        return await service.invoke(
            prompt=input_data,
            task=unified_task,
            **kwargs
        )
    
    async def _execute_embedding_task(self, service, input_data, task, **kwargs):
        """Execute embedding tasks using unified invoke method"""
        
        # Map common task names to unified task names
        task_mapping = {
            "create_embedding": "embed",
            "embed": "embed",
            "embed_batch": "embed_batch",
            "chunk_and_embed": "chunk_and_embed",
            "similarity": "similarity",
            "find_similar": "find_similar"
        }
        
        unified_task = task_mapping.get(task, task)
        
        # Use unified invoke method
        return await service.invoke(
            input_data=input_data,
            task=unified_task,
            **kwargs
        )
    
    def clear_cache(self):
        """Clear service cache"""
        self._service_cache.clear()
        logger.info("Service cache cleared")
    
    async def get_available_models(self, service_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available models
        
        Args:
            service_type: Optional filter by service type
            
        Returns:
            List of available models with metadata
        """
        if INTELLIGENT_SELECTOR_AVAILABLE:
            try:
                if self.model_selector is None:
                    self.model_selector = await get_model_selector(self.config)
                return await self.model_selector.get_available_models(service_type)
            except Exception as e:
                logger.error(f"Failed to get available models: {e}")
                return []
        else:
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of client and underlying services
        
        Returns:
            Health status dictionary
        """
        try:
            health_status = {
                "client": "healthy",
                "ai_factory": "healthy" if self.ai_factory else "unavailable",
                "model_selector": "healthy" if self.model_selector else "unavailable",
                "services": {}
            }
            
            # Check a few key services
            test_services = [
                ("vision", "openai", "gpt-4.1-mini"),
                ("audio", "openai", "whisper-1"),
                ("text", "openai", "gpt-4.1-mini")
            ]
            
            for service_type, provider, model in test_services:
                try:
                    await self._get_service(service_type, model, provider, "test")
                    health_status["services"][f"{service_type}_{provider}"] = "healthy"
                except Exception as e:
                    health_status["services"][f"{service_type}_{provider}"] = f"error: {str(e)}"
            
            return health_status
            
        except Exception as e:
            return {
                "client": "error",
                "error": str(e)
            }
    
    async def _invoke_local(
        self,
        input_data: Union[str, bytes, Path, Dict[str, Any]],
        task: str,
        service_type: str,
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Local invoke using AI Factory (original logic)"""
        try:
            # Step 1: Select best model for this task
            selected_model = await self._select_model(
                input_data=input_data,
                task=task, 
                service_type=service_type,
                model_hint=model_hint,
                provider_hint=provider_hint
            )
            
            # Step 2: Get appropriate service
            service = await self._get_service(
                service_type=service_type,
                model_name=selected_model["model_id"],
                provider=selected_model["provider"],
                task=task,
                tools=tools
            )
            
            # Step 3: Execute task with unified interface
            result = await self._execute_task(
                service=service,
                input_data=input_data,
                task=task,
                service_type=service_type,
                **kwargs
            )
            
            # Step 4: Return unified response
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "model_used": selected_model["model_id"],
                    "provider": selected_model["provider"], 
                    "task": task,
                    "service_type": service_type,
                    "selection_reason": selected_model.get("reason", "Default selection")
                }
            }
        except Exception as e:
            logger.error(f"Local invoke failed: {e}")
            raise
    
    async def _invoke_api(
        self,
        input_data: Union[str, bytes, Path, Dict[str, Any]],
        task: str,
        service_type: str,
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """API invoke using HTTP requests"""
        
        # Handle file inputs
        if isinstance(input_data, Path):
            return await self._invoke_api_file(
                file_path=input_data,
                task=task,
                service_type=service_type,
                model_hint=model_hint,
                provider_hint=provider_hint,
                **kwargs
            )
        
        # Handle binary data
        if isinstance(input_data, bytes):
            return await self._invoke_api_binary(
                data=input_data,
                task=task,
                service_type=service_type,
                model_hint=model_hint,
                provider_hint=provider_hint,
                **kwargs
            )
        
        # Handle text/JSON data
        payload = {
            "input_data": input_data,
            "task": task,
            "service_type": service_type,
            "model_hint": model_hint,
            "provider_hint": provider_hint,
            "parameters": kwargs
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
            try:
                async with session.post(
                    f"{self.api_url}/api/v1/invoke",
                    json=payload,
                    headers=self.headers
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"API error {response.status}: {error_data}")
                        
            except Exception as e:
                logger.error(f"API invoke failed: {e}")
                raise
    
    async def _invoke_api_file(
        self,
        file_path: Path,
        task: str,
        service_type: str,
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """API file upload"""
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        data = aiohttp.FormData()
        data.add_field('task', task)
        data.add_field('service_type', service_type)
        
        if model_hint:
            data.add_field('model_hint', model_hint)
        if provider_hint:
            data.add_field('provider_hint', provider_hint)
        
        data.add_field('file', 
                      open(file_path, 'rb'),
                      filename=file_path.name,
                      content_type='application/octet-stream')
        
        headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
            try:
                async with session.post(
                    f"{self.api_url}/api/v1/invoke-file",
                    data=data,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"API error {response.status}: {error_data}")
                        
            except Exception as e:
                logger.error(f"API file upload failed: {e}")
                raise
    
    async def _invoke_api_binary(
        self,
        data: bytes,
        task: str,
        service_type: str,
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """API binary upload"""
        
        form_data = aiohttp.FormData()
        form_data.add_field('task', task)
        form_data.add_field('service_type', service_type)
        
        if model_hint:
            form_data.add_field('model_hint', model_hint)
        if provider_hint:
            form_data.add_field('provider_hint', provider_hint)
        
        form_data.add_field('file', 
                           data,
                           filename='data.bin',
                           content_type='application/octet-stream')
        
        headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
            try:
                async with session.post(
                    f"{self.api_url}/api/v1/invoke-file",
                    data=form_data,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"API error {response.status}: {error_data}")
                        
            except Exception as e:
                logger.error(f"API binary upload failed: {e}")
                raise

    async def _stream_local(
        self,
        input_data: Union[str, bytes, Path, Dict[str, Any]],
        task: str,
        service_type: str,
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        **kwargs
    ):
        """Local streaming using AI Factory"""
        # Step 1: Select best model for this task
        selected_model = await self._select_model(
            input_data=input_data,
            task=task, 
            service_type=service_type,
            model_hint=model_hint,
            provider_hint=provider_hint
        )
        
        # Step 2: Get appropriate service
        service = await self._get_service(
            service_type=service_type,
            model_name=selected_model["model_id"],
            provider=selected_model["provider"],
            task=task,
            tools=tools
        )
        
        # Step 3: Yield tokens from the stream
        async for token in service.astream(input_data):
            yield token

    async def _stream_api(
        self,
        input_data: Union[str, bytes, Path, Dict[str, Any]],
        task: str,
        service_type: str,
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None,
        **kwargs
    ):
        """API streaming using Server-Sent Events (SSE)"""
        
        # Only support text streaming for now
        if not isinstance(input_data, (str, dict)):
            raise ValueError("API streaming only supports text input")
        
        payload = {
            "input_data": input_data,
            "task": task,
            "service_type": service_type,
            "model_hint": model_hint,
            "provider_hint": provider_hint,
            "stream": True,
            "parameters": kwargs
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
            try:
                async with session.post(
                    f"{self.api_url}/api/v1/stream",
                    json=payload,
                    headers=self.headers
                ) as response:
                    
                    if response.status == 200:
                        # Parse SSE stream
                        async for line in response.content:
                            if line:
                                line_str = line.decode().strip()
                                if line_str.startswith("data: "):
                                    try:
                                        # Parse SSE data
                                        import json
                                        json_str = line_str[6:]  # Remove "data: " prefix
                                        data = json.loads(json_str)
                                        
                                        if data.get("type") == "token" and "token" in data:
                                            yield data["token"]
                                        elif data.get("type") == "completion":
                                            # End of stream
                                            break
                                        elif data.get("type") == "error":
                                            raise Exception(f"Server error: {data.get('error')}")
                                            
                                    except json.JSONDecodeError:
                                        # Skip malformed lines
                                        continue
                    else:
                        error_data = await response.text()
                        raise Exception(f"API streaming error {response.status}: {error_data}")
                        
            except Exception as e:
                logger.error(f"API streaming failed: {e}")
                raise


# Convenience function for quick access
def create_client(
    config: Optional[Dict[str, Any]] = None,
    mode: str = "local",
    api_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> ISAModelClient:
    """Create ISA Model Client instance
    
    Args:
        config: Optional configuration
        mode: "local" for direct AI Factory, "api" for HTTP API calls
        api_url: API base URL (required if mode="api")  
        api_key: API key for authentication (optional)
        
    Returns:
        ISAModelClient instance
    """
    return ISAModelClient(config=config, mode=mode, api_url=api_url, api_key=api_key)


# Export for easy import
__all__ = ["ISAModelClient", "create_client"]