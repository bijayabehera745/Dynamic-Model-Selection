import { Handle, Position, useReactFlow } from '@xyflow/react';
import { Camera, Upload, File as FileIcon, Image as ImageIcon } from 'lucide-react';
import { useRef } from 'react';

export default function VisionScannerNode({ id, data }) {
  const { setNodes } = useReactFlow();
  const fileInputRef = useRef(null);
  
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };
  
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const base64 = event.target.result;
      setNodes((nds) =>
        nds.map((n) => {
          if (n.id === id) {
            return {
              ...n,
              data: {
                ...n.data,
                fileName: file.name,
                fileType: file.type,
                fileBase64: base64,
              },
            };
          }
          return n;
        })
      );
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="custom-node" style={{ borderTop: '4px solid var(--accent-cyan)' }}>
      <div className="custom-node-header" style={{ color: 'var(--accent-cyan)' }}>
        <Camera size={16} /> <span>Vision Scanner</span>
      </div>
      <div className="custom-node-box" style={{ cursor: 'pointer', padding: '15px' }} onClick={handleUploadClick}>
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          accept="image/*,.pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" 
          onChange={handleFileChange}
        />
        {data.fileName ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
            {data.fileType?.startsWith('image/') ? <ImageIcon size={24} color="var(--accent-cyan)" /> : <FileIcon size={24} color="var(--accent-cyan)" />}
            <span style={{ fontSize: '0.8rem', wordBreak: 'break-all', textAlign: 'center', color: 'var(--text-secondary)' }}>
              {data.fileName}
            </span>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
            <Upload size={20} />
            <span style={{ fontSize: '0.8rem' }}>Click to Upload</span>
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
