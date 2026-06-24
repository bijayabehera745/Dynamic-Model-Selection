import { Handle, Position } from '@xyflow/react';
import { GitBranch } from 'lucide-react';

export default function DeciderNode({ data }) {
  return (
    <div className="custom-node" style={{ borderTop: '4px solid #F59E0B' }}>
      <Handle type="target" position={Position.Left} />
      <div className="custom-node-header" style={{ color: '#F59E0B' }}>
        <GitBranch size={16} /> <span>The Decider</span>
      </div>
      <div className="custom-node-box" style={{ marginBottom: '10px' }}>
        Routes based on logic
      </div>
      
      <div style={{ position: 'relative', marginTop: '10px' }}>
        <div style={{ fontSize: '10px', textAlign: 'right', color: 'var(--accent-green)', paddingRight: '15px' }}>True</div>
        <Handle type="source" position={Position.Right} id="true" style={{ top: 8, borderColor: 'var(--accent-green)' }} />
        
        <div style={{ fontSize: '10px', textAlign: 'right', color: 'var(--accent-red)', marginTop: '8px', paddingRight: '15px' }}>False</div>
        <Handle type="source" position={Position.Right} id="false" style={{ top: 28, borderColor: 'var(--accent-red)' }} />
      </div>
    </div>
  );
}
