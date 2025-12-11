"""
Digital Twin Server Extension - WebSocket routes for twin widgets
"""
import json
import asyncio
from aiohttp import web
from server import PromptServer
from .state_manager import DigitalTwinStateManager
from .shadow_api import ShadowAPIRegistry


class DigitalTwinServerExtension:
    """
    Extends PromptServer with digital twin specific routes
    """

    def __init__(self, server: PromptServer):
        self.server = server
        self.state_manager = DigitalTwinStateManager()
        self.shadow_api_registry = ShadowAPIRegistry()

    def add_routes(self):
        """Register custom routes"""

        # Widget interaction routes
        @self.server.routes.post('/digital_twin/widget/event')
        async def handle_widget_event(request):
            """
            Handle widget events from frontend (button clicks, sensor updates, etc.)

            POST body: {
                "widget_id": str,
                "widget_type": "button" | "sensor" | ...,
                "value": Any,
                "auto_execute": bool  # Optional: trigger workflow execution
            }
            """
            try:
                data = await request.json()
                widget_id = data.get('widget_id')
                widget_type = data.get('widget_type')
                value = data.get('value')

                # Store widget state
                self.state_manager.set("widgets", widget_id, value)

                # Broadcast to all connected clients
                await self.server.send_json("widget_state_update", {
                    "widget_id": widget_id,
                    "widget_type": widget_type,
                    "value": value
                })

                # Optionally auto-execute workflow
                if data.get('auto_execute'):
                    # TODO: Trigger workflow execution
                    pass

                return web.json_response({"status": "success"})

            except Exception as e:
                return web.json_response({"status": "error", "error": str(e)}, status=400)

        # Shadow API management routes
        @self.server.routes.get('/digital_twin/shadow_api/{node_id}')
        async def get_shadow_api(request):
            """Get shadow API definition for a node"""
            node_id = request.match_info['node_id']
            api = self.shadow_api_registry.get(node_id)

            if api:
                return web.json_response(api.get_definition())
            else:
                return web.json_response({"error": "API not found"}, status=404)

        @self.server.routes.post('/digital_twin/shadow_api/{node_id}')
        async def update_shadow_api(request):
            """
            Update shadow API definition

            POST body: {
                "function_name": str,
                "input_args": [{name, type, default}, ...],
                "return_type": str,
                "code": str
            }
            """
            try:
                node_id = request.match_info['node_id']
                definition = await request.json()

                # Update API
                self.shadow_api_registry.update(node_id, definition)

                return web.json_response({"status": "success"})

            except Exception as e:
                return web.json_response({"status": "error", "error": str(e)}, status=400)

        @self.server.routes.get('/digital_twin/shadow_api')
        async def list_shadow_apis(request):
            """List all shadow API definitions"""
            apis = self.shadow_api_registry.get_all_definitions()
            return web.json_response(apis)

        # State management routes
        @self.server.routes.get('/digital_twin/state/{level}')
        async def get_state(request):
            """Get state for a specific level"""
            level = request.match_info['level']
            state = self.state_manager.get(level)
            return web.json_response(state or {})

        @self.server.routes.get('/digital_twin/state/{level}/{key}')
        async def get_state_key(request):
            """Get specific state value"""
            level = request.match_info['level']
            key = request.match_info['key']
            value = self.state_manager.get(level, key)
            return web.json_response({"value": value})

        @self.server.routes.get('/digital_twin/hierarchy')
        async def get_hierarchy(request):
            """Get complete hierarchy state"""
            hierarchy = self.state_manager.get_hierarchy()
            return web.json_response(hierarchy)

        # Code generation route
        @self.server.routes.post('/digital_twin/generate_code')
        async def generate_code(request):
            """
            Generate code from workflow

            POST body: {
                "workflow": {...},  # ComfyUI workflow JSON
                "target": "python" | "javascript"
            }
            """
            try:
                data = await request.json()
                workflow = data.get('workflow', {})
                target = data.get('target', 'python')

                # Import code generator
                from .code_generator import DigitalTwinCodeGenerator

                generator = DigitalTwinCodeGenerator()
                code = generator.generate_from_workflow(workflow, target)

                return web.json_response({
                    "status": "success",
                    "code": code,
                    "target": target
                })

            except Exception as e:
                return web.json_response({
                    "status": "error",
                    "error": str(e)
                }, status=500)


def setup_server_extension():
    """Initialize server extension"""
    try:
        server = PromptServer.instance
        extension = DigitalTwinServerExtension(server)
        extension.add_routes()
        print("[Digital Twin] Server extension loaded successfully")
        return extension
    except Exception as e:
        print(f"[Digital Twin] Failed to load server extension: {e}")
        return None
