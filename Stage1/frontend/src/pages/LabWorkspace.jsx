import React, { useState, useEffect } from 'react';
import DataCanvas from '../components/workspace/DataCanvas';
import ResultsOverlay from '../components/workspace/ResultsOverlay';
import api from '../api';
import { ArrowLeft, Beaker } from 'lucide-react';

const LabWorkspace = ({ onBackToDashboard }) => {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [selectedVariant, setSelectedVariant] = useState(null);
  
  const [previewData, setPreviewData] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  
  const [experimentResult, setExperimentResult] = useState(null);
  const [experimentError, setExperimentError] = useState(null);
  const [isTraining, setIsTraining] = useState(false);
  const [showResults, setShowResults] = useState(false);

  // Fetch all scenarios
  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const response = await api.get('/scenarios/');
        // We fetch ALL scenarios, not filtered by activeModule
        setScenarios(response.data);
      } catch (err) {
        console.error("Failed to fetch scenarios", err);
      }
    };
    fetchScenarios();
  }, []);

  useEffect(() => {
    if (selectedScenario && selectedVariant) {
      fetchPreview();
    }
  }, [selectedScenario, selectedVariant]);

  const fetchPreview = async () => {
    setLoadingPreview(true);
    setPreviewData(null);
    try {
      const response = await api.get(`/${selectedScenario.model_type.toLowerCase()}/preview/`, {
        params: {
          scenario_id: selectedScenario.id,
          variant_name: selectedVariant
        }
      });
      setPreviewData(response.data);
    } catch (err) {
      console.error("Failed to fetch preview", err);
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleRunModel = async () => {
    setIsTraining(true);
    setShowResults(false);
    setExperimentResult(null);
    setExperimentError(null);
    try {
      const response = await api.post(`/${selectedScenario.model_type.toLowerCase()}/run/`, {
        scenario_id: selectedScenario.id,
        variant_name: selectedVariant,
        student_prompt: ''
      });
      setExperimentResult(response.data);
      setShowResults(true);
    } catch (err) {
      console.error("Experiment failed", err);
      setExperimentError(err.response?.data?.error || err.message);
    } finally {
      setIsTraining(false);
    }
  };

  if (!selectedScenario) {
    // RENDER FULL-SCREEN GRID OF SCENARIOS
    return (
      <div style={{ padding: '40px', height: '100vh', overflowY: 'auto' }}>
        <button className="btn-secondary" onClick={onBackToDashboard} style={{ marginBottom: '30px' }}>
          <ArrowLeft size={18} /> Back to Dashboard
        </button>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '10px' }}><Beaker size={36} style={{ verticalAlign: 'middle', marginRight: '10px' }} /> Prediction Engine</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '40px' }}>Select an experiment below to start training AI models!</p>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
          {scenarios.map(scenario => (
            <div 
              key={scenario.id}
              className="glass-panel"
              onClick={() => {
                setSelectedScenario(scenario);
                setSelectedVariant(null);
                setPreviewData(null);
              }}
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
      
      {/* Top Header with Back Button */}
      <div style={{ padding: '15px 20px', borderBottom: '1px solid var(--glass-border)', display: 'flex', alignItems: 'center', background: 'rgba(10, 15, 30, 0.8)' }}>
        <button 
          className="btn-secondary" 
          onClick={() => setSelectedScenario(null)}
          style={{ padding: '8px 15px', marginRight: '20px' }}
        >
          <ArrowLeft size={18} /> Back to Scenarios
        </button>
        <h2 style={{ margin: 0, fontSize: '1.3rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
          {selectedScenario.icon} {selectedScenario.title}
        </h2>
      </div>

      {/* Main Data Canvas */}
      <div style={{ flex: 1, position: 'relative', overflowY: 'auto' }}>
        <DataCanvas 
          scenario={selectedScenario}
          selectedVariant={selectedVariant}
          onSelectVariant={setSelectedVariant}
          previewData={previewData}
          loading={loadingPreview}
          onRunModel={handleRunModel}
          isTraining={isTraining}
          experimentResult={experimentResult}
          experimentError={experimentError}
        />

        {/* OVERLAY: Results frosted glass card */}
        {showResults && experimentResult && (
          <ResultsOverlay 
            result={experimentResult} 
            onClose={() => setShowResults(false)} 
          />
        )}
      </div>

    </div>
  );
};

export default LabWorkspace;
