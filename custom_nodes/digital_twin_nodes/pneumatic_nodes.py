"""
Pneumatic Hello World - Digital Twin Nodes with Editable Shadow APIs
"""
import asyncio
import time
import json
from .state_manager import DigitalTwinStateManager
from .shadow_api import ShadowAPIFunction, ShadowAPIRegistry, ShadowAPIMode
from server import PromptServer


class DT_L1_PneumaticCylinder:
    """
    Level 1 Component Twin - Pneumatic Cylinder
    Includes editable Shadow API for component control
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "component_id": ("STRING", {"default": "SAC_CYL_001"}),
                "air_pressure_psi": ("FLOAT", {"default": 80.0, "min": 0, "max": 150}),
                "extend_command": ("BOOLEAN", {"default": False}),
                "extension_time_ms": ("FLOAT", {"default": 2000, "min": 100, "max": 10000}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
                # Shadow API configuration
                "shadow_api_enabled": ("BOOLEAN", {"default": True}),
                "shadow_api_definition": ("STRING", {
                    "default": json.dumps({
                        "function_name": "control_cylinder",
                        "input_args": [
                            {"name": "component_id", "type": "str"},
                            {"name": "action", "type": "str"},
                            {"name": "pressure", "type": "float"}
                        ],
                        "return_type": "dict",
                        "code": ""  # Will use default
                    }, indent=2),
                    "multiline": True
                }),
            }
        }

    RETURN_TYPES = ("DT_FLOW", "DT_COMPONENT_STATE", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("output_flow", "cylinder_state", "position_mm", "is_extended")
    FUNCTION = "execute"
    CATEGORY = "Digital Twin/L1 Component/Pneumatic"
    DESCRIPTION = "Pneumatic cylinder with simulated physics and editable Shadow API"

    def __init__(self):
        self.shadow_api = None
        self.node_id = None

    async def execute(self, component_id, air_pressure_psi, extend_command, extension_time_ms,
                     input_flow=None, shadow_api_enabled=True, shadow_api_definition="{}"):
        """Execute cylinder operation with shadow API"""

        # Initialize shadow API if enabled
        if shadow_api_enabled:
            await self._setup_shadow_api(component_id, shadow_api_definition)

        # Call shadow API if available
        api_response = await self._call_shadow_api({
            "component_id": component_id,
            "action": "extend" if extend_command else "retract",
            "pressure": air_pressure_psi
        })

        # Simulate physical movement time
        if extend_command:
            print(f"[{component_id}] Extending cylinder... ({extension_time_ms}ms)")
            await asyncio.sleep(extension_time_ms / 1000)
            position = 200.0  # Fully extended (mm)
            is_extended = True
        else:
            print(f"[{component_id}] Retracting cylinder... ({extension_time_ms * 0.75}ms)")
            await asyncio.sleep(extension_time_ms * 0.75 / 1000)
            position = 0.0    # Retracted
            is_extended = False

        # Build component state
        state = {
            "component_id": component_id,
            "type": "pneumatic_cylinder",
            "position_mm": position,
            "pressure_psi": air_pressure_psi,
            "is_extended": is_extended,
            "health": api_response.get("health", "OK"),
            "timestamp": time.time(),
            "shadow_api_response": api_response
        }

        # Store in state manager
        state_manager = DigitalTwinStateManager()
        state_manager.set("components", component_id, state)

        # Create flow data
        flow = {
            "type": "component_flow",
            "component_id": component_id,
            "level": "L1",
            "action": "extend" if extend_command else "retract",
            "previous_flow": input_flow,
            "timestamp": time.time()
        }

        # Send WebSocket update for 3D visualization
        await self._send_widget_update(component_id, state, "extend" if extend_command else "retract")

        return (flow, state, position, is_extended)

    async def _setup_shadow_api(self, component_id, api_definition_str):
        """Setup shadow API from definition"""
        try:
            api_def = json.loads(api_definition_str)
        except:
            api_def = {}

        # Create shadow API
        self.node_id = f"pneumatic_cyl_{component_id}"
        registry = ShadowAPIRegistry()

        existing_api = registry.get(self.node_id)
        if existing_api:
            # Update existing
            existing_api.set_definition(api_def)
            self.shadow_api = existing_api
        else:
            # Create new with default code
            code = api_def.get("code", "") or self._get_default_shadow_api_code()
            self.shadow_api = ShadowAPIFunction(
                name=api_def.get("function_name", "control_cylinder"),
                input_args=api_def.get("input_args", []),
                return_type=api_def.get("return_type", "dict"),
                code=code,
                node_id=self.node_id
            )
            registry.register(self.node_id, self.shadow_api)

    def _get_default_shadow_api_code(self) -> str:
        """Default shadow API implementation"""
        return '''async def execute(**kwargs):
    """
    Shadow API for Pneumatic Cylinder Control

    Args:
        component_id: Cylinder identifier
        action: "extend" or "retract"
        pressure: Air pressure in PSI

    Returns:
        dict with status and health
    """
    import aiohttp
    import os

    mode = os.getenv("DT_MODE", "simulation")

    if mode == "simulation":
        # Simulation mode - return mock data
        return {
            "status": "success",
            "health": "OK",
            "simulated": True,
            "action": kwargs.get("action"),
            "pressure": kwargs.get("pressure")
        }

    elif mode == "production":
        # Production mode - call real PLC API
        async with aiohttp.ClientSession() as session:
            url = f"http://plc-{kwargs['component_id']}.local/api/actuate"
            async with session.post(url, json=kwargs) as resp:
                return await resp.json()

    return {"status": "error", "message": "Unknown mode"}
'''

    async def _call_shadow_api(self, data: dict) -> dict:
        """Call the shadow API"""
        if self.shadow_api:
            try:
                return await self.shadow_api.execute(**data)
            except Exception as e:
                return {"status": "error", "error": str(e)}
        return {"status": "no_api"}

    async def _send_widget_update(self, component_id, state, animation):
        """Send update to 3D widget"""
        try:
            server = PromptServer.instance
            await server.send_json("twin_widget_update", {
                "widget_type": "component_3d",
                "component_id": component_id,
                "state": state,
                "animation": animation
            })
        except:
            pass


class DT_L2_SAC_Asset:
    """
    Level 2 Asset Twin - Single Acting Cylinder (SAC) Asset
    Aggregates cylinder + valve + sensors with editable Shadow API
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "asset_id": ("STRING", {"default": "SAC_ASSET_001"}),
                "operation": (["EXTEND", "RETRACT", "HOLD"], {"default": "EXTEND"}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
                "cylinder_state": ("DT_COMPONENT_STATE",),
                "shadow_api_definition": ("STRING", {
                    "default": json.dumps({
                        "function_name": "control_sac_asset",
                        "input_args": [
                            {"name": "asset_id", "type": "str"},
                            {"name": "operation", "type": "str"}
                        ],
                        "return_type": "dict",
                        "code": ""
                    }, indent=2),
                    "multiline": True
                }),
            }
        }

    RETURN_TYPES = ("DT_FLOW", "DT_ASSET_STATE", "STRING")
    RETURN_NAMES = ("output_flow", "asset_state", "status_message")
    FUNCTION = "execute"
    CATEGORY = "Digital Twin/L2 Asset/Pneumatic"

    def __init__(self):
        self.shadow_api = None

    async def execute(self, asset_id, operation, input_flow=None,
                     cylinder_state=None, shadow_api_definition="{}"):
        """Execute SAC asset operation"""

        # Setup shadow API
        await self._setup_shadow_api(asset_id, shadow_api_definition)

        # Call shadow API
        api_response = await self._call_shadow_api({
            "asset_id": asset_id,
            "operation": operation,
            "cylinder_state": cylinder_state
        })

        # Build asset state (aggregates component states)
        state = {
            "asset_id": asset_id,
            "type": "sac_asset",
            "operation": operation,
            "cylinder_state": cylinder_state,
            "health": api_response.get("health", "OK"),
            "timestamp": time.time(),
            "shadow_api_response": api_response
        }

        # Store state
        state_manager = DigitalTwinStateManager()
        state_manager.set("assets", asset_id, state)

        flow = {
            "type": "asset_flow",
            "asset_id": asset_id,
            "level": "L2",
            "operation": operation,
            "previous_flow": input_flow,
            "timestamp": time.time()
        }

        status_msg = f"SAC Asset {asset_id}: {operation} operation completed"

        return (flow, state, status_msg)

    async def _setup_shadow_api(self, asset_id, api_definition_str):
        """Setup shadow API"""
        try:
            api_def = json.loads(api_definition_str)
        except:
            api_def = {}

        node_id = f"sac_asset_{asset_id}"
        registry = ShadowAPIRegistry()

        code = api_def.get("code", "") or self._get_default_shadow_api_code()
        self.shadow_api = ShadowAPIFunction(
            name=api_def.get("function_name", "control_sac_asset"),
            input_args=api_def.get("input_args", []),
            return_type=api_def.get("return_type", "dict"),
            code=code,
            node_id=node_id
        )
        registry.register(node_id, self.shadow_api)

    def _get_default_shadow_api_code(self) -> str:
        return '''async def execute(**kwargs):
    """Shadow API for SAC Asset Control"""
    return {
        "status": "success",
        "health": "OK",
        "operation": kwargs.get("operation")
    }
'''

    async def _call_shadow_api(self, data: dict) -> dict:
        if self.shadow_api:
            try:
                return await self.shadow_api.execute(**data)
            except Exception as e:
                return {"status": "error", "error": str(e)}
        return {"status": "no_api"}


