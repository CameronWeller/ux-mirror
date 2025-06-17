#!/usr/bin/env python3
"""
UX-MIRROR Analysis Pipeline Framework
====================================

Provides a composable pipeline architecture for chaining analysis stages
with caching, parallel execution, and configuration support.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import pickle
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from core.exceptions import AnalysisError, ValidationError
from core.error_handler import retry, RetryConfig, with_error_handling
from core.configuration_manager import get_configuration_manager

logger = logging.getLogger(__name__)


@dataclass
class StageResult:
    """Result from a pipeline stage execution"""
    stage_name: str
    success: bool
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error: Optional[Exception] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'stage_name': self.stage_name,
            'success': self.success,
            'data': self.data if not isinstance(self.data, bytes) else '<binary_data>',
            'metadata': self.metadata,
            'execution_time': self.execution_time,
            'error': str(self.error) if self.error else None,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class PipelineContext:
    """Context passed between pipeline stages"""
    input_data: Any
    results: Dict[str, StageResult] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    cache_key: Optional[str] = None
    
    def get_previous_result(self, stage_name: str) -> Optional[Any]:
        """Get result from a previous stage"""
        if stage_name in self.results:
            return self.results[stage_name].data
        return None
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to context"""
        self.metadata[key] = value


class AnalysisStage(ABC):
    """
    Abstract base class for analysis pipeline stages.
    
    Each stage performs a specific analysis task and can be chained
    together to form complex analysis pipelines.
    """
    
    def __init__(self, name: str, cache_enabled: bool = True, cache_ttl: int = 3600):
        """
        Initialize analysis stage.
        
        Args:
            name: Unique name for this stage
            cache_enabled: Whether to cache results
            cache_ttl: Cache time-to-live in seconds
        """
        self.name = name
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.config_manager = get_configuration_manager()
        
        # Load stage-specific configuration
        self.config = self.config_manager.get(f"pipeline.stages.{name}", {})
    
    @abstractmethod
    async def process(self, context: PipelineContext) -> Any:
        """
        Process the input and return results.
        
        Args:
            context: Pipeline context with input data and previous results
            
        Returns:
            Processed data
        """
        pass
    
    def validate_input(self, context: PipelineContext) -> bool:
        """
        Validate input data for this stage.
        
        Override this method to add custom validation.
        
        Args:
            context: Pipeline context
            
        Returns:
            True if input is valid
            
        Raises:
            ValidationError: If input is invalid
        """
        return True
    
    def get_cache_key(self, context: PipelineContext) -> str:
        """
        Generate cache key for this stage's input.
        
        Override this method for custom cache key generation.
        
        Args:
            context: Pipeline context
            
        Returns:
            Cache key string
        """
        # Create a deterministic key from input data
        data_str = json.dumps(context.input_data, sort_keys=True, default=str)
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        return f"{self.name}:{data_hash}"
    
    async def execute(self, context: PipelineContext) -> StageResult:
        """
        Execute the stage with error handling and caching.
        
        Args:
            context: Pipeline context
            
        Returns:
            StageResult with processing results
        """
        start_time = time.time()
        
        try:
            # Validate input
            self.validate_input(context)
            
            # Check cache if enabled
            if self.cache_enabled:
                cache_key = self.get_cache_key(context)
                cached_result = await self._get_cached_result(cache_key)
                if cached_result is not None:
                    logger.debug(f"Stage '{self.name}' using cached result")
                    return StageResult(
                        stage_name=self.name,
                        success=True,
                        data=cached_result,
                        metadata={'cache_hit': True},
                        execution_time=time.time() - start_time
                    )
            
            # Process data
            result_data = await self.process(context)
            
            # Cache result if enabled
            if self.cache_enabled:
                await self._cache_result(cache_key, result_data)
            
            # Return success result
            return StageResult(
                stage_name=self.name,
                success=True,
                data=result_data,
                metadata={'cache_hit': False},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Stage '{self.name}' failed: {e}")
            return StageResult(
                stage_name=self.name,
                success=False,
                data=None,
                error=e,
                execution_time=time.time() - start_time
            )
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result if available and not expired"""
        # TODO: Implement actual cache backend (Redis, disk, etc.)
        # For now, using simple in-memory cache
        cache_file = Path(f".cache/pipeline/{cache_key}.pkl")
        
        if cache_file.exists():
            try:
                # Check if cache is expired
                cache_age = time.time() - cache_file.stat().st_mtime
                if cache_age < self.cache_ttl:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache for {cache_key}: {e}")
        
        return None
    
    async def _cache_result(self, cache_key: str, data: Any):
        """Cache the result"""
        # TODO: Implement actual cache backend
        cache_dir = Path(".cache/pipeline")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        cache_file = cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to cache result for {cache_key}: {e}")


class Pipeline:
    """
    Composable analysis pipeline that chains multiple stages.
    
    Features:
    - Sequential and parallel stage execution
    - Result caching
    - Error handling and recovery
    - Progress tracking
    - Configuration via JSON/YAML
    """
    
    def __init__(self, name: str, stages: Optional[List[AnalysisStage]] = None):
        """
        Initialize pipeline.
        
        Args:
            name: Pipeline name
            stages: Initial list of stages
        """
        self.name = name
        self.stages: List[AnalysisStage] = stages or []
        self.config_manager = get_configuration_manager()
        self.config = self.config_manager.get(f"pipeline.{name}", {})
        
        # Execution configuration
        self.parallel_execution = self.config.get('parallel_execution', False)
        self.stop_on_error = self.config.get('stop_on_error', True)
        self.max_workers = self.config.get('max_workers', 4)
        
        # Progress tracking
        self.progress_callbacks: List[Callable] = []
        
        logger.info(f"Pipeline '{name}' initialized with {len(self.stages)} stages")
    
    def add_stage(self, stage: AnalysisStage):
        """Add a stage to the pipeline"""
        self.stages.append(stage)
        logger.debug(f"Added stage '{stage.name}' to pipeline '{self.name}'")
    
    def remove_stage(self, stage_name: str):
        """Remove a stage from the pipeline"""
        self.stages = [s for s in self.stages if s.name != stage_name]
    
    def register_progress_callback(self, callback: Callable):
        """Register a callback for progress updates"""
        self.progress_callbacks.append(callback)
    
    @with_error_handling("pipeline_execution")
    async def execute(self, input_data: Any, metadata: Optional[Dict[str, Any]] = None) -> PipelineContext:
        """
        Execute the pipeline on input data.
        
        Args:
            input_data: Input data for the pipeline
            metadata: Optional metadata
            
        Returns:
            PipelineContext with all results
        """
        context = PipelineContext(
            input_data=input_data,
            metadata=metadata or {}
        )
        
        logger.info(f"Executing pipeline '{self.name}' with {len(self.stages)} stages")
        
        if self.parallel_execution and len(self.stages) > 1:
            await self._execute_parallel(context)
        else:
            await self._execute_sequential(context)
        
        return context
    
    async def _execute_sequential(self, context: PipelineContext):
        """Execute stages sequentially"""
        total_stages = len(self.stages)
        
        for i, stage in enumerate(self.stages):
            # Progress update
            self._report_progress(i, total_stages, f"Executing {stage.name}")
            
            # Execute stage
            result = await stage.execute(context)
            context.results[stage.name] = result
            
            # Check for errors
            if not result.success and self.stop_on_error:
                raise AnalysisError(
                    f"Pipeline '{self.name}' failed at stage '{stage.name}'",
                    analysis_type='pipeline',
                    context={'stage': stage.name, 'error': str(result.error)}
                )
            
            # Update context for next stage
            if result.success:
                context.input_data = result.data
        
        self._report_progress(total_stages, total_stages, "Pipeline completed")
    
    async def _execute_parallel(self, context: PipelineContext):
        """Execute independent stages in parallel"""
        # Group stages by dependencies
        # For now, simple parallel execution of all stages
        # TODO: Implement dependency graph for smarter parallel execution
        
        async def execute_stage(stage: AnalysisStage) -> tuple[str, StageResult]:
            result = await stage.execute(context)
            return stage.name, result
        
        # Execute all stages in parallel
        tasks = [execute_stage(stage) for stage in self.stages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for stage_name, result in results:
            if isinstance(result, Exception):
                result = StageResult(
                    stage_name=stage_name,
                    success=False,
                    data=None,
                    error=result
                )
            
            context.results[stage_name] = result
            
            if not result.success and self.stop_on_error:
                raise AnalysisError(
                    f"Pipeline '{self.name}' failed at stage '{stage_name}'",
                    analysis_type='pipeline',
                    context={'stage': stage_name, 'error': str(result.error)}
                )
    
    def _report_progress(self, current: int, total: int, message: str):
        """Report progress to registered callbacks"""
        progress = {
            'pipeline': self.name,
            'current': current,
            'total': total,
            'percentage': (current / total * 100) if total > 0 else 0,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        for callback in self.progress_callbacks:
            try:
                callback(progress)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    @classmethod
    def from_config(cls, config_path: str) -> 'Pipeline':
        """
        Create a pipeline from configuration file.
        
        Args:
            config_path: Path to pipeline configuration (JSON/YAML)
            
        Returns:
            Configured Pipeline instance
        """
        # Load configuration
        import yaml
        
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config = yaml.safe_load(f)
            else:
                config = json.load(f)
        
        # Create pipeline
        pipeline = cls(name=config['name'])
        
        # Configure pipeline settings
        if 'settings' in config:
            pipeline.parallel_execution = config['settings'].get('parallel_execution', False)
            pipeline.stop_on_error = config['settings'].get('stop_on_error', True)
            pipeline.max_workers = config['settings'].get('max_workers', 4)
        
        # Load stages
        # TODO: Implement dynamic stage loading from config
        
        return pipeline
    
    def to_config(self) -> Dict[str, Any]:
        """Export pipeline configuration"""
        return {
            'name': self.name,
            'settings': {
                'parallel_execution': self.parallel_execution,
                'stop_on_error': self.stop_on_error,
                'max_workers': self.max_workers
            },
            'stages': [
                {
                    'name': stage.name,
                    'cache_enabled': stage.cache_enabled,
                    'cache_ttl': stage.cache_ttl,
                    'config': stage.config
                }
                for stage in self.stages
            ]
        }


class PipelineBuilder:
    """
    Fluent builder for creating analysis pipelines.
    
    Example:
        pipeline = (PipelineBuilder("my_pipeline")
                   .add_stage(PreprocessingStage())
                   .add_stage(AnalysisStage())
                   .add_stage(PostprocessingStage())
                   .with_parallel_execution()
                   .with_caching(ttl=7200)
                   .build())
    """
    
    def __init__(self, name: str):
        self.pipeline = Pipeline(name)
    
    def add_stage(self, stage: AnalysisStage) -> 'PipelineBuilder':
        """Add a stage to the pipeline"""
        self.pipeline.add_stage(stage)
        return self
    
    def with_parallel_execution(self, max_workers: int = 4) -> 'PipelineBuilder':
        """Enable parallel execution"""
        self.pipeline.parallel_execution = True
        self.pipeline.max_workers = max_workers
        return self
    
    def with_sequential_execution(self) -> 'PipelineBuilder':
        """Use sequential execution (default)"""
        self.pipeline.parallel_execution = False
        return self
    
    def continue_on_error(self) -> 'PipelineBuilder':
        """Continue execution even if a stage fails"""
        self.pipeline.stop_on_error = False
        return self
    
    def stop_on_error(self) -> 'PipelineBuilder':
        """Stop execution if any stage fails (default)"""
        self.pipeline.stop_on_error = True
        return self
    
    def with_progress_callback(self, callback: Callable) -> 'PipelineBuilder':
        """Add a progress callback"""
        self.pipeline.register_progress_callback(callback)
        return self
    
    def build(self) -> Pipeline:
        """Build and return the pipeline"""
        return self.pipeline


# Example concrete stages
class ImagePreprocessingStage(AnalysisStage):
    """Example stage for image preprocessing"""
    
    def __init__(self):
        super().__init__("image_preprocessing")
    
    async def process(self, context: PipelineContext) -> Any:
        """Preprocess image data"""
        # Example implementation
        image = context.input_data
        
        # Add preprocessing logic here
        # For now, just pass through
        return image
    
    def validate_input(self, context: PipelineContext) -> bool:
        """Validate that input is an image"""
        # Add validation logic
        return True


class UIElementDetectionStage(AnalysisStage):
    """Example stage for UI element detection"""
    
    def __init__(self):
        super().__init__("ui_element_detection")
    
    async def process(self, context: PipelineContext) -> Any:
        """Detect UI elements in image"""
        # Get preprocessed image from previous stage
        image = context.get_previous_result("image_preprocessing") or context.input_data
        
        # Add UI detection logic here
        detected_elements = []
        
        return {
            'elements': detected_elements,
            'element_count': len(detected_elements)
        }


class AccessibilityAnalysisStage(AnalysisStage):
    """Example stage for accessibility analysis"""
    
    def __init__(self):
        super().__init__("accessibility_analysis")
    
    async def process(self, context: PipelineContext) -> Any:
        """Analyze accessibility of detected UI elements"""
        # Get detected elements from previous stage
        ui_data = context.get_previous_result("ui_element_detection")
        
        if not ui_data:
            raise ValidationError("No UI element data available")
        
        # Add accessibility analysis logic here
        issues = []
        
        return {
            'accessibility_score': 0.8,
            'issues': issues,
            'wcag_compliance': 'AA'
        }