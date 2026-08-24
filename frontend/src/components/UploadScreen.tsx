import { useState } from 'react'

export function UploadScreen() {
  const [error, setError] = useState<string | null>(null)

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    if (!['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)) {
      setError('Only PDF and DOCX files are allowed.')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File must be under 10 MB.')
      return
    }
    setError(null)
  }

  return (
    <div>
      <input type="file" onChange={handleFileChange} accept=".pdf,.docx" />
      {error && <p role="alert">{error}</p>}
    </div>
  )
}
