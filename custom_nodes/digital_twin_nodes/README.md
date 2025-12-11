# Digital Twin Nodes for ComfyUI

**Pneumatic Hello World - Proof of Concept**

Turn ComfyUI into a Digital Twin Logic Engine with editable Shadow API functions and code generation.

## 🎯 Features

- ✅ **6-Level Digital Twin Hierarchy** (Component → Asset → System → Process → Product → Facility)
- ✅ **Editable Shadow API Functions** - Define API calls inline with custom code
- ✅ **Twin Widgets** - Input (buttons, sensors) and Output (status, 3D viewers)
- ✅ **State Persistence** - Memory across workflow executions
- ✅ **Async/Await Support** - Non-blocking operations with real physics timing
- ✅ **WebSocket Communication** - Real-time updates to frontend
- ✅ **Code Generation** - Export workflows to Python/JavaScript

## 📦 Installation

The nodes are already installed in your `custom_nodes/digital_twin_nodes/` directory.

### Restart ComfyUI

```bash
# Stop ComfyUI if running, then:
python main.py
```

You should see:
```
[Digital Twin Nodes] Loaded successfully!
  - 24 nodes registered
  - Server extension initialized
  - Shadow API framework ready
```

## 🚀 Quick Start - Pneumatic Hello World

### Workflow Overview

This proof of concept demonstrates:
1. User clicks "Start" button
2. System checks cable connection
3. Logic AND gate ensures both conditions met
4. Pneumatic cylinder extends (with 2s physics delay)
5. Stopwatch measures cycle time
6. Status displayed to user

### Building the Workflow

**Nodes needed:**
1. `🔘 Button Input` - Start button
2. `📡 Sensor Input` - Cable connection status
3. `∧ AND Gate` - Logic check
4. `🔧 L1: Pneumatic Cylinder` - Component twin
5. `⏱️ Stopwatch Timer` - Cycle time measurement
6. `📊 Status Display` - Output result

**Connections:**
```
[Button] ──┬──> [AND Gate] ──> [Pneumatic Cylinder] ──> [Stopwatch]
           │                                                   │
[Sensor] ──┘                                                   ▼
                                                        [Status Display]
```

### Step-by-Step Setup

#### 1. Add Button Input Widget
- Add node: `DT_Widget_ButtonInput`
- Set `widget_id`: `"btn_start"`
- Set `button_label`: `"Start Cycle"`

#### 2. Add Sensor Input Widget
- Add node: `DT_Widget_SensorInput`
- Set `widget_id`: `"sensor_cable"`
- Set `sensor_label`: `"Cable Connected"`
- Set `sensor_type`: `"BOOLEAN"`

#### 3. Add AND Gate
- Add node: `DT_Logic_AND`
- Connect `Button.button_pressed` → `AND.input_a`
- Connect `Sensor.bool_value` → `AND.input_b`

#### 4. Add Pneumatic Cylinder (with Shadow API!)
- Add node: `DT_L1_PneumaticCylinder`
- Set `component_id`: `"SAC_001"`
- Set `air_pressure_psi`: `80.0`
- Set `extension_time_ms`: `2000`
- Connect `AND.output` → `Cylinder.extend_command`

**Edit Shadow API** (see section below)

#### 5. Add Stopwatch
- Add node: `DT_Logic_Stopwatch`
- Set `stopwatch_id`: `"timer_01"`
- Connect `Button.button_pressed` → `Stopwatch.start_signal`
- Connect `Cylinder.is_extended` → `Stopwatch.stop_signal`

#### 6. Add Status Display
- Add node: `DT_Widget_StatusOutput`
- Set `widget_id`: `"status_main"`
- Connect `Stopwatch.status_message` → `StatusOutput.display_value`

## 🔧 Editing Shadow API Functions

### What is a Shadow API?

Each digital twin node can have a **Shadow API** - a custom function that:
- Defines input arguments and types
- Contains custom Python code
- Can call real system APIs or return simulated data
- Is editable from within the node

### Example: Pneumatic Cylinder Shadow API

In the `DT_L1_PneumaticCylinder` node, the `shadow_api_definition` parameter contains JSON:

```json
{
  "function_name": "control_cylinder",
  "input_args": [
    {"name": "component_id", "type": "str"},
    {"name": "action", "type": "str"},
    {"name": "pressure", "type": "float"}
  ],
  "return_type": "dict",
  "code": "... your Python code here ..."
}
```

