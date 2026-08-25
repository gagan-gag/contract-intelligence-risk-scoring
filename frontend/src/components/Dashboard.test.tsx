import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Dashboard } from './Dashboard'
import { RiskResults } from './RiskResults'

describe('Dashboard', () => {
  it('renders the main heading and upload control', () => {
    render(<Dashboard />)

    expect(screen.getByText('Contract Intelligence')).toBeInTheDocument()
    expect(screen.getByLabelText('Upload contract')).toBeInTheDocument()
  })
})

describe('RiskResults', () => {
  it('renders a risk summary when data is provided', () => {
    render(
      <RiskResults
        risk={{
          score: 82,
          level: 'medium',
          reasons: ['Unusual indemnity language', 'Auto-renewal risk'],
        }}
      />,
    )

    expect(screen.getByText('Risk Level: MEDIUM')).toBeInTheDocument()
    expect(screen.getByText('Score: 82')).toBeInTheDocument()
    expect(screen.getByText('Unusual indemnity language')).toBeInTheDocument()
  })
})
