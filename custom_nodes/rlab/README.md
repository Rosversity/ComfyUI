# RLab Custom Nodes for ComfyUI

This directory contains the pneumatic kit nodes for ComfyUI, providing digital twin workflow capabilities.

## Structure

```
rlab/
├── __init__.py              # Package initialization
└── pneumatic_kit/           # Pneumatic kit nodes
    ├── __init__.py
    └── nodes/               # ComfyUI custom nodes
        ├── asset_nodes.py
        ├── config_nodes.py
        ├── generator_node.py
        ├── system_nodes.py
        ├── widget_nodes.py
        ├── base_node.py
        └── web/             # Frontend JavaScript
            └── js/
                └── pneumatic_kit_badge.js
```

## Separation from rlabSDK

The generators (code generation tools) remain in the rlabSDK repository:
- `rlabSDK/comfy/pneumatic_kit/generators/` - Code generation tools for C++ output

This separation allows:
1. ComfyUI to build independently without rlabSDK dependency
2. Generators to be used by other tools/workflows
3. Cleaner deployment in Docker containers
4. Easier maintenance and version control

## Installation

These nodes are automatically loaded by ComfyUI when the container starts.

## Web Extensions

The web extension is located at:
- `ComfyUI/web/extensions/rlab_generate.js`
