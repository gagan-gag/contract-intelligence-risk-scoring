import { render, screen, fireEvent } from '@testing-library/react'
import { UploadScreen } from './UploadScreen'
import { describe, it, expect, vi } from 'vitest'

describe('UploadScreen', () => {
  it('rejects disallowed file type', () => {
    const handleSuccess = vi.fn()
    const setIsUploading = vi.fn()

    const { container } = render(
      <UploadScreen
        onUploadSuccess={handleSuccess}
        isUploading={false}
        setIsUploading={setIsUploading}
      />
    )

    const input = container.querySelector('input[type="file"]') as HTMLInputElement
    expect(input).toBeTruthy()

    const file = new File(['content'], 'test.txt', { type: 'text/plain' })
    fireEvent.change(input, { target: { files: [file] } })

    const alert = screen.getByRole('alert')
    expect(alert.textContent).toContain('Only PDF (.pdf) and Word (.docx) documents are supported.')
  })
})