// src/components/ReportViewer.jsx

import React from 'react';

export default function ReportViewer({ report, onClose }) {
  if (!report) return null;

  return (
    <div style={{
      marginTop: '24px',
      padding: '24px',
      border: '1px solid #e0e0e0',
      borderRadius: '12px',
      backgroundColor: '#fff',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
      }}>
        <h3>Pr&uuml;fbericht</h3>
        <button
          onClick={onClose}
          style={{
            padding: '6px 12px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            cursor: 'pointer',
            background: '#fff',
          }}
        >
          Schlie&szlig;en
        </button>
      </div>

      {/* Problematische Claims auflisten */}
      {report.issues && report.issues.map((issue, i) => (
        <div key={i} style={{
          padding: '16px',
          marginBottom: '12px',
          borderRadius: '8px',
          border: '1px solid',
          borderColor: issue.severity === 'critical' ? '#f44336'
                     : issue.severity === 'major' ? '#ff9800'
                     : '#ffc107',
          backgroundColor: issue.severity === 'critical' ? '#fdecea'
                         : issue.severity === 'major' ? '#fff3e0'
                         : '#fffde7',
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '8px'
          }}>
            <strong>{issue.claim_text}</strong>
            <span style={{
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '12px',
              fontWeight: 'bold',
              color: '#fff',
              backgroundColor: issue.severity === 'critical' ? '#f44336'
                             : issue.severity === 'major' ? '#ff9800'
                             : '#ffc107',
            }}>
              {issue.severity}
            </span>
          </div>

          {/* Welcher Agent hat das Problem gefunden? */}
          <p style={{ fontSize: '14px', color: '#666' }}>
            Gefunden von: <strong>{issue.found_by}</strong>
          </p>
          <p style={{ fontSize: '14px' }}>{issue.description}</p>

          {/* Verbesserungsvorschlag */}
          {issue.suggestion && (
            <div style={{
              marginTop: '8px',
              padding: '10px',
              backgroundColor: '#e8f5e9',
              borderRadius: '4px',
              fontSize: '14px',
            }}>
              <strong>Vorschlag:</strong> {issue.suggestion}
            </div>
          )}
        </div>
      ))}

      {/* Wenn keine Probleme */}
      {(!report.issues || report.issues.length === 0) && (
        <p style={{ color: '#4caf50', textAlign: 'center', padding: '20px' }}>
          Keine Probleme gefunden. Alle Behauptungen wurden best&auml;tigt.
        </p>
      )}
    </div>
  );
}
