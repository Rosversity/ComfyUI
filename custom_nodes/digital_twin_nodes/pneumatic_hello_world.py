"""
Pneumatic Hello World - Complete Implementation
Based on the specified workflow with shadow functions
"""
import asyncio
import time
import json
from typing import Dict, Any
from .state_manager import DigitalTwinStateManager
from .shadow_api import ShadowAPIFunction, ShadowAPIRegistry


class PneumaticControlSystem:
    """
    Control System Node - Manages timing and control flow

    Shadow Functions:
    1. on_button_press - Start timer, send signal to electrical
    2. on_sac_feedback - Stop timer, calculate duration, update display
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_id": ("STRING", {"default": "control_system_01"}),
            },
            "optional": {
                "button_pressed": ("BOOLEAN", {"default": False}),
                "sac_feedback": ("BOOLEAN", {"default": False}),
                "input_flow": ("DT_FLOW",),
            }
        }

    RETURN_TYPES = ("DT_FLOW", "BOOLEAN", "STRING", "FLOAT")
    RETURN_NAMES = ("output_flow", "send_signal_to_electrical", "timer_display", "duration_ms")
    FUNCTION = "execute"
    CATEGORY = "Digital Twin/Pneumatic Hello World"

    def execute(self, system_id, button_pressed=False, sac_feedback=False, input_flow=None):
        """Execute control system with shadow functions"""

        state_manager = DigitalTwinStateManager()

        # Get system state
        system_state = state_manager.get("systems", system_id, {
            "start_time": 0,
            "end_time": 0,
            "running": False,
            "duration": 0
        })

        send_signal = False
        timer_display = "Idle"
        duration = 0.0

        # Shadow Function 1: on_button_press
        if button_pressed and not system_state["running"]:
            # Start timer
            system_state["start_time"] = time.time() * 1000  # ms
            system_state["running"] = True
            send_signal = True  # Trigger output to electrical
            timer_display = "Cycle Started"
            print(f"[{system_id}] Shadow Fn: on_button_press - Timer started")

        # Shadow Function 2: on_sac_feedback
        elif sac_feedback and system_state["running"]:
            # Stop timer
            system_state["end_time"] = time.time() * 1000
            duration = system_state["end_time"] - system_state["start_time"]
            system_state["duration"] = duration
            system_state["running"] = False
            timer_display = f"Cycle Complete: {int(duration)} ms"
            print(f"[{system_id}] Shadow Fn: on_sac_feedback - Duration: {int(duration)} ms")

        # Update state
        state_manager.set("systems", system_id, system_state)

        flow = {
            "type": "control_system_flow",
            "system_id": system_id,
            "timestamp": time.time()
        }

        return (flow, send_signal, timer_display, duration)


class PneumaticElectricalSystem:
    """
    Electrical System Node - Power gating logic

    Shadow Function:
    1. check_power_conditions - AND logic for control signal + cable connection
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_id": ("STRING", {"default": "electrical_01"}),
            },
            "optional": {
                "input_control_signal": ("BOOLEAN", {"default": False}),
                "input_cable_connected": ("BOOLEAN", {"default": False}),
                "input_flow": ("DT_FLOW",),
            }
        }

    RETURN_TYPES = ("DT_FLOW", "BOOLEAN")
    RETURN_NAMES = ("output_flow", "pass_power")
    FUNCTION = "execute"
    CATEGORY = "Digital Twin/Pneumatic Hello World"

    def execute(self, system_id, input_control_signal=False, input_cable_connected=False, input_flow=None):
        """Execute electrical system with shadow function"""

        # Shadow Function: check_power_conditions
        # IF (Input_Control == TRUE) AND (Input_Cable == CONNECTED)
        pass_power = input_control_signal and input_cable_connected

        if pass_power:
            print(f"[{system_id}] Shadow Fn: check_power_conditions - PASS (Power ON)")
        else:
            print(f"[{system_id}] Shadow Fn: check_power_conditions - BLOCK (Power OFF)")

        flow = {
            "type": "electrical_flow",
            "system_id": system_id,
            "power_state": pass_power,
            "timestamp": time.time()
        }

        return (flow, pass_power)


