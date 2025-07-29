"""
Trace Context Management

Provides thread-local context management for trace state and metadata.
"""

import threading
from contextvars import ContextVar
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class TraceContext(BaseModel):
    """Thread-local context for trace execution with validation."""
    
    trace_id: str = Field(..., min_length=1, max_length=255, description="Unique identifier for this trace")
    tool_name: str = Field(..., min_length=1, max_length=255, description="Name of the tool being traced")
    started_at: datetime = Field(..., description="When the trace started")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional trace metadata")
    parent_trace_id: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Parent trace ID for nested calls")
    
    @field_validator('tool_name')
    @classmethod
    def validate_tool_name(cls, v: str) -> str:
        """Validate tool name follows conventions."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Tool name must contain only alphanumeric characters, hyphens, and underscores")
        return v
    
    @field_validator('trace_id', 'parent_trace_id')
    @classmethod 
    def validate_trace_ids(cls, v: Optional[str]) -> Optional[str]:
        """Validate trace IDs are not empty strings."""
        if v is not None and v.strip() == "":
            raise ValueError("Trace ID cannot be empty")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for event creation."""
        data = self.model_dump()
        # Convert datetime to ISO string for serialization
        data['started_at'] = self.started_at.isoformat()
        return data
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"  # Don't allow extra fields
        validate_assignment = True  # Validate when fields are modified


class TraceContextManager:
    """Manages trace context using context variables for async/thread safety."""
    
    def __init__(self):
        self._context: ContextVar[Optional[TraceContext]] = ContextVar(
            'trace_context', 
            default=None
        )
    
    def get_current_context(self) -> Optional[TraceContext]:
        """Get the current trace context."""
        return self._context.get()
    
    def set_context(self, context: TraceContext) -> None:
        """Set the current trace context."""
        self._context.set(context)
    
    def clear_context(self) -> None:
        """Clear the current trace context."""
        self._context.set(None)
    
    def is_tracing(self) -> bool:
        """Check if currently within a trace context."""
        return self._context.get() is not None
    
    def get_trace_id(self) -> Optional[str]:
        """Get current trace ID if available."""
        context = self.get_current_context()
        return context.trace_id if context else None
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to current context if available."""
        context = self.get_current_context()
        if context:
            context.metadata[key] = value


# Global context manager instance
_context_manager = TraceContextManager()


def get_current_context() -> Optional[TraceContext]:
    """Get the current trace context."""
    return _context_manager.get_current_context()


def set_context(context: TraceContext) -> None:
    """Set the current trace context."""
    _context_manager.set_context(context)


def clear_context() -> None:
    """Clear the current trace context."""
    _context_manager.clear_context()


def is_tracing() -> bool:
    """Check if currently within a trace context."""
    return _context_manager.is_tracing()


def get_trace_id() -> Optional[str]:
    """Get current trace ID if available."""
    return _context_manager.get_trace_id()


def add_metadata(key: str, value: Any) -> None:
    """Add metadata to current context if available."""
    _context_manager.add_metadata(key, value)
