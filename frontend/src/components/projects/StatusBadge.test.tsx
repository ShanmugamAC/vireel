import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { StatusBadge } from '@/components/projects/StatusBadge';
import type { ProjectStatus } from '@/types';

describe('StatusBadge', () => {
  const cases: [ProjectStatus, string][] = [
    ['pending', 'Pending'],
    ['downloading', 'Downloading'],
    ['transcribing', 'Transcribing'],
    ['analyzing', 'Analyzing'],
    ['scripting', 'Scripting'],
    ['rendering', 'Rendering'],
    ['completed', 'Completed'],
    ['failed', 'Failed'],
  ];

  it.each(cases)('renders the correct label for status=%s', (status, label) => {
    render(<StatusBadge status={status} />);
    expect(screen.getByText(label)).toBeInTheDocument();
  });

  it('applies the pending color classes', () => {
    render(<StatusBadge status="pending" />);
    expect(screen.getByText('Pending')).toHaveClass('bg-gray-200', 'text-gray-700');
  });

  it('applies the completed color classes', () => {
    render(<StatusBadge status="completed" />);
    expect(screen.getByText('Completed')).toHaveClass('bg-green-100', 'text-green-700');
  });

  it('applies the failed color classes', () => {
    render(<StatusBadge status="failed" />);
    expect(screen.getByText('Failed')).toHaveClass('bg-red-100', 'text-red-700');
  });

  it('applies the in-progress color classes and shows the pulsing indicator for active stages', () => {
    const { container } = render(<StatusBadge status="rendering" />);
    expect(screen.getByText('Rendering')).toHaveClass('bg-blue-100', 'text-blue-700');
    expect(container.querySelector('.animate-ping')).not.toBeNull();
  });

  it('does not show the pulsing indicator for terminal statuses', () => {
    const { container } = render(<StatusBadge status="completed" />);
    expect(container.querySelector('.animate-ping')).toBeNull();
  });
});
