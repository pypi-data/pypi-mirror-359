"""
Trace Manager

Coordinates trace execution, event collection, and remote configuration.
"""

import uuid
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import json
import random
import os

from pydantic import BaseModel, Field, ValidationError

from .models import AnalyticsEvent, ToolExecutionEvent
from .transport import HTTPTransport
from .buffer import EventBuffer
from .trace_context import TraceContext, set_context, clear_context, get_current_context
from .exceptions import VeritaxAnalyticsError


class RemoteConfig(BaseModel):
    """Manages remote configuration for tracing."""
    
    enabled: bool = Field(
        default=True,
        description="Whether tracing is enabled globally"
    )
    sampling_rate: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Sampling rate between 0.0 (no sampling) and 1.0 (100 percent sampling)"
    )
    buffer_size: int = Field(
        default=100,
        ge=1,
        description="Maximum number of events in buffer before flush"
    )
    flush_interval: float = Field(
        default=30.0,
        ge=1.0,
        description="Seconds between automatic buffer flushes"
    )
    excluded_tools: List[str] = Field(
        default_factory=list,
        description="List of tool names to exclude from tracing"
    )
    metadata_keys: List[str] = Field(
        default_factory=list,
        description="List of metadata keys to include in events"
    )
    last_update: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last configuration update"
    )
    
    def update_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary with validation."""
        try:
            # Add timestamp for this update
            update_data = {
                **config_data,
                'last_update': datetime.utcnow()
            }
            
            # Use Pydantic's model_copy with update - most efficient approach
            updated_instance = self.model_copy(update=update_data)
            
            # Update current instance with validated values
            for field_name, field_value in updated_instance.model_dump().items():
                setattr(self, field_name, field_value)
                
        except ValidationError as e:
            raise VeritaxAnalyticsError(f"Invalid configuration update: {e}")
    
    def should_trace(self, tool_name: str) -> bool:
        """Check if tool should be traced based on configuration."""
        if not self.enabled:
            return False
        
        if tool_name in self.excluded_tools:
            return False
        
        # Simple sampling based on rate
        return random.random() < self.sampling_rate


class TraceManager:
    """Manages trace execution and event collection."""
    
    def __init__(
        self,
        transport: Optional[HTTPTransport] = None,
        config: Optional[RemoteConfig] = None,
        buffer_size: int = 100,
        flush_interval: float = 30.0,
        file_path: Optional[str] = None
    ):
        self.transport = transport
        self.config = config or RemoteConfig()
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
        
        # Event buffer
        self.buffer = EventBuffer(
            max_size=buffer_size,
            flush_interval=flush_interval,
            auto_flush=True
        )
        
        # Add flush callback to send events
        self.buffer.add_flush_callback(self._send_events)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Active traces tracking
        self._active_traces: Dict[str, TraceContext] = {}
    
    def should_trace(self, tool_name: str) -> bool:
        """Check if tool should be traced."""
        return self.config.should_trace(tool_name)
    
    def start_trace(
        self,
        tool_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_trace_id: Optional[str] = None
    ) -> str:
        """
        Start a new trace.
        
        Returns trace_id.
        """
        if not self.should_trace(tool_name):
            self.logger.debug(f"Skipping trace for excluded tool: {tool_name}")
            return ""
        
        trace_id = str(uuid.uuid4())
        started_at = datetime.utcnow()
        
        # Create trace context
        context = TraceContext(
            trace_id=trace_id,
            tool_name=tool_name,
            started_at=started_at,
            metadata=metadata or {},
            parent_trace_id=parent_trace_id
        )
        
        # Set context
        set_context(context)
        
        # Track active trace
        with self._lock:
            self._active_traces[trace_id] = context
        
        self.logger.debug(f"Started trace {trace_id} for tool {tool_name}")
        return trace_id
    
    def end_trace(
        self,
        trace_id: str,
        success: bool = True,
        error: Optional[Exception] = None,
        result: Any = None,
        metrics: Optional[Dict[str, float]] = None
    ) -> None:
        """
        End a trace and create tool execution event.
        
        Args:
            trace_id: The trace ID to end
            success: Whether the operation succeeded
            error: Exception if operation failed
            result: Function result (if include_result=True)
            metrics: Additional metrics from @trace decorator (e.g., from automatic collection)
        """
        if not trace_id:  # Skip if tracing was disabled
            return
        
        with self._lock:
            context = self._active_traces.pop(trace_id, None)
        
        if not context:
            self.logger.warning(f"Attempted to end unknown trace: {trace_id}")
            return
        
        ended_at = datetime.utcnow()
        duration_ms = (ended_at - context.started_at).total_seconds() * 1000
        
        # Create tool execution event
        tool_event = ToolExecutionEvent(
            server_id="trace-manager",  # Required by AnalyticsEvent base class
            tool_name=context.tool_name,
            execution_start_time=context.started_at,
            execution_end_time=ended_at,
            success=success,
            error_type=type(error).__name__ if error else None,
            error_message=str(error) if error else None,
            metadata=context.metadata or {}
        )
        
        # Add any additional metrics from decorator parameters
        if metrics:
            for k, v in metrics.items():
                tool_event.metadata[f"metric_{k}"] = v
        
        self._add_event(tool_event)
        
        # Clear context
        clear_context()
        
        self.logger.debug(f"Ended trace {trace_id} (success={success}, duration={duration_ms:.2f}ms)")
    
    def add_metric(self, name: str, value: float) -> None:
        """Add a metric to the current trace context with metric_ prefix."""
        context = get_current_context()
        if not context:
            self.logger.debug("No active trace for metric")
            return
        
        # Add metric with standardized prefix for easy identification
        metric_key = f"metric_{name}"
        context.metadata[metric_key] = value
        
        self.logger.debug(f"Added metric {name}={value} to trace {context.trace_id}")
    
    def _add_event(self, event: AnalyticsEvent) -> None:
        """Add event to buffer."""
        success = self.buffer.add_event(event)
        if not success:
            self.logger.warning(f"Failed to buffer event: {event.event_type}")
    
    def _send_events(self, events: List[AnalyticsEvent]) -> None:
        """Send events via transport and/or write to file (called by buffer)."""
        if not events:
            return
        
        try:
            # Convert events to dictionaries
            event_dicts = []
            for event in events:
                try:
                    event_dict = event.model_dump()
                    for key, value in event_dict.items():
                        if isinstance(value, datetime):
                            event_dict[key] = value.isoformat()
                    event_dicts.append(event_dict)
                except Exception as e:
                    self.logger.error(f"Error serializing event: {e}")
            
            # Background , daemon thread to send events
            def send_worker():
                try:
                    # Original HTTP transport (if configured)
                    if self.transport:
                        self.transport.send_events(event_dicts)
                        self.logger.debug(f"Sent {len(event_dicts)} events via transport")
                    
                    # File writing (if file_path configured)
                    if self.file_path:
                        self._write_events_to_file(event_dicts)
                        self.logger.debug(f"Wrote {len(event_dicts)} events to {self.file_path}")
                        
                except Exception as e:
                    self.logger.error(f"Error sending/writing events: {e}")
            
            thread = threading.Thread(target=send_worker, daemon=True)
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Error preparing events for transport: {e}")
    
    def _write_events_to_file(self, event_dicts: List[Dict[str, Any]]) -> None:
        """Write events to JSON file (overwrites existing file)."""
        try:
            # Ensure directory exists (if file_path has a directory component)
            dir_path = os.path.dirname(self.file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            # Write events to file (overwrite mode) with pretty printing
            with open(self.file_path, 'w') as f:
                json.dump(event_dicts, f, indent=2, sort_keys=True)  # Pretty-printed JSON
                
        except Exception as e:
            self.logger.error(f"Error writing events to file {self.file_path}: {e}")
    
    def _summarize_result(self, result: Any) -> Optional[str]:
        """Create a summary of the result for logging."""
        try:
            if result is None:
                return None
            
            # Simple summarization
            result_str = str(result)
            if len(result_str) > 200:
                return result_str[:200] + "..."
            return result_str
            
        except Exception:
            return "<error serializing result>"
    
    def update_config(self, config_data: Dict[str, Any]) -> None:
        """Update remote configuration."""
        try:
            self.config.update_from_dict(config_data)
            self.logger.info("Updated trace configuration")
        except Exception as e:
            self.logger.error(f"Error updating config: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracing statistics."""
        with self._lock:
            return {
                'buffer_size': self.buffer.size(),
                'active_traces': len(self._active_traces),
                'config': {
                    'enabled': self.config.enabled,
                    'sampling_rate': self.config.sampling_rate,
                    'excluded_tools': self.config.excluded_tools
                }
            }
    
    def flush(self) -> int:
        """Force flush of buffered events. Returns number of events flushed."""
        events = self.buffer.flush(force=True)
        return len(events)
    
    def shutdown(self) -> None:
        """Shutdown the trace manager."""
        try:
            # Flush any remaining events
            self.flush()
            
            # Shutdown buffer
            self.buffer.shutdown()
            
            self.logger.info("Trace manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Global trace manager instance
_trace_manager: Optional[TraceManager] = None
_manager_lock = threading.Lock()


def get_trace_manager() -> TraceManager:
    """Get or create the global trace manager."""
    global _trace_manager
    
    if _trace_manager is None:
        with _manager_lock:
            if _trace_manager is None:
                _trace_manager = TraceManager()
    
    return _trace_manager


def configure_trace_manager(
    transport: Optional[HTTPTransport] = None,
    config: Optional[RemoteConfig] = None,
    file_path: Optional[str] = None,
    **kwargs
) -> TraceManager:
    """Configure the global trace manager."""
    global _trace_manager
    
    with _manager_lock:
        _trace_manager = TraceManager(
            transport=transport,
            config=config,
            file_path=file_path,
            **kwargs
        )
    
    return _trace_manager
