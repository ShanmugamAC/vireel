import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { ProjectStatus } from '@/types';

interface PipelineProgressProps {
  status: ProjectStatus;
  errorMessage?: string | null;
}

const STAGES: { key: ProjectStatus; label: string }[] = [
  { key: 'downloading', label: 'Downloading' },
  { key: 'transcribing', label: 'Transcribing' },
  { key: 'analyzing', label: 'Analyzing' },
  { key: 'scripting', label: 'Scripting' },
  { key: 'rendering', label: 'Rendering' },
  { key: 'completed', label: 'Completed' },
];

function stageIndex(status: ProjectStatus): number {
  if (status === 'pending') return -1;
  return STAGES.findIndex((stage) => stage.key === status);
}

export function PipelineProgress({ status, errorMessage }: PipelineProgressProps) {
  if (status === 'failed') {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4">
        <p className="text-sm font-medium text-red-700">Pipeline failed</p>
        {errorMessage && <p className="mt-1 text-sm text-red-600">{errorMessage}</p>}
      </div>
    );
  }

  const currentIndex = stageIndex(status);

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-2">
      {STAGES.map((stage, index) => {
        const isDone = index < currentIndex || status === 'completed';
        const isCurrent = index === currentIndex && status !== 'completed';

        return (
          <div key={stage.key} className="flex flex-1 items-center gap-2">
            <div className="flex flex-1 flex-col items-center gap-1 text-center">
              <motion.div
                animate={isCurrent ? { scale: [1, 1.15, 1] } : { scale: 1 }}
                transition={isCurrent ? { repeat: Infinity, duration: 1.2 } : undefined}
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full border-2 text-xs font-semibold',
                  isDone && 'border-green-500 bg-green-500 text-white',
                  isCurrent && 'border-blue-500 bg-blue-100 text-blue-700',
                  !isDone && !isCurrent && 'border-gray-300 bg-gray-100 text-gray-400'
                )}
              >
                {index + 1}
              </motion.div>
              <span
                className={cn(
                  'text-xs',
                  (isDone || isCurrent) && 'font-medium opacity-100',
                  !isDone && !isCurrent && 'opacity-50'
                )}
              >
                {stage.label}
              </span>
            </div>
            {index < STAGES.length - 1 && (
              <div className={cn('hidden h-0.5 flex-1 sm:block', isDone ? 'bg-green-500' : 'bg-gray-200')} />
            )}
          </div>
        );
      })}
    </div>
  );
}
