#!/usr/bin/env python3
"""
Quick test to verify all Digital Twin nodes can be imported
Run this before restarting ComfyUI to catch any errors
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Add ComfyUI to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_imports():
    """Test all module imports"""
    logging.info("Testing Digital Twin Node imports...\n")

    try:
        logging.info("1. Testing state_manager...")
        from custom_nodes.digital_twin_nodes.state_manager import DigitalTwinStateManager
        state = DigitalTwinStateManager()
        logging.info("   ✓ State Manager imported successfully")

        logging.info("\n2. Testing shadow_api...")
        from custom_nodes.digital_twin_nodes.shadow_api import (
            ShadowAPIFunction,
            ShadowAPIRegistry,
            ShadowAPIMode
        )
        logging.info("   ✓ Shadow API framework imported successfully")

        logging.info("\n3. Testing widget_nodes...")
        from custom_nodes.digital_twin_nodes.widget_nodes import (
            DT_Widget_ButtonInput,
            DT_Widget_SensorInput,
            DT_Widget_StatusOutput,
            DT_Widget_3DViewer,
            DT_Widget_ConnectionIndicator,
        )
        logging.info("   ✓ Widget nodes imported successfully")
        logging.info(f"     - {len([DT_Widget_ButtonInput, DT_Widget_SensorInput, DT_Widget_StatusOutput, DT_Widget_3DViewer, DT_Widget_ConnectionIndicator])} widget node classes")

        logging.info("\n4. Testing pneumatic_nodes...")
        from custom_nodes.digital_twin_nodes.pneumatic_nodes import (
            DT_L1_PneumaticCylinder,
            DT_L2_SAC_Asset,
            DT_Logic_Stopwatch,
            DT_Logic_AND,
        )
        logging.info("   ✓ Pneumatic nodes imported successfully")
        logging.info(f"     - {len([DT_L1_PneumaticCylinder, DT_L2_SAC_Asset, DT_Logic_Stopwatch, DT_Logic_AND])} pneumatic node classes")

        logging.info("\n5. Testing server_extension...")
        # Note: This requires PromptServer which may not be available in test
        try:
            from custom_nodes.digital_twin_nodes.server_extension import DigitalTwinServerExtension
            logging.info("   ✓ Server extension imported successfully")
        except Exception as e:
            logging.info(f"   ⚠ Server extension import (expected if PromptServer not available): {e}")

        logging.info("\n6. Testing code_generator...")
        from custom_nodes.digital_twin_nodes.code_generator import DigitalTwinCodeGenerator
        generator = DigitalTwinCodeGenerator()
        logging.info("   ✓ Code generator imported successfully")

        logging.info("\n7. Testing digital_twin_nodes (existing)...")
        from custom_nodes.digital_twin_nodes.digital_twin_nodes import (
            DT_APICall,
            DT_StateNode,
            DT_WorkflowOutput,
        )
        logging.info("   ✓ Existing digital twin nodes imported successfully")

        logging.info("\n" + "="*60)
        logging.info("✅ ALL IMPORTS SUCCESSFUL!")
        logging.info("="*60)
        logging.info("\nYour Digital Twin nodes are ready to use.")
        logging.info("Restart ComfyUI to see them in the node menu.")
        return True

    except SyntaxError as e:
        logging.error(f"\n❌ SYNTAX ERROR: {e}")
        logging.error(f"   File: {e.filename}")
        logging.error(f"   Line: {e.lineno}")
        logging.error(f"   Problem: {e.text}")
        return False

    except ImportError as e:
        logging.error(f"\n❌ IMPORT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    except Exception as e:
        logging.error(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
