# Multi-Shadow Function Nodes - Complete Guide

## 🎯 Architecture Overview

Each digital twin node can have **multiple shadow functions** that are configured via JSON. The node acts as a **Control System** that routes inputs to the appropriate shadow functions.

```
┌──────────────────────────────────────────────────────┐
│         Control System Node                          │
│                                                      │
│  Node Inputs:                                        │
│    input_1 (mapped to "temp")   ──┐                 │
│    input_2 (mapped to "pressure")─┼─┐               │
│    input_3 (mapped to "position")─┼─┼─┐             │
│                                   │ │ │             │
│  Shadow Functions:                │ │ │             │
│  ┌──────────────────────────────┐ │ │ │            │
│  │ read_sensor(temp, pressure) ◄─┴─┴─┘            │
│  │   Code: async def execute... │                  │
│  │   Returns: sensor_data       │                  │
│  └──────────────────────────────┘                  │
│                                                     │
│  ┌──────────────────────────────┐                  │
│  │ write_actuator(position)     │                  │
│  │   Code: async def execute... │                  │
│  │   Returns: actuator_status   │                  │
│  └──────────────────────────────┘                  │
│                                                     │
│  Node Outputs:                                      │
│    output_1 → sensor_data                          │
│    output_2 → actuator_status                      │
└──────────────────────────────────────────────────────┘
```

## 📝 Configuration Format

Shadow functions are configured as JSON in the node:

```json
{
  "input_mapping": {
    "input_1": "temp",
    "input_2": "pressure",
    "input_3": "position"
  },
  "functions": [
    {
      "name": "read_sensor",
      "inputs": ["temp", "pressure"],
      "output": "sensor_data",
      "input_types": {
        "temp": "float",
        "pressure": "float"
      },
      "output_type": "dict",
      "code": "async def execute(**kwargs):\n    temp = kwargs.get('temp', 0.0)\n    pressure = kwargs.get('pressure', 0.0)\n    \n    # Simulate sensor reading\n    return {\n        'temperature': temp,\n        'pressure': pressure,\n        'timestamp': time.time()\n    }\n"
    },
    {
      "name": "write_actuator",
      "inputs": ["position"],
      "output": "actuator_status",
      "input_types": {
        "position": "float"
      },
      "output_type": "bool",
      "code": "async def execute(**kwargs):\n    import aiohttp\n    position = kwargs.get('position', 0.0)\n    \n    # Call actuator API\n    async with aiohttp.ClientSession() as session:\n        async with session.post(\n            'http://actuator.local/api/move',\n            json={'position': position}\n        ) as resp:\n            result = await resp.json()\n            return result.get('success', False)\n"
    }
  ]
}
```

## 🔧 How It Works

### 1. Input Mapping
Node generic inputs (`input_1`, `input_2`, etc.) are mapped to named parameters:

```json
"input_mapping": {
  "input_1": "temp",      // input_1 becomes "temp" parameter
  "input_2": "pressure",  // input_2 becomes "pressure" parameter
  "input_3": "position"   // input_3 becomes "position" parameter
}
```

### 2. Shadow Functions
Each function defines:
- **name**: Function identifier
- **inputs**: Which parameters it uses (from input_mapping)
- **output**: Name of the output variable
- **code**: Python async function implementation

### 3. Execution Flow

```python
# User connects nodes in ComfyUI:
[Temperature Sensor] → Control System.input_1
[Pressure Sensor]    → Control System.input_2
[Position Command]   → Control System.input_3

# Node receives:
input_1 = 25.5  (temperature)
input_2 = 101.3 (pressure)
input_3 = 150.0 (position)

# Input mapping transforms to:
mapped_inputs = {
  "temp": 25.5,
  "pressure": 101.3,
  "position": 150.0
}

# Shadow functions execute:
read_sensor(temp=25.5, pressure=101.3)
  → returns: {"temperature": 25.5, "pressure": 101.3, "timestamp": ...}
  → stored as output_1 (sensor_data)

write_actuator(position=150.0)
  → returns: True
  → stored as output_2 (actuator_status)

# Node outputs:
output_1 = {"temperature": 25.5, ...}
output_2 = True
```

## 🎨 Example: Pneumatic Control System

### Node Configuration

```json
{
  "input_mapping": {
    "input_1": "start_signal",
    "input_2": "air_pressure",
    "input_3": "target_position"
  },
  "functions": [
    {
      "name": "read_sensors",
      "inputs": ["air_pressure"],
      "output": "sensor_readings",
      "code": "async def execute(**kwargs):\n    pressure = kwargs.get('air_pressure', 0.0)\n    return {\n        'pressure_psi': pressure,\n        'is_safe': pressure > 60 and pressure < 100\n    }\n"
    },
    {
      "name": "control_cylinder",
      "inputs": ["start_signal", "target_position"],
      "output": "cylinder_state",
      "code": "async def execute(**kwargs):\n    if not kwargs.get('start_signal', False):\n        return {'state': 'idle'}\n    \n    target = kwargs.get('target_position', 0.0)\n    \n    # Simulate movement\n    await asyncio.sleep(2.0)\n    \n    return {\n        'state': 'extended',\n        'position_mm': target,\n        'duration_ms': 2000\n    }\n"
    },
    {
      "name": "safety_check",
      "inputs": ["air_pressure", "start_signal"],
      "output": "safety_status",
      "code": "async def execute(**kwargs):\n    pressure = kwargs.get('air_pressure', 0.0)\n    start = kwargs.get('start_signal', False)\n    \n    is_safe = pressure >= 70 and pressure <= 90\n    \n    return {\n        'can_start': is_safe and start,\n        'reason': 'OK' if is_safe else 'Pressure out of range'\n    }\n"
    }
  ]
}
```

