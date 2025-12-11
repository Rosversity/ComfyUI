"""
Shadow API Framework - Editable API functions within nodes
"""
import asyncio
import inspect
import json
from typing import Any, Dict, List, Optional, Callable
import aiohttp


class ShadowAPIFunction:
    """
    Represents an editable Shadow API function
    Users can define arguments, types, return type, and implementation code
    """

    def __init__(
        self,
        name: str = "shadow_api",
        input_args: Optional[List[Dict]] = None,
        return_type: str = "dict",
        code: str = "",
        node_id: Optional[str] = None
    ):
        """
        Initialize Shadow API function

        Args:
            name: Function name
            input_args: List of {"name": str, "type": str, "default": Any}
            return_type: Return type as string
            code: Python code to execute
            node_id: Associated node ID
        """
        self.name = name
        self.input_args = input_args or []
        self.return_type = return_type
        self.code = code or self._default_code()
        self.node_id = node_id
        self._compiled_func = None

    def _default_code(self) -> str:
        """Default code template"""
        return '''async def execute(**kwargs):
    """
    Shadow API function - Edit this code

    Available kwargs based on your input_args
    Returns: Based on your return_type
    """
    # Example: Call external API
    # async with aiohttp.ClientSession() as session:
    #     async with session.post("http://api.example.com", json=kwargs) as resp:
    #         return await resp.json()

    # For now, return simulated data
    return {
        "status": "success",
        "data": kwargs
    }
'''

    def get_definition(self) -> Dict:
        """Get API definition as dict"""
        return {
            "name": self.name,
            "input_args": self.input_args,
            "return_type": self.return_type,
            "code": self.code,
            "node_id": self.node_id
        }

    def set_definition(self, definition: Dict):
        """Update API definition"""
        self.name = definition.get("name", self.name)
        self.input_args = definition.get("input_args", self.input_args)
        self.return_type = definition.get("return_type", self.return_type)
        self.code = definition.get("code", self.code)
        self._compiled_func = None  # Reset compilation

    def add_input_arg(self, name: str, arg_type: str, default: Any = None):
        """Add an input argument"""
        self.input_args.append({
            "name": name,
            "type": arg_type,
            "default": default
        })

    def remove_input_arg(self, name: str):
        """Remove an input argument"""
        self.input_args = [arg for arg in self.input_args if arg["name"] != name]

    def update_code(self, code: str):
        """Update implementation code"""
        self.code = code
        self._compiled_func = None  # Reset compilation

    async def execute(self, **kwargs) -> Any:
        """
        Execute the shadow API function

        Args:
            **kwargs: Arguments matching input_args

        Returns:
            Result based on return_type
        """
        # Compile code if not already done
        if self._compiled_func is None:
            self._compile()

        # Execute
        try:
            result = await self._compiled_func(**kwargs)
            return result
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "node_id": self.node_id
            }

    def _compile(self):
        """Compile the code string into executable function"""
        # Create execution namespace
        namespace = {
            "asyncio": asyncio,
            "aiohttp": aiohttp,
            "json": json,
        }

        # Execute code to define the function
        exec(self.code, namespace)

        # Get the execute function
        if "execute" in namespace:
            self._compiled_func = namespace["execute"]
        else:
            raise ValueError(f"Shadow API code must define 'async def execute(**kwargs)' function")

    def validate_args(self, **kwargs) -> bool:
        """Validate provided arguments match definition"""
        for arg_def in self.input_args:
            arg_name = arg_def["name"]
            arg_type = arg_def["type"]

            if arg_name not in kwargs:
                # Check if has default
                if arg_def.get("default") is None:
                    return False
        return True


class ShadowAPIRegistry:
    """Registry for managing shadow APIs across all nodes"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.apis = {}
        return cls._instance

    def register(self, node_id: str, api: ShadowAPIFunction):
        """Register a shadow API for a node"""
        self.apis[node_id] = api

    def get(self, node_id: str) -> Optional[ShadowAPIFunction]:
        """Get shadow API for a node"""
        return self.apis.get(node_id)

    def update(self, node_id: str, definition: Dict):
        """Update shadow API definition"""
        if node_id in self.apis:
            self.apis[node_id].set_definition(definition)
        else:
            api = ShadowAPIFunction(node_id=node_id)
            api.set_definition(definition)
            self.register(node_id, api)

    def remove(self, node_id: str):
        """Remove shadow API"""
        if node_id in self.apis:
            del self.apis[node_id]

    def get_all_definitions(self) -> Dict[str, Dict]:
        """Get all API definitions for code generation"""
        return {
            node_id: api.get_definition()
            for node_id, api in self.apis.items()
        }


# Modes for shadow API execution
class ShadowAPIMode:
    """Execution modes for shadow APIs"""
    SIMULATION = "simulation"   # Return mock data
    TESTING = "testing"          # Call test APIs
    PRODUCTION = "production"    # Call real system APIs

    @staticmethod
    def get_current_mode() -> str:
        """Get current execution mode from environment"""
        import os
        return os.getenv("DT_MODE", ShadowAPIMode.SIMULATION)
