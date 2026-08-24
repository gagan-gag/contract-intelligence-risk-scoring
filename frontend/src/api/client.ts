const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(\\/documents/upload\, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) throw new Error(\Upload failed: \\)
  return response.json()
}