### Default Shadow API Code

The cylinder comes with default code:

```python
async def execute(**kwargs):
    """
    Shadow API for Pneumatic Cylinder Control

    Args:
        component_id: Cylinder identifier
        action: "extend" or "retract"
        pressure: Air pressure in PSI

    Returns:
        dict with status and health
    """
    import aiohttp
    import os

    mode = os.getenv("DT_MODE", "simulation")

    if mode == "simulation":
        # Simulation mode - return mock data
        return {
            "status": "success",
            "health": "OK",
            "simulated": True,
            "action": kwargs.get("action"),
            "pressure": kwargs.get("pressure")
        }

    elif mode == "production":
        # Production mode - call real PLC API
        async with aiohttp.ClientSession() as session:
            url = f"http://plc-{kwargs['component_id']}.local/api/actuate"
            async with session.post(url, json=kwargs) as resp:
                return await resp.json()

    return {"status": "error", "message": "Unknown mode"}
```

### Customizing Shadow API

You can edit the `shadow_api_definition` parameter to:

1. **Change function name**
2. **Add/remove input arguments**
3. **Change return type**
4. **Write custom implementation code**

#### Example: Add Real PLC Integration

```json
{
  "function_name": "control_sac_plc",
  "input_args": [
    {"name": "component_id", "type": "str"},
    {"name": "action", "type": "str"},
    {"name": "pressure", "type": "float"},
    {"name": "plc_address", "type": "str", "default": "192.168.1.100"}
  ],
  "return_type": "dict",
  "code": "async def execute(**kwargs):\n    import aiohttp\n    \n    plc_url = f\"http://{kwargs['plc_address']}/api/cylinder\"\n    \n    async with aiohttp.ClientSession() as session:\n        async with session.post(plc_url, json={\n            'id': kwargs['component_id'],\n            'action': kwargs['action'],\n            'pressure': kwargs['pressure']\n        }) as resp:\n            return await resp.json()\n"
}
```

## 🌐 WebSocket API Endpoints

The server extension adds these routes:

### Widget Events
```http
POST /digital_twin/widget/event
Content-Type: application/json

{
  "widget_id": "btn_start",
  "widget_type": "button",
  "value": true,
  "auto_execute": false
}
```

### Shadow API Management

**Get Shadow API Definition:**
```http
GET /digital_twin/shadow_api/{node_id}
```

**Update Shadow API:**
```http
POST /digital_twin/shadow_api/{node_id}
Content-Type: application/json

{
  "function_name": "my_function",
  "input_args": [...],
  "return_type": "dict",
  "code": "async def execute(**kwargs): ..."
}
```

**List All Shadow APIs:**
```http
GET /digital_twin/shadow_api
```

### State Management

**Get State:**
```http
GET /digital_twin/state/{level}
GET /digital_twin/state/{level}/{key}
```

Levels: `components`, `assets`, `systems`, `processes`, `products`, `facility`, `widgets`

**Get Complete Hierarchy:**
```http
GET /digital_twin/hierarchy
```

### Code Generation

```http
POST /digital_twin/generate_code
Content-Type: application/json

{
  "workflow": { /* ComfyUI workflow JSON */ },
  "target": "python"  // or "javascript"
}
```

Returns generated executable code.

## 📝 Code Generation

### Generate Python Code from Workflow

```bash
curl -X POST http://localhost:8188/digital_twin/generate_code \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": { /* your workflow */ },
    "target": "python"
  }'
```

The generated code includes:
- All Shadow API function implementations
- Node execution in dependency order
- State management
- Async/await for timing
- Standalone executable Python script

### Example Generated Code

