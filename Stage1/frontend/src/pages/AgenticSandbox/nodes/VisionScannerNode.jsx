import { Handle, Position } from '@xyflow/react';
import { Camera } from 'lucide-react';

export default function VisionScannerNode({ data }) {
  return (
    <div className="custom-node" style={{ borderTop: '4px solid var(--accent-cyan)' }}>
      <div className="custom-node-header" style={{ color: 'var(--accent-cyan)' }}>
        <Camera size={16} /> <span>Vision Scanner</span>
      </div>
      <div className="custom-node-box" style={{ cursor: 'pointer' }}>
        Upload Image
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
