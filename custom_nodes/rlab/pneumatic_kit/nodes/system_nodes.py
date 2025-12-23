"""
System nodes for Digital Twin systems

These nodes represent system-level twins in the hierarchy:
- Control System (PLC, Ladder Logic, HMI)
- Electrical System (Power distribution, signals)
- Pneumatic System (Air pressure, flow control)
"""

from .base_node import RoslabSystemNode


class ControlSystemNode(RoslabSystemNode):
    """
    Control System Node

    Represents the Control System twin which manages:
    - PLC operations
    - Ladder logic execution
    - HMI button inputs
    - Process timing and state management
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_name": ("STRING", {
                    "default": "Control System",
                    "multiline": False
                }),
            },
            "optional": {
                "button_inputs": ("ROSLAB_TRIGGER",),
                "ladder_logic": ("ROSLAB_LADDER_LOGIC",),
                "process_config": ("ROSLAB_PROCESS_CONFIG",),
            }
        }

    RETURN_TYPES = ("ROSLAB_SYSTEM", "ROSLAB_DATA")

    RETURN_NAMES = ("control_system", "plc_outputs")

    def execute(self, system_name, button_inputs=None, ladder_logic=None, process_config=None):
        """
        Configure Control System

        Returns:
            tuple: (system configuration, PLC output signals)
        """
        system_config = {
            "type": "system",
            "system_type": "control",
            "name": system_name,
            "class_name": "ControlSystem",
            "shadow_class": "ControlSystemShadow",
            "implementor": "IControlSystemImplementor",
            "plugin": "libpneumatickit_controlsystem_impl.so",
            "has_plc": True,
            "inputs": {
                "button_triggers": button_inputs.get("source") if button_inputs else None,
                "ladder_logic": ladder_logic if ladder_logic else None
            },
            "initialization": {
                "requires": ["electrical_system", "ssv_asset"],
                "method": "Initialize",
                "ladder_logic_path": ladder_logic.get("file_path") if ladder_logic else None
            }
        }

        plc_outputs = {
            "type": "data",
            "source": "plc_outputs",
            "data_type": "signal",
            "signals": ["ssv_energize", "led_status"]
        }

        return (system_config, plc_outputs)


class ElectricalSystemNode(RoslabSystemNode):
    """
    Electrical System Node

    Represents the Electrical System twin which manages:
    - Power distribution
    - Signal routing
    - Voltage/current monitoring
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_name": ("STRING", {
                    "default": "Electrical System",
                    "multiline": False
                }),
            },
            "optional": {
                "control_signals": ("ROSLAB_DATA",),
                "voltage": ("FLOAT", {
                    "default": 24.0,
                    "min": 0.0,
                    "max": 240.0
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_SYSTEM", "ROSLAB_DATA")

    RETURN_NAMES = ("electrical_system", "power_signals")

    def execute(self, system_name, control_signals=None, voltage=24.0):
        """
        Configure Electrical System

        Returns:
            tuple: (system configuration, power signal outputs)
        """
        system_config = {
            "type": "system",
            "system_type": "electrical",
            "name": system_name,
            "class_name": "ElectricalSystem",
            "shadow_class": "ElectricalSystemShadow",
            "implementor": "IElectricalSystemImplementor",
            "plugin": "libpneumatickit_electricalsystem_impl.so",
            "inputs": {
                "control_signals": control_signals.get("source") if control_signals else None
            },
            "parameters": {
                "voltage": voltage
            },
            "initialization": {
                "requires": ["pneumatic_system"],
                "method": "Initialize"
            }
        }

        power_signals = {
            "type": "data",
            "source": "power_signals",
            "data_type": "signal",
            "signals": ["valve_power", "sensor_power"]
        }

        return (system_config, power_signals)


class PneumaticSystemNode(RoslabSystemNode):
    """
    Pneumatic System Node

    Represents the Pneumatic System twin which manages:
    - Compressed air distribution
    - Pressure regulation
    - Flow control
    - Valve and cylinder coordination
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_name": ("STRING", {
                    "default": "Pneumatic System",
                    "multiline": False
                }),
                "supply_pressure": ("FLOAT", {
                    "default": 6.0,
                    "min": 0.0,
                    "max": 10.0
                }),
            },
            "optional": {
                "electrical_signals": ("ROSLAB_DATA",),
                "flow_rate": ("FLOAT", {
                    "default": 100.0,
                    "min": 0.0,
                    "max": 1000.0
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_SYSTEM", "ROSLAB_DATA")

    RETURN_NAMES = ("pneumatic_system", "air_flow")

    def execute(self, system_name, supply_pressure, electrical_signals=None, flow_rate=100.0):
        """
        Configure Pneumatic System

        Returns:
            tuple: (system configuration, air flow data outputs)
        """
        system_config = {
            "type": "system",
            "system_type": "pneumatic",
            "name": system_name,
            "class_name": "PneumaticSystem",
            "shadow_class": "PneumaticSystemShadow",
            "implementor": "IPneumaticSystemImplementor",
            "plugin": "libpneumatickit_pneumaticsystem_impl.so",
            "inputs": {
                "electrical_signals": electrical_signals.get("source") if electrical_signals else None
            },
            "parameters": {
                "supply_pressure_bar": supply_pressure,
                "flow_rate_lpm": flow_rate
            },
            "initialization": {
                "requires": ["ssv_asset"],  # Can have multiple valves
                "method": "Initialize",
                "assets_list": True  # Takes a vector of assets
            }
        }

        air_flow = {
            "type": "data",
            "source": "air_flow",
            "data_type": "physical",
            "measurements": ["pressure", "flow_rate", "temperature"]
        }

        return (system_config, air_flow)


# Node class mappings for registration
NODE_CLASS_MAPPINGS = {
    "pneumatic-kitControlSystem": ControlSystemNode,
    "pneumatic-kitElectricalSystem": ElectricalSystemNode,
    "pneumatic-kitPneumaticSystem": PneumaticSystemNode,
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "pneumatic-kitControlSystem": "Control System",
    "pneumatic-kitElectricalSystem": "Electrical System",
    "pneumatic-kitPneumaticSystem": "Pneumatic System",
}
