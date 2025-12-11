# Digital Twin Nodes - Quick Start Guide

## ✅ Installation Complete!

The syntax error has been **fixed**. Your nodes are ready to use.

## 🚀 Step-by-Step Setup

### 1. Restart ComfyUI

```bash
# Stop current ComfyUI instance (Ctrl+C)
# Then restart:
python main.py
```

**Look for this in the console:**
```
[Digital Twin Nodes] Loaded successfully!
  - 24 nodes registered
  - Server extension initialized
  - Shadow API framework ready
```

### 2. Verify Nodes Loaded

In ComfyUI web interface:
- Right-click on canvas → "Add Node"
- Look for "Digital Twin" category
- You should see:
  - **Digital Twin/Widgets/Input**
    - 🔘 Button Input
    - 📡 Sensor Input
  - **Digital Twin/Widgets/Output**
    - 📊 Status Display
    - 🎨 3D Viewer
    - 🔌 Connection Indicator
  - **Digital Twin/L1 Component/Pneumatic**
    - 🔧 L1: Pneumatic Cylinder
  - **Digital Twin/L2 Asset/Pneumatic**
    - ⚙️ L2: SAC Asset
  - **Digital Twin/Logic**
    - ⏱️ Stopwatch Timer
    - ∧ AND Gate

### 3. Build Pneumatic Hello World

**Add these nodes to the canvas:**

1. **Button Input Widget**
   - Right-click → Add Node → Digital Twin/Widgets/Input → 🔘 Button Input
   - Set `widget_id` to: `"btn_start"`
   - Set `button_label` to: `"Start Cycle"`

2. **Sensor Input Widget**
   - Add Node → Digital Twin/Widgets/Input → 📡 Sensor Input
   - Set `widget_id` to: `"sensor_cable"`
   - Set `sensor_type` to: `BOOLEAN`

3. **AND Gate**
   - Add Node → Digital Twin/Logic → ∧ AND Gate
   - Connect: `Button.button_pressed` → `AND.input_a`
   - Connect: `Sensor.bool_value` → `AND.input_b`

4. **Pneumatic Cylinder** (The main component!)
   - Add Node → Digital Twin/L1 Component/Pneumatic → �� L1: Pneumatic Cylinder
   - Set `component_id` to: `"SAC_001"`
   - Set `air_pressure_psi` to: `80.0`
   - Set `extension_time_ms` to: `2000`
   - Connect: `AND.output` → `Cylinder.extend_command`

5. **Stopwatch Timer**
   - Add Node → Digital Twin/Logic → ⏱️ Stopwatch Timer
   - Set `stopwatch_id` to: `"timer_01"`
   - Connect: `Button.button_pressed` → `Stopwatch.start_signal`
   - Connect: `Cylinder.is_extended` → `Stopwatch.stop_signal`

6. **Status Display**
   - Add Node → Digital Twin/Widgets/Output → 📊 Status Display
   - Set `widget_id` to: `"status_main"`
   - Connect: `Stopwatch.status_message` → `StatusDisplay.display_value`

### 4. Run the Workflow

**Option A: Simulate Button Press**
- Set `Button Input` node's initial value to trigger
- Queue the workflow
- Watch the console output

**Option B: Use the API** (More realistic)

```bash
# Simulate button press
curl -X POST http://localhost:8188/digital_twin/widget/event \
  -H "Content-Type: application/json" \
  -d '{
    "widget_id": "btn_start",
    "widget_type": "button",
    "value": true
  }'

# Set cable connection status
curl -X POST http://localhost:8188/digital_twin/widget/event \
  -H "Content-Type: application/json" \
  -d '{
    "widget_id": "sensor_cable",
    "widget_type": "sensor",
    "value": true
  }'

# Then queue the workflow in ComfyUI
```

### 5. Watch it Execute

In the console, you should see:
```
[SAC_001] Extending cylinder... (2000ms)
... (2 second delay) ...
Cycle Time: 2000 ms
```

## 🔧 Editing Shadow API Functions

### In the Pneumatic Cylinder Node

The `shadow_api_definition` parameter contains JSON defining the API:

```json
{
  "function_name": "control_cylinder",
  "input_args": [
    {"name": "component_id", "type": "str"},
    {"name": "action", "type": "str"},
    {"name": "pressure", "type": "float"}
  ],
  "return_type": "dict",
  "code": ""
}
```

**To customize:**

1. **Edit the code field** - Add your Python implementation:
```json
{
  ...,
  "code": "async def execute(**kwargs):\n    import aiohttp\n    async with aiohttp.ClientSession() as session:\n        url = f\"http://plc-{kwargs['component_id']}.local/api\"\n        async with session.post(url, json=kwargs) as resp:\n            return await resp.json()\n"
}
```

2. **Add new arguments:**
```json
{
  "input_args": [
    {"name": "component_id", "type": "str"},
    {"name": "action", "type": "str"},
    {"name": "pressure", "type": "float"},
    {"name": "plc_ip", "type": "str", "default": "192.168.1.100"}  ← New!
  ]
}
```

3. **Change execution mode:**
```bash
# Simulation mode (default)
export DT_MODE=simulation

# Production mode (calls real APIs)
export DT_MODE=production
```

## 📊 Monitoring State

### Check Current State

```bash
# Get all component states
curl http://localhost:8188/digital_twin/state/components

# Get widget states
curl http://localhost:8188/digital_twin/state/widgets

# Get complete hierarchy
curl http://localhost:8188/digital_twin/hierarchy
```

### Check Shadow APIs

```bash
# List all registered shadow APIs
curl http://localhost:8188/digital_twin/shadow_api

# Get specific shadow API
curl http://localhost:8188/digital_twin/shadow_api/pneumatic_cyl_SAC_001
```

## 🎨 Generating Code

### Export Your Workflow

1. Save your workflow in ComfyUI (it becomes a JSON file)

2. Generate Python code:
```bash
curl -X POST http://localhost:8188/digital_twin/generate_code \
  -H "Content-Type: application/json" \
  -d @workflow.json > generated_twin.py
```

3. Run standalone:
```bash
python generated_twin.py
```

## 🐛 Troubleshooting

### Nodes Don't Appear

**Check console for:**
```
[Digital Twin Nodes] Loaded successfully!
```

**If you see import errors:**
- Check [test_imports.py](test_imports.py) results
- Verify all `.py` files in `custom_nodes/digital_twin_nodes/`
- Look for syntax errors in console

### Shadow API Not Executing

1. Check `shadow_api_enabled` is `True`
2. Verify JSON format in `shadow_api_definition`
3. Look for errors in console during execution

### Workflow Doesn't Execute

1. Ensure all node connections are valid
2. Check console for execution errors
3. Verify widget states are set (if using API)

## 📚 Next Steps

1. ✅ Build the basic workflow (above)
2. 📝 Edit shadow API to add your custom code
3. 🌐 Create a simple frontend dashboard
4. 🏭 Add more L3-L6 nodes for your systems
5. 🚀 Generate and deploy production code

## 📖 Documentation

- [README.md](README.md) - Complete user guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details
- [pneumatic_nodes.py](pneumatic_nodes.py) - See shadow API implementation
- [shadow_api.py](shadow_api.py) - API framework details

## 🆘 Need Help?

Check the console logs when ComfyUI starts:
- Look for `[Digital Twin]` messages
- Check for import errors
- Verify server extension loaded

---

**You're ready to build your digital twin! 🎉**

Start by restarting ComfyUI and building the Pneumatic Hello World workflow above.
