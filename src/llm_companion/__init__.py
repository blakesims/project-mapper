"""LLM Project Companion - Automated project documentation for LLM-assisted development."""

from .core import ProjectScanner
from .cursorrules_manager import CursorRulesManager

__version__ = "0.0.1"
__all__ = ["ProjectScanner", "CursorRulesManager"] 