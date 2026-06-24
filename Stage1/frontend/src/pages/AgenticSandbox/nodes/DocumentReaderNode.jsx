import { Handle, Position } from '@xyflow/react';
import { FileText } from 'lucide-react';

export default function DocumentReaderNode({ data }) {
  return (
    <div className="custom-node" style={{ borderTop: '4px solid var(--accent-cyan)' }}>
      <div className="custom-node-header" style={{ color: 'var(--accent-cyan)' }}>
        <FileText size={16} /> <span>Document Reader</span>
      </div>
      <div className="custom-node-box" style={{ cursor: 'pointer' }}>
        Click to upload PDF/CSV
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
