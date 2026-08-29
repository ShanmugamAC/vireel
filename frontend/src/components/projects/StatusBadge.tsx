import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { ProjectStatus } from '@/types';

interface StatusBadgeProps {
  status: ProjectStatus;
  className?: string;
}

const IN_PROGRESS_STATUSES = new Set<ProjectStatus>([
  'downloading',
  'transcribing',
  'analyzing',
  'scripting',
  'rendering',
]);

const LABELS: Record<ProjectStatus, string> = {
  pending: 'Pending',
  downloading: 'Downloading',
  transcribing: 'Transcribing',
  analyzing: 'Analyzing',
  scripting: 'Scripting',
  rendering: 'Rendering',
  completed: 'Completed',
  failed: 'Failed',
};

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const isInProgress = IN_PROGRESS_STATUSES.has(status);

  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium',
        status === 'pending' && 'bg-gray-200 text-gray-700',
        isInProgress && 'bg-blue-100 text-blue-700',
        status === 'completed' && 'bg-green-100 text-green-700',
        status === 'failed' && 'bg-red-100 text-red-700',
        className
      )}
    >
      {isInProgress && (
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-500 opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-blue-500" />
        </span>
      )}
      {LABELS[status]}
    </motion.span>
  );
}
