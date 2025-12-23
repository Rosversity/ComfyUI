"""
Process Generator Node for ComfyUI
Triggers C++ process generation from the workflow
"""

from .base_node import RoslabConfigNode
import requests
import json
import logging

# Setup logger
logger = logging.getLogger(__name__)


class ProcessGeneratorNode(RoslabConfigNode):
    """
    Process Generator Node
    
    Triggers the generation of C++ process from the current workflow.
    Connects to pneumatic_kit_runtime API to initiate build.
    
    Renders as a button in the UI for easy access.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "runtime_url": ("STRING", {
                    "default": "http://localhost:8080",
                    "multiline": False
                }),
            },
            "optional": {
                "process_config": ("ROSLAB_PROCESS_CONFIG",),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "generate_process"
    OUTPUT_NODE = True
    CATEGORY = "Rlab/pneumatic-kit/actions"

    def generate(self, runtime_url, process_config=None, node_id=None):
        """
        Trigger process generation
        
        Args:
            runtime_url: URL of pneumatic_kit_runtime
            process_config: Optional process configuration
            node_id: Node ID (auto-provided by ComfyUI)
            
        Returns:
            tuple: Status message
        """
        logger.info("=" * 70)
        logger.info("PROCESS GENERATOR TRIGGERED")
        logger.info("=" * 70)
        logger.info(f"Runtime URL: {runtime_url}")
        logger.info(f"Node ID: {node_id}")
        
        if process_config:
            logger.info(f"Process Config: {process_config.get('process_name', 'N/A')}")
        
        try:
            # Test connection to runtime
            health_check = f"{runtime_url}/health"
            logger.info(f"Checking runtime health at: {health_check}")
            
            response = requests.get(health_check, timeout=2)
            
            if response.ok:
                logger.info("✅ Runtime is online and ready")
                status = f"✅ Connected to runtime at {runtime_url}\n"
                status += "Ready to generate process.\n"
                status += "Click 'Queue Prompt' to trigger generation."
                
                logger.info("Waiting for workflow execution to complete...")
                return (status,)
            else:
                logger.error(f"❌ Runtime responded with status: {response.status_code}")
                return (f"❌ Runtime error: {response.status_code}",)
                
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Cannot connect to runtime at {runtime_url}")
            logger.error("Make sure pneumatic_kit_runtime is running:")
            logger.error("  cd /home/surya/rosv_ws/RoslabSDK/build/examples")
            logger.error("  ./pneumatic_kit_runtime")
            return (f"❌ Cannot connect to runtime\nMake sure it's running on {runtime_url}",)
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return (f"❌ Error: {str(e)}",)


# Register the node
NODE_CLASS_MAPPINGS = {
    "pneumatic-kitProcessGenerator": ProcessGeneratorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "pneumatic-kitProcessGenerator": "🚀 Generate Process",
}
