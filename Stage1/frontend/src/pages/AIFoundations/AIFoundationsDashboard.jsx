import React from 'react';
import { ArrowLeft, PlayCircle, Lock } from 'lucide-react';

const AIFoundationsDashboard = ({ onBackToDashboard, onNavigateToLesson1 }) => {
  const lessons = [
    {
      id: 'lesson1',
      title: 'Emergence of AI',
      subtitle: 'Lesson 01',
      description: 'Trace the history of mathematics from counting stones to the dawn of artificial intelligence.',
      active: true,
      onClick: onNavigateToLesson1,
      color: 'var(--accent-purple)'
    },
    {
      id: 'lesson2',
      title: 'The Learning Machines',
      subtitle: 'Lesson 02',
      description: 'Discover how computers learned to recognize patterns instead of following rigid rules.',
      active: false,
      color: 'var(--accent-cyan)'
    },
    {
      id: 'lesson3',
      title: 'Neural Networks Deep Dive',
      subtitle: 'Lesson 03',
      description: 'Explore the architecture inspired by the human brain that powers modern AI.',
      active: false,
      color: 'var(--accent-green)'
    }
  ];

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto', color: 'var(--text-primary)' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '50px' }}>
        <button className="btn-secondary" onClick={onBackToDashboard} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ArrowLeft size={18} /> Back
        </button>
        <div>
          <h1 style={{ fontSize: '2.5rem', margin: 0 }}>AI Foundations</h1>
          <p style={{ color: 'var(--text-secondary)', margin: '5px 0 0 0' }}>Understand the core concepts of artificial intelligence.</p>
        </div>
      </div>

      {/* Grid of Lessons */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '30px' }}>
        {lessons.map(lesson => (
          <div 
            key={lesson.id}
            className="glass-panel"
            onClick={lesson.active ? lesson.onClick : undefined}
            style={{ 
              flex: '1 1 300px',
              maxWidth: '400px',
              padding: '30px', 
              cursor: lesson.active ? 'pointer' : 'not-allowed',
              opacity: lesson.active ? 1 : 0.6,
              display: 'flex',
              flexDirection: 'column',
              transition: 'transform 0.2s, box-shadow 0.2s',
              border: lesson.active ? `1px solid ${lesson.color}` : '1px solid var(--glass-border)'
            }}
            onMouseEnter={(e) => {
              if(lesson.active) {
                e.currentTarget.style.transform = 'translateY(-5px)';
                e.currentTarget.style.boxShadow = `0 10px 30px rgba(0,0,0,0.5), 0 0 15px ${lesson.color}33`;
              }
            }}
            onMouseLeave={(e) => {
              if(lesson.active) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }
            }}
          >
            <div style={{ fontSize: '0.85rem', color: lesson.color, fontWeight: '600', marginBottom: '10px', textTransform: 'uppercase' }}>
              {lesson.subtitle}
            </div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '15px' }}>{lesson.title}</h2>
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.5', fontSize: '0.95rem', flexGrow: 1 }}>
              {lesson.description}
            </p>
            
            <div style={{ marginTop: '20px' }}>
              {lesson.active ? (
                <button className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', fontSize: '0.9rem' }}>
                  <PlayCircle size={18} /> Start Lesson
                </button>
              ) : (
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', fontSize: '0.85rem' }}>
                  <Lock size={16} /> Locked
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AIFoundationsDashboard;
