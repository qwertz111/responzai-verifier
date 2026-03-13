// src/components/VerificationBadge.jsx

import React, { useState, useEffect } from 'react';

export default function VerificationBadge() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://api.responzai.eu/reports/latest')
      .then(res => res.json())
      .then(data => {
        setStatus(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return null;
  if (!status) return null;

  const isHealthy = status.issues_found === 0;

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      padding: '6px 12px',
      borderRadius: '20px',
      fontSize: '13px',
      backgroundColor: isHealthy ? '#e8f5e9' : '#fff3e0',
      color: isHealthy ? '#2e7d32' : '#e65100'
    }}>
      <span style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        backgroundColor: isHealthy ? '#4caf50' : '#ff9800'
      }} />
      <span>
        Letzte Pr&uuml;fung: {new Date(status.created_at).toLocaleDateString('de-DE')}
        {' \u00B7 '}
        {status.total_claims} Claims gepr&uuml;ft
        {status.issues_found > 0 && ` \u00B7 ${status.issues_found} in Bearbeitung`}
      </span>
    </div>
  );
}
