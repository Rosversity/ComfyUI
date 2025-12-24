"""
ComfyUI nodes for PneumaticKit digital twin.

This package contains pneumatic-kit specific ComfyUI custom nodes:
- Nodes: Custom nodes for pneumatic systems and assets
- Web: Frontend JavaScript extensions

Note: Generators (code generation tools) are located in rlabSDK repository
"""

from . import nodes

# Export NODE_CLASS_MAPPINGS for ComfyUI
NODE_CLASS_MAPPINGS = nodes.NODE_CLASS_MAPPINGS
NODE_DISPLAY_NAME_MAPPINGS = getattr(nodes, 'NODE_DISPLAY_NAME_MAPPINGS', {})

__all__ = ['nodes', 'NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
