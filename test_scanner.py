"""Test script for the LLM Project Companion."""

from pathlib import Path
from llm_companion import ProjectScanner

def main():
    """Run the project scanner on the current directory."""
    project_root = Path.cwd()
    scanner = ProjectScanner(project_root)
    
    print("Scanning project structure...")
    structure = scanner.scan_project()
    
    print("\nFound structure:")
    print_structure(structure)
    
    print("\nUpdating .cursorrules file...")
    scanner.update_cursorrules(structure)
    print("Done!")

def print_structure(structure, indent=""):
    """Print the project structure in a readable format."""
    for key, value in structure.items():
        if isinstance(value, dict):
            print(f"{indent}{key}/")
            print_structure(value, indent + "  ")
        else:
            print(f"{indent}{key}: {value.splitlines()[0]}")

if __name__ == "__main__":
    main() 