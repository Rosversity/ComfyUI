"""
Asset nodes for physical components

These nodes represent asset-level twins in the hierarchy:
- SSV Asset (Single Solenoid Valve)
- DSV Asset (Double Solenoid Valve)
- SAC Asset (Single Acting Cylinder)
- DAC Asset (Double Acting Cylinder)
- Sensors (Position, Pressure, Flow)
"""

from .base_node import RoslabAssetNode


class SSVAssetNode(RoslabAssetNode):
    """
    SSV (Single Solenoid Valve) Asset Node

    Represents a solenoid valve that controls pneumatic flow.
    Receives electrical signals and controls air direction.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_name": ("STRING", {
                    "default": "SSV Asset",
                    "multiline": False
                }),
                "valve_type": (["3/2", "5/2"], {
                    "default": "3/2"
                }),
                "physical_valve": (["SSV_5/2", "SSV_3/2"], {
                    "default": "SSV_5/2"
                }),
            },
            "optional": {
                "electrical_input": ("*",),
                "response_time_ms": ("FLOAT", {
                    "default": 10.0,
                    "min": 1.0,
                    "max": 100.0
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_ASSET", "ROSLAB_DATA")

    RETURN_NAMES = ("ssv_asset", "valve_state")

    def execute(self, asset_name, valve_type, physical_valve, electrical_input=None, response_time_ms=10.0):
        """
        Configure SSV Asset

        Returns:
            tuple: (asset configuration, valve state output)
        """
        asset_config = {
            "type": "asset",
            "asset_type": "ssv",
            "name": asset_name,
            "class_name": "SSVAsset",
            "shadow_class": "SSVAssetShadow",
            "implementor": "ISSVAssetImplementor",
            "plugin": "libpneumatickit_ssv_impl.so",
            "inputs": {
                "electrical_signal": electrical_input.get("source") if electrical_input else None
            },
            "parameters": {
                "valve_type": valve_type,
                "physical_valve": physical_valve,
                "response_time_ms": response_time_ms,
                "ports": self._get_port_config(valve_type)
            },
            "initialization": {
                "requires": ["sac_asset"],  # SSV controls SAC
                "method": "Initialize"
            },
            "cable_ports": self._get_cable_ports(valve_type)
        }

        valve_state = {
            "type": "data",
            "source": "ssv_state",
            "data_type": "state",
            "states": ["energized", "de_energized"],
            "flow_direction": "A_to_P" if valve_type == "3/2" else "A_to_B"
        }

        return (asset_config, valve_state)

    def _get_port_config(self, valve_type):
        """Get port configuration based on valve type"""
        if valve_type == "3/2":
            return {
                "P": "Pressure inlet",
                "A": "Work port (to cylinder)",
                "R": "Exhaust"
            }
        else:  # 5/2
            return {
                "P": "Pressure inlet",
                "A": "Work port A",
                "B": "Work port B",
                "R": "Exhaust A",
                "S": "Exhaust B"
            }

    def _get_cable_ports(self, valve_type):
        """Get cable connection ports"""
        if valve_type == "3/2":
            return ["P", "A"]  # Only P and A for 3/2
        else:
            return ["P", "A", "B"]  # P, A, B for 5/2
        return []


class SACAssetNode(RoslabAssetNode):
    """
    SAC (Single Acting Cylinder) Asset Node

    Represents a pneumatic cylinder that extends with air pressure
    and retracts with spring force.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_name": ("STRING", {
                    "default": "SAC Asset",
                    "multiline": False
                }),
                "stroke_length_mm": ("FLOAT", {
                    "default": 100.0,
                    "min": 10.0,
                    "max": 500.0
                }),
            },
            "optional": {
                "air_input": ("*",),
                "spring_force_n": ("FLOAT", {
                    "default": 50.0,
                    "min": 1.0,
                    "max": 500.0
                }),
                "flow_coefficient": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.1,
                    "max": 2.0
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_ASSET", "ROSLAB_DATA", "ROSLAB_DATA")

    RETURN_NAMES = ("sac_asset", "position", "velocity")

    def execute(self, asset_name, stroke_length_mm, air_input=None,
                spring_force_n=50.0, flow_coefficient=0.5):
        """
        Configure SAC Asset

        Returns:
            tuple: (asset configuration, position data, velocity data)
        """
        asset_config = {
            "type": "asset",
            "asset_type": "sac",
            "name": asset_name,
            "class_name": "SACAsset",
            "shadow_class": "SACAssetShadow",
            "implementor": "ISACAssetImplementor",
            "plugin": "libpneumatickit_sac_impl.so",
            "inputs": {
                "air_pressure": air_input.get("source") if air_input else None
            },
            "parameters": {
                "stroke_length_mm": stroke_length_mm,
                "spring_force_n": spring_force_n,
                "flow_coefficient": flow_coefficient,
                "piston_diameter_mm": 20.0,  # Default value
            },
            "initialization": {
                "requires": [],  # SAC is leaf node
                "method": "Initialize",
                "ros2_publisher": True  # Publishes joint_states
            },
            "cable_ports": ["A"]  # Single port for air inlet
        }

        position_data = {
            "type": "data",
            "source": "sac_position",
            "data_type": "physical",
            "unit": "mm",
            "range": [0.0, stroke_length_mm]
        }

        velocity_data = {
            "type": "data",
            "source": "sac_velocity",
            "data_type": "physical",
            "unit": "mm/s",
            "range": [-1000.0, 1000.0]
        }

        return (asset_config, position_data, velocity_data)


class DSVAssetNode(RoslabAssetNode):
    """
    DSV (Double Solenoid Valve) Asset Node

    Represents a double solenoid valve with two control coils.
    Used to control double-acting cylinders with independent extend/retract control.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_name": ("STRING", {
                    "default": "DSV Asset",
                    "multiline": False
                }),
                "valve_type": (["5/2", "5/3"], {
                    "default": "5/3"
                }),
                "physical_valve": (["DSV_5/3", "DSV_5/2_1", "DSV_5/2_2"], {
                    "default": "DSV_5/3"
                }),
            },
            "optional": {
                "electrical_input": ("*",),  # Optional visualization of control connection
                "response_time_ms": ("FLOAT", {
                    "default": 10.0,
                    "min": 1.0,
                    "max": 100.0
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_ASSET", "ROSLAB_DATA")

    RETURN_NAMES = ("dsv_asset", "valve_state")

    def execute(self, asset_name, valve_type, physical_valve, electrical_input=None, response_time_ms=10.0):
        """
        Configure DSV Asset

        Returns:
            tuple: (asset configuration, valve state output)
        """
        asset_config = {
            "type": "asset",
            "asset_type": "dsv",
            "name": asset_name,
            "class_name": "DSVAsset",
            "shadow_class": "DSVAssetShadow",
            "implementor": "IDSVAssetImplementor",
            "plugin": "libpneumatickit_dsv_impl.so",
            "inputs": {
                "electrical_signal": electrical_input.get("source") if electrical_input else None
            },
            "parameters": {
                "valve_type": valve_type,
                "physical_valve": physical_valve,
                "response_time_ms": response_time_ms,
                "ports": self._get_port_config(valve_type)
            },
            "initialization": {
                "requires": ["dac_asset"],  # DSV controls DAC
                "method": "Initialize"
            },
            "cable_ports": self._get_cable_ports(valve_type)
        }

        valve_state = {
            "type": "data",
            "source": "dsv_state",
            "data_type": "state",
            "states": ["neutral", "extend", "retract"],
            "flow_direction": "A_or_B"
        }

        return (asset_config, valve_state)

    def _get_port_config(self, valve_type):
        """Get port configuration based on valve type"""
        # Both 5/2 and 5/3 have the same physical ports, just different internal logic
        return {
            "P": "Pressure inlet",
            "A": "Work port A (extend)",
            "B": "Work port B (retract)",
            "R": "Exhaust A",
            "S": "Exhaust B"
        }

    def _get_cable_ports(self, valve_type):
        """Get cable connection ports"""
        return ["P", "A", "B"]


class DACAssetNode(RoslabAssetNode):
    """
    DAC (Double Acting Cylinder) Asset Node

    Represents a pneumatic cylinder that extends and retracts
    using air pressure in both directions (no spring).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_name": ("STRING", {
                    "default": "DAC Asset",
                    "multiline": False
                }),
                "physical_actuator": (["DAC_1", "DAC_2"], {
                    "default": "DAC_1"
                }),
                "stroke_length_mm": ("FLOAT", {
                    "default": 100.0,
                    "min": 10.0,
                    "max": 500.0
                }),
            },
            "optional": {
                "air_input": ("*",),  # Optional visualization of valve→cylinder connection
                "flow_coefficient": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.1,
                    "max": 2.0
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_ASSET", "ROSLAB_DATA", "ROSLAB_DATA")

    RETURN_NAMES = ("dac_asset", "position", "velocity")

    def execute(self, asset_name, physical_actuator, stroke_length_mm, air_input=None, flow_coefficient=0.5):
        """
        Configure DAC Asset

        Returns:
            tuple: (asset configuration, position data, velocity data)
        """
        asset_config = {
            "type": "asset",
            "asset_type": "dac",
            "name": asset_name,
            "class_name": "DACAsset",
            "shadow_class": "DACAssetShadow",
            "implementor": "IDACAssetImplementor",
            "plugin": "libpneumatickit_dac_impl.so",
            "inputs": {
                "air_supply": air_input.get("source") if air_input else None
            },
            "parameters": {
                "physical_actuator": physical_actuator,
                "stroke_length_mm": stroke_length_mm,
                "flow_coefficient": flow_coefficient,
                "piston_diameter_mm": 25.0,  # Default value (larger than SAC)
            },
            "initialization": {
                "requires": [],  # DAC is leaf node
                "method": "Initialize",
                "ros2_publisher": True  # Publishes joint_states
            },
            "cable_ports": ["A", "B"]  # Two ports for extend/retract
        }

        position_data = {
            "type": "data",
            "source": "dac_position",
            "data_type": "physical",
            "unit": "mm",
            "range": [0.0, stroke_length_mm]
        }

        velocity_data = {
            "type": "data",
            "source": "dac_velocity",
            "data_type": "physical",
            "unit": "mm/s",
            "range": [-1000.0, 1000.0]
        }

        return (asset_config, position_data, velocity_data)


class PositionSensorNode(RoslabAssetNode):
    """
    Position Sensor Node

    Measures cylinder position for feedback control.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sensor_name": ("STRING", {
                    "default": "Position Sensor",
                    "multiline": False
                }),
                "sensor_type": (["magnetic", "optical", "potentiometer"], {
                    "default": "magnetic"
                }),
            },
            "optional": {
                "cylinder_input": ("*",),
                "accuracy_mm": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.01,
                    "max": 10.0
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_ASSET", "ROSLAB_DATA")

    RETURN_NAMES = ("sensor_asset", "position_reading")

    def execute(self, sensor_name, sensor_type, cylinder_input=None, accuracy_mm=0.1):
        """
        Configure position sensor

        Returns:
            tuple: (sensor configuration, position measurement output)
        """
        asset_config = {
            "type": "asset",
            "asset_type": "position_sensor",
            "name": sensor_name,
            "sensor_type": sensor_type,
            "inputs": {
                "cylinder_position": cylinder_input.get("source") if cylinder_input else None
            },
            "parameters": {
                "accuracy_mm": accuracy_mm,
                "response_time_ms": 1.0
            }
        }

        position_reading = {
            "type": "data",
            "source": "position_measurement",
            "data_type": "sensor",
            "unit": "mm",
            "accuracy": accuracy_mm
        }

        return (asset_config, position_reading)


class PressureSensorNode(RoslabAssetNode):
    """
    Pressure Sensor Node

    Measures pneumatic pressure in the system.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sensor_name": ("STRING", {
                    "default": "Pressure Sensor",
                    "multiline": False
                }),
                "range_bar": ("FLOAT", {
                    "default": 10.0,
                    "min": 1.0,
                    "max": 16.0
                }),
            },
            "optional": {
                "air_input": ("*",),
                "accuracy_percent": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.1,
                    "max": 5.0
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_ASSET", "ROSLAB_DATA")

    RETURN_NAMES = ("sensor_asset", "pressure_reading")

    def execute(self, sensor_name, range_bar, air_input=None, accuracy_percent=0.5):
        """
        Configure pressure sensor

        Returns:
            tuple: (sensor configuration, pressure measurement output)
        """
        asset_config = {
            "type": "asset",
            "asset_type": "pressure_sensor",
            "name": sensor_name,
            "range_bar": range_bar,
            "inputs": {
                "air_pressure": air_input.get("source") if air_input else None
            },
            "parameters": {
                "accuracy_percent": accuracy_percent,
                "response_time_ms": 5.0
            }
        }

        pressure_reading = {
            "type": "data",
            "source": "pressure_measurement",
            "data_type": "sensor",
            "unit": "bar",
            "range": [0.0, range_bar],
            "accuracy": accuracy_percent
        }

        return (asset_config, pressure_reading)


# Node class mappings for registration
NODE_CLASS_MAPPINGS = {
    "pneumatic-kitSSVAsset": SSVAssetNode,
    "pneumatic-kitDSVAsset": DSVAssetNode,
    "pneumatic-kitSACAsset": SACAssetNode,
    "pneumatic-kitDACAsset": DACAssetNode,
    "pneumatic-kitPositionSensor": PositionSensorNode,
    "pneumatic-kitPressureSensor": PressureSensorNode,
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "pneumatic-kitSSVAsset": "SSV Asset (Single Solenoid Valve)",
    "pneumatic-kitDSVAsset": "DSV Asset (Double Solenoid Valve)",
    "pneumatic-kitSACAsset": "SAC Asset (Single Acting Cylinder)",
    "pneumatic-kitDACAsset": "DAC Asset (Double Acting Cylinder)",
    "pneumatic-kitPositionSensor": "Position Sensor",
    "pneumatic-kitPressureSensor": "Pressure Sensor",
}
