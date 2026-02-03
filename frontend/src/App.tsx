import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { Upload, CheckCircle, AlertTriangle, Clock, Image as ImageIcon } from 'lucide-react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

interface ModerationResult {
  id: number
  filename: string
  label: string
  confidence: number
  status: 'safe' | 'flagged'
  timestamp: string
}

function App() {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<ModerationResult | null>(null)
  const [history, setHistory] = useState<ModerationResult[]>([])
  const [error, setError] = useState<string | null>(null)

  const fetchHistory = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/history?limit=20`)
      setHistory(response.data.events)
    } catch (err) {
      console.error('Failed to fetch history:', err)
    }
  }, [])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  const handleFile = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file')
      return
    }

    setError(null)
    setUploading(true)
    setResult(null)

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setPreview(e.target?.result as string)
    }
    reader.readAsDataURL(file)

    // Upload to backend
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${API_URL}/moderate`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setResult(response.data)
      fetchHistory()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to moderate image')
      setPreview(null)
    } finally {
      setUploading(false)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(true)
  }

  const handleDragLeave = () => {
    setDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)

    const file = e.dataTransfer.files[0]
    if (file) {
      handleFile(file)
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFile(file)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const formatConfidence = (confidence: number) => {
    return `${(confidence * 100).toFixed(1)}%`
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>Image Review Portal</h1>
          <p className="subtitle">Automated content moderation with AI-powered classification</p>
        </header>

        <div className="upload-section">
          <div
            className={`upload-zone ${dragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="file-input"
              accept="image/*"
              onChange={handleFileInput}
              style={{ display: 'none' }}
            />
            <label htmlFor="file-input" className="upload-label">
              {uploading ? (
                <>
                  <div className="spinner"></div>
                  <span>Processing image...</span>
                </>
              ) : (
                <>
                  <Upload size={48} />
                  <span className="upload-text">
                    Drag and drop an image here, or click to select
                  </span>
                  <span className="upload-hint">Supports: JPG, PNG, GIF, WebP</span>
                </>
              )}
            </label>
          </div>

          {error && (
            <div className="error-message">
              <AlertTriangle size={20} />
              <span>{error}</span>
            </div>
          )}

          {preview && result && (
            <div className="result-card">
              <div className="result-header">
                <h2>Moderation Result</h2>
                <div className={`status-badge ${result.status}`}>
                  {result.status === 'safe' ? (
                    <CheckCircle size={20} />
                  ) : (
                    <AlertTriangle size={20} />
                  )}
                  <span>{result.status.toUpperCase()}</span>
                </div>
              </div>

              <div className="result-content">
                <div className="image-preview">
                  <img src={preview} alt={result.filename} />
                </div>

                <div className="result-details">
                  <div className="detail-item">
                    <span className="detail-label">Filename:</span>
                    <span className="detail-value">{result.filename}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Predicted Label:</span>
                    <span className="detail-value label-value">{result.label}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Confidence:</span>
                    <span className="detail-value">{formatConfidence(result.confidence)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Timestamp:</span>
                    <span className="detail-value">
                      <Clock size={16} />
                      {formatDate(result.timestamp)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="history-section">
          <h2>Recent Moderation History</h2>
          {history.length === 0 ? (
            <div className="empty-history">
              <ImageIcon size={48} />
              <p>No moderation history yet. Upload an image to get started.</p>
            </div>
          ) : (
            <div className="history-table-container">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Image</th>
                    <th>Filename</th>
                    <th>Label</th>
                    <th>Confidence</th>
                    <th>Status</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((event) => (
                    <tr key={event.id}>
                      <td>
                        <div className="table-image-placeholder">
                          <ImageIcon size={20} />
                        </div>
                      </td>
                      <td className="filename-cell">{event.filename}</td>
                      <td className="label-cell">{event.label}</td>
                      <td>{formatConfidence(event.confidence)}</td>
                      <td>
                        <span className={`status-badge-small ${event.status}`}>
                          {event.status === 'safe' ? (
                            <CheckCircle size={14} />
                          ) : (
                            <AlertTriangle size={14} />
                          )}
                          {event.status}
                        </span>
                      </td>
                      <td className="timestamp-cell">
                        <Clock size={14} />
                        {formatDate(event.timestamp)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App

