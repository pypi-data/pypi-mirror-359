"""
@trace Decorator

MVP implementation of the @trace decorator for automatic tool tracking.
"""

from functools import wraps
import inspect
import logging
import asyncio
from typing import Any, Dict, Optional, Callable, Union
from datetime import datetime

from .trace_manager import get_trace_manager
from .trace_context import get_current_context, add_metadata
from .exceptions import VeritaxAnalyticsError
from .utils import sanitize_metadata


def trace(
    tool_name: Optional[str] = None,
    include_args: bool = False,
    include_result: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, str]] = None,
    enabled: Optional[bool] = None
):
    """
    Decorator for automatic tool execution tracing.
    
    Args:
        tool_name: Override tool name (defaults to function name)
        include_args: Include function arguments in metadata
        include_result: Include function result in event
        metadata: Static metadata to include
        metrics: Mapping of metric names to function attribute names
        enabled: Override global enabled setting
    
    Example:
        @trace(tool_name="mcp_tool_1", include_args=True)
        def mcp_tool_1(filename: str) -> str:
            return open(filename).read()
    """
    
    def decorator(func: Callable) -> Callable:
        # Get function metadata
        func_name = tool_name or func.__name__
        func_module = getattr(func, '__module__', 'unknown')

        def prepare_trace_metadata():
            trace_metadata = {
                'function_name': func.__name__,
                'module': func_module,
                **(metadata or {})
            }
            return trace_metadata

        def capture_arguments(*args, **kwargs):
            """Capture and sanitize function arguments if requested."""
            if not include_args:
                return {}
            
            try:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                sanitized_args = sanitize_metadata(
                    bound_args.arguments, 
                    max_size=200 # we might need to add this to config but good for now
                )
                return {'arguments': sanitized_args}
            except Exception as e:
                logging.getLogger(__name__).warning(f"Error capturing arguments: {e}")
                return {}

        def collect_metrics(result, metrics_config):
            """Extract metrics from function result based on configuration."""
            collected_metrics = {}
            if not metrics_config:
                return collected_metrics
                
            for metric_name, attr_name in metrics_config.items():
                try:
                    if hasattr(result, attr_name):
                        metric_value = getattr(result, attr_name)
                        if isinstance(metric_value, (int, float)):
                            collected_metrics[metric_name] = float(metric_value)
                except Exception as e:
                    logging.getLogger(__name__).warning(
                        f"Error collecting metric {metric_name}: {e}"
                    )
            return collected_metrics

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check if tracing is globally disabled
            manager = get_trace_manager()
            
            # Local override check
            if enabled is False:
                return func(*args, **kwargs)
            
            # Check if this tool should be traced
            if not manager.should_trace(func_name):
                return func(*args, **kwargs)
            
            # Prepare metadata
            trace_metadata = prepare_trace_metadata()
            trace_metadata.update(capture_arguments(*args, **kwargs))
            
            # Get parent trace ID if nested
            parent_context = get_current_context()
            parent_trace_id = parent_context.trace_id if parent_context else None
            
            # Start trace
            trace_id = manager.start_trace(
                tool_name=func_name,
                metadata=trace_metadata,
                parent_trace_id=parent_trace_id
            )
            
            success = False
            result = None
            error = None
            collected_metrics = {}
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                success = True
                
                # Collect metrics if specified
                collected_metrics = collect_metrics(result, metrics)
                
                return result
                
            except Exception as e:
                error = e
                success = False
                raise
                
            finally:
                # End trace
                manager.end_trace(
                    trace_id=trace_id,
                    success=success,
                    error=error,
                    result=result if include_result else None,
                    metrics=collected_metrics if collected_metrics else None
                )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check if tracing is globally disabled
            manager = get_trace_manager()
            
            # Local override check
            if enabled is False:
                return await func(*args, **kwargs)
            
            # Check if this tool should be traced
            if not manager.should_trace(func_name):
                return await func(*args, **kwargs)
            
            # Prepare metadata
            trace_metadata = prepare_trace_metadata()
            trace_metadata.update(capture_arguments(*args, **kwargs))
            
            # Get parent trace ID if nested
            parent_context = get_current_context()
            parent_trace_id = parent_context.trace_id if parent_context else None
            
            # Start trace
            trace_id = manager.start_trace(
                tool_name=func_name,
                metadata=trace_metadata,
                parent_trace_id=parent_trace_id
            )
            
            success = False
            result = None
            error = None
            collected_metrics = {}
            
            try:
                # Execute async function
                result = await func(*args, **kwargs)
                success = True
                
                # Collect metrics if specified
                collected_metrics = collect_metrics(result, metrics)
                
                return result
                
            except Exception as e:
                error = e
                success = False
                raise
                
            finally:
                # End trace
                manager.end_trace(
                    trace_id=trace_id,
                    success=success,
                    error=error,
                    result=result if include_result else None,
                    metrics=collected_metrics if collected_metrics else None
                )

        if asyncio.iscoroutinefunction(func):
            wrapper = async_wrapper
        else:
            wrapper = sync_wrapper
        
        # Add metadata to wrapper for introspection
        wrapper._trace_config = {
            'tool_name': func_name,
            'include_args': include_args,
            'include_result': include_result,
            'metadata': metadata,
            'metrics': metrics,
            'enabled': enabled
        }
        
        return wrapper
    
    return decorator


def add_trace_metadata(key: str, value: Any) -> None:
    """
    Add metadata to the current trace context.
    
    Args:
        key: Metadata key
        value: Metadata value
    """
    try:
        add_metadata(key, value)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error adding trace metadata: {e}")


def add_trace_metric(name: str, value: float) -> None:
    """
    Add a metric to the current trace.
    
    Args:
        name: Metric name
        value: Metric value
    """
    try:
        manager = get_trace_manager()
        manager.add_metric(name, value)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error adding trace metric: {e}")


class TraceContextDecorator:
    """
    Context manager for manual trace management.
    
    Example:
        with TraceContextDecorator("manual_tool") as trace:
            trace.add_metadata("step", "processing")
            result = do_work()
            trace.add_metric("items_processed", len(result))
    """
    
    def __init__(
        self,
        tool_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        # Lightweight validation without Pydantic overhead , if any one feels pydantic is needed here lets add it
        if not tool_name or not isinstance(tool_name, str):
            raise ValueError("tool_name must be a non-empty string")
        if len(tool_name) > 255:
            raise ValueError("tool_name cannot exceed 255 characters")
        
        self.tool_name = tool_name
        self.metadata = metadata or {}
        self.trace_id: Optional[str] = None
        self.manager = get_trace_manager()
        self.success = True
        self.error: Optional[Exception] = None
    
    def __enter__(self) -> 'TraceContextDecorator':
        parent_context = get_current_context()
        parent_trace_id = parent_context.trace_id if parent_context else None
        
        self.trace_id = self.manager.start_trace(
            tool_name=self.tool_name,
            metadata=self.metadata,
            parent_trace_id=parent_trace_id
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.success = False
            self.error = exc_val
        
        if self.trace_id:
            self.manager.end_trace(
                trace_id=self.trace_id,
                success=self.success,
                error=self.error
            )
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to this trace."""
        add_trace_metadata(key, value)
    
    def add_metric(self, name: str, value: float) -> None:
        """Add metric to this trace."""
        add_trace_metric(name, value)

# Diff name we might need to change them to avoid any conflicts 
trace_context = TraceContextDecorator
manual_trace = TraceContextDecorator
