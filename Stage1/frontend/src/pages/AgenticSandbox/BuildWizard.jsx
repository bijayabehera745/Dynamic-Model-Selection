import React, { useState } from 'react';
import { ArrowLeft, Bot, Sparkles, ArrowRight } from 'lucide-react';

export default function BuildWizard({ onBack, onComplete }) {
  const [prompt, setPrompt] = useState('');

  return (
    <div style={{ minHeight: '100vh', background: '#0f111a', color: 'white', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <button onClick={onBack} className="btn-secondary" style={{ position: 'absolute', top: 40, left: 40, display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.05)', border: 'none', padding: '10px 20px', borderRadius: '8px', color: '#cbd5e1', cursor: 'pointer' }}>
        <ArrowLeft size={18} /> Back
      </button>

      <div style={{ textAlign: 'center', maxWidth: '600px', animation: 'fadeInUp 0.5s ease-out' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '30px' }}>
          <div style={{ background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', padding: '20px', borderRadius: '24px', boxShadow: '0 10px 30px rgba(59, 130, 246, 0.3)' }}>
            <Bot size={60} color="#fff" />
          </div>
        </div>

        <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '20px' }}>What do you want to build?</h1>
        <p style={{ color: '#94a3b8', fontSize: '1.2rem', marginBottom: '40px' }}>
          Describe your AI pipeline idea.
        </p>

        <div style={{ position: 'relative', marginBottom: '30px' }}>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., An agent that reads resumes, extracts skills, and scores them..."
            style={{
              width: '100%',
              minHeight: '120px',
              background: 'rgba(30, 41, 59, 0.5)',
              border: '2px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '16px',
              padding: '20px',
              fontSize: '1.1rem',
              color: 'white',
              fontFamily: 'inherit',
              resize: 'none',
              outline: 'none',
              transition: 'border-color 0.3s'
            }}
            onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
            onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'}
          />
          <Sparkles size={20} color="#3b82f6" style={{ position: 'absolute', top: 20, right: 20, opacity: prompt ? 1 : 0.3 }} />
        </div>

        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
          <button
            onClick={() => onComplete(prompt)}
            disabled={!prompt.trim()}
            style={{
              padding: '12px 30px',
              fontSize: '1.1rem',
              borderRadius: '12px',
              background: prompt.trim() ? 'linear-gradient(135deg, #3b82f6, #2563eb)' : '#334155',
              color: prompt.trim() ? 'white' : '#94a3b8',
              border: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              cursor: prompt.trim() ? 'pointer' : 'not-allowed',
              transition: 'all 0.3s'
            }}
          >
            Start Building <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
