"""
Core components for the tinyAgent framework.

This package contains the core components of the tinyAgent framework, including
the Agent class, Tool framework, configuration management, and utilities.
"""

try:
    from ._version import __version__
except ImportError:
    # This happens during development or if setuptools_scm is not installed
    __version__ = "0.0.0.dev0"  # Default or placeholder version

from .decorators import tool
from .exceptions import (
    AgentNotFoundError,
    AgentRetryExceeded,
    ConfigurationError,
    OrchestratorError,
    ParsingError,
    RateLimitExceeded,
    TinyAgentError,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
)
from .react.react_agent import ReactAgent
from .tool import ParamType, Tool

__all__ = [
    "Tool",
    "ParamType",
    "tool",
    "ReactAgent",
    "TinyAgentError",
    "ConfigurationError",
    "ToolError",
    "ToolNotFoundError",
    "ToolExecutionError",
    "RateLimitExceeded",
    "ParsingError",
    "AgentRetryExceeded",
    "OrchestratorError",
    "AgentNotFoundError",
    "__version__",
]
