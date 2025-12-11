/**
 * ComfyUI Extension: Workflow Export Bridge
 * Bidirectional communication for workflow save/load with parent window
 */

import { app } from "../../scripts/app.js";

// Listen for messages from parent window
window.addEventListener('message', (event) => {
    // Only accept messages from trusted origins (or * for debugging if needed, but safer to list)
    // Since parent uses postMessage('*'), we don't check event.origin strictly here against a fixed list if we want to be permissive during dev
    // But let's check basic validity of message
    if (!event.data || !event.data.type) return;

    // GET_WORKFLOW: Export current workflow
    if (event.data.type === 'GET_WORKFLOW') {
        try {
            const workflow = app.graph.serialize();
            const nodeCount = workflow.nodes?.length || 0;
            console.log('[ComfyUI Extension] Exporting workflow with', nodeCount, 'nodes');
            
            event.source.postMessage({
                type: 'WORKFLOW_DATA',
                workflow: {
                    workflow: workflow,
                    metadata: {
                        name: app.graph.title || 'Untitled Workflow',
                        nodes: nodeCount,
                        links: workflow.links?.length || 0,
                        timestamp: new Date().toISOString()
                    }
                }
            }, event.origin);
        } catch (error) {
            console.error('[ComfyUI Extension] ❌ Export error:', error);
            event.source.postMessage({ type: 'WORKFLOW_ERROR', error: error.message }, event.origin);
        }
    }
    
    // LOAD_WORKFLOW: Load workflow into canvas
    if (event.data.type === 'LOAD_WORKFLOW') {
        try {
            console.log('[ComfyUI Extension] Received workflow load request');
            const data = event.data.workflow;
            
            // Handle potentially nested workflow object or direct graph object
            // Our saver saves { workflow: graph, ... }, so we expect data.workflow to be the graph
            let workflowToLoad = data.workflow || data;
            
            // Double check for double nesting
            if (workflowToLoad.workflow) {
                console.log('[ComfyUI Extension] Detected double nesting, fixing...');
                workflowToLoad = workflowToLoad.workflow;
            }

            const nodeCount = workflowToLoad.nodes?.length || 0;
            console.log('[ComfyUI Extension] Loading graph with', nodeCount, 'nodes');
            
            if (nodeCount === 0) {
                 console.warn('[ComfyUI Extension] ⚠️ Warning: Loading empty workflow!');
            }

            // Clear first to ensure clean state
            app.graph.clear();
            app.loadGraphData(workflowToLoad);
            
            console.log('[ComfyUI Extension] ✅ Graph loaded');
        } catch (error) {
            console.error('[ComfyUI Extension] ❌ Load error:', error);
        }
    }
    
    // CLEAR_WORKFLOW: Clear the canvas
    if (event.data.type === 'CLEAR_WORKFLOW') {
        console.log('[ComfyUI Extension] Clearing canvas...');
        try {
            app.graph.clear();
        } catch (error) {
            console.error('[ComfyUI Extension] ❌ Clear error:', error);
        }
    }
});

app.registerExtension({
    name: "Comfy.WorkflowExportBridge",
    async setup() {
        console.log('[ComfyUI Extension] 🚀 Workflow Export Bridge loaded v2.0');
    }
});
