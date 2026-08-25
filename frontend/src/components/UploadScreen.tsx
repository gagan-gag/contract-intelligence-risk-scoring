import { useRef, useState, type ChangeEvent } from 'react'

type UploadScreenProps = {
  onFileSelected?: (fileName: string) => void
  onAnalyzingChange?: (value: boolean) => void
  onUpload?: (file: File) => void
  onClear?: () => void
  selectedFile?: string | null
}

const allowedMimeTypes = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

export function UploadScreen({
  onFileSelected,
  onAnalyzingChange,
  onUpload,
  onClear,
  selectedFile: externalSelectedFile,
}: UploadScreenProps) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [internalFile, setInternalFile] = useState<string | null>(null)

  const selectedFile = externalSelectedFile !== undefined ? externalSelectedFile : internalFile

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    const isAllowedType =
      allowedMimeTypes.includes(file.type) || /\.(pdf|docx)$/i.test(file.name)

    if (!isAllowedType) {
      setError('Only PDF and DOCX files are allowed.')
      setInternalFile(null)
      onFileSelected?.('')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File must be under 10 MB.')
      setInternalFile(null)
      onFileSelected?.('')
      return
    }

    setError(null)
    setInternalFile(file.name)
    onFileSelected?.(file.name)
    onAnalyzingChange?.(true)
    onUpload?.(file)
  }

  function handleClear() {
    setError(null)
    setInternalFile(null)
    if (inputRef.current) inputRef.current.value = ''
    onFileSelected?.('')
    onClear?.()
  }

  return (
    <div className="surface-panel min-h-[382px] p-6">
      <div className="mb-6 flex items-center justify-between gap-3">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-sky-300">Upload</p>
          <h2 className="mt-2 text-xl font-semibold leading-7 text-white">Contract analysis</h2>
        </div>
        <div className="flex items-center gap-2">
          {selectedFile && (
            <button
              id="clear-document-btn"
              type="button"
              onClick={handleClear}
              className="rounded-full border border-rose-500/30 bg-rose-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-rose-300 transition hover:bg-rose-500/20"
              aria-label="Clear current document"
            >
              Clear
            </button>
          )}
          <div className="shrink-0 rounded-full border border-sky-400/30 bg-sky-500/10 px-2.5 py-1 text-[11px] font-medium text-sky-200">
            PDF / DOCX
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="flex min-h-[176px] w-full cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-600 bg-slate-950/80 px-5 py-6 text-center transition duration-200 hover:border-sky-400 hover:bg-slate-900"
      >
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-sky-500/10 text-2xl text-sky-300">
          ⤴
        </div>
        <div>
          <div className="text-sm font-semibold text-white">Choose a contract</div>
          <div className="mt-1 text-xs leading-5 text-slate-400">Upload a file up to 10 MB</div>
        </div>
      </button>

      <input
        ref={inputRef}
        id="contract-upload"
        type="file"
        onChange={handleFileChange}
        accept=".pdf,.docx"
        aria-label="Upload contract"
        className="sr-only"
      />

      <div className="mt-4 flex min-h-10 items-center justify-between gap-3 rounded-xl border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm">
        <span className="truncate text-slate-300">{selectedFile ?? 'No file selected yet'}</span>
        {selectedFile && (
          <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300">
            Ready
          </span>
        )}
      </div>

      {error && (
        <p role="alert" className="status-alert mt-4">
          {error}
        </p>
      )}
    </div>
  )
}