class DT_Logic_Stopwatch:
    """
    Logic Node - Stopwatch timer for measuring cycle time
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "stopwatch_id": ("STRING", {"default": "stopwatch_01"}),
                "start_signal": ("BOOLEAN", {"default": False}),
                "stop_signal": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
            }
        }

    RETURN_TYPES = ("DT_FLOW", "FLOAT", "STRING")
    RETURN_NAMES = ("output_flow", "duration_ms", "status_message")
    FUNCTION = "calculate"
    CATEGORY = "Digital Twin/Logic"

    def calculate(self, stopwatch_id, start_signal, stop_signal, input_flow=None):
        """Calculate elapsed time"""
        state_manager = DigitalTwinStateManager()

        # Get stopwatch state
        stopwatch_state = state_manager.get("components", stopwatch_id, {
            "running": False,
            "start_time": 0,
            "duration": 0
        })

        current_time = time.time() * 1000  # Convert to ms

        if start_signal and not stopwatch_state["running"]:
            # Start timer
            stopwatch_state["start_time"] = current_time
            stopwatch_state["running"] = True
            stopwatch_state["duration"] = 0
            status = "Timer Started"
            duration = 0

        elif stop_signal and stopwatch_state["running"]:
            # Stop timer
            duration = current_time - stopwatch_state["start_time"]
            stopwatch_state["duration"] = duration
            stopwatch_state["running"] = False
            status = f"Cycle Time: {int(duration)} ms"

        elif stopwatch_state["running"]:
            # Timer running
            duration = current_time - stopwatch_state["start_time"]
            stopwatch_state["duration"] = duration
            status = f"Running: {int(duration)} ms"

        else:
            # Idle
            duration = stopwatch_state.get("duration", 0)
            status = "Idle"

        # Save state
        state_manager.set("components", stopwatch_id, stopwatch_state)

        flow = {
            "type": "logic_flow",
            "stopwatch_id": stopwatch_id,
            "previous_flow": input_flow,
            "timestamp": time.time()
        }

        return (flow, duration, status)


class DT_Logic_AND:
    """Logic AND gate"""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_a": ("BOOLEAN",),
                "input_b": ("BOOLEAN",),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("output",)
    FUNCTION = "compute"
    CATEGORY = "Digital Twin/Logic"

    def compute(self, input_a, input_b):
        return (input_a and input_b,)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "DT_L1_PneumaticCylinder": DT_L1_PneumaticCylinder,
    "DT_L2_SAC_Asset": DT_L2_SAC_Asset,
    "DT_Logic_Stopwatch": DT_Logic_Stopwatch,
    "DT_Logic_AND": DT_Logic_AND,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DT_L1_PneumaticCylinder": "L1: Pneumatic Cylinder",
    "DT_L2_SAC_Asset": "L2: SAC Asset",
    "DT_Logic_Stopwatch": "Logic: Stopwatch",
    "DT_Logic_AND": "Logic: AND Gate",
}
