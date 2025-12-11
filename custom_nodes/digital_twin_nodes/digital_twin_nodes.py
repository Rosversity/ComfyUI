import json

class DT_ProcessStart:
    """Start node for digital twin process workflow"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "process_name": ("STRING", {"default": "WeldingProcess"}),
                "initial_state": ("STRING", {"default": "INITIALIZE"}),
            }
        }
    
    RETURN_TYPES = ("DT_FLOW",)
    RETURN_NAMES = ("process_flow",)
    FUNCTION = "start_process"
    CATEGORY = "Digital Twin/Process"
    
    def start_process(self, process_name, initial_state):
        flow_data = {
            "type": "process_start",
            "process_name": process_name,
            "initial_state": initial_state,
            "timestamp": "start"
        }
        return (flow_data,)

class DT_StateNode:
    """Process state node (INITIALIZE, WELDING, etc.)"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "state_name": (["INITIALIZE", "MOVE_TO_SCAN_POSE", "CLOSE_GRIPPER", "MOVE_TO_PICK", "LIFT_OBJECT", "MOVE_TO_PLACE", "OPEN_GRIPPER", "MOVE_TO_HOME", "COMPLETE"], {"default": "INITIALIZE"}),
                "description": ("STRING", {"default": "State description"}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
            }
        }
    
    RETURN_TYPES = ("DT_FLOW", "DT_STATE")
    RETURN_NAMES = ("output_flow", "state_info")
    FUNCTION = "process_state"
    CATEGORY = "Digital Twin/Process"
    
    def process_state(self, state_name, description, input_flow=None):
        state_data = {
            "type": "state",
            "name": state_name,
            "description": description,
            "input_flow": input_flow
        }
        
        flow_data = {
            "type": "state_flow",
            "current_state": state_name,
            "previous_flow": input_flow
        }
        
        return (flow_data, state_data)

class DT_APICall:
    """API call nodes for robot actions"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_command": (["MoveToHome", "MoveToPose", "OpenGripper", "CloseGripper", "StartWelding", "StopWelding", "GetCurrentTask", "GetOverallHealth"], {"default": "MoveToHome"}),
                "system_type": (["CRB15000Product", "KR8WeldingProduct", "RobotArmSystem", "WeldingSystem", "GripperSystem"], {"default": "CRB15000Product"}),
                "parameters": ("STRING", {"default": "{}"}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
                "state_input": ("DT_STATE",),
            }
        }
    
    RETURN_TYPES = ("DT_FLOW", "DT_RESULT")
    RETURN_NAMES = ("output_flow", "api_result")
    FUNCTION = "execute_api"
    CATEGORY = "Digital Twin/API"
    
    def execute_api(self, api_command, system_type, parameters, input_flow=None, state_input=None):
        # Parse parameters
        try:
            params = json.loads(parameters) if parameters else {}
        except:
            params = {}
        
        full_command = f"{system_type}.{api_command}()"
        
        api_result = {
            "type": "api_call",
            "command": full_command,
            "api_command": api_command,
            "system_type": system_type,
            "parameters": params,
            "state_context": state_input
        }
        
        flow_data = {
            "type": "api_flow",
            "executed_command": full_command,
            "previous_flow": input_flow
        }
        
        return (flow_data, api_result)

class DT_ConditionNode:
    """Condition check node for transitions"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "condition_type": (["On Success", "On Failure", "On Timeout", "On Safety Check", "Custom Condition"], {"default": "On Success"}),
                "custom_condition": ("STRING", {"default": ""}),
            },
            "optional": {
                "api_result": ("DT_RESULT",),
                "input_flow": ("DT_FLOW",),
            }
        }
    
    RETURN_TYPES = ("DT_FLOW", "BOOLEAN")
    RETURN_NAMES = ("output_flow", "condition_met")
    FUNCTION = "check_condition"
    CATEGORY = "Digital Twin/Logic"
    
    def check_condition(self, condition_type, custom_condition, api_result=None, input_flow=None):
        # Simulate condition checking
        condition_met = True  # In real implementation, would check actual conditions
        
        if condition_type == "Custom Condition" and custom_condition:
            # Would evaluate custom condition here
            pass
        
        flow_data = {
            "type": "condition_flow",
            "condition_type": condition_type,
            "condition_met": condition_met,
            "api_context": api_result,
            "previous_flow": input_flow
        }
        
        return (flow_data, condition_met)

