"""
Event Buffer Management

Provides thread-safe buffering of analytics events with automatic flushing.
"""

import threading
import queue
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from .models import AnalyticsEvent


class EventBuffer:
    """Thread-safe buffer for analytics events with automatic flushing."""
    
    def __init__(
        self,
        max_size: int = 100,
        flush_interval: float = 30.0,
        auto_flush: bool = True
    ):
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.auto_flush = auto_flush
        
        self._buffer: queue.Queue = queue.Queue(maxsize=max_size * 2)  # Double size to reduce contention
        self._lock = threading.RLock()
        self._last_flush = time.time()
        self._flush_callbacks: List[callable] = []
        
        # Auto-flush timer
        self._flush_timer: Optional[threading.Timer] = None
        if auto_flush:
            self._start_flush_timer()
        
        self.logger = logging.getLogger(__name__)
    
    def add_event(self, event: AnalyticsEvent) -> bool:
        """
        Add event to buffer.
        
        Returns True if added successfully, False if buffer is full.
        """
        try:
            # Non-blocking put with immediate return if full
            self._buffer.put_nowait(event)
            self.logger.debug(f"Added event to buffer: {event.event_type}")
            
            # Check if we need to flush due to size
            if self._buffer.qsize() >= self.max_size:
                self._trigger_flush("size_limit")
            
            return True
            
        except queue.Full:
            self.logger.warning("Event buffer is full, dropping event")
            return False
    
    def get_events(self, max_count: Optional[int] = None) -> List[AnalyticsEvent]:
        """
        Get events from buffer without removing them.
        """
        events = []
        temp_events = []
        # I know this kinda sound stupid , but we need to use a temporary list to avoid modifying the buffer while iterating
        # over it, we will need to revisit this anyways.
        # Get events up to max_count
        count = 0
        try:
            while not self._buffer.empty():
                if max_count and count >= max_count:
                    break
                
                event = self._buffer.get_nowait()
                events.append(event)
                temp_events.append(event)
                count += 1
                
        except queue.Empty:
            pass
        
        # Put events back
        for event in temp_events:
            try:
                self._buffer.put_nowait(event)
            except queue.Full:
                self.logger.warning("Lost event during buffer peek operation")
        
        return events
    
    def flush(self, force: bool = False) -> List[AnalyticsEvent]:
        """
        Flush events from buffer.
        
        Returns list of events that were flushed.
        """
        with self._lock:
            now = time.time()
            
            # Check if we should flush
            time_to_flush = (now - self._last_flush) >= self.flush_interval
            size_to_flush = self._buffer.qsize() >= self.max_size
            
            if not (force or time_to_flush or size_to_flush):
                return []
            
            # Collect all events
            events = []
            while not self._buffer.empty():
                try:
                    events.append(self._buffer.get_nowait())
                except queue.Empty:
                    break
            
            if events:
                self.logger.debug(f"Flushing {len(events)} events from buffer")
                self._last_flush = now
                
                # Call flush callbacks
                for callback in self._flush_callbacks:
                    try:
                        callback(events.copy())
                    except Exception as e:
                        self.logger.error(f"Error in flush callback: {e}")
            
            return events
    
    def add_flush_callback(self, callback: callable) -> None:
        """Add callback to be called when events are flushed."""
        self._flush_callbacks.append(callback)
    
    def remove_flush_callback(self, callback: callable) -> None:
        """Remove flush callback."""
        if callback in self._flush_callbacks:
            self._flush_callbacks.remove(callback)
    
    def _trigger_flush(self, reason: str) -> None:
        """Trigger flush in background thread."""
        def flush_worker():
            try:
                events = self.flush(force=True)
                if events:
                    self.logger.debug(f"Auto-flushed {len(events)} events (reason: {reason})")
            except Exception as e:
                self.logger.error(f"Error during auto-flush: {e}")
        
        thread = threading.Thread(target=flush_worker, daemon=True)
        thread.start()
    
    def _start_flush_timer(self) -> None:
        """Start the auto-flush timer."""
        
        ## @todo @mark or anyone , corner case here like what if timer clashes with retry 
        ## for failed events we might need to manage both through an orchastrator as well
        if self._flush_timer:
            self._flush_timer.cancel()
        
        def timer_callback():
            self._trigger_flush("timer")
            if self.auto_flush:
                self._start_flush_timer()
        
        self._flush_timer = threading.Timer(self.flush_interval, timer_callback)
        self._flush_timer.daemon = True
        self._flush_timer.start()
    
    def size(self) -> int:
        """Get current buffer size."""
        return self._buffer.qsize()
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return self._buffer.empty()
    
    def clear(self) -> int:
        """Clear all events from buffer. Returns number of events cleared."""
        count = 0
        while not self._buffer.empty():
            try:
                self._buffer.get_nowait()
                count += 1
            except queue.Empty:
                break
        return count
    
    def shutdown(self) -> List[AnalyticsEvent]:
        """Shutdown buffer and return any remaining events."""
        if self._flush_timer:
            self._flush_timer.cancel()
            self._flush_timer = None
        
        # Flush any remaining events
        return self.flush(force=True)
