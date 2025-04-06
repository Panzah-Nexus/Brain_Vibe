import { useEffect, useRef, useMemo } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import coseBilkent from 'cytoscape-cose-bilkent';

// Register the layout extensions
cytoscape.use(dagre);
cytoscape.use(coseBilkent);

/**
 * TopicGraph component for visualizing topic dependency graphs
 * 
 * @param {Object} props
 * @param {Array} props.topics - Array of topic objects
 * @param {Function} props.onNodeClick - Callback when a node is clicked
 * @param {string} props.layout - Layout algorithm ('dagre' or 'cose-bilkent')
 * @param {string} props.height - Height of the graph container
 */
const TopicGraph = ({ 
  topics = [], 
  onNodeClick = () => {}, 
  layout = 'dagre',
  height = '600px'
}) => {
  const cyRef = useRef(null);

  useEffect(() => {
    if (cyRef.current) {
      // Apply double-click handler
      cyRef.current.on('tap', 'node', (event) => {
        const node = event.target;
        onNodeClick(node.data());
      });
    }
  }, [onNodeClick]);

  // Convert topics to Cytoscape elements
  const elements = useMemo(() => {
    if (!topics || topics.length === 0) return { nodes: [], edges: [] };

    // Create nodes
    const nodes = topics.map(topic => ({
      data: {
        id: topic.topic_id,
        label: topic.title || topic.name,
        status: topic.status || 'not_learned',
        description: topic.description || '',
        // Store additional data for access on click
        ...topic
      }
    }));

    // Create edges from prerequisites
    const edges = [];
    topics.forEach(topic => {
      if (topic.prerequisites && topic.prerequisites.length > 0) {
        topic.prerequisites.forEach(prereqId => {
          edges.push({
            data: {
              id: `${prereqId}-${topic.topic_id}`,
              source: prereqId,
              target: topic.topic_id
            }
          });
        });
      }
    });

    return [...nodes, ...edges];
  }, [topics]);

  // Layout configuration
  const layoutConfig = {
    dagre: {
      name: 'dagre',
      rankDir: 'TB', // Top to bottom
      rankSep: 100,  // Vertical spacing between nodes
      nodeSep: 50,   // Horizontal spacing between nodes
      padding: 30,   // Padding around the graph
      animate: true, // Animate when applying layout
      fit: true      // Fit graph to container
    },
    'cose-bilkent': {
      name: 'cose-bilkent',
      animationDuration: 500,
      nodeDimensionsIncludeLabels: true,
      fit: true,
      padding: 30,
      randomize: false
    }
  };

  // Style for the graph
  const stylesheet = [
    // Node styles
    {
      selector: 'node',
      style: {
        'background-color': '#f5f5f5',
        'label': 'data(label)',
        'text-valign': 'center',
        'text-halign': 'center',
        'text-wrap': 'wrap',
        'text-max-width': '120px',
        'height': '40px',
        'width': '40px',
        'font-size': '10px',
        'border-width': '2px',
        'border-color': '#ddd',
        'shape': 'roundrectangle',
        'padding': '10px'
      }
    },
    // Status-specific styles
    {
      selector: 'node[status = "learned"]',
      style: {
        'background-color': '#a8e6cf', // Light green
        'border-color': '#69c595'
      }
    },
    {
      selector: 'node[status = "in_progress"]',
      style: {
        'background-color': '#ffd3b6', // Light orange
        'border-color': '#ffaa77'
      }
    },
    {
      selector: 'node[status = "not_learned"]',
      style: {
        'background-color': '#f4f4f4', // Light grey
        'border-color': '#dcdcdc'
      }
    },
    // Edge styles
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': '#ccc',
        'target-arrow-color': '#ccc',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'arrow-scale': 1
      }
    },
    // Hover styles
    {
      selector: 'node:hover',
      style: {
        'background-color': '#e0e0e0',
        'border-width': '3px',
        'border-color': '#aaa',
        'z-index': 999
      }
    }
  ];

  return (
    <div style={{ 
      height, 
      width: '100%', 
      border: '1px solid #e0e0e0', 
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      <CytoscapeComponent
        cy={(cy) => { cyRef.current = cy; }}
        elements={elements}
        layout={layoutConfig[layout]}
        stylesheet={stylesheet}
        style={{ width: '100%', height: '100%' }}
        boxSelectionEnabled={false}
        autounselectify={false}
        userZoomingEnabled={true}
        userPanningEnabled={true}
      />
    </div>
  );
};

export default TopicGraph; 