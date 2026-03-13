// src/pages/verify.jsx

import React, { useState } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import VerificationDashboard from '../components/VerificationDashboard';

export default function VerifyPage() {
  const [mode, setMode] = useState('full');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(null);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 20px' }}>
      <h1>responzai Verifier</h1>
      <p>Pr&uuml;fen Sie Ihre Texte auf Richtigkeit, Aktualit&auml;t und Konsistenz.</p>

      {!result && (
        <>
          <DocumentUpload
            mode={mode}
            onModeChange={setMode}
            onResult={setResult}
            onProgress={setProgress}
            onLoadingChange={setLoading}
          />
          {loading && progress && (
            <ProgressDisplay progress={progress} />
          )}
        </>
      )}

      {result && (
        <VerificationDashboard
          result={result}
          onReset={() => { setResult(null); setProgress(null); }}
        />
      )}
    </div>
  );
}

function ProgressDisplay({ progress }) {
  const agents = [
    { key: 'simon', name: 'Simon', label: 'Behauptungen finden' },
    { key: 'vera', name: 'Vera', label: 'Faktenpr\u00FCfung' },
    { key: 'conrad', name: 'Conrad', label: 'Gegenpr\u00FCfung' },
    { key: 'sven', name: 'Sven', label: 'Konsistenzpr\u00FCfung' },
    { key: 'pia', name: 'Pia', label: 'Aktualit\u00E4tspr\u00FCfung' },
  ];

  return (
    <div style={{
      marginTop: '24px',
      padding: '20px',
      border: '1px solid #e0e0e0',
      borderRadius: '8px'
    }}>
      <h3>Pr&uuml;fung l&auml;uft...</h3>
      {agents.map(agent => {
        const status = progress[agent.key];
        const icon = status === 'done' ? '\u2705'
                   : status === 'running' ? '\uD83D\uDD04'
                   : '\u23F3';
        return (
          <div key={agent.key} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 0',
            opacity: status === 'waiting' ? 0.5 : 1
          }}>
            <span>{icon}</span>
            <strong>{agent.name}:</strong>
            <span>{agent.label}</span>
            {status === 'done' && progress[`${agent.key}_summary`] && (
              <span style={{ color: '#666', marginLeft: '8px' }}>
                {progress[`${agent.key}_summary`]}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
