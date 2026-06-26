import React, { useState, useEffect } from 'react';
import DataLabCanvas from '../components/workspace/DataLabCanvas';
import api from '../api';
import { ArrowLeft, BarChart2 } from 'lucide-react';

const DataLabWorkspace = ({ onBackToDashboard }) => {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);

  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const response = await api.get('/scenarios/');
        setScenarios(response.data);
      } catch (err) {
        console.error("Failed to fetch scenarios", err);
      }
    };
    fetchScenarios();
  }, []);

  if (!selectedScenario) {
    return (
      <div style={{ padding: '40px', height: '100vh', overflowY: 'auto' }}>
        <button className="btn-secondary" onClick={onBackToDashboard} style={{ marginBottom: '30px' }}>
          <ArrowLeft size={18} /> Back to Dashboard
        </button>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '10px' }}>
          <BarChart2 size={36} style={{ verticalAlign: 'middle', marginRight: '10px' }} /> Data Lab
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '40px' }}>
          Welcome to the Data Lab! Here you can create and collect custom data to feed into the Prediction Engine.
        </p>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
          {scenarios.map(scenario => (
            <div 
              key={scenario.id}
              className="glass-panel"
              onClick={() => setSelectedScenario(scenario)}
              style={{
                cursor: 'pointer',
                padding: '20px',
                transition: 'transform 0.2s',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              <div style={{ fontSize: '3rem' }}>{scenario.icon}</div>
              <h3 style={{ fontSize: '1.2rem', margin: 0 }}>{scenario.title}</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: 'bold' }}>
                {scenario.model_type.replace('_', ' ')}
              </span>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', flex: 1 }}>{scenario.challenge}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <div style={{ padding: '15px 20px', borderBottom: '1px solid var(--glass-border)', display: 'flex', alignItems: 'center', background: 'rgba(10, 15, 30, 0.8)' }}>
        <button 
          className="btn-secondary" 
          onClick={() => setSelectedScenario(null)}
          style={{ padding: '8px 15px', marginRight: '20px' }}
        >
          <ArrowLeft size={18} /> Back to Scenarios
        </button>
        <h2 style={{ margin: 0, fontSize: '1.3rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
          {selectedScenario.icon} {selectedScenario.title} - Data Collection
        </h2>
      </div>

      <div style={{ flex: 1, position: 'relative', overflowY: 'auto' }}>
        <DataLabCanvas 
          scenario={selectedScenario}
          onBackToDashboard={onBackToDashboard}
        />
      </div>
    </div>
  );
};

export default DataLabWorkspace;
