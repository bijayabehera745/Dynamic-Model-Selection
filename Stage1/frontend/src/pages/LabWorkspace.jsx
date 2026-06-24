import React, { useState, useEffect } from 'react';
import TimelineSidebar from '../components/workspace/TimelineSidebar';
import DataCanvas from '../components/workspace/DataCanvas';
import ResultsOverlay from '../components/workspace/ResultsOverlay';
import api from '../api';

const LabWorkspace = ({ onBackToDashboard }) => {
  const [activeModule, setActiveModule] = useState('regression');
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  
  // selectedVariant is now null by default to show the Variant Cards Grid
  const [selectedVariant, setSelectedVariant] = useState(null);
  
  const [previewData, setPreviewData] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  
  const [experimentResult, setExperimentResult] = useState(null);
  const [experimentError, setExperimentError] = useState(null);
  const [isTraining, setIsTraining] = useState(false);
  const [showResults, setShowResults] = useState(false);

  // 1. Fetch scenarios when module changes
  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const response = await api.get('/scenarios/');
        const filtered = response.data.filter(s => s.model_type.toLowerCase() === activeModule);
        setScenarios(filtered);
        
        // Auto-select first scenario if available, but DO NOT auto-select variant
        if (filtered.length > 0) {
          setSelectedScenario(filtered[0]);
          setSelectedVariant(null);
        } else {
          setSelectedScenario(null);
          setSelectedVariant(null);
        }
      } catch (err) {
        console.error("Failed to fetch scenarios", err);
      }
    };
    fetchScenarios();
  }, [activeModule]);

  // 2. Fetch preview data when a specific variant is selected
  useEffect(() => {
    if (selectedScenario && selectedVariant) {
      fetchPreview();
    }
  }, [selectedScenario, selectedVariant]);

  const handleScenarioSelect = (scenario) => {
    setSelectedScenario(scenario);
    setSelectedVariant(null); // Reset variant so user sees the cards
    setPreviewData(null);
  };

  const fetchPreview = async () => {
    setLoadingPreview(true);
    setPreviewData(null);
    try {
      const response = await api.get(`/${activeModule}/preview/`, {
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
      const response = await api.post(`/${activeModule}/run/`, {
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

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      
      {/* LEFT: Timeline Navigation */}
      <div style={{ width: '320px', borderRight: '1px solid var(--glass-border)' }}>
        <TimelineSidebar 
          activeModule={activeModule}
          setActiveModule={setActiveModule}
          scenarios={scenarios}
          selectedScenario={selectedScenario}
          onSelectScenario={handleScenarioSelect}
          onBackToDashboard={onBackToDashboard}
        />
      </div>

      {/* RIGHT: Main Data Canvas */}
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
