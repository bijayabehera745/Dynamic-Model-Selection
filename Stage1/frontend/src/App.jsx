import React, { useContext, useState } from 'react';
import { AuthContext, AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import StudentDashboard from './pages/StudentDashboard';
import LabWorkspace from './pages/LabWorkspace';
import DataLabWorkspace from './pages/DataLabWorkspace';
import AgenticLanding from './pages/AgenticSandbox/AgenticLanding';
import AIFoundationsDashboard from './pages/AIFoundations/AIFoundationsDashboard';
import EmergenceOfIntelligence from './pages/AIFoundations/EmergenceOfIntelligence';
import './index.css';

const AppContent = () => {
  const { user, loading } = useContext(AuthContext);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard' | 'lab'

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'white' }}>
        <h2>Loading...</h2>
      </div>
    );
  }

  // Pure SPA routing based on auth state and role
  if (!user) {
    return <Login />;
  }

  if (user.is_staff) {
    return <AdminDashboard />;
  }

  // Student Routing
  if (currentView === 'dashboard') {
    return <StudentDashboard 
             onNavigateToLab={() => setCurrentView('lab')} 
             onNavigateToDataLab={() => setCurrentView('data_lab')}
             onNavigateToAgentic={() => setCurrentView('agentic')} 
             onNavigateToFoundations={() => setCurrentView('foundations')}
           />;
  }

  if (currentView === 'lab') {
    return <LabWorkspace onBackToDashboard={() => setCurrentView('dashboard')} />;
  }

  if (currentView === 'data_lab') {
    return <DataLabWorkspace onBackToDashboard={() => setCurrentView('dashboard')} />;
  }

  if (currentView === 'agentic') {
    return <AgenticLanding onBackToDashboard={() => setCurrentView('dashboard')} />;
  }

  if (currentView === 'foundations') {
    return <AIFoundationsDashboard 
             onBackToDashboard={() => setCurrentView('dashboard')} 
             onNavigateToLesson1={() => setCurrentView('emergence_lesson')}
           />;
  }

  if (currentView === 'emergence_lesson') {
    return <EmergenceOfIntelligence onBackToDashboard={() => setCurrentView('foundations')} />;
  }
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
