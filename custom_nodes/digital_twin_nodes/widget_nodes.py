"""
Digital Twin Widget Nodes - Input/Output interface nodes
"""
import asyncio
import time
from .state_manager import DigitalTwinStateManager
from server import PromptServer


class DT_Widget_ButtonInput:
    """
    Twin Widget - Button input from frontend
    Receives button press events via WebSocket
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "widget_id": ("STRING", {"default": "btn_start"}),
                "button_label": ("STRING", {"default": "Start"}),
                "auto_reset": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "DT_FLOW")
    RETURN_NAMES = ("button_pressed", "output_flow")
    FUNCTION = "get_button_state"
    CATEGORY = "Digital Twin/Widgets/Input"
    DESCRIPTION = "Receives button press events from frontend dashboard"

    def get_button_state(self, widget_id, button_label, auto_reset):
        """Get current button state from state manager"""
        state_manager = DigitalTwinStateManager()

        # Get button state (set by WebSocket handler)
        pressed = state_manager.get("widgets", widget_id, False)

        # Auto-reset button after reading
        if auto_reset and pressed:
            state_manager.set("widgets", widget_id, False)

        # Create flow data
        flow = {
            "type": "widget_input",
            "widget_id": widget_id,
            "widget_type": "button",
            "value": pressed,
            "timestamp": time.time()
        }

        return (pressed, flow)


class DT_Widget_SensorInput:
    """
    Twin Widget - Sensor/feedback input (e.g., cable connection status)
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "widget_id": ("STRING", {"default": "sensor_cable"}),
                "sensor_label": ("STRING", {"default": "Cable Status"}),
                "sensor_type": (["BOOLEAN", "FLOAT", "STRING"], {"default": "BOOLEAN"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN", "FLOAT", "STRING", "DT_FLOW")
    RETURN_NAMES = ("bool_value", "float_value", "string_value", "output_flow")
    FUNCTION = "get_sensor_value"
    CATEGORY = "Digital Twin/Widgets/Input"

    def get_sensor_value(self, widget_id, sensor_label, sensor_type):
        """Get sensor value from state manager"""
        state_manager = DigitalTwinStateManager()

        # Get sensor state
        sensor_data = state_manager.get("widgets", widget_id, {
            "value": False,
            "type": sensor_type
        })

        value = sensor_data.get("value", False)

        # Type conversion
        bool_val = bool(value)
        float_val = float(value) if isinstance(value, (int, float)) else 0.0
        str_val = str(value)

        flow = {
            "type": "widget_input",
            "widget_id": widget_id,
            "widget_type": "sensor",
            "sensor_type": sensor_type,
            "value": value,
            "timestamp": time.time()
        }

        return (bool_val, float_val, str_val, flow)


class DT_Widget_StatusOutput:
    """
    Twin Widget - Display status/text in frontend
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "widget_id": ("STRING", {"default": "status_display"}),
                "display_value": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
            }
        }

    OUTPUT_NODE = True
    RETURN_TYPES = ()
    FUNCTION = "display_status"
    CATEGORY = "Digital Twin/Widgets/Output"

    def display_status(self, widget_id, display_value, input_flow=None):
        """Send status to frontend via WebSocket"""
        # Get PromptServer instance
        try:
            server = PromptServer.instance

            # Send to all connected clients
            asyncio.create_task(server.send_json("twin_widget_update", {
                "widget_type": "status_display",
                "widget_id": widget_id,
                "value": display_value,
                "timestamp": time.time()
            }))
        except Exception as e:
            print(f"[DT Widget] Could not send WebSocket update: {e}")

        # Also store in state manager
        state_manager = DigitalTwinStateManager()
        state_manager.set("widgets", widget_id, {
            "type": "status_display",
            "value": display_value,
            "timestamp": time.time()
        })

        return ()


class DT_Widget_3DViewer:
    """
    Twin Widget - 3D visualization of components/assets
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "widget_id": ("STRING", {"default": "viewer_3d"}),
                "model_path": ("STRING", {"default": "/models/cylinder.stl"}),
            },
            "optional": {
                "component_state": ("DT_COMPONENT_STATE",),
                "animation_command": ("STRING", {"default": ""}),
                "input_flow": ("DT_FLOW",),
            }
        }

    OUTPUT_NODE = True
    RETURN_TYPES = ()
    FUNCTION = "update_3d_view"
    CATEGORY = "Digital Twin/Widgets/Output"

    def update_3d_view(self, widget_id, model_path,
                      component_state=None, animation_command="", input_flow=None):
        """Update 3D viewer in frontend"""
        try:
            server = PromptServer.instance

            # Prepare update data
            update_data = {
                "widget_type": "3d_viewer",
                "widget_id": widget_id,
                "model_path": model_path,
                "timestamp": time.time()
            }

            # Add component state if available
            if component_state:
                update_data["component_state"] = component_state

            # Add animation command
            if animation_command:
                update_data["animation"] = animation_command

            asyncio.create_task(server.send_json("twin_widget_update", update_data))
        except Exception as e:
            print(f"[DT Widget] Could not send 3D update: {e}")

        return ()


class DT_Widget_ConnectionIndicator:
    """
    Twin Widget - Connection/status indicator (like cable connection)
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "widget_id": ("STRING", {"default": "indicator_cable"}),
                "label": ("STRING", {"default": "Cable Connection"}),
                "is_connected": ("BOOLEAN", {"forceInput": True}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
            }
        }

    OUTPUT_NODE = True
    RETURN_TYPES = ()
    FUNCTION = "update_indicator"
    CATEGORY = "Digital Twin/Widgets/Output"

    def update_indicator(self, widget_id, label, is_connected, input_flow=None):
        """Update connection indicator in frontend"""
        try:
            server = PromptServer.instance

            asyncio.create_task(server.send_json("twin_widget_update", {
                "widget_type": "connection_indicator",
                "widget_id": widget_id,
                "label": label,
                "connected": is_connected,
                "timestamp": time.time()
            }))
        except Exception as e:
            print(f"[DT Widget] Could not send indicator update: {e}")

        # Store state
        state_manager = DigitalTwinStateManager()
        state_manager.set("widgets", widget_id, {
            "type": "connection_indicator",
            "label": label,
            "connected": is_connected,
            "timestamp": time.time()
        })

        return ()


# Node mappings
NODE_CLASS_MAPPINGS = {
    "DT_Widget_ButtonInput": DT_Widget_ButtonInput,
    "DT_Widget_SensorInput": DT_Widget_SensorInput,
    "DT_Widget_StatusOutput": DT_Widget_StatusOutput,
    "DT_Widget_3DViewer": DT_Widget_3DViewer,
    "DT_Widget_ConnectionIndicator": DT_Widget_ConnectionIndicator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DT_Widget_ButtonInput": "Button Input Widget",
    "DT_Widget_SensorInput": "Sensor Input Widget",
    "DT_Widget_StatusOutput": "Status Display Widget",
    "DT_Widget_3DViewer": "3D Viewer Widget",
    "DT_Widget_ConnectionIndicator": "Connection Indicator Widget",
}
