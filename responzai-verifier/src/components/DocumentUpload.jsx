// src/components/DocumentUpload.jsx

import React, { useState, useRef, useCallback } from 'react';

const API_BASE = 'https://api.responzai.eu';

const ALLOWED_FORMATS = {
  'application/pdf': 'PDF',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
  'text/plain': 'Text',
  'text/html': 'HTML',
  'text/markdown': 'Markdown',
  'text/csv': 'CSV',
  'image/png': 'PNG',
  'image/jpeg': 'JPEG',
  'message/rfc822': 'E-Mail',
};

const MAX_SIZE = 50 * 1024 * 1024; // 50 MB

export default function DocumentUpload({
  mode, onModeChange, onResult, onProgress, onLoadingChange
}) {
  const [inputType, setInputType] = useState('file');  // 'url', 'text', 'file'
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // Drag and Drop Handler
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  }, []);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (f) => {
    setError(null);

    if (f.size > MAX_SIZE) {
      setError(`Datei zu gro\u00DF: ${(f.size / 1024 / 1024).toFixed(1)} MB. Maximum: 50 MB.`);
      return;
    }

    setFile(f);
    setInputType('file');
  };

  const handleSubmit = async () => {
    setError(null);
    onLoadingChange(true);

    try {
      let response;

      if (inputType === 'file' && file) {
        // Datei hochladen
        const formData = new FormData();
        formData.append('file', file);
        formData.append('mode', mode);

        response = await fetch(`${API_BASE}/verify/document`, {
          method: 'POST',
          body: formData,
        });

      } else if (inputType === 'url' && url) {
        // URL pr\u00FCfen
        response = await fetch(`${API_BASE}/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url, mode }),
        });

      } else if (inputType === 'text' && text) {
        // Text direkt pr\u00FCfen
        response = await fetch(`${API_BASE}/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, mode }),
        });
      }

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Pr\u00FCfung fehlgeschlagen');
      }

      const result = await response.json();
      onResult(result);

    } catch (err) {
      setError(err.message);
    } finally {
      onLoadingChange(false);
    }
  };

  const canSubmit = (inputType === 'file' && file)
                 || (inputType === 'url' && url.trim())
                 || (inputType === 'text' && text.trim());

  return (
    <div>
      {/* Tab-Auswahl: URL, Text, Datei */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '16px'
      }}>
        {[
          { key: 'url', label: 'URL' },
          { key: 'text', label: 'Text' },
          { key: 'file', label: 'Datei hochladen' },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setInputType(tab.key)}
            style={{
              padding: '10px 20px',
              border: '2px solid',
              borderColor: inputType === tab.key ? '#1a73e8' : '#e0e0e0',
              borderRadius: '8px',
              background: inputType === tab.key ? '#e8f0fe' : '#fff',
              cursor: 'pointer',
              fontWeight: inputType === tab.key ? 'bold' : 'normal',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* URL-Eingabe */}
      {inputType === 'url' && (
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://responzai.eu/..."
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '16px',
            border: '1px solid #ccc',
            borderRadius: '8px',
          }}
        />
      )}

      {/* Text-Eingabe */}
      {inputType === 'text' && (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Text hier einf\u00FCgen..."
          rows={8}
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '16px',
            border: '1px solid #ccc',
            borderRadius: '8px',
            resize: 'vertical',
          }}
        />
      )}

      {/* Datei-Upload (Drag and Drop) */}
      {inputType === 'file' && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${dragOver ? '#1a73e8' : '#ccc'}`,
            borderRadius: '12px',
            padding: '40px 20px',
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: dragOver ? '#e8f0fe' : '#fafafa',
            transition: 'all 0.2s',
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            accept=".pdf,.docx,.xlsx,.pptx,.odt,.ods,.odp,.html,.htm,.md,.txt,.csv,.eml,.msg,.png,.jpg,.jpeg,.tiff,.tif"
          />

          {file ? (
            <div>
              <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                {file.name}
              </p>
              <p style={{ color: '#666' }}>
                {(file.size / 1024 / 1024).toFixed(1)} MB
              </p>
              <p style={{ color: '#1a73e8', fontSize: '14px' }}>
                Andere Datei w&auml;hlen
              </p>
            </div>
          ) : (
            <div>
              <p style={{ fontSize: '18px', marginBottom: '8px' }}>
                Datei hierher ziehen oder klicken
              </p>
              <p style={{ color: '#666', fontSize: '14px' }}>
                PDF, Word, Excel, PowerPoint, Bilder, E-Mails und mehr
              </p>
              <p style={{ color: '#999', fontSize: '13px' }}>
                Maximal 50 MB
              </p>
            </div>
          )}
        </div>
      )}

      {/* Modus-Auswahl */}
      <div style={{ marginTop: '16px', display: 'flex', gap: '16px' }}>
        <label style={{ cursor: 'pointer' }}>
          <input
            type="radio"
            value="quick"
            checked={mode === 'quick'}
            onChange={() => onModeChange('quick')}
          />
          {' '}Schnellpr&uuml;fung (Simon + Vera)
        </label>
        <label style={{ cursor: 'pointer' }}>
          <input
            type="radio"
            value="full"
            checked={mode === 'full'}
            onChange={() => onModeChange('full')}
          />
          {' '}Vollst&auml;ndige Pr&uuml;fung (alle 8 Agenten)
        </label>
      </div>

      {/* Fehlermeldung */}
      {error && (
        <div style={{
          marginTop: '12px',
          padding: '12px',
          backgroundColor: '#fdecea',
          color: '#b71c1c',
          borderRadius: '8px',
        }}>
          {error}
        </div>
      )}

      {/* Absenden */}
      <button
        onClick={handleSubmit}
        disabled={!canSubmit}
        style={{
          marginTop: '16px',
          padding: '14px 32px',
          fontSize: '16px',
          fontWeight: 'bold',
          color: '#fff',
          backgroundColor: canSubmit ? '#1a73e8' : '#ccc',
          border: 'none',
          borderRadius: '8px',
          cursor: canSubmit ? 'pointer' : 'not-allowed',
          width: '100%',
        }}
      >
        Pr&uuml;fung starten
      </button>
    </div>
  );
}
