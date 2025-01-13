"""Project documentation mapper for LLM-assisted development."""

from .core import BaseScanner
from .adapters import PythonScanner
from .core.xml_manager import XMLManager

__version__ = "0.0.1"
__all__ = ["BaseScanner", "PythonScanner", "XMLManager"] 