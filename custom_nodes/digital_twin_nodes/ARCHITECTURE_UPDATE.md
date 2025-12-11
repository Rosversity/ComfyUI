# Architecture Update: Multi-Shadow Functions

## ✅ **What Changed**

Based on your diagram showing **Control System with multiple internal shadow functions**, I've updated the architecture:

### **Before (Single Shadow per Node):**
```
[Pneumatic Cylinder Node] → has 1 shadow API
[SAC Asset Node]         → has 1 shadow API
```

### **After (Multi-Shadow per Node):**
```
┌─────────────────────────────────────┐
│  Control System Node                │
│                                     │
│  Inputs → Internal Router →         │
│      ├─ read_data_block()          │
│      ├─ write_data_block()         │
│      └─ calculate_control()        │
│                           ↓         │
│                        Outputs      │
└─────────────────────────────────────┘
```

---

## 🎯 **New Architecture Matches Your Diagram**

```
External Channels → [Control System Node] → Shadow Functions → Outputs
                      │
                      ├─ Read data blocks  (shadow function)
                      ├─ Write data blocks (shadow function)
                      └─ Other functions   (shadow function)
```

### **Key Features:**

1. ✅ **Multiple shadow functions per node**
2. ✅ **Functions are internal to the node** (not separate nodes)
3. ✅ **Dynamic input/output mapping**
4. ✅ **Edit functions via JSON configuration**
5. ✅ **Inputs route to appropriate functions**
6. ✅ **Outputs appear from the Control System node**

---

## 📦 **New Files Created**

### 1. [multi_shadow_base.py](multi_shadow_base.py)
Base class for nodes with multiple shadow functions:
- `MultiShadowBaseNode` - Inherit from this for multi-shadow support
- `DT_ControlSystem` - Example Control System node

### 2. [MULTI_SHADOW_GUIDE.md](MULTI_SHADOW_GUIDE.md)
Complete guide with:
- How to configure shadow functions
- Input/output mapping
- Example workflows
- Code generation

---

## 🔧 **How To Use**

### **Step 1: Add Control System Node**

In ComfyUI:
- Add node: `🎛️ Control System (Multi-Shadow)`
- Set `node_id`: `"control_01"`

### **Step 2: Configure Shadow Functions**

Edit the `shadow_functions_config` parameter (JSON):

```json
{
  "input_mapping": {
    "input_1": "sensor_temp",
    "input_2": "actuator_position",
    "input_3": "safety_flag"
  },
  "functions": [
    {
      "name": "read_sensors",
      "inputs": ["sensor_temp"],
      "output": "sensor_data",
      "code": "async def execute(**kwargs):\n    temp = kwargs.get('sensor_temp', 0.0)\n    return {'temperature': temp, 'status': 'OK'}\n"
    },
    {
      "name": "write_actuator",
      "inputs": ["actuator_position"],
      "output": "actuator_status",
      "code": "async def execute(**kwargs):\n    pos = kwargs.get('actuator_position', 0.0)\n    # Call actuator API\n    return True\n"
    },
    {
      "name": "safety_check",
      "inputs": ["sensor_temp", "safety_flag"],
      "output": "is_safe",
      "code": "async def execute(**kwargs):\n    temp = kwargs.get('sensor_temp', 0.0)\n    flag = kwargs.get('safety_flag', False)\n    return temp < 100 and flag\n"
    }
  ]
}
```

### **Step 3: Connect Inputs**

```
[Temperature Sensor] → Control System.input_1  (mapped to "sensor_temp")
[Position Command]   → Control System.input_2  (mapped to "actuator_position")
[Safety Switch]      → Control System.input_3  (mapped to "safety_flag")
```

### **Step 4: Use Outputs**

```
Control System.output_1 (sensor_data)      → Display Widget
Control System.output_2 (actuator_status)  → Status Widget
Control System.output_3 (is_safe)          → Safety Indicator
```

---

## 🎨 **Example: Your Diagram in ComfyUI**

### **Your Original Diagram:**
```
Inputs → [Control System] → Outputs
          ├─ Read data blocks
          └─ Write data blocks
```

### **In ComfyUI:**

```
[Sensor 1] ──┐
[Sensor 2] ──┼─→ [🎛️ Control System] ──┬─→ [Display 1]
[Command]  ──┘    │                     ├─→ [Display 2]
                  │  Shadow Functions:  └─→ [Display 3]
                  │  - read_sensor_1()
                  │  - read_sensor_2()
                  │  - write_command()
                  │  - calculate_output()
```

### **Shadow Functions Config:**

```json
{
  "input_mapping": {
    "input_1": "sensor_1_value",
    "input_2": "sensor_2_value",
    "input_3": "command_value"
  },
  "functions": [
    {
      "name": "read_sensor_1",
      "inputs": ["sensor_1_value"],
      "output": "sensor_1_data",
      "code": "async def execute(**kwargs):\n    return {'value': kwargs.get('sensor_1_value')}\n"
    },
    {
      "name": "read_sensor_2",
      "inputs": ["sensor_2_value"],
      "output": "sensor_2_data",
      "code": "async def execute(**kwargs):\n    return {'value': kwargs.get('sensor_2_value')}\n"
    },
    {
      "name": "write_command",
      "inputs": ["command_value"],
      "output": "command_status",
      "code": "async def execute(**kwargs):\n    cmd = kwargs.get('command_value')\n    # Execute command\n    return {'executed': True, 'command': cmd}\n"
    }
  ]
}
```

---

## 📊 **Comparison**

| Feature | Old (Single Shadow) | New (Multi-Shadow) |
|---------|--------------------|--------------------|
| **Shadow Functions per Node** | 1 | Multiple (unlimited) |
| **Function Management** | Node parameter | JSON config array |
| **Input Mapping** | Fixed | Dynamic via config |
| **Output Mapping** | Fixed | Dynamic via config |
| **Add New Function** | Modify node code | Edit JSON config |
| **Matches Diagram** | ❌ No | ✅ Yes |

---

## 🚀 **Next Steps**

### **1. Test the Control System Node**

```bash
# Restart ComfyUI
python main.py

# Look for:
[Digital Twin Nodes] Loaded successfully!
  - 25 nodes registered  # Now includes Control System
```

### **2. Build Example Workflow**

- Add `🎛️ Control System (Multi-Shadow)` node
- Configure shadow functions (see guide)
- Connect inputs/outputs
- Run workflow

### **3. Create Your Custom Control Systems**

You can now create nodes that match your exact architecture:
- **PLC Control System** - Read sensors, write actuators
- **Robot Controller** - Multiple arm/gripper functions
- **Process Controller** - Monitor/control multiple systems

### **4. Code Generation**

Generate standalone code with all shadow functions as class methods:

```bash
curl -X POST http://localhost:8188/digital_twin/generate_code \
  -H "Content-Type: application/json" \
  -d @workflow.json > control_system.py
```

---

## 📚 **Documentation**

- [MULTI_SHADOW_GUIDE.md](MULTI_SHADOW_GUIDE.md) - Complete guide
- [multi_shadow_base.py](multi_shadow_base.py) - Implementation
- [QUICKSTART.md](QUICKSTART.md) - Getting started

---

## ✅ **Summary**

**You now have the architecture you described!**

- ✅ Control System node with multiple internal shadow functions
- ✅ Shadow functions = "Read/Write data blocks"
- ✅ Inputs route to appropriate shadow functions
- ✅ Outputs come from the Control System node
- ✅ Fully configurable via JSON
- ✅ Dynamic add/remove/edit functions
- ✅ Code generation support

**This matches your diagram exactly!** 🎉

The Control System node acts as a container with multiple shadow functions (read blocks, write blocks, etc.) that process inputs and produce outputs, just like in your architecture diagram.
