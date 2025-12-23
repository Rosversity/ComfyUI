/**
 * ComfyUI Web Extension for Pneumatic Kit Node Badges
 *
 * This extension overrides the default badge display to show "pneumatic-kit"
 * for all nodes under the rlab/pneumatic-kit category.
 */

import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "rlab.pneumatic_kit.badge",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Check if this node belongs to pneumatic-kit
        if (nodeData.category && nodeData.category.includes("pneumatic-kit")) {
            // Override the badge display
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);

                // Set the badge to "pneumatic-kit"
                this.badge = "pneumatic-kit";
                this.badgeColor = "#2a5caa"; // Blue color for pneumatic-kit

                return result;
            };
        }
    },

    async loadedGraphNode(node, app) {
        // Also handle nodes loaded from saved workflows
        if (node.type && node.type.startsWith("pneumatic-kit")) {
            node.badge = "pneumatic-kit";
            node.badgeColor = "#2a5caa";
        }
    }
});