```python
"""
Generated Digital Twin Workflow
Auto-generated from ComfyUI workflow with Shadow APIs
"""

import asyncio
import time
import aiohttp
import json

# Shadow API for pneumatic_cyl_SAC_001
async def execute(**kwargs):
    mode = os.getenv("DT_MODE", "simulation")
    if mode == "simulation":
        return {"status": "success", "health": "OK"}
    # ... production code ...

async def execute_digital_twin_workflow():
    state = {}

    # Node 1: Button Input
    button_pressed = state.get("widgets", {}).get("btn_start", False)

    # Node 2: Sensor Input
    cable_connected = state.get("widgets", {}).get("sensor_cable", False)

    # Node 3: AND Logic
    result = button_pressed and cable_connected

    # Node 4: Pneumatic Cylinder
    if result:
        print("[SAC_001] Extending cylinder...")
        api_result = await execute(component_id="SAC_001", action="extend", pressure=80.0)
        await asyncio.sleep(2.0)
        state["SAC_001"] = {"position": 200.0, "extended": True}

    # Node 5: Stopwatch
    # ... timer logic ...

    return state

if __name__ == '__main__':
    asyncio.run(execute_digital_twin_workflow())
```

## 🔌 Frontend Integration Example

### Simple HTML Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>Digital Twin Dashboard</title>
</head>
<body>
    <h1>Pneumatic Hello World</h1>

    <button id="btnStart">Start Cycle</button>
    <label>
        <input type="checkbox" id="sensorCable"> Cable Connected
    </label>

    <div id="status">Idle</div>

    <script>
        const ws = new WebSocket('ws://localhost:8188/ws?clientId=' + crypto.randomUUID());

        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);

            if (msg.type === 'twin_widget_update') {
                if (msg.data.widget_id === 'status_main') {
                    document.getElementById('status').innerText = msg.data.value;
                }
            }
        };

        // Send button click
        document.getElementById('btnStart').onclick = async () => {
            await fetch('http://localhost:8188/digital_twin/widget/event', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    widget_id: 'btn_start',
                    widget_type: 'button',
                    value: true
                })
            });
        };

        // Send cable status
        document.getElementById('sensorCable').onchange = async (e) => {
            await fetch('http://localhost:8188/digital_twin/widget/event', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    widget_id: 'sensor_cable',
                    widget_type: 'sensor',
                    value: e.target.checked
                })
            });
        };
    </script>
</body>
</html>
```

## 🎨 Available Nodes

### Widget Nodes (Input)
- `🔘 Button Input` - Button press events
- `📡 Sensor Input` - Sensor/feedback data (BOOLEAN/FLOAT/STRING)

### Widget Nodes (Output)
- `📊 Status Display` - Text display
- `🎨 3D Viewer` - 3D model visualization
- `🔌 Connection Indicator` - Connection status

### Level 1 - Component Twins
- `🔧 L1: Pneumatic Cylinder` - Pneumatic cylinder with shadow API

### Level 2 - Asset Twins
- `⚙️ L2: SAC Asset` - Single Acting Cylinder asset

### Logic Nodes
- `⏱️ Stopwatch Timer` - Cycle time measurement
- `∧ AND Gate` - Boolean AND operation

### Existing Nodes (Workflow Planning)
- All your existing DT nodes for robot workflows

## 🐛 Debugging

### Check Shadow API Registry

```python
from custom_nodes.digital_twin_nodes.shadow_api import ShadowAPIRegistry

registry = ShadowAPIRegistry()
apis = registry.get_all_definitions()
print(apis)
```

### Check State

```python
from custom_nodes.digital_twin_nodes.state_manager import DigitalTwinStateManager

state = DigitalTwinStateManager()
print(state.get_hierarchy())
```

### Set Execution Mode

```bash
# Simulation mode (default)
export DT_MODE=simulation

# Production mode (calls real APIs)
export DT_MODE=production
```

## 🚀 Next Steps

1. **Test the PoC**: Build the Pneumatic Hello World workflow
2. **Customize Shadow APIs**: Add your actual PLC/robot API calls
3. **Expand Hierarchy**: Add L3-L6 nodes for your systems
4. **Build Dashboard**: Create frontend for visualization
5. **Code Generation**: Export workflows to standalone apps

## 📚 Documentation Files

- `state_manager.py` - State persistence
- `shadow_api.py` - Editable API framework
- `widget_nodes.py` - Input/Output widgets
- `pneumatic_nodes.py` - Pneumatic PoC nodes
- `server_extension.py` - WebSocket routes
- `code_generator.py` - Code generation engine

## 🆘 Support

Check the console logs for:
```
[Digital Twin Nodes] Loaded successfully!
[Digital Twin] Server extension loaded successfully
```

If nodes don't appear, check for Python import errors.

---

**Built for real-time digital twin orchestration with ComfyUI as the Logic Engine.**
