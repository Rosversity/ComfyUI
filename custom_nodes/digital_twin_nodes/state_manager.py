"""
Digital Twin State Manager - Singleton for persistent state across workflow executions
"""
import time
import json
from typing import Any, Dict, Optional


class DigitalTwinStateManager:
    """
    Singleton state manager for all digital twin levels and widgets.
    Persists state between workflow executions.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize state storage"""
        self.states = {
            "components": {},    # Level 1
            "assets": {},        # Level 2
            "systems": {},       # Level 3
            "processes": {},     # Level 4
            "products": {},      # Level 5
            "facility": {},      # Level 6
            "widgets": {},       # UI widgets
            "shadow_apis": {},   # Shadow API function storage
        }
        self.history = []
        self.max_history = 1000

    def set(self, level: str, key: str, value: Any):
        """
        Store state at specific level

        Args:
            level: One of: components, assets, systems, processes, products, facility, widgets
            key: Unique identifier
            value: State data
        """
        if level not in self.states:
            self.states[level] = {}

        self.states[level][key] = value

        # Add to history
        self.history.append({
            "level": level,
            "key": key,
            "value": value,
            "timestamp": time.time()
        })

        # Trim history if too long
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get(self, level: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Retrieve state from specific level

        Args:
            level: State level
            key: Specific key (if None, returns entire level)
            default: Default value if not found
        """
        if key is None:
            return self.states.get(level, default)
        return self.states.get(level, {}).get(key, default)

    def delete(self, level: str, key: str):
        """Delete state"""
        if level in self.states and key in self.states[level]:
            del self.states[level][key]

    def get_hierarchy(self, facility_id: str = None) -> Dict:
        """Get complete hierarchy state"""
        return {
            "facility": self.get("facility", facility_id) if facility_id else self.get("facility"),
            "products": self.get("products"),
            "processes": self.get("processes"),
            "systems": self.get("systems"),
            "assets": self.get("assets"),
            "components": self.get("components"),
        }

    def get_history(self, level: Optional[str] = None, limit: int = 100) -> list:
        """Get state history"""
        history = self.history[-limit:]
        if level:
            return [h for h in history if h["level"] == level]
        return history

    def clear(self, level: Optional[str] = None):
        """Clear state (for level or all)"""
        if level:
            self.states[level] = {}
        else:
            self._initialize()

    def export_state(self) -> str:
        """Export current state as JSON"""
        return json.dumps({
            "states": self.states,
            "timestamp": time.time()
        }, indent=2, default=str)

    def import_state(self, state_json: str):
        """Import state from JSON"""
        data = json.loads(state_json)
        self.states = data.get("states", {})

    # Shadow API specific methods
    def register_shadow_api(self, node_id: str, api_definition: Dict):
        """
        Register a shadow API function definition

        Args:
            node_id: Unique node identifier
            api_definition: {
                "function_name": str,
                "input_args": [{"name": str, "type": str, "default": Any}, ...],
                "return_type": str,
                "code": str
            }
        """
        self.states["shadow_apis"][node_id] = api_definition

    def get_shadow_api(self, node_id: str) -> Optional[Dict]:
        """Get shadow API definition for a node"""
        return self.states["shadow_apis"].get(node_id)

    def update_shadow_api_code(self, node_id: str, code: str):
        """Update just the code portion of a shadow API"""
        if node_id in self.states["shadow_apis"]:
            self.states["shadow_apis"][node_id]["code"] = code
