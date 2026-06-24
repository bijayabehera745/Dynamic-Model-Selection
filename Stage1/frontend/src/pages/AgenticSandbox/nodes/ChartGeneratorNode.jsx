import { Handle, Position } from '@xyflow/react';
import { BarChart3 } from 'lucide-react';

export default function ChartGeneratorNode({ data }) {
  return (
    <div className="custom-node" style={{ borderTop: '4px solid var(--accent-green)' }}>
      <Handle type="target" position={Position.Left} />
      <div className="custom-node-header" style={{ color: 'var(--accent-green)' }}>
        <BarChart3 size={16} /> <span>Chart Generator</span>
      </div>
      <div className="custom-node-box" style={{ borderColor: 'var(--accent-green)' }}>
        📊 Chart Output
      </div>
    </div>
  );
}
