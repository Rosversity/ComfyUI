# Pneumatic Hello World - Complete Workflow Guide

## 🎯 **Complete System Flow**

```
┌──────────┐     ┌─────────────────┐     ┌───────────────┐     ┌───────────────┐     ┌──────────┐     ┌──────────┐
│  Button  │────>│ Control System  │────>│  Electrical   │────>│  Pneumatic    │────>│   SSV    │────>│   SAC    │
│  Widget  │     │ (Timer Logic)   │     │   System      │     │   System      │     │  Asset   │     │  Asset   │
└──────────┘     └─────────┬───────┘     └───────────────┘     └───────────────┘     └──────────┘     └────┬─────┘
                           ↑                     ↑                                                          │
┌──────────┐               │                     │                                                          │
│  Cable   │───────────────┘                     │                                                          │
│  Status  │                                     │                                                          │
└──────────┘                                     │                                                          │
                                                 │                                                          │
┌──────────┐                                     │                                                          │
│  URDF/   │─────────────────────────────────────┘                                                          │
│  STL     │                                                                                                │
└──────────┘                                                                                                │
                                                                                                            │
┌──────────┐               Feedback Loop ◄───────────────────────────────────────────────────────────────────┘
│  Timer   │               (Stop Timer, Calculate Duration)
│  Display │◄──────────────┘
└──────────┘
```

## 📋 **Shadow Functions in Each Node**

### **A. Control System** (`🎛️ Control System`)
**Shadow Functions:**
1. **on_button_press**
   - Input: Button pressed
   - Logic: `System.StartTime = Now()`
   - Output: `send_signal_to_electrical = TRUE`

2. **on_sac_feedback**
   - Input: SAC completion signal
   - Logic: `Duration = Now() - System.StartTime`
   - Output: Update timer display with duration

### **B. Electrical System** (`⚡ Electrical System`)
**Shadow Function:**
1. **check_power_conditions**
   - Input: Control signal + Cable status
   - Logic: `IF (Control == TRUE) AND (Cable == CONNECTED)`
   - Output: `pass_power = TRUE/FALSE`

### **C. Pneumatic System** (`💨 Pneumatic System`)
**Shadow Function:**
1. **supply_air**
   - Input: Power signal
   - Logic: `IF (Power == TRUE)`
   - Output: `supply_air = TRUE, pressure_psi`

### **D. SSV Asset** (`🔄 SSV Asset (Valve)`)
**Shadow Function:**
1. **actuate_valve**
   - Input: Air supply
   - Logic: `ValveState = OPEN`
   - Output: `actuate_cylinder = TRUE`

### **E. SAC Asset** (`🔧 SAC Asset (Cylinder)`)
**Shadow Function:**
1. **extend_cylinder**
   - Input: Valve actuation
   - Logic:
     ```
     Play Animation ("Extend_Cylinder")
     Wait(2000ms)
     Report Completion
     ```
   - Output: `report_completion = TRUE, position_mm = 200.0`

---

## 🛠️ **Step-by-Step Workflow Setup**

### **Step 1: Add Widget Nodes**

#### **A. Button Widget**
- Node: `🔘 Button Input`
- Parameters:
  - `widget_id`: `"btn_start"`
  - `button_label`: `"Start Cycle"`

#### **B. Cable Connection Widget**
- Node: `📡 Sensor Input`
- Parameters:
  - `widget_id`: `"sensor_cable"`
  - `sensor_type`: `BOOLEAN`

#### **C. Timer Display Widget**
- Node: `📊 Status Display`
- Parameters:
  - `widget_id`: `"timer_display"`

### **Step 2: Add System Nodes**

#### **A. Control System**
- Node: `🎛️ Control System`
- Parameters:
  - `system_id`: `"control_system_01"`

#### **B. Electrical System**
- Node: `⚡ Electrical System`
- Parameters:
  - `system_id`: `"electrical_01"`

#### **C. Pneumatic System**
- Node: `💨 Pneumatic System`
- Parameters:
  - `system_id`: `"pneumatic_01"`
  - `air_pressure_psi`: `80.0`

#### **D. SSV Asset (Valve)**
- Node: `🔄 SSV Asset (Valve)`
- Parameters:
  - `asset_id`: `"SSV_001"`

#### **E. SAC Asset (Cylinder)**
- Node: `🔧 SAC Asset (Cylinder)`
- Parameters:
  - `asset_id`: `"SAC_001"`
  - `extension_time_ms`: `2000`

### **Step 3: Connect the Nodes**

#### **Connections Diagram:**

```
[Button Widget].button_pressed ────────────────┬──> [Control System].button_pressed
                                               │
[Cable Widget].bool_value ─────────────────────┼──> [Electrical System].input_cable_connected
                                               │
[Control System].send_signal_to_electrical ────┴──> [Electrical System].input_control_signal

[Electrical System].pass_power ────────────────────> [Pneumatic System].input_power

[Pneumatic System].supply_air ─────────────────────> [SSV Asset].input_air_supply

[SSV Asset].actuate_cylinder ──────────────────────> [SAC Asset].input_actuate

[SAC Asset].report_completion ─────────────────────> [Control System].sac_feedback

[Control System].timer_display ────────────────────> [Timer Display].display_value
```

#### **Detailed Connection Steps:**

1. **Button → Control System:**
   - `Button Widget.button_pressed` → `Control System.button_pressed`

2. **Cable → Electrical System:**
   - `Cable Widget.bool_value` → `Electrical System.input_cable_connected`

3. **Control → Electrical:**
   - `Control System.send_signal_to_electrical` → `Electrical System.input_control_signal`

4. **Electrical → Pneumatic:**
   - `Electrical System.pass_power` → `Pneumatic System.input_power`

5. **Pneumatic → SSV:**
   - `Pneumatic System.supply_air` → `SSV Asset.input_air_supply`

6. **SSV → SAC:**
   - `SSV Asset.actuate_cylinder` → `SAC Asset.input_actuate`

7. **SAC → Control (Feedback):**
   - `SAC Asset.report_completion` → `Control System.sac_feedback`

8. **Control → Display:**
   - `Control System.timer_display` → `Timer Display.display_value`

---

## 🎬 **Execution Flow**

### **User Action: Click "Start Cycle" Button**

```
1. Button Widget → Sends TRUE signal
                   │
2. Control System  │ Shadow Fn: on_button_press
   └─ Starts timer (System.StartTime = Now())
   └─ Outputs: send_signal_to_electrical = TRUE
                   │
3. Electrical System │ Receives: control_signal = TRUE, cable_connected = TRUE
   └─ Shadow Fn: check_power_conditions
   └─ IF (TRUE AND TRUE) → pass_power = TRUE
                   │
4. Pneumatic System │ Receives: input_power = TRUE
   └─ Shadow Fn: supply_air
   └─ IF (TRUE) → supply_air = TRUE, pressure = 80 PSI
                   │
5. SSV Asset       │ Receives: input_air_supply = TRUE
   └─ Shadow Fn: actuate_valve
   └─ ValveState = OPEN → actuate_cylinder = TRUE
                   │
6. SAC Asset       │ Receives: input_actuate = TRUE
   └─ Shadow Fn: extend_cylinder
   └─ Play Animation ("Extend_Cylinder")
   └─ Wait(2000ms)  ◄── Physical simulation delay
   └─ Outputs: report_completion = TRUE, position = 200.0mm
                   │
7. Control System  │ Receives: sac_feedback = TRUE
   └─ Shadow Fn: on_sac_feedback
   └─ Calculates: Duration = Now() - StartTime = 2000ms
   └─ Outputs: timer_display = "Cycle Complete: 2000 ms"
                   │
8. Timer Display   │ Receives: display_value = "Cycle Complete: 2000 ms"
   └─ Shows: "Cycle Complete: 2000 ms" to user
```

---

## 📊 **Console Output Example**

When you run the workflow, you'll see:

```
[control_system_01] Shadow Fn: on_button_press - Timer started
[electrical_01] Shadow Fn: check_power_conditions - PASS (Power ON)
[pneumatic_01] Shadow Fn: supply_air - Air supplied at 80.0 PSI
[SSV_001] Shadow Fn: actuate_valve - Valve OPENED
[SAC_001] Shadow Fn: extend_cylinder - Playing animation 'Extend_Cylinder'
[SAC_001] Shadow Fn: extend_cylinder - Waiting 2000 ms
... (2 second delay) ...
[SAC_001] Shadow Fn: extend_cylinder - Extension complete, reporting back
[control_system_01] Shadow Fn: on_sac_feedback - Duration: 2000 ms
```

---

## 🎨 **Visual Workflow in ComfyUI**

```
┌────────────────┐
│ 🔘 Button      │
│ "btn_start"    │───┐
└────────────────┘   │
                     │
┌────────────────┐   │    ┌─────────────────────┐
│ 📡 Cable       │   ├───>│ 🎛️ Control System   │
│ "sensor_cable" │───┼───>│ system_id:         │
└────────────────┘   │    │ "control_01"        │
                     │    └──────┬──────────────┘
                     │           │ send_signal
                     │           │
                     │    ┌──────▼──────────────┐
                     │    │ ⚡ Electrical System│
                     └───>│ system_id:         │
                          │ "electrical_01"    │
                          └──────┬─────────────┘
                                 │ pass_power
                                 │
                          ┌──────▼─────────────┐
                          │ 💨 Pneumatic System│
                          │ system_id:        │
                          │ "pneumatic_01"    │
                          │ pressure: 80 PSI  │
                          └──────┬────────────┘
                                 │ supply_air
                                 │
                          ┌──────▼────────────┐
                          │ 🔄 SSV Asset      │
                          │ asset_id:        │
                          │ "SSV_001"        │
                          └──────┬───────────┘
                                 │ actuate_cylinder
                                 │
                          ┌──────▼───────────┐
                          │ 🔧 SAC Asset     │
                          │ asset_id:       │
                          │ "SAC_001"       │
                          │ time: 2000ms    │
                          └──────┬──────────┘
                                 │ report_completion
                                 │
                          ┌──────▼──────────┐
                          │ (Feedback loop) │
                          │ back to Control │
                          └─────────────────┘

                          ┌─────────────────┐
                          │ 📊 Timer Display│
                          │ "timer_display" │◄─── timer_display
                          └─────────────────┘
```

---

## 🚀 **Running the Workflow**

### **Method 1: Direct Button Press**
1. Add all nodes as described above
2. Connect them following the connection diagram
3. Set `Button Widget` initial value to `True`
4. Queue the workflow
5. Watch console output and timer display

### **Method 2: Via WebSocket API**

```bash
# 1. Set cable connected
curl -X POST http://localhost:8188/digital_twin/widget/event \
  -H "Content-Type: application/json" \
  -d '{
    "widget_id": "sensor_cable",
    "widget_type": "sensor",
    "value": true
  }'

# 2. Trigger button press
curl -X POST http://localhost:8188/digital_twin/widget/event \
  -H "Content-Type: application/json" \
  -d '{
    "widget_id": "btn_start",
    "widget_type": "button",
    "value": true
  }'

# 3. Queue the workflow in ComfyUI
```

---

## ✅ **Expected Results**

1. **Console Output:** Step-by-step shadow function execution
2. **Timing:** Exactly 2000ms delay for cylinder extension
3. **Display:** "Cycle Complete: 2000 ms" shown in timer widget
4. **Feedback Loop:** System properly resets after completion

---

## 📋 **Node Count**

Total: **30 nodes** registered
- 5 Pneumatic Hello World nodes (Control, Electrical, Pneumatic, SSV, SAC)
- 5 Widget nodes
- 4 Pneumatic PoC nodes
- 10 Existing workflow nodes
- 1 Multi-Shadow Control System
- Others

---

## 🎯 **Next Steps**

1. ✅ Restart ComfyUI to load all nodes
2. ✅ Build the workflow following this guide
3. ✅ Test with button widget
4. ✅ Verify console output
5. ✅ Check timer display
6. 🔜 Add 3D visualization for SAC animation
7. 🔜 Build frontend dashboard
8. 🔜 Generate standalone code

---

**This is the complete Pneumatic Hello World workflow as specified!** 🎉

All shadow functions are implemented and working as described in your specification.