class DT_TransitionNode:
    """State transition node"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "from_state": ("STRING", {"default": "CURRENT_STATE"}),
                "to_state": (["INITIALIZE", "MOVE_TO_SCAN_POSE", "CLOSE_GRIPPER", "MOVE_TO_PICK", "LIFT_OBJECT", "MOVE_TO_PLACE", "OPEN_GRIPPER", "MOVE_TO_HOME", "COMPLETE", "TERMINATE"], {"default": "COMPLETE"}),
            },
            "optional": {
                "condition_flow": ("DT_FLOW",),
                "condition_result": ("BOOLEAN",),
            }
        }
    
    RETURN_TYPES = ("DT_FLOW",)
    RETURN_NAMES = ("transition_flow",)
    FUNCTION = "transition_state"
    CATEGORY = "Digital Twin/Logic"
    
    def transition_state(self, from_state, to_state, condition_flow=None, condition_result=True):
        flow_data = {
            "type": "transition",
            "from_state": from_state,
            "to_state": to_state,
            "condition_met": condition_result,
            "condition_context": condition_flow
        }
        
        return (flow_data,)

class DT_ProcessEnd:
    """End node for digital twin process"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "end_status": (["SUCCESS", "FAILURE", "ABORTED"], {"default": "SUCCESS"}),
                "final_message": ("STRING", {"default": "Process completed successfully"}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("process_result",)
    FUNCTION = "end_process"
    CATEGORY = "Digital Twin/Process"
    
    def end_process(self, end_status, final_message, input_flow=None):
        result = {
            "status": end_status,
            "message": final_message,
            "flow_chain": input_flow,
            "completed": True
        }
        
        return (json.dumps(result, indent=2),)

# Specialized system nodes

class DT_WeldingSystem:
    """Welding system specific actions"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "action": (["StartWelding", "StopWelding", "SetWeldingParameters", "CheckTorchHealth"], {"default": "StartWelding"}),
                "current_a": ("FLOAT", {"default": 150.0, "min": 0.0, "max": 300.0}),
                "voltage_v": ("FLOAT", {"default": 24.0, "min": 0.0, "max": 50.0}),
                "speed_mm_s": ("FLOAT", {"default": 10.0, "min": 0.0, "max": 100.0}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
            }
        }
    
    RETURN_TYPES = ("DT_FLOW", "DT_RESULT")
    RETURN_NAMES = ("output_flow", "welding_result")
    FUNCTION = "welding_action"
    CATEGORY = "Digital Twin/Systems"
    
    def welding_action(self, action, current_a, voltage_v, speed_mm_s, input_flow=None):
        params = {
            "current_a": current_a,
            "voltage_v": voltage_v,
            "speed_mm_s": speed_mm_s
        }
        
        command = f"WeldingSystem.{action}({', '.join([f'{k}={v}' for k, v in params.items()])})"
        
        result = {
            "type": "welding_action",
            "action": action,
            "command": command,
            "parameters": params
        }
        
        flow_data = {
            "type": "welding_flow",
            "executed_action": action,
            "parameters": params,
            "previous_flow": input_flow
        }
        
        return (flow_data, result)

class DT_RobotArm:
    """Robot arm specific actions"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "action": (["MoveToHome", "MoveToJointAngles", "MoveToPose", "ExecuteTrajectory"], {"default": "MoveToHome"}),
                "joint_angles": ("STRING", {"default": "[0, 0, 0, 0, 0, 0]"}),
                "pose_x": ("FLOAT", {"default": 0.5, "min": -2.0, "max": 2.0}),
                "pose_y": ("FLOAT", {"default": 0.0, "min": -2.0, "max": 2.0}),
                "pose_z": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 2.0}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
            }
        }
    
    RETURN_TYPES = ("DT_FLOW", "DT_RESULT")
    RETURN_NAMES = ("output_flow", "robot_result")
    FUNCTION = "robot_action"
    CATEGORY = "Digital Twin/Systems"
    
    def robot_action(self, action, joint_angles, pose_x, pose_y, pose_z, input_flow=None):
        if action == "MoveToJointAngles":
            try:
                angles = json.loads(joint_angles)
                command = f"RobotArmSystem.{action}({angles})"
            except:
                command = f"RobotArmSystem.{action}([0, 0, 0, 0, 0, 0])"
        elif action == "MoveToPose":
            command = f"RobotArmSystem.{action}(x={pose_x}, y={pose_y}, z={pose_z})"
        else:
            command = f"RobotArmSystem.{action}()"
        
        result = {
            "type": "robot_action",
            "action": action,
            "command": command,
            "joint_angles": joint_angles,
            "pose": {"x": pose_x, "y": pose_y, "z": pose_z}
        }
        
        flow_data = {
            "type": "robot_flow",
            "executed_action": action,
            "previous_flow": input_flow
        }
        
        return (flow_data, result)

class DT_Gripper:
    """Gripper control actions"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "action": (["OpenGripper", "CloseGripper", "SetGripForce", "CheckGripStatus"], {"default": "CloseGripper"}),
                "grip_force": ("FLOAT", {"default": 50.0, "min": 0.0, "max": 100.0}),
                "grip_width": ("FLOAT", {"default": 0.05, "min": 0.0, "max": 0.1}),
            },
            "optional": {
                "input_flow": ("DT_FLOW",),
            }
        }
    
    RETURN_TYPES = ("DT_FLOW", "DT_RESULT")
    RETURN_NAMES = ("output_flow", "gripper_result")
    FUNCTION = "gripper_action"
    CATEGORY = "Digital Twin/Systems"
    
    def gripper_action(self, action, grip_force, grip_width, input_flow=None):
        if action in ["SetGripForce"]:
            command = f"GripperSystem.{action}(force={grip_force})"
        elif action in ["OpenGripper", "CloseGripper"]:
            command = f"GripperSystem.{action}(width={grip_width})"
        else:
            command = f"GripperSystem.{action}()"
        
        result = {
            "type": "gripper_action",
            "action": action,
            "command": command,
            "grip_force": grip_force,
            "grip_width": grip_width
        }
        
        flow_data = {
            "type": "gripper_flow",
            "executed_action": action,
            "previous_flow": input_flow
        }
        
        return (flow_data, result)

class DT_WorkflowOutput:
    """
    A terminal 'sink' node. Its only purpose is to receive the final workflow
    result and have zero outputs, which satisfies the ComfyUI prompt validator.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "final_json": ("STRING", {"forceInput": True}),
            }
        }
    
    # This is the critical part: an empty RETURN_TYPES tuple
    RETURN_TYPES = ()
    FUNCTION = "execute"
    CATEGORY = "Digital Twin/Process"

    def execute(self, final_json):
        # This node does nothing. It just successfully terminates the graph.
        print(f"Workflow completed with result: {final_json}")
        return ()