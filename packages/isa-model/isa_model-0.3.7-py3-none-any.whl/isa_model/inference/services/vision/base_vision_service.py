from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, BinaryIO
import logging

from isa_model.inference.services.base_service import BaseService
from isa_model.inference.services.vision.helpers.image_utils import (
    get_image_data, prepare_image_base64, prepare_image_data_url, 
    get_image_mime_type, get_image_dimensions, validate_image_format
)

logger = logging.getLogger(__name__)

class BaseVisionService(BaseService):
    """Base class for vision understanding services with common task implementations"""
    
    async def invoke(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一的任务分发方法 - Base类提供通用实现
        
        Args:
            image: Path to image file or image data
            prompt: Optional text prompt/question about the image
            task: Task type - 支持两大类：图像理解 + 检测抽取
            **kwargs: Additional task-specific parameters
            
        Returns:
            Dict containing task results
        """
        task = task or "analyze"
        
        # ==================== 图像理解类任务 ====================
        if task == "analyze":
            return await self.analyze_image(image, prompt, kwargs.get("max_tokens", 1000))
        elif task == "describe":
            return await self.describe_image(image, kwargs.get("detail_level", "medium"))
        elif task == "classify":
            return await self.classify_image(image, kwargs.get("categories"))
        elif task == "compare":
            return await self.compare_images(image, kwargs.get("image2"))
        
        # ==================== 检测抽取类任务 ====================
        elif task == "extract_text":
            return await self.extract_text(image)
        elif task == "detect_objects":
            return await self.detect_objects(image, kwargs.get("confidence_threshold", 0.5))
        elif task == "detect_ui_elements":
            return await self.detect_ui_elements(image, kwargs.get("element_types"), kwargs.get("confidence_threshold", 0.5))
        elif task == "detect_document_elements":
            return await self.detect_document_elements(image, kwargs.get("element_types"), kwargs.get("confidence_threshold", 0.5))
        elif task == "extract_table_data":
            return await self.extract_table_data(image, kwargs.get("table_format", "json"), kwargs.get("preserve_formatting", True))
        elif task == "get_coordinates":
            return await self.get_object_coordinates(image, kwargs.get("object_name", ""))
        
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
    
    async def analyze_image(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        通用图像分析 - Provider可选实现
        
        Args:
            image: Path to image file or image data
            prompt: Optional text prompt/question about the image
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict containing analysis results with keys:
            - text: Description or answer about the image
            - confidence: Confidence score (if available)
            - detected_objects: List of detected objects (if available)
            - metadata: Additional metadata about the analysis
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support analyze_image task")
    
    # ==================== 图像理解类方法 ====================
    
    async def describe_image(
        self, 
        image: Union[str, BinaryIO],
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        图像描述 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support describe_image task")
    
    async def classify_image(
        self, 
        image: Union[str, BinaryIO],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        图像分类 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support classify_image task")
    
    async def compare_images(
        self, 
        image1: Union[str, BinaryIO],
        image2: Union[str, BinaryIO]
    ) -> Dict[str, Any]:
        """
        图像比较 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support compare_images task")
    
    # ==================== 检测抽取类方法 ====================
    
    async def extract_text(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """
        文本提取(OCR) - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support extract_text task")
    
    async def detect_objects(
        self, 
        image: Union[str, BinaryIO],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        通用物体检测 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support detect_objects task")
    
    async def detect_ui_elements(
        self,
        image: Union[str, BinaryIO],
        element_types: Optional[List[str]] = None,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        UI界面元素检测 - Provider可选实现
        
        Args:
            image: 输入图像
            element_types: 要检测的元素类型 ['button', 'input', 'text', 'image', 'link', etc.]
            confidence_threshold: 置信度阈值
            
        Returns:
            Dict containing detected UI elements with their bounding boxes and types
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support detect_ui_elements task")
    
    async def detect_document_elements(
        self,
        image: Union[str, BinaryIO],
        element_types: Optional[List[str]] = None,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        文档结构元素检测 - Provider可选实现
        
        Args:
            image: 输入图像
            element_types: 要检测的元素类型 ['table', 'header', 'paragraph', 'list', etc.]
            confidence_threshold: 置信度阈值
            
        Returns:
            Dict containing detected document elements with their structure and content
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support detect_document_elements task")
    
    async def get_object_coordinates(
        self,
        image: Union[str, BinaryIO],
        object_name: str
    ) -> Dict[str, Any]:
        """
        获取对象坐标 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support get_object_coordinates task")
    
    async def extract_table_data(
        self,
        image: Union[str, BinaryIO],
        table_format: str = "json",
        preserve_formatting: bool = True
    ) -> Dict[str, Any]:
        """
        表格数据结构化抽取 - Provider可选实现
        
        Args:
            image: 输入图像
            table_format: 输出格式 ('json', 'csv', 'markdown', 'html')
            preserve_formatting: 是否保持原始格式（合并单元格、样式等）
            
        Returns:
            Dict containing extracted table data in structured format:
            {
                "tables": [
                    {
                        "table_id": "table_1",
                        "headers": ["Column1", "Column2", "Column3"],
                        "rows": [
                            ["cell1", "cell2", "cell3"],
                            ["cell4", "cell5", "cell6"]
                        ],
                        "metadata": {
                            "row_count": 2,
                            "column_count": 3,
                            "has_headers": true,
                            "merged_cells": [],
                            "table_caption": "optional_caption"
                        }
                    }
                ],
                "raw_data": "original_table_text",
                "format": "json"
            }
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support extract_table_data task")
    
    async def close(self):
        """Cleanup resources - default implementation does nothing"""
        pass
    
    def get_supported_tasks(self) -> List[str]:
        """
        获取provider支持的任务列表
        
        Returns:
            List of supported task names
        """
        supported = []
        
        # 检查哪些方法被实现了
        if hasattr(self, 'analyze_image') and callable(getattr(self, 'analyze_image')):
            try:
                # 尝试调用看是否抛出NotImplementedError
                import inspect
                if not 'NotImplementedError' in inspect.getsource(self.analyze_image):
                    supported.append('analyze')
            except:
                pass
                
        # 检查各类任务支持情况
        method_task_map = {
            # 图像理解类
            'describe_image': 'describe',
            'classify_image': 'classify',
            'compare_images': 'compare',
            # 检测抽取类
            'extract_text': 'extract_text', 
            'detect_objects': 'detect_objects',
            'detect_ui_elements': 'detect_ui_elements',
            'detect_document_elements': 'detect_document_elements',
            'extract_table_data': 'extract_table_data',
            'get_object_coordinates': 'get_coordinates'
        }
        
        for method_name, task_name in method_task_map.items():
            if hasattr(self, method_name):
                # 检查是否是默认实现（基于analyze_image）还是provider自己的实现
                supported.append(task_name)
                
        return supported
    
    # ==================== COMMON TASK IMPLEMENTATIONS ====================
    # 为每个provider提供可选的默认实现，provider可以覆盖这些方法
    
    async def analyze_images(
        self, 
        images: List[Union[str, BinaryIO]],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        批量图像分析 - Provider可选实现
        默认实现：如果provider支持analyze_image，则逐个调用
        """
        if hasattr(self, 'analyze_image'):
            results = []
            for image in images:
                try:
                    result = await self.analyze_image(image, prompt, max_tokens)
                    results.append(result)
                except NotImplementedError:
                    raise NotImplementedError(f"{self.__class__.__name__} does not support analyze_images task")
            return results
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support analyze_images task")
    
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的图像格式 - Provider应该实现
        """
        return ['jpg', 'jpeg', 'png', 'gif', 'webp']  # 通用格式
    
    def get_max_image_size(self) -> Dict[str, int]:
        """
        获取最大图像尺寸 - Provider应该实现
        """
        return {"width": 2048, "height": 2048, "file_size_mb": 10}  # 通用限制
    
    # ==================== UTILITY METHODS ====================
    
    def _parse_coordinates_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本响应中解析对象坐标 - 使用统一的解析工具
        """
        from isa_model.inference.services.vision.helpers.image_utils import parse_coordinates_from_text
        return parse_coordinates_from_text(text)
    
    def _parse_center_coordinates_from_text(self, text: str) -> tuple[bool, Optional[List[int]], str]:
        """
        从结构化文本响应中解析中心坐标 - 使用统一的解析工具
        """
        from isa_model.inference.services.vision.helpers.image_utils import parse_center_coordinates_from_text
        return parse_center_coordinates_from_text(text)
