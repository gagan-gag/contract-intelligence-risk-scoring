import { render, screen, fireEvent } from '@testing-library/react'
import { UploadScreen } from './UploadScreen'
import { describe, it, expect } from 'vitest'

describe('UploadScreen', () => {
  it('rejects disallowed file type', () => {
    render(<UploadScreen />)
    const input = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement
    
    const file = new File(['content'], 'test.txt', { type: 'text/plain' })
    fireEvent.change(input, { target: { files: [file] } })
    
    expect(screen.getByRole('alert')).toHaveTextContent('Only PDF and DOCX')
  })
})
