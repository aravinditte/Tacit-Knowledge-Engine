import React, { useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import './App.css';

import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Panel,
  MarkerType,
  ConnectionLineType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from '@dagrejs/dagre';

const API_URL = 'http://127.0.0.1:8000/process-map';

// Dagre layout helper
const dagreGraph = new dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
const NODE_W = 220;
const NODE_H = 64;

function getLayouted(nodes, edges, direction = 'TB') {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((n) => dagreGraph.setNode(n.id, { width: NODE_W, height: NODE_H }));
  edges.forEach((e) => dagreGraph.setEdge(e.source, e.target));
  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((n) => {
    const pos = dagreGraph.node(n.id);
    return {
      ...n,
      targetPosition: isHorizontal ? 'left' : 'top',
      sourcePosition: isHorizontal ? 'right' : 'bottom',
      position: { x: pos.x - NODE_W / 2, y: pos.y - NODE_H / 2 },
    };
  });

  return { nodes: layoutedNodes, edges };
}

function App() {
  const [rawNodes, setRawNodes] = useState([]);
  const [rawEdges, setRawEdges] = useState([]);
  const [direction, setDirection] = useState('TB');
  const [loading, setLoading] = useState(false);

  const defaultEdgeOptions = useMemo(
    () => ({
      type: 'smoothstep',
      animated: true,
      style: { strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, width: 18, height: 18 },
      // 🎯 Use the bright accent color for edge labels to make them pop
      labelStyle: { fill: '#22d3ee', fontWeight: 700, fontSize: 12 },
      labelBgStyle: { fill: 'rgba(11, 18, 32, 0.7)' }, // Add a subtle dark background to the label text
      labelBgPadding: [4, 8],
      labelBgBorderRadius: 4,
    }),
    []
  );

  const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(() => {
    const nodes = rawNodes.map((node) => ({
      id: node.id,
      data: { label: node.label },
      position: { x: 0, y: 0 },
      style: {
        padding: '12px 16px',
        borderRadius: 10,
        fontWeight: 600,
        fontSize: 14,
      },
    }));

    const edges = rawEdges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      label: `count: ${edge.label}`,
    }));

    return getLayouted(nodes, edges, direction);
  }, [rawNodes, rawEdges, direction]);

  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges);

  useEffect(() => {
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  }, [layoutedNodes, layoutedEdges, setNodes, setEdges]);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(API_URL);
      const data = response.data;
      setRawNodes(data.nodes || []);
      setRawEdges(data.edges || []);
    } catch (error) {
      console.error('🔥 Error fetching process map data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const onConnect = useCallback(
    (params) =>
      setEdges((eds) =>
        addEdge({ ...params, type: ConnectionLineType.SmoothStep, animated: true }, eds)
      ),
    [setEdges]
  );

  const nodeColorForMiniMap = useCallback(() => '#64748b', []);

  return (
    <div className="app-shell">
      <div className="app-header">
        <div className="app-title">Tacit Studio — Process Map</div>
        <div className="app-subtitle">{loading ? 'Loading…' : 'Interactive flow view'}</div>
      </div>

      <div className="flow-wrap">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          defaultEdgeOptions={defaultEdgeOptions}
          connectionLineType={ConnectionLineType.SmoothStep}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          proOptions={{ hideAttribution: true }}
        >
          <Panel position="top-right" className="panel">
            <button
              className={`btn ${direction === 'TB' ? 'btn-active' : ''}`}
              onClick={() => setDirection('TB')}
              title="Vertical layout"
            >
              Vertical
            </button>
            <button
              className={`btn ${direction === 'LR' ? 'btn-active' : ''}`}
              onClick={() => setDirection('LR')}
              title="Horizontal layout"
            >
              Horizontal
            </button>
            <button className="btn" onClick={fetchData} title="Reload data">
              Refresh
            </button>
          </Panel>

          <Controls position="bottom-left" showInteractive orientation="vertical" />
          <MiniMap pannable zoomable nodeColor={nodeColorForMiniMap} nodeStrokeWidth={2} />
          <Background variant="dots" gap={20} size={1.5} />
        </ReactFlow>
      </div>
    </div>
  );
}

export default App;