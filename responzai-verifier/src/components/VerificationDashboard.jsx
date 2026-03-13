// src/components/VerificationDashboard.jsx

import React, { useState } from 'react';
import ReportViewer from './ReportViewer';

export default function VerificationDashboard({ result, onReset }) {
  const [showReport, setShowReport] = useState(false);

  // Gesamtbewertung bestimmen
  const getOverallStatus = () => {
    if (result.issues_found === 0) return { label: 'Alles in Ordnung', color: '#4caf50' };
    if (result.issues_found <= 2) return { label: 'Kleine Auff\u00E4lligkeiten', color: '#ff9800' };
    return { label: 'Handlungsbedarf', color: '#f44336' };
  };

  const status = getOverallStatus();

  return (
    <div>
      {/* Kopfzeile mit Gesamtergebnis */}
      <div style={{
        padding: '24px',
        borderRadius: '12px',
        backgroundColor: `${status.color}15`,
        border: `2px solid ${status.color}`,
        marginBottom: '24px',
        textAlign: 'center',
      }}>
        <h2 style={{ color: status.color, marginBottom: '8px' }}>
          {status.label}
        </h2>
        {result.filename && (
          <p style={{ color: '#666' }}>Gepr&uuml;fte Datei: {result.filename}</p>
        )}
      </div>

      {/* Kennzahlen */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
        marginBottom: '24px',
      }}>
        <StatCard
          label="Behauptungen"
          value={result.total_claims}
          color="#1a73e8"
        />
        <StatCard
          label="Best\u00E4tigt"
          value={result.verified_claims}
          color="#4caf50"
        />
        <StatCard
          label="Probleme"
          value={result.issues_found}
          color={result.issues_found > 0 ? '#f44336' : '#4caf50'}
        />
        <StatCard
          label="Seiten"
          value={result.pages || '-'}
          color="#666"
        />
      </div>

      {/* Dokumentinfo (bei Datei-Uploads) */}
      {result.metadata && (
        <div style={{
          padding: '16px',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          marginBottom: '24px',
          fontSize: '14px',
        }}>
          <strong>Dokumentdetails:</strong>
          <div style={{ marginTop: '8px', display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
            {result.format && <span>Format: {result.format}</span>}
            {result.text_length && <span>Textl&auml;nge: {result.text_length.toLocaleString()} Zeichen</span>}
            {result.metadata.author && <span>Autor: {result.metadata.author}</span>}
            {result.metadata.modified && <span>Ge&auml;ndert: {new Date(result.metadata.modified).toLocaleDateString('de-DE')}</span>}
          </div>
        </div>
      )}

      {/* Aktionsbuttons */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          onClick={() => setShowReport(true)}
          style={{
            padding: '12px 24px',
            backgroundColor: '#1a73e8',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Vollst&auml;ndigen Bericht anzeigen
        </button>
        <button
          onClick={onReset}
          style={{
            padding: '12px 24px',
            backgroundColor: '#fff',
            color: '#333',
            border: '1px solid #ccc',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Neue Pr&uuml;fung
        </button>
      </div>

      {/* Detailbericht */}
      {showReport && result.report && (
        <ReportViewer
          report={result.report}
          onClose={() => setShowReport(false)}
        />
      )}
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div style={{
      padding: '16px',
      borderRadius: '8px',
      border: '1px solid #e0e0e0',
      textAlign: 'center',
    }}>
      <div style={{ fontSize: '28px', fontWeight: 'bold', color }}>{value}</div>
      <div style={{ fontSize: '13px', color: '#666', marginTop: '4px' }}>{label}</div>
    </div>
  );
}
