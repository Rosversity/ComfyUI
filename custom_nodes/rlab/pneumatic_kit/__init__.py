"""
Comfy nodes and generators for PneumaticKit digital twin.

This package contains all pneumatic-kit specific comfy functionality:
- Generators: Process code generators from workflow definitions
- Nodes: Custom nodes for pneumatic systems and assets
"""

from . import nodes
from . import generators

# Export NODE_CLASS_MAPPINGS for ComfyUI
NODE_CLASS_MAPPINGS = nodes.NODE_CLASS_MAPPINGS
NODE_DISPLAY_NAME_MAPPINGS = getattr(nodes, 'NODE_DISPLAY_NAME_MAPPINGS', {})

__all__ = ['nodes', 'generators', 'NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
