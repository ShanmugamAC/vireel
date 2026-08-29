import { useState } from 'react';
import { GlassCard } from '@/components/ui/GlassCard';
import { GradientButton } from '@/components/ui/GradientButton';
import { projectService } from '@/services/projectService';
import type { Output } from '@/types';

interface OutputCardProps {
  projectId: number;
  output: Output;
}

const TYPE_LABELS: Record<Output['output_type'], string> = {
  trailer_30s: '30s Trailer',
  trailer_1min: '1min Trailer',
  summary_3min: '3min Summary',
};

/**
 * NOTE: the API only exposes an authenticated download endpoint, not a
 * public streaming URL, so this renders a Download button rather than an
 * inline <video> preview (download-only, per the MVP fallback in the spec).
 */
export function OutputCard({ projectId, output }: OutputCardProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async () => {
    setError(null);
    setIsDownloading(true);
    try {
      const extension = output.file_path.split('.').pop() ?? 'mp4';
      const filename = `${output.output_type}-${output.category}.${extension}`;
      await projectService.downloadOutput(projectId, output.id, filename);
    } catch {
      setError('Download failed. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <GlassCard className="flex flex-col gap-3">
      <div>
        <p className="text-sm font-semibold">{TYPE_LABELS[output.output_type]}</p>
        <p className="text-xs opacity-70">{output.category}</p>
      </div>
      <p className="text-xs opacity-60">{output.duration_seconds}s</p>
      {output.status === 'completed' ? (
        <GradientButton
          onClick={() => void handleDownload()}
          disabled={isDownloading}
          className="disabled:opacity-60"
        >
          {isDownloading ? 'Downloading...' : 'Download'}
        </GradientButton>
      ) : (
        <span className="text-xs italic opacity-60">
          {output.status === 'failed' ? 'Rendering failed' : 'Rendering...'}
        </span>
      )}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </GlassCard>
  );
}
