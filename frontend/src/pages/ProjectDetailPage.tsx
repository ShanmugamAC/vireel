import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useParams } from 'react-router-dom';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { GlassCard } from '@/components/ui/GlassCard';
import { GradientButton } from '@/components/ui/GradientButton';
import { StatusBadge } from '@/components/projects/StatusBadge';
import { PipelineProgress } from '@/components/projects/PipelineProgress';
import { OutputCard } from '@/components/projects/OutputCard';
import { useDeleteProject, useProject, useRetryProject } from '@/hooks/useProjects';

export function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id ? Number(params.id) : undefined;
  const navigate = useNavigate();

  const { data: project, isLoading, isError } = useProject(projectId);
  const retryProject = useRetryProject();
  const deleteProject = useDeleteProject();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!projectId) return;
    const confirmed = window.confirm('Delete this project? This cannot be undone.');
    if (!confirmed) return;

    setIsDeleting(true);
    try {
      await deleteProject.mutateAsync(projectId);
      navigate('/projects');
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <PageWrapper>
        <div className="p-6 text-sm opacity-70">Loading project...</div>
      </PageWrapper>
    );
  }

  if (isError || !project) {
    return (
      <PageWrapper>
        <div className="p-6 text-sm text-red-500">Failed to load project.</div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <div className="mx-auto max-w-3xl p-6">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">{project.title ?? `Project #${project.id}`}</h1>
            <p className="mt-1 break-all text-xs opacity-60">{project.source_url}</p>
          </div>
          <StatusBadge status={project.status} />
        </div>

        <GlassCard className="mb-6">
          <PipelineProgress status={project.status} errorMessage={project.error_message} />
        </GlassCard>

        {project.outputs.length > 0 && (
          <div className="mb-6">
            <h2 className="mb-3 text-lg font-semibold">Outputs</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              {project.outputs.map((output) => (
                <OutputCard key={output.id} projectId={project.id} output={output} />
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-3">
          {project.status === 'failed' && (
            <GradientButton
              onClick={() => void retryProject.mutateAsync(project.id)}
              disabled={retryProject.isPending}
              className="disabled:opacity-60"
            >
              {retryProject.isPending ? 'Retrying...' : 'Retry'}
            </GradientButton>
          )}
          <motion.button
            type="button"
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => void handleDelete()}
            disabled={isDeleting}
            className="rounded-full border border-red-300 px-6 py-3 text-sm font-semibold text-red-600 transition hover:bg-red-50 disabled:opacity-60"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </motion.button>
        </div>
      </div>
    </PageWrapper>
  );
}
