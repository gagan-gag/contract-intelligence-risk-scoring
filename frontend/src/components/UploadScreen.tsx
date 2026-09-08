import { useState, useRef } from 'react'
import { uploadDocument } from '../api/client'

interface UploadScreenProps {
  onUploadSuccess: (documentId: string, filename: string) => void
  isUploading: boolean
  setIsUploading: (uploading: boolean) => void
}

export function UploadScreen({
  onUploadSuccess,
  isUploading,
  setIsUploading,
}: UploadScreenProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  const validateAndSetFile = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    const allowedExtensions = ['pdf', 'docx']

    if (!ext || !allowedExtensions.includes(ext)) {
      setError('Only PDF (.pdf) and Word (.docx) documents are supported.')
      setSelectedFile(null)
      return false
    }

    if (file.size > 10 * 1024 * 1024) {
      setError(`File size (${(file.size / (1024 * 1024)).toFixed(2)} MB) exceeds the 10 MB limit.`)
      setSelectedFile(null)
      return false
    }

    setError(null)
    setSelectedFile(file)
    return true
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      validateAndSetFile(file)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    const file = e.dataTransfer.files?.[0]
    if (file) {
      validateAndSetFile(file)
    }
  }

  const handleSubmit = async () => {
    if (!selectedFile) return
    setIsUploading(true)
    setError(null)

    try {
      const resp = await uploadDocument(selectedFile)
      onUploadSuccess(resp.document_id, resp.filename)
    } catch (err: any) {
      setError(err.message || 'Failed to upload document. Please ensure backend is running.')
    } finally {
      setIsUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div
        className={`dropzone ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileChange}
        />
        <div className="dropzone-icon">📄</div>
        <div className="dropzone-title">
          {selectedFile ? 'Click or drop to replace document' : 'Drag & drop contract file here'}
        </div>
        <div className="dropzone-subtitle">Supported formats: PDF, DOCX (Max: 10 MB)</div>
        <button
          type="button"
          className="file-label"
          onClick={(e) => {
            e.stopPropagation()
            fileInputRef.current?.click()
          }}
        >
          Browse Local Files
        </button>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          ⚠️ {error}
        </div>
      )}

      {selectedFile && (
        <div className="file-card">
          <div className="file-info">
            <span className="file-icon">📑</span>
            <div>
              <div className="file-name" title={selectedFile.name}>
                {selectedFile.name}
              </div>
              <div className="file-meta">{formatFileSize(selectedFile.size)}</div>
            </div>
          </div>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={handleSubmit}
            disabled={isUploading}
          >
            {isUploading ? 'Analyzing...' : 'Run NLP Analysis →'}
          </button>
        </div>
      )}
    </div>
  )
}
