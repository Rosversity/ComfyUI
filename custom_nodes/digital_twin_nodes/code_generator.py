"""
Digital Twin Code Generator - Generate executable code from workflows
"""
import json
from typing import Dict, List, Any
from .shadow_api import ShadowAPIRegistry


class DigitalTwinCodeGenerator:
    """
    Generates executable code from ComfyUI workflow + Shadow API definitions
    """

    def __init__(self):
        self.shadow_api_registry = ShadowAPIRegistry()

    def generate_from_workflow(self, workflow: Dict, target: str = "python") -> str:
        """
        Generate code from workflow

        Args:
            workflow: ComfyUI workflow JSON
            target: "python" or "javascript"

        Returns:
            Generated code as string
        """
        if target == "python":
            return self._generate_python(workflow)
        elif target == "javascript":
            return self._generate_javascript(workflow)
        else:
            raise ValueError(f"Unsupported target: {target}")

    def _generate_python(self, workflow: Dict) -> str:
        """Generate Python code"""

        nodes = workflow.get("nodes", {})
        links = workflow.get("links", [])

        code_parts = []

        # Header
        code_parts.append(self._python_header())

        # Shadow API functions
        code_parts.append("\n# Shadow API Functions\n")
        api_defs = self.shadow_api_registry.get_all_definitions()

        for node_id, api_def in api_defs.items():
            code_parts.append(f"\n# Shadow API for {node_id}")
            code_parts.append(api_def.get("code", ""))

        # Main execution function
        code_parts.append("\n\nasync def execute_digital_twin_workflow():")
        code_parts.append("    '''Generated workflow execution'''")
        code_parts.append("    \n    # Initialize state")
        code_parts.append("    state = {}")

        # Generate node execution code
        execution_order = self._get_execution_order(nodes, links)

        code_parts.append("\n    # Execute nodes in order")
        for node_id in execution_order:
            node = nodes.get(str(node_id), {})
            node_type = node.get("type", "")
            inputs = node.get("inputs", {})

            code_parts.append(f"\n    # Node {node_id}: {node_type}")

            if "Pneumatic" in node_type:
                code_parts.append(self._generate_pneumatic_node_code(node_id, node, inputs))
            elif "Widget" in node_type:
                code_parts.append(self._generate_widget_node_code(node_id, node, inputs))
            elif "Logic" in node_type:
                code_parts.append(self._generate_logic_node_code(node_id, node, inputs))
            else:
                code_parts.append(f"    # TODO: Implement {node_type}")

        # Footer
        code_parts.append("\n    return state")
        code_parts.append("\n\n")
        code_parts.append("if __name__ == '__main__':")
        code_parts.append("    asyncio.run(execute_digital_twin_workflow())")

        return "\n".join(code_parts)

    def _python_header(self) -> str:
        """Generate Python header with imports"""
        return '''"""
Generated Digital Twin Workflow
Auto-generated from ComfyUI workflow with Shadow APIs
"""

import asyncio
import time
import aiohttp
import json
from typing import Dict, Any


class DigitalTwinState:
    """State management for generated code"""
    def __init__(self):
        self.components = {}
        self.assets = {}
        self.widgets = {}

    def set(self, level, key, value):
        getattr(self, level)[key] = value

    def get(self, level, key, default=None):
        return getattr(self, level, {}).get(key, default)

'''

    def _get_execution_order(self, nodes: Dict, links: List) -> List:
        """
        Determine node execution order based on links
        Simple topological sort
        """
        # Build dependency graph
        dependencies = {}
        for node_id in nodes:
            dependencies[node_id] = []

        for link in links:
            from_node = str(link[1])  # Source node
            to_node = str(link[3])    # Target node
            if to_node in dependencies:
                dependencies[to_node].append(from_node)

        # Topological sort
        visited = set()
        order = []

        def visit(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            for dep in dependencies.get(node_id, []):
                visit(dep)
            order.append(node_id)

        for node_id in nodes:
            visit(node_id)

        return order

    def _generate_pneumatic_node_code(self, node_id: str, node: Dict, inputs: Dict) -> str:
        """Generate code for pneumatic nodes"""
        component_id = inputs.get("component_id", f"component_{node_id}")
        extend = inputs.get("extend_command", False)

        code = f'''
    # Pneumatic Cylinder {component_id}
    print(f"[{component_id}] {'Extending' if extend else 'Retracting'}...")

    # Call shadow API
    api_result = await execute(
        component_id="{component_id}",
        action="{'extend' if extend else 'retract'}",
        pressure={inputs.get('air_pressure_psi', 80.0)}
    )

    # Simulate physical delay
    await asyncio.sleep({inputs.get('extension_time_ms', 2000) / 1000})

    # Store state
    state["{component_id}"] = {{
        "position": {200.0 if extend else 0.0},
        "extended": {extend},
        "api_response": api_result
    }}
    '''
        return code

    def _generate_widget_node_code(self, node_id: str, node: Dict, inputs: Dict) -> str:
        """Generate code for widget nodes"""
        widget_id = inputs.get("widget_id", f"widget_{node_id}")

        if "Button" in node.get("type", ""):
            return f'''
    # Button Widget {widget_id}
    button_pressed = state.get("widgets", {{}}).get("{widget_id}", False)
    print(f"Button {widget_id}: {{button_pressed}}")
    '''
        elif "Status" in node.get("type", ""):
            display_value = inputs.get("display_value", "Status")
            return f'''
    # Status Widget {widget_id}
    print(f"[Display] {widget_id}: {display_value}")
    state.setdefault("widgets", {{}})["{{widget_id}}"] = "{display_value}"
    '''
        else:
            return f"    # Widget {widget_id}"

    def _generate_logic_node_code(self, node_id: str, node: Dict, inputs: Dict) -> str:
        """Generate code for logic nodes"""
        if "Stopwatch" in node.get("type", ""):
            return f'''
    # Stopwatch Logic
    if state.get("stopwatch_running"):
        elapsed = (time.time() - state["stopwatch_start"]) * 1000
        print(f"Elapsed time: {{elapsed:.0f}} ms")
    '''
        elif "AND" in node.get("type", ""):
            return f'''
    # AND Logic Gate
    result = {inputs.get('input_a', False)} and {inputs.get('input_b', False)}
    '''
        else:
            return f"    # Logic node {node_id}"

    def _generate_javascript(self, workflow: Dict) -> str:
        """Generate JavaScript code (for Node.js or browser)"""

        code_parts = []

        # Header
        code_parts.append('''/**
 * Generated Digital Twin Workflow
 * Auto-generated from ComfyUI workflow
 */

class DigitalTwinWorkflow {
    constructor() {
        this.state = {
            components: {},
            assets: {},
            widgets: {}
        };
    }

    async execute() {
        console.log("Starting Digital Twin Workflow...");
''')

        # Generate execution code
        nodes = workflow.get("nodes", {})
        for node_id, node in nodes.items():
            node_type = node.get("type", "")
            code_parts.append(f"\n        // Node {node_id}: {node_type}")

        code_parts.append('''
        return this.state;
    }
}

// Execute workflow
const workflow = new DigitalTwinWorkflow();
workflow.execute().then(state => {
    console.log("Workflow completed:", state);
});
''')

        return "\n".join(code_parts)


def generate_example_code():
    """Generate example code for pneumatic hello world"""
    generator = DigitalTwinCodeGenerator()

    example_workflow = {
        "nodes": {
            "1": {"type": "DT_Widget_ButtonInput", "inputs": {"widget_id": "btn_start"}},
            "2": {"type": "DT_Widget_SensorInput", "inputs": {"widget_id": "sensor_cable"}},
            "3": {"type": "DT_Logic_AND", "inputs": {}},
            "4": {"type": "DT_L1_PneumaticCylinder", "inputs": {
                "component_id": "SAC_001",
                "extension_time_ms": 2000
            }},
            "5": {"type": "DT_Logic_Stopwatch", "inputs": {"stopwatch_id": "timer_01"}},
            "6": {"type": "DT_Widget_StatusOutput", "inputs": {"widget_id": "status_display"}},
        },
        "links": [
            [0, 1, 0, 3, 0],  # button -> AND
            [0, 2, 0, 3, 1],  # sensor -> AND
            [0, 3, 0, 4, 0],  # AND -> cylinder
            [0, 1, 0, 5, 0],  # button -> stopwatch start
            [0, 4, 3, 5, 1],  # cylinder is_extended -> stopwatch stop
            [0, 5, 2, 6, 0],  # stopwatch status -> status display
        ]
    }

    return generator.generate_from_workflow(example_workflow, "python")
