"""
Antonnia Events SDK

This package provides event types and utilities for working with Antonnia webhook events.
"""

from .types import (
    # Event types
    Event,
    EventBase,
    MessageCreated,
    SessionCreated,
    SessionFinished,
    SessionTransferred,
    
    # App types
    App,
    AppConnection,
)

__version__ = "1.0.0"

__all__ = [
    # Event types
    "Event",
    "EventBase", 
    "MessageCreated",
    "SessionCreated",
    "SessionFinished",
    "SessionTransferred",
    
    # App types
    "App",
    "AppConnection",
] 