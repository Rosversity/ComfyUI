"""
Digital Twin Nodes - Custom nodes for digital twin workflows
"""

# Import existing nodes (workflow planning)
from .digital_twin_nodes import *

# Import new widget nodes
from .widget_nodes import (
    DT_Widget_ButtonInput,
    DT_Widget_SensorInput,
    DT_Widget_StatusOutput,
    DT_Widget_3DViewer,
    DT_Widget_ConnectionIndicator,
)

# Import pneumatic nodes (Proof of Concept)
from .pneumatic_nodes import (
    DT_L1_PneumaticCylinder,
    DT_L2_SAC_Asset,
    DT_Logic_Stopwatch,
    DT_Logic_AND,
)

# Import multi-shadow base and Control System
from .multi_shadow_base import DT_ControlSystem

# Import Pneumatic Hello World nodes
from .pneumatic_hello_world import (
    PneumaticControlSystem,
    PneumaticElectricalSystem,
    PneumaticAirSystem,
    PneumaticSSVAsset,
    PneumaticSACAsset,
)

# Initialize server extension
from .server_extension import setup_server_extension
server_ext = setup_server_extension()


# Node registry - Existing nodes
NODE_CLASS_MAPPINGS = {
    # Existing workflow planning nodes
    "DT_APICall": DT_APICall,
    "DT_StateNode": DT_StateNode,
    "DT_ConditionNode": DT_ConditionNode,
    "DT_TransitionNode": DT_TransitionNode,
    "DT_ProcessStart": DT_ProcessStart,
    "DT_ProcessEnd": DT_ProcessEnd,
    "DT_WeldingSystem": DT_WeldingSystem,
    "DT_RobotArm": DT_RobotArm,
    "DT_Gripper": DT_Gripper,
    "DT_WorkflowOutput": DT_WorkflowOutput,

    # Widget nodes (Input/Output)
    "DT_Widget_ButtonInput": DT_Widget_ButtonInput,
    "DT_Widget_SensorInput": DT_Widget_SensorInput,
    "DT_Widget_StatusOutput": DT_Widget_StatusOutput,
    "DT_Widget_3DViewer": DT_Widget_3DViewer,
    "DT_Widget_ConnectionIndicator": DT_Widget_ConnectionIndicator,

    # Pneumatic PoC nodes
    "DT_L1_PneumaticCylinder": DT_L1_PneumaticCylinder,
    "DT_L2_SAC_Asset": DT_L2_SAC_Asset,
    "DT_Logic_Stopwatch": DT_Logic_Stopwatch,
    "DT_Logic_AND": DT_Logic_AND,

    # Multi-Shadow Control System
    "DT_ControlSystem": DT_ControlSystem,

    # Pneumatic Hello World - Complete Workflow
    "Pneumatic_ControlSystem": PneumaticControlSystem,
    "Pneumatic_ElectricalSystem": PneumaticElectricalSystem,
    "Pneumatic_AirSystem": PneumaticAirSystem,
    "Pneumatic_SSVAsset": PneumaticSSVAsset,
    "Pneumatic_SACAsset": PneumaticSACAsset,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # Existing nodes
    "DT_APICall": "API Call",
    "DT_StateNode": "Process State",
    "DT_ConditionNode": "Condition Check",
    "DT_TransitionNode": "State Transition",
    "DT_ProcessStart": "Process Start",
    "DT_ProcessEnd": "Process End",
    "DT_WeldingSystem": "Welding System",
    "DT_RobotArm": "Robot Arm",
    "DT_Gripper": "Gripper Control",
    "DT_WorkflowOutput": "Workflow Output (Sink)",

    # Widget nodes
    "DT_Widget_ButtonInput": "🔘 Button Input",
    "DT_Widget_SensorInput": "📡 Sensor Input",
    "DT_Widget_StatusOutput": "📊 Status Display",
    "DT_Widget_3DViewer": "🎨 3D Viewer",
    "DT_Widget_ConnectionIndicator": "🔌 Connection Indicator",

    # Pneumatic nodes
    "DT_L1_PneumaticCylinder": "🔧 L1: Pneumatic Cylinder",
    "DT_L2_SAC_Asset": "⚙️ L2: SAC Asset",
    "DT_Logic_Stopwatch": "⏱️ Stopwatch Timer",
    "DT_Logic_AND": "∧ AND Gate",

    # Multi-Shadow Control System
    "DT_ControlSystem": "🎛️ Control System (Multi-Shadow)",

    # Pneumatic Hello World - Complete Workflow
    "Pneumatic_ControlSystem": "🎛️ Control System",
    "Pneumatic_ElectricalSystem": "⚡ Electrical System",
    "Pneumatic_AirSystem": "💨 Pneumatic System",
    "Pneumatic_SSVAsset": "🔄 SSV Asset (Valve)",
    "Pneumatic_SACAsset": "🔧 SAC Asset (Cylinder)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("[Digital Twin Nodes] Loaded successfully!")
print(f"  - {len(NODE_CLASS_MAPPINGS)} nodes registered")
print("  - Server extension initialized")
print("  - Shadow API framework ready")