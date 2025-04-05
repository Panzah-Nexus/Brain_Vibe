import React, { useEffect, useRef, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';

const GraphVisualization = ({ graphData, onNodeClick }) => {
  const cyRef = useRef(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredNodes, setFilteredNodes] = useState([]);

  useEffect(() => {
    if (cyRef.current) {
      // Apply styling to the graph
      cyRef.current.style([
        {
          selector: 'node',
          style: {
            'background-color': '#6FB1FC',
            'label': 'data(display_name)',
            'text-valign': 'center',
            'text-halign': 'center',
            'color': '#fff',
            'font-size': '12px',
            'text-outline-width': 1,
            'text-outline-color': '#222',
            'width': 'label',
            'height': 'label',
            'padding': '10px',
            'shape': 'round-rectangle'
          }
        },
        {
          selector: 'node[status = "LEARNED"]',
          style: {
            'background-color': '#7FBF7F',  // Green for learned topics
          }
        },
        {
          selector: 'node[status = "NOT_LEARNED"]',
          style: {
            'background-color': '#6FB1FC',  // Blue for not learned topics
          }
        },
        {
          selector: 'node.highlight',
          style: {
            'border-color': '#FFA500',
            'border-width': '3px'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier'
          }
        }
      ]);

      // Add event handlers
      cyRef.current.on('tap', 'node', function(evt) {
        const node = evt.target;
        if (onNodeClick) {
          onNodeClick(node.data());
        }
      });

      // Layout configuration
      const layout = cyRef.current.layout({
        name: 'breadthfirst',
        directed: true,
        padding: 30,
        spacingFactor: 1.5,
        animate: true
      });
      
      layout.run();

      // Fit the graph to the viewport
      cyRef.current.fit();
    }
  }, [graphData, onNodeClick]);

  // Handle search functionality
  useEffect(() => {
    if (!cyRef.current || !searchTerm) {
      // Clear highlights if searchTerm is empty
      if (cyRef.current) {
        cyRef.current.nodes().removeClass('highlight');
        setFilteredNodes([]);
      }
      return;
    }

    const lowercaseSearch = searchTerm.toLowerCase();
    const matchingNodes = cyRef.current.nodes().filter(node => {
      const displayName = node.data('display_name')?.toLowerCase() || '';
      const id = node.data('id')?.toLowerCase() || '';
      const description = node.data('short_description')?.toLowerCase() || '';
      
      return displayName.includes(lowercaseSearch) || 
             id.includes(lowercaseSearch) || 
             description.includes(lowercaseSearch);
    });

    // Clear previous highlights
    cyRef.current.nodes().removeClass('highlight');
    
    // Add highlight class to matching nodes
    matchingNodes.addClass('highlight');
    
    // Update filtered nodes list for display
    const nodeDataList = matchingNodes.map(node => node.data());
    setFilteredNodes(nodeDataList);
    
    // If there are matching nodes, center the view on them
    if (matchingNodes.length > 0) {
      cyRef.current.fit(matchingNodes, 50);
    }
  }, [searchTerm]);

  // Convert graph data to Cytoscape format
  const elements = [];
  
  // Add nodes
  if (graphData && graphData.nodes) {
    graphData.nodes.forEach(node => {
      elements.push({
        data: { 
          id: node.id || node.topic_id,
          ...node
        }
      });
    });
  }
  
  // Add edges
  if (graphData && graphData.edges) {
    graphData.edges.forEach((edge, index) => {
      elements.push({
        data: { 
          id: `edge-${index}`,
          source: edge.source,
          target: edge.target
        }
      });
    });
  }

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleNodeClick = (node) => {
    if (cyRef.current) {
      const selectedNode = cyRef.current.getElementById(node.id);
      cyRef.current.fit(selectedNode, 100);
      
      // Highlight the node
      cyRef.current.nodes().removeClass('highlight');
      selectedNode.addClass('highlight');
      
      // Also click it to trigger the regular node click handler
      if (onNodeClick) {
        onNodeClick(node);
      }
    }
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '10px', display: 'flex', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Search topics..."
          value={searchTerm}
          onChange={handleSearch}
          style={{ 
            padding: '8px', 
            borderRadius: '4px',
            border: '1px solid #ccc',
            marginRight: '10px',
            flexGrow: 1
          }}
        />
      </div>
      
      {searchTerm && filteredNodes.length > 0 && (
        <div style={{ 
          padding: '10px', 
          maxHeight: '150px', 
          overflowY: 'auto',
          borderBottom: '1px solid #eee'
        }}>
          <p>Found {filteredNodes.length} matches:</p>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {filteredNodes.map(node => (
              <li 
                key={node.id} 
                onClick={() => handleNodeClick(node)}
                style={{ 
                  padding: '5px',
                  cursor: 'pointer',
                  borderRadius: '3px',
                  marginBottom: '3px',
                  backgroundColor: '#f5f5f5'
                }}
              >
                {node.display_name}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      <div style={{ flexGrow: 1 }}>
        <CytoscapeComponent
          elements={elements}
          style={{ width: '100%', height: '100%' }}
          cy={(cy) => { cyRef.current = cy; }}
          wheelSensitivity={0.3}
        />
      </div>
    </div>
  );
};

export default GraphVisualization; 