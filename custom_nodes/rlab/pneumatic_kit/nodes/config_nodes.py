"""
Configuration nodes for process setup

These nodes configure process-level settings like name, description,
ladder logic files, and cable connections.
"""

import json
import os
from pathlib import Path
from .base_node import RoslabConfigNode


class ProcessSettingsNode(RoslabConfigNode):
    """
    Process Settings Node

    Configures the basic process parameters including:
    - Process name
    - Description
    - Ladder logic file path
    - PLC configuration
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "process_name": ("STRING", {
                    "default": "my_process",
                    "multiline": False
                }),
                "description": ("STRING", {
                    "default": "Process description",
                    "multiline": True
                }),
                "project_name": ("STRING", {
                    "default": "pneumatic-kit",
                    "multiline": False
                }),
            },
            "optional": {
                "ladder_logic_file": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "plc_mode": (["auto", "real", "mock"], {
                    "default": "auto"
                }),
                "scan_cycle_ms": ("INT", {
                    "default": 50,
                    "min": 10,
                    "max": 1000
                }),
                "plc_ip": ("STRING", {
                    "default": "192.168.0.1",
                    "multiline": False
                }),
                "plc_rack": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 7
                }),
                "plc_slot": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 31
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_PROCESS_CONFIG",)
    RETURN_NAMES = ("process_config",)
    FUNCTION = "execute"
    CATEGORY = "Rlab/pneumatic-kit/config"

    def execute(self, process_name, description, project_name,
                ladder_logic_file="", plc_mode="auto", scan_cycle_ms=50,
                plc_ip="192.168.0.1", plc_rack=0, plc_slot=1):
        """
        Execute process settings configuration

        Returns:
            tuple: Process configuration dictionary
        """
        config = {
            "type": "process_config",
            "process_name": process_name,
            "description": description,
            "project_name": project_name,
            "ladder_logic_file": ladder_logic_file,
            "plc_config": {
                "mode": plc_mode,
                "scan_cycle_ms": scan_cycle_ms,
                "ip": plc_ip,
                "rack": plc_rack,
                "slot": plc_slot,
                "auto_detect": plc_mode == "auto"
            },
            "output_path": f"DigitalTwinProcesses/{project_name}/{process_name}"
        }

        return (config,)


class CableConnectionNode(RoslabConfigNode):
    """
    Cable Connection Node

    Defines physical cable connections between components.
    Connections are stored as JSON configuration.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "connections_json": ("STRING", {
                    "default": "{}",
                    "multiline": True
                }),
            },
            "optional": {
                "validate": ("BOOLEAN", {
                    "default": True
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_CABLE_CONFIG",)
    RETURN_NAMES = ("cable_config",)
    FUNCTION = "execute"
    CATEGORY = "Rlab/pneumatic-kit/config"

    def execute(self, connections_json, validate=True):
        """
        Parse and validate cable connections

        Args:
            connections_json: JSON string defining cable connections
            validate: Whether to validate connection schema

        Returns:
            tuple: Cable configuration dictionary
        """
        try:
            connections = json.loads(connections_json)
        except json.JSONDecodeError as e:
            print(f"Error parsing cable connections JSON: {e}")
            connections = {}

        if validate:
            # Basic validation
            if not isinstance(connections, dict):
                print("Warning: Cable connections must be a dictionary")
                connections = {}

        config = {
            "type": "cable_config",
            "connections": connections,
            "validated": validate
        }

        return (config,)


class LadderLogicUploadNode(RoslabConfigNode):
    """
    Ladder Logic Upload Node

    Uploads or references ladder logic JSON file.
    Provides options to either upload a file or reference an existing path.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source_type": (["file_path", "upload", "inline"], {
                    "default": "file_path"
                }),
                "content": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
            },
            "optional": {
                "file_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_LADDER_LOGIC",)
    RETURN_NAMES = ("ladder_logic",)
    FUNCTION = "execute"
    CATEGORY = "Rlab/pneumatic-kit/config"

    def execute(self, source_type, content, file_path=""):
        """
        Process ladder logic configuration

        Args:
            source_type: How ladder logic is provided (file_path/upload/inline)
            content: Inline JSON content or uploaded file content
            file_path: Path to existing ladder logic file

        Returns:
            tuple: Ladder logic configuration
        """
        config = {
            "type": "ladder_logic",
            "source_type": source_type,
            "content": content,
            "file_path": file_path
        }

        # Validate JSON if inline or upload
        if source_type in ["upload", "inline"] and content:
            try:
                json.loads(content)
                config["valid"] = True
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid ladder logic JSON: {e}")
                config["valid"] = False
        elif source_type == "file_path" and file_path:
            config["valid"] = os.path.exists(file_path)
            if not config["valid"]:
                print(f"Warning: Ladder logic file not found: {file_path}")
        else:
            config["valid"] = False

        return (config,)


class BuildConfigNode(RoslabConfigNode):
    """
    Build Configuration Node

    Configures CMake build settings and compiler options.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "cmake_build_type": (["Debug", "Release", "RelWithDebInfo"], {
                    "default": "Release"
                }),
                "auto_build": ("BOOLEAN", {
                    "default": False
                }),
            },
            "optional": {
                "additional_cmake_flags": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            }
        }

    RETURN_TYPES = ("ROSLAB_BUILD_CONFIG",)
    RETURN_NAMES = ("build_config",)
    FUNCTION = "execute"
    CATEGORY = "Rlab/pneumatic-kit/config"

    def execute(self, cmake_build_type, auto_build, additional_cmake_flags=""):
        """
        Configure build settings

        Returns:
            tuple: Build configuration dictionary
        """
        config = {
            "type": "build_config",
            "cmake_build_type": cmake_build_type,
            "auto_build": auto_build,
            "additional_flags": additional_cmake_flags.split() if additional_cmake_flags else []
        }

        return (config,)


# Node class mappings for registration
NODE_CLASS_MAPPINGS = {
    "pneumatic-kitProcessSettings": ProcessSettingsNode,
    "pneumatic-kitCableConnection": CableConnectionNode,
    "pneumatic-kitLadderLogicUpload": LadderLogicUploadNode,
    "pneumatic-kitBuildConfig": BuildConfigNode,
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "pneumatic-kitProcessSettings": "Process Settings",
    "pneumatic-kitCableConnection": "Cable Connections",
    "pneumatic-kitLadderLogicUpload": "Ladder Logic Upload",
    "pneumatic-kitBuildConfig": "Build Configuration",
}
