/**
 * Knowledge Graph Utilities
 * 
 * Utility functions for knowledge graph operations
 */

class KnowledgeGraphUtils {
    constructor() {
        this.graphData = null;
        this.nodeTypes = new Set();
        this.relationshipTypes = new Set();
        
        console.log('✅ Knowledge Graph Utils initialized');
    }

    /**
     * Process raw graph data
     */
    processGraphData(rawData) {
        if (!rawData || !rawData.nodes || !rawData.links) {
            return { nodes: [], links: [] };
        }

        const processedNodes = rawData.nodes.map(node => ({
            id: node.id,
            label: node.label || node.id,
            type: node.type || 'concept',
            weight: node.weight || 1,
            x: node.x || Math.random() * 800,
            y: node.y || Math.random() * 600
        }));

        const processedLinks = rawData.links.map(link => ({
            source: link.source,
            target: link.target,
            type: link.type || 'related',
            weight: link.weight || 1,
            label: link.label || ''
        }));

        this.graphData = {
            nodes: processedNodes,
            links: processedLinks
        };

        this.extractMetadata();
        return this.graphData;
    }

    /**
     * Extract metadata from graph
     */
    extractMetadata() {
        if (!this.graphData) return;

        this.nodeTypes.clear();
        this.relationshipTypes.clear();

        this.graphData.nodes.forEach(node => {
            this.nodeTypes.add(node.type);
        });

        this.graphData.links.forEach(link => {
            this.relationshipTypes.add(link.type);
        });
    }

    /**
     * Filter graph by node type
     */
    filterByNodeType(types) {
        if (!this.graphData) return { nodes: [], links: [] };

        const typeSet = new Set(Array.isArray(types) ? types : [types]);
        const filteredNodes = this.graphData.nodes.filter(node => 
            typeSet.has(node.type)
        );
        
        const nodeIds = new Set(filteredNodes.map(node => node.id));
        const filteredLinks = this.graphData.links.filter(link =>
            nodeIds.has(link.source) && nodeIds.has(link.target)
        );

        return {
            nodes: filteredNodes,
            links: filteredLinks
        };
    }

    /**
     * Get node neighbors
     */
    getNodeNeighbors(nodeId) {
        if (!this.graphData) return [];

        const neighbors = new Set();
        this.graphData.links.forEach(link => {
            if (link.source === nodeId) {
                neighbors.add(link.target);
            } else if (link.target === nodeId) {
                neighbors.add(link.source);
            }
        });

        return Array.from(neighbors);
    }

    /**
     * Calculate node centrality
     */
    calculateCentrality() {
        if (!this.graphData) return {};

        const centrality = {};
        
        // Initialize centrality scores
        this.graphData.nodes.forEach(node => {
            centrality[node.id] = 0;
        });

        // Calculate degree centrality
        this.graphData.links.forEach(link => {
            centrality[link.source] = (centrality[link.source] || 0) + 1;
            centrality[link.target] = (centrality[link.target] || 0) + 1;
        });

        return centrality;
    }

    /**
     * Find shortest path between nodes
     */
    findShortestPath(startId, endId) {
        if (!this.graphData) return [];

        const queue = [[startId]];
        const visited = new Set([startId]);

        while (queue.length > 0) {
            const path = queue.shift();
            const current = path[path.length - 1];

            if (current === endId) {
                return path;
            }

            const neighbors = this.getNodeNeighbors(current);
            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push([...path, neighbor]);
                }
            }
        }

        return [];
    }

    /**
     * Get graph statistics
     */
    getStatistics() {
        if (!this.graphData) {
            return {
                nodeCount: 0,
                linkCount: 0,
                nodeTypes: 0,
                relationshipTypes: 0,
                density: 0
            };
        }

        const nodeCount = this.graphData.nodes.length;
        const linkCount = this.graphData.links.length;
        const maxPossibleLinks = nodeCount * (nodeCount - 1) / 2;
        const density = maxPossibleLinks > 0 ? linkCount / maxPossibleLinks : 0;

        return {
            nodeCount,
            linkCount,
            nodeTypes: this.nodeTypes.size,
            relationshipTypes: this.relationshipTypes.size,
            density: Math.round(density * 1000) / 1000
        };
    }

    /**
     * Export graph data
     */
    exportGraph(format = 'json') {
        if (!this.graphData) return null;

        switch (format) {
            case 'json':
                return JSON.stringify(this.graphData, null, 2);
            case 'csv':
                return this.exportToCSV();
            case 'gexf':
                return this.exportToGEXF();
            default:
                return this.graphData;
        }
    }

    /**
     * Export to CSV format
     */
    exportToCSV() {
        if (!this.graphData) return '';

        const nodesCsv = 'id,label,type,weight\n' + 
            this.graphData.nodes.map(node => 
                `${node.id},${node.label},${node.type},${node.weight}`
            ).join('\n');

        const linksCsv = 'source,target,type,weight,label\n' + 
            this.graphData.links.map(link => 
                `${link.source},${link.target},${link.type},${link.weight},${link.label}`
            ).join('\n');

        return { nodes: nodesCsv, links: linksCsv };
    }

    /**
     * Export to GEXF format
     */
    exportToGEXF() {
        if (!this.graphData) return '';

        let gexf = '<?xml version="1.0" encoding="UTF-8"?>\n';
        gexf += '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n';
        gexf += '<graph mode="static" defaultedgetype="undirected">\n';
        
        // Nodes
        gexf += '<nodes>\n';
        this.graphData.nodes.forEach(node => {
            gexf += `<node id="${node.id}" label="${node.label}"/>\n`;
        });
        gexf += '</nodes>\n';
        
        // Edges
        gexf += '<edges>\n';
        this.graphData.links.forEach((link, index) => {
            gexf += `<edge id="${index}" source="${link.source}" target="${link.target}"/>\n`;
        });
        gexf += '</edges>\n';
        
        gexf += '</graph>\n</gexf>';
        return gexf;
    }
}

// Initialize knowledge graph utils
const knowledgeGraphUtils = new KnowledgeGraphUtils();

// Make available globally
window.knowledgeGraphUtils = knowledgeGraphUtils;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KnowledgeGraphUtils;
}