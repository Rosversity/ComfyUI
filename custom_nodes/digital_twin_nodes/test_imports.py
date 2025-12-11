#!/usr/bin/env python3
"""
Quick test to verify all Digital Twin nodes can be imported
Run this before restarting ComfyUI to catch any errors
"""

import sys
import os

# Add ComfyUI to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_imports():
    """Test all module imports"""
    print("Testing Digital Twin Node imports...\n")

    try:
        print("1. Testing state_manager...")
        from custom_nodes.digital_twin_nodes.state_manager import DigitalTwinStateManager
        state = DigitalTwinStateManager()
        print("   ✓ State Manager imported successfully")

        print("\n2. Testing shadow_api...")
        from custom_nodes.digital_twin_nodes.shadow_api import (
            ShadowAPIFunction,
            ShadowAPIRegistry,
            ShadowAPIMode
        )
        print("   ✓ Shadow API framework imported successfully")

        print("\n3. Testing widget_nodes...")
        from custom_nodes.digital_twin_nodes.widget_nodes import (
            DT_Widget_ButtonInput,
            DT_Widget_SensorInput,
            DT_Widget_StatusOutput,
            DT_Widget_3DViewer,
            DT_Widget_ConnectionIndicator,
        )
        print("   ✓ Widget nodes imported successfully")
        print(f"     - {len([DT_Widget_ButtonInput, DT_Widget_SensorInput, DT_Widget_StatusOutput, DT_Widget_3DViewer, DT_Widget_ConnectionIndicator])} widget node classes")

        print("\n4. Testing pneumatic_nodes...")
        from custom_nodes.digital_twin_nodes.pneumatic_nodes import (
            DT_L1_PneumaticCylinder,
            DT_L2_SAC_Asset,
            DT_Logic_Stopwatch,
            DT_Logic_AND,
        )
        print("   ✓ Pneumatic nodes imported successfully")
        print(f"     - {len([DT_L1_PneumaticCylinder, DT_L2_SAC_Asset, DT_Logic_Stopwatch, DT_Logic_AND])} pneumatic node classes")

        print("\n5. Testing server_extension...")
        # Note: This requires PromptServer which may not be available in test
        try:
            from custom_nodes.digital_twin_nodes.server_extension import DigitalTwinServerExtension
            print("   ✓ Server extension imported successfully")
        except Exception as e:
            print(f"   ⚠ Server extension import (expected if PromptServer not available): {e}")

        print("\n6. Testing code_generator...")
        from custom_nodes.digital_twin_nodes.code_generator import DigitalTwinCodeGenerator
        generator = DigitalTwinCodeGenerator()
        print("   ✓ Code generator imported successfully")

        print("\n7. Testing digital_twin_nodes (existing)...")
        from custom_nodes.digital_twin_nodes.digital_twin_nodes import (
            DT_APICall,
            DT_StateNode,
            DT_WorkflowOutput,
        )
        print("   ✓ Existing digital twin nodes imported successfully")

        print("\n" + "="*60)
        print("✅ ALL IMPORTS SUCCESSFUL!")
        print("="*60)
        print("\nYour Digital Twin nodes are ready to use.")
        print("Restart ComfyUI to see them in the node menu.")
        return True

    except SyntaxError as e:
        print(f"\n❌ SYNTAX ERROR: {e}")
        print(f"   File: {e.filename}")
        print(f"   Line: {e.lineno}")
        print(f"   Problem: {e.text}")
        return False

    except ImportError as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
