"""
Configuration system for stacked services
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Define stacked service specific layer types
class StackedLayerType(Enum):
    """Types of processing layers for stacked services"""
    INTELLIGENCE = "intelligence"      # High-level understanding
    DETECTION = "detection"           # Element/object detection  
    CLASSIFICATION = "classification" # Detailed classification
    VALIDATION = "validation"         # Result validation
    TRANSFORMATION = "transformation" # Data transformation
    GENERATION = "generation"         # Content generation
    ENHANCEMENT = "enhancement"       # Quality enhancement
    CONTROL = "control"              # Precise control/refinement
    UPSCALING = "upscaling"          # Resolution enhancement

@dataclass
class LayerConfig:
    """Configuration for a processing layer"""
    name: str
    layer_type: StackedLayerType
    service_type: str                  # e.g., 'vision', 'llm'
    model_name: str
    parameters: Dict[str, Any]
    depends_on: List[str]             # Layer dependencies
    timeout: float = 30.0
    retry_count: int = 1
    fallback_enabled: bool = True

@dataclass
class LayerResult:
    """Result from a processing layer"""
    layer_name: str
    success: bool
    data: Any
    metadata: Dict[str, Any]
    execution_time: float
    error: Optional[str] = None

class WorkflowType(Enum):
    """Predefined workflow types"""
    UI_ANALYSIS_FAST = "ui_analysis_fast"
    UI_ANALYSIS_ACCURATE = "ui_analysis_accurate"
    UI_ANALYSIS_COMPREHENSIVE = "ui_analysis_comprehensive"
    SEARCH_PAGE_ANALYSIS = "search_page_analysis"
    CONTENT_EXTRACTION = "content_extraction"
    FORM_INTERACTION = "form_interaction"
    NAVIGATION_ANALYSIS = "navigation_analysis"
    CUSTOM = "custom"

@dataclass
class StackedServiceConfig:
    """Configuration for a stacked service workflow"""
    name: str
    workflow_type: WorkflowType
    layers: List[LayerConfig] = field(default_factory=list)
    global_timeout: float = 120.0
    parallel_execution: bool = False
    fail_fast: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    """Manager for stacked service configurations"""
    
    PREDEFINED_CONFIGS = {
        WorkflowType.UI_ANALYSIS_FAST: {
            "name": "Fast UI Analysis",
            "layers": [
                LayerConfig(
                    name="page_intelligence",
                    layer_type=StackedLayerType.INTELLIGENCE,
                    service_type="vision",
                    model_name="gpt-4.1-nano",
                    parameters={"max_tokens": 300},
                    depends_on=[],
                    timeout=10.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="element_detection",
                    layer_type=StackedLayerType.DETECTION,
                    service_type="vision",
                    model_name="omniparser",
                    parameters={
                        "imgsz": 480,
                        "box_threshold": 0.08,
                        "iou_threshold": 0.2
                    },
                    depends_on=["page_intelligence"],
                    timeout=15.0,
                    fallback_enabled=True
                ),
                LayerConfig(
                    name="element_classification",
                    layer_type=StackedLayerType.CLASSIFICATION,
                    service_type="vision",
                    model_name="gpt-4.1-nano",
                    parameters={"max_tokens": 200},
                    depends_on=["page_intelligence", "element_detection"],
                    timeout=20.0,
                    fallback_enabled=False
                )
            ],
            "global_timeout": 60.0,
            "parallel_execution": False,
            "fail_fast": False,
            "metadata": {
                "description": "Fast UI analysis optimized for speed",
                "expected_time": "30-45 seconds",
                "accuracy": "medium"
            }
        }
    }
    
    @classmethod
    def get_config(cls, workflow_type: WorkflowType) -> StackedServiceConfig:
        """Get predefined configuration for a workflow type"""
        if workflow_type not in cls.PREDEFINED_CONFIGS:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        config_data = cls.PREDEFINED_CONFIGS[workflow_type]
        
        return StackedServiceConfig(
            name=config_data["name"],
            workflow_type=workflow_type,
            layers=config_data["layers"],
            global_timeout=config_data["global_timeout"],
            parallel_execution=config_data["parallel_execution"],
            fail_fast=config_data["fail_fast"],
            metadata=config_data["metadata"]
        )

# Convenience function for quick access
def get_ui_analysis_config(speed: str = "accurate") -> StackedServiceConfig:
    """Get UI analysis configuration by speed preference"""
    speed_mapping = {
        "fast": WorkflowType.UI_ANALYSIS_FAST,
        "accurate": WorkflowType.UI_ANALYSIS_ACCURATE,
        "comprehensive": WorkflowType.UI_ANALYSIS_COMPREHENSIVE
    }
    
    workflow_type = speed_mapping.get(speed.lower(), WorkflowType.UI_ANALYSIS_ACCURATE)
    return ConfigManager.get_config(workflow_type)