"""
HMI Widget nodes for user interface components

These nodes represent UI elements like buttons, displays, indicators, etc.
"""

from .base_node import RoslabWidgetNode


class HMIButtonNode(RoslabWidgetNode):
    """
    HMI Button Widget Node

    Represents a push button on the HMI panel.
    Generates trigger signals when pressed/released.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "button_id": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 8
                }),
                "button_type": (["momentary", "toggle", "emergency"], {
                    "default": "momentary"
                }),
                "label": ("STRING", {
                    "default": "Button",
                    "multiline": False
                }),
            },
            "optional": {
                "db_address": ("STRING", {
                    "default": "",  # Auto-assigned if empty
                    "multiline": False
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_TRIGGER", "ROSLAB_WIDGET_CONFIG")

    RETURN_NAMES = ("trigger", "widget_config")

    def execute(self, button_id, button_type, label, db_address=""):
        """
        Configure HMI button

        Returns:
            tuple: (trigger signal, widget configuration)
        """
        # Auto-assign DB address if not provided
        if not db_address:
            db_address = f"DB2.DBX2.{button_id - 1}"

        widget_config = {
            "type": "hmi_button",
            "widget_type": "button",
            "button_id": button_id,
            "button_type": button_type,
            "label": label,
            "db_address": db_address,
            "endpoint": f"/hmi/start_button"  # Will be parameterized
        }

        trigger = {
            "type": "trigger",
            "source": f"button_{button_id}",
            "address": db_address
        }

        return (trigger, widget_config)


class DisplayNode(RoslabWidgetNode):
    """
    Display Widget Node

    Shows numeric or text data on the HMI panel.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "display_type": (["numeric", "text", "timer", "position"], {
                    "default": "numeric"
                }),
                "label": ("STRING", {
                    "default": "Display",
                    "multiline": False
                }),
                "units": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            },
            "optional": {
                "data_input": ("*",),
                "precision": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 6
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_WIDGET_CONFIG",)

    RETURN_NAMES = ("widget_config",)

    def execute(self, display_type, label, units, data_input=None, precision=2):
        """
        Configure display widget

        Returns:
            tuple: Widget configuration
        """
        widget_config = {
            "type": "display",
            "widget_type": "display",
            "display_type": display_type,
            "label": label,
            "units": units,
            "precision": precision,
            "data_source": data_input.get("source") if data_input else "none"
        }

        return (widget_config,)


class TimerDisplayNode(RoslabWidgetNode):
    """
    Timer Display Node

    Shows elapsed time for process timing.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "label": ("STRING", {
                    "default": "Elapsed Time",
                    "multiline": False
                }),
                "format": (["ms", "seconds", "mm:ss", "hh:mm:ss"], {
                    "default": "mm:ss"
                }),
            },
            "optional": {
                "start_trigger": ("ROSLAB_TRIGGER",),
                "stop_trigger": ("*",),
            }
        }

    RETURN_TYPES = ("ROSLAB_WIDGET_CONFIG", "ROSLAB_DATA")

    RETURN_NAMES = ("widget_config", "elapsed_time")

    def execute(self, label, format, start_trigger=None, stop_trigger=None):
        """
        Configure timer display

        Returns:
            tuple: (widget configuration, elapsed time data output)
        """
        widget_config = {
            "type": "timer_display",
            "widget_type": "timer",
            "label": label,
            "format": format,
            "start_trigger": start_trigger.get("source") if start_trigger else None,
            "stop_trigger": stop_trigger.get("source") if stop_trigger else None
        }

        data_output = {
            "type": "data",
            "source": "elapsed_time",
            "data_type": "float"
        }

        return (widget_config, data_output)


class IndicatorLEDNode(RoslabWidgetNode):
    """
    LED Indicator Node

    Shows status indicators (lights) on HMI panel.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "label": ("STRING", {
                    "default": "Status",
                    "multiline": False
                }),
                "color": (["green", "red", "yellow", "blue", "white"], {
                    "default": "green"
                }),
            },
            "optional": {
                "control_signal": ("*",),
                "blink": ("BOOLEAN", {
                    "default": False
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_WIDGET_CONFIG",)

    RETURN_NAMES = ("widget_config",)

    def execute(self, label, color, control_signal=None, blink=False):
        """
        Configure LED indicator

        Returns:
            tuple: Widget configuration
        """
        widget_config = {
            "type": "indicator_led",
            "widget_type": "indicator",
            "label": label,
            "color": color,
            "blink": blink,
            "control_source": control_signal.get("source") if control_signal else "none"
        }

        return (widget_config,)


class SensorReadingNode(RoslabWidgetNode):
    """
    Sensor Reading Node

    Displays real-time sensor data (position, pressure, etc.)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sensor_type": (["position", "pressure", "flow", "temperature"], {
                    "default": "position"
                }),
                "label": ("STRING", {
                    "default": "Sensor",
                    "multiline": False
                }),
            },
            "optional": {
                "sensor_input": ("*",),
                "min_value": ("FLOAT", {
                    "default": 0.0
                }),
                "max_value": ("FLOAT", {
                    "default": 100.0
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_WIDGET_CONFIG", "ROSLAB_DATA")

    RETURN_NAMES = ("widget_config", "sensor_data")

    def execute(self, sensor_type, label, sensor_input=None, min_value=0.0, max_value=100.0):
        """
        Configure sensor reading display

        Returns:
            tuple: (widget configuration, sensor data output)
        """
        widget_config = {
            "type": "sensor_reading",
            "widget_type": "sensor",
            "sensor_type": sensor_type,
            "label": label,
            "min_value": min_value,
            "max_value": max_value,
            "input_source": sensor_input.get("source") if sensor_input else "none"
        }

        data_output = {
            "type": "data",
            "source": f"sensor_{sensor_type}",
            "data_type": "float",
            "range": [min_value, max_value]
        }

        return (widget_config, data_output)


# Node class mappings for registration
NODE_CLASS_MAPPINGS = {
    "pneumatic-kitHMIButton": HMIButtonNode,
    "pneumatic-kitDisplay": DisplayNode,
    "pneumatic-kitTimerDisplay": TimerDisplayNode,
    "pneumatic-kitIndicatorLED": IndicatorLEDNode,
    "pneumatic-kitSensorReading": SensorReadingNode,
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "pneumatic-kitHMIButton": "HMI Button",
    "pneumatic-kitDisplay": "Display",
    "pneumatic-kitTimerDisplay": "Timer Display",
    "pneumatic-kitIndicatorLED": "LED Indicator",
    "pneumatic-kitSensorReading": "Sensor Reading",
}
