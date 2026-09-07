import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { PipelineProgress } from '@/components/projects/PipelineProgress';

describe('PipelineProgress', () => {
  it('shows the failure panel with the error message when status=failed', () => {
    render(<PipelineProgress status="failed" errorMessage="ffmpeg crashed" />);
    expect(screen.getByText('Pipeline failed')).toBeInTheDocument();
    expect(screen.getByText('ffmpeg crashed')).toBeInTheDocument();
  });

  it('shows the failure panel without an error message when none is given', () => {
    render(<PipelineProgress status="failed" />);
    expect(screen.getByText('Pipeline failed')).toBeInTheDocument();
  });

  it('does not render the stage stepper when failed', () => {
    render(<PipelineProgress status="failed" />);
    expect(screen.queryByText('Downloading')).not.toBeInTheDocument();
  });

  it('marks the current stage and earlier stages as done/current, later stages as pending', () => {
    render(<PipelineProgress status="analyzing" />);

    // Earlier stage: done.
    expect(screen.getByText('Downloading')).toHaveClass('font-medium', 'opacity-100');
    // Current stage: highlighted, not yet "done".
    expect(screen.getByText('Analyzing')).toHaveClass('font-medium', 'opacity-100');
    // Later stage: still pending/dim.
    expect(screen.getByText('Rendering')).toHaveClass('opacity-50');
  });

  it('marks every stage done when completed', () => {
    render(<PipelineProgress status="completed" />);
    expect(screen.getByText('Downloading')).toHaveClass('font-medium', 'opacity-100');
    expect(screen.getByText('Rendering')).toHaveClass('font-medium', 'opacity-100');
    expect(screen.getByText('Completed')).toHaveClass('font-medium', 'opacity-100');
  });

  it('treats pending as before the first stage (nothing done or current)', () => {
    render(<PipelineProgress status="pending" />);
    expect(screen.getByText('Downloading')).toHaveClass('opacity-50');
    expect(screen.getByText('Downloading')).not.toHaveClass('font-medium');
  });
});