class PneumaticAirSystem:
    """
    Pneumatic System Node - Air supply control

    Shadow Function:
    1. supply_air - Check power and supply air if enabled
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_id": ("STRING", {"default": "pneumatic_01"}),
            },
            "optional": {
                "input_power": ("BOOLEAN", {"default": False}),
                "air_pressure_psi": ("FLOAT", {"default": 80.0, "min": 0, "max": 150}),
                "input_flow": ("DT_FLOW",),
            }
        }

    RETURN_TYPES = ("DT_FLOW", "BOOLEAN", "FLOAT")
    RETURN_NAMES = ("output_flow", "supply_air", "pressure_psi")
    FUNCTION = "execute"
    CATEGORY = "Digital Twin/Pneumatic Hello World"

    def execute(self, system_id, input_power=False, air_pressure_psi=80.0, input_flow=None):
        """Execute pneumatic system with shadow function"""

        # Shadow Function: supply_air
        # IF (Input_Power == TRUE)
        supply_air = input_power

        if supply_air:
            print(f"[{system_id}] Shadow Fn: supply_air - Air supplied at {air_pressure_psi} PSI")
        else:
            print(f"[{system_id}] Shadow Fn: supply_air - No air supply")

        flow = {
            "type": "pneumatic_flow",
            "system_id": system_id,
            "air_supply": supply_air,
            "pressure": air_pressure_psi,
            "timestamp": time.time()
        }

        return (flow, supply_air, air_pressure_psi)


class PneumaticSSVAsset:
    """
    SSV Asset (Solenoid Switching Valve) Node

    Shadow Function:
    1. actuate_valve - Open valve when air supplied
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_id": ("STRING", {"default": "SSV_001"}),
            },
            "optional": {
                "input_air_supply": ("BOOLEAN", {"default": False}),
                "input_flow": ("DT_FLOW",),
            }
        }

    RETURN_TYPES = ("DT_FLOW", "BOOLEAN", "STRING")
    RETURN_NAMES = ("output_flow", "actuate_cylinder", "valve_state")
    FUNCTION = "execute"
    CATEGORY = "Digital Twin/Pneumatic Hello World"

    def execute(self, asset_id, input_air_supply=False, input_flow=None):
        """Execute SSV asset with shadow function"""

        # Shadow Function: actuate_valve
        if input_air_supply:
            valve_state = "OPEN"
            actuate_cylinder = True
            print(f"[{asset_id}] Shadow Fn: actuate_valve - Valve OPENED")
        else:
            valve_state = "CLOSED"
            actuate_cylinder = False
            print(f"[{asset_id}] Shadow Fn: actuate_valve - Valve CLOSED")

        flow = {
            "type": "ssv_flow",
            "asset_id": asset_id,
            "valve_state": valve_state,
            "timestamp": time.time()
        }

        return (flow, actuate_cylinder, valve_state)


class PneumaticSACAsset:
    """
    SAC Asset (Single Acting Cylinder) Node

    Shadow Functions:
    1. extend_cylinder - Play animation, wait for duration, report completion
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_id": ("STRING", {"default": "SAC_001"}),
                "extension_time_ms": ("FLOAT", {"default": 2000, "min": 100, "max": 10000}),
            },
            "optional": {
                "input_actuate": ("BOOLEAN", {"default": False}),
                "model_path": ("STRING", {"default": "/models/cylinder.stl"}),
                "input_flow": ("DT_FLOW",),
            }
        }

    RETURN_TYPES = ("DT_FLOW", "BOOLEAN", "FLOAT", "STRING")
    RETURN_NAMES = ("output_flow", "report_completion", "position_mm", "animation_state")
    FUNCTION = "execute"
    CATEGORY = "Digital Twin/Pneumatic Hello World"

    async def execute(self, asset_id, extension_time_ms, input_actuate=False,
                     model_path="", input_flow=None):
        """Execute SAC asset with shadow function"""

        report_completion = False
        position_mm = 0.0
        animation_state = "Idle"

        # Shadow Function: extend_cylinder
        if input_actuate:
            animation_state = "Extending"
            print(f"[{asset_id}] Shadow Fn: extend_cylinder - Playing animation 'Extend_Cylinder'")

            # Play animation (send to 3D widget)
            # This would trigger the 3D viewer to animate

            # Wait for animation duration
            print(f"[{asset_id}] Shadow Fn: extend_cylinder - Waiting {extension_time_ms} ms")
            await asyncio.sleep(extension_time_ms / 1000)

            # Cylinder fully extended
            position_mm = 200.0
            animation_state = "Extended"
            report_completion = True

            print(f"[{asset_id}] Shadow Fn: extend_cylinder - Extension complete, reporting back")

        flow = {
            "type": "sac_flow",
            "asset_id": asset_id,
            "position": position_mm,
            "state": animation_state,
            "timestamp": time.time()
        }

        return (flow, report_completion, position_mm, animation_state)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "Pneumatic_ControlSystem": PneumaticControlSystem,
    "Pneumatic_ElectricalSystem": PneumaticElectricalSystem,
    "Pneumatic_AirSystem": PneumaticAirSystem,
    "Pneumatic_SSVAsset": PneumaticSSVAsset,
    "Pneumatic_SACAsset": PneumaticSACAsset,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Pneumatic_ControlSystem": "🎛️ Control System",
    "Pneumatic_ElectricalSystem": "⚡ Electrical System",
    "Pneumatic_AirSystem": "💨 Pneumatic System",
    "Pneumatic_SSVAsset": "🔄 SSV Asset (Valve)",
    "Pneumatic_SACAsset": "🔧 SAC Asset (Cylinder)",
}