### ComfyUI Workflow

```
[Button Widget]         → Control System.input_1 (start_signal)
[Pressure Sensor]       → Control System.input_2 (air_pressure)
[Position Command]      → Control System.input_3 (target_position)

Control System → output_1 (sensor_readings) → Display Widget
              → output_2 (cylinder_state)   → Status Widget
              → output_3 (safety_status)    → Safety Indicator
```

## 🔄 Dynamic Updates

### Adding a New Shadow Function

1. **Edit the configuration JSON:**
```json
{
  "functions": [
    // ... existing functions ...
    {
      "name": "calculate_force",
      "inputs": ["air_pressure", "cylinder_area"],
      "output": "force_newtons",
      "code": "async def execute(**kwargs):\n    pressure = kwargs.get('air_pressure', 0.0)\n    area = kwargs.get('cylinder_area', 0.01)\n    force = pressure * 6894.76 * area  # PSI to Pa\n    return force\n"
    }
  ]
}
```

2. **Add input mapping:**
```json
"input_mapping": {
  "input_1": "start_signal",
  "input_2": "air_pressure",
  "input_3": "target_position",
  "input_4": "cylinder_area"  // New!
}
```

3. **Connect the input in ComfyUI:**
```
[Cylinder Area Constant] → Control System.input_4
```

4. **Use the output:**
```
Control System.output_4 → Force Display Widget
```

## 📊 Code Generation

When you generate code, each shadow function becomes a method:

```python
class ControlSystem:
    def __init__(self, node_id):
        self.node_id = node_id

    async def read_sensors(self, air_pressure):
        """Generated from shadow function: read_sensors"""
        pressure = air_pressure
        return {
            'pressure_psi': pressure,
            'is_safe': pressure > 60 and pressure < 100
        }

    async def control_cylinder(self, start_signal, target_position):
        """Generated from shadow function: control_cylinder"""
        if not start_signal:
            return {'state': 'idle'}

        target = target_position

        # Simulate movement
        await asyncio.sleep(2.0)

        return {
            'state': 'extended',
            'position_mm': target,
            'duration_ms': 2000
        }

    async def safety_check(self, air_pressure, start_signal):
        """Generated from shadow function: safety_check"""
        pressure = air_pressure
        start = start_signal

        is_safe = pressure >= 70 and pressure <= 90

        return {
            'can_start': is_safe and start,
            'reason': 'OK' if is_safe else 'Pressure out of range'
        }

    async def execute(self, input_1, input_2, input_3, input_4=None, input_5=None):
        """Execute all shadow functions"""
        # Input mapping
        start_signal = input_1
        air_pressure = input_2
        target_position = input_3

        # Execute functions
        sensor_readings = await self.read_sensors(air_pressure)
        cylinder_state = await self.control_cylinder(start_signal, target_position)
        safety_status = await self.safety_check(air_pressure, start_signal)

        return {
            'output_1': sensor_readings,
            'output_2': cylinder_state,
            'output_3': safety_status
        }
```

## 🎯 Best Practices

### 1. Name Inputs Meaningfully
```json
"input_mapping": {
  "input_1": "sensor_temp",        // ✅ Clear
  "input_2": "actuator_position"   // ✅ Clear
}

// Not:
"input_mapping": {
  "input_1": "a",   // ❌ Unclear
  "input_2": "b"    // ❌ Unclear
}
```

### 2. Keep Functions Focused
```json
// ✅ Good - single responsibility
{
  "name": "read_temperature",
  "inputs": ["sensor_id"],
  "code": "..."
}

// ❌ Too broad
{
  "name": "do_everything",
  "inputs": ["all", "the", "things"],
  "code": "... 500 lines ..."
}
```

### 3. Document Your Functions
```python
"code": """async def execute(**kwargs):
    '''
    Read temperature from sensor

    Args:
        sensor_id: Sensor identifier

    Returns:
        dict with temperature and timestamp
    '''
    # Implementation...
"""
```

### 4. Handle Errors Gracefully
```python
"code": """async def execute(**kwargs):
    try:
        result = await call_api(**kwargs)
        return result
    except Exception as e:
        return {
            'error': str(e),
            'status': 'failed'
        }
"""
```

## 🚀 Next Steps

1. **Use the Control System node** with multi-shadow functions
2. **Configure your shadow functions** via JSON
3. **Map inputs** to function parameters
4. **Connect in ComfyUI** workflow
5. **Generate code** for production deployment

---

**This architecture gives you the flexibility to add/remove/modify shadow functions without changing the node code!**
