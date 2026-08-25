import { render, screen, fireEvent } from '@testing-library/react'
import { UploadScreen } from './UploadScreen'
import { describe, it, expect, vi } from 'vitest'

describe('UploadScreen', () => {
  it('rejects disallowed file type', () => {
    render(<UploadScreen />)
    const input = screen.getByLabelText('Upload contract') as HTMLInputElement

    const file = new File(['content'], 'test.txt', { type: 'text/plain' })
    fireEvent.change(input, { target: { files: [file] } })

    expect(screen.getByRole('alert')).toHaveTextContent('Only PDF and DOCX')
  })

  it('renders Clear button when file is selected and triggers onClear callback', () => {
    const handleClear = vi.fn()
    render(<UploadScreen selectedFile="contract.pdf" onClear={handleClear} />)

    const clearButton = screen.getByRole('button', { name: /clear current document/i })
    expect(clearButton).toBeInTheDocument()

    fireEvent.click(clearButton)
    expect(handleClear).toHaveBeenCalledTimes(1)
  })
})
