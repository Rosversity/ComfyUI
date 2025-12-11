"""
Multi-Shadow Function Base Node
Allows nodes to have multiple shadow functions with dynamic inputs/outputs
"""
import json
import asyncio
from typing import Dict, List, Any, Tuple
from .shadow_api import ShadowAPIFunction, ShadowAPIRegistry


class MultiShadowBaseNode:
    """
    Base class for digital twin nodes with multiple shadow functions

    Shadow functions are configured as a JSON parameter:
    {
        "functions": [
            {
                "name": "read_sensor",
                "inputs": ["temp", "pressure"],
                "output": "sensor_data",
                "code": "async def execute(**kwargs): ..."
            },
            {
                "name": "write_actuator",
                "inputs": ["position"],
                "output": "actuator_status",
                "code": "async def execute(**kwargs): ..."
            }
        ]
    }

    Node inputs are matched to shadow function inputs by name.
    Node outputs are the outputs from all shadow functions.
    """

    @classmethod
    def get_shadow_function_config_param(cls):
        """
        Returns the parameter definition for shadow functions configuration

        Add this to your INPUT_TYPES "optional" section
        """
        return ("STRING", {
            "default": json.dumps({
                "functions": [
                    {
                        "name": "default_function",
                        "inputs": ["input_value"],
                        "output": "result",
                        "input_types": {"input_value": "FLOAT"},
                        "output_type": "FLOAT",
                        "code": """async def execute(**kwargs):
    # Default shadow function
    return {"result": kwargs.get("input_value", 0.0)}
"""
                    }
                ]
            }, indent=2),
            "multiline": True
        })

    def __init__(self):
        """Initialize multi-shadow node"""
        self.shadow_functions = {}
        self.function_config = None

    def setup_shadow_functions(self, config_json: str, node_id: str):
        """
        Setup shadow functions from JSON configuration

        Args:
            config_json: JSON string with shadow function definitions
            node_id: Unique identifier for this node instance
        """
        try:
            config = json.loads(config_json)
        except:
            config = {"functions": []}

        self.function_config = config
        registry = ShadowAPIRegistry()

        # Create shadow API for each function
        for func_def in config.get("functions", []):
            func_name = func_def.get("name", "unnamed")
            func_node_id = f"{node_id}_{func_name}"

            # Build input args from definition
            input_names = func_def.get("inputs", [])
            input_types = func_def.get("input_types", {})

            input_args = [
                {
                    "name": inp,
                    "type": input_types.get(inp, "any")
                }
                for inp in input_names
            ]

            # Create shadow API function
            shadow_func = ShadowAPIFunction(
                name=func_name,
                input_args=input_args,
                return_type=func_def.get("output_type", "dict"),
                code=func_def.get("code", ""),
                node_id=func_node_id
            )

            # Register
            registry.register(func_node_id, shadow_func)
            self.shadow_functions[func_name] = shadow_func

    async def execute_shadow_functions(self, **node_inputs) -> Dict[str, Any]:
        """
        Execute all shadow functions with appropriate inputs

        Args:
            **node_inputs: All inputs to the node

        Returns:
            Dict mapping output names to values
        """
        results = {}

        for func_def in self.function_config.get("functions", []):
            func_name = func_def.get("name")
            shadow_func = self.shadow_functions.get(func_name)

            if not shadow_func:
                continue

            # Extract inputs for this function
            func_inputs = {}
            for input_name in func_def.get("inputs", []):
                if input_name in node_inputs:
                    func_inputs[input_name] = node_inputs[input_name]

            # Execute function
            try:
                result = await shadow_func.execute(**func_inputs)

                # Store output
                output_name = func_def.get("output", func_name + "_output")
                results[output_name] = result

            except Exception as e:
                print(f"[MultiShadow] Error executing {func_name}: {e}")
                results[func_def.get("output", func_name + "_output")] = {
                    "error": str(e)
                }

        return results

    def get_output_mapping(self) -> List[str]:
        """
        Get list of output names based on shadow function configuration

        Returns:
            List of output names
        """
        if not self.function_config:
            return ["output"]

        return [
            func.get("output", func.get("name") + "_output")
            for func in self.function_config.get("functions", [])
        ]


# Example usage in a node
class DT_ControlSystem(MultiShadowBaseNode):
    """
    Control System node with multiple shadow functions
    Users can configure Read/Write/Calculate functions
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "node_id": ("STRING", {"default": "control_system_01"}),
            },
            "optional": {
                # Generic inputs - will be mapped to shadow functions
                "input_1": ("FLOAT", {"default": 0.0}),
                "input_2": ("FLOAT", {"default": 0.0}),
                "input_3": ("FLOAT", {"default": 0.0}),
                "input_4": ("BOOLEAN", {"default": False}),
                "input_5": ("STRING", {"default": ""}),

                "input_flow": ("DT_FLOW",),

                # Shadow functions configuration
                "shadow_functions_config": cls.get_shadow_function_config_param(),
            }
        }

    # Output types - generic, will be mapped based on shadow functions
    RETURN_TYPES = ("DT_FLOW", "*", "*", "*", "*", "*")
    RETURN_NAMES = ("output_flow", "output_1", "output_2", "output_3", "output_4", "output_5")
    FUNCTION = "execute"
    CATEGORY = "Digital Twin/Control Systems"

    async def execute(self, node_id,
                     input_1=0.0, input_2=0.0, input_3=0.0,
                     input_4=False, input_5="",
                     input_flow=None,
                     shadow_functions_config="{}"):
        """Execute control system with shadow functions"""

        # Setup shadow functions
        self.setup_shadow_functions(shadow_functions_config, node_id)

        # Prepare inputs (using naming convention from config)
        node_inputs = {
            "input_1": input_1,
            "input_2": input_2,
            "input_3": input_3,
            "input_4": input_4,
            "input_5": input_5,
        }

        # Also support direct parameter names from shadow function inputs
        # Users can map: input_1 → temp, input_2 → pressure, etc.
        config = json.loads(shadow_functions_config) if shadow_functions_config else {}

        # Create mapping from input slots to shadow function parameter names
        input_mapping = config.get("input_mapping", {})
        # Example: {"input_1": "temp", "input_2": "pressure"}

        mapped_inputs = {}
        for slot_name, param_name in input_mapping.items():
            if slot_name in node_inputs:
                mapped_inputs[param_name] = node_inputs[slot_name]

        # Execute all shadow functions
        results = await self.execute_shadow_functions(**mapped_inputs)

        # Build flow data
        flow = {
            "type": "control_system_flow",
            "node_id": node_id,
            "shadow_functions": list(self.shadow_functions.keys()),
            "previous_flow": input_flow,
        }

        # Extract outputs in order
        output_names = self.get_output_mapping()
        outputs = [results.get(name, None) for name in output_names]

        # Pad with None if fewer outputs than slots
        while len(outputs) < 5:
            outputs.append(None)

        return (flow, *outputs[:5])


# Node mappings
NODE_CLASS_MAPPINGS = {
    "DT_ControlSystem": DT_ControlSystem,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DT_ControlSystem": "🎛️ Control System (Multi-Shadow)",
}
