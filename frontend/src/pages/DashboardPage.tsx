import { Link } from 'react-router-dom';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { GlassCard } from '@/components/ui/GlassCard';
import { GradientButton } from '@/components/ui/GradientButton';
import { AnimatedList } from '@/components/ui/AnimatedList';
import { ProjectCard } from '@/components/projects/ProjectCard';
import { useProjects } from '@/hooks/useProjects';
import { useAuth } from '@/hooks/useAuth';

const IN_PROGRESS_STATUSES = new Set(['pending', 'downloading', 'transcribing', 'analyzing', 'scripting', 'rendering']);

export function DashboardPage() {
  const { user } = useAuth();
  const { data: projects, isLoading } = useProjects();

  const recentProjects = (projects ?? []).slice(0, 5);
  const inProgressCount = (projects ?? []).filter((p) => IN_PROGRESS_STATUSES.has(p.status)).length;
  const completedCount = (projects ?? []).filter((p) => p.status === 'completed').length;
  const failedCount = (projects ?? []).filter((p) => p.status === 'failed').length;

  return (
    <PageWrapper>
      <div className="mx-auto max-w-3xl p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">
              Welcome{user?.full_name ? `, ${user.full_name}` : ''}
            </h1>
            <p className="text-sm opacity-70">Here&apos;s what&apos;s happening with your videos.</p>
          </div>
          <Link to="/projects/new">
            <GradientButton>Submit a link</GradientButton>
          </Link>
        </div>

        <div className="mb-6 grid grid-cols-3 gap-4">
          <GlassCard className="text-center">
            <p className="text-2xl font-semibold">{inProgressCount}</p>
            <p className="text-xs opacity-70">In progress</p>
          </GlassCard>
          <GlassCard className="text-center">
            <p className="text-2xl font-semibold">{completedCount}</p>
            <p className="text-xs opacity-70">Completed</p>
          </GlassCard>
          <GlassCard className="text-center">
            <p className="text-2xl font-semibold">{failedCount}</p>
            <p className="text-xs opacity-70">Failed</p>
          </GlassCard>
        </div>

        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Recent projects</h2>
          <Link to="/projects" className="text-sm font-medium text-purple-500 hover:underline">
            View all
          </Link>
        </div>

        {isLoading && <p className="text-sm opacity-70">Loading projects...</p>}

        {recentProjects.length === 0 && !isLoading && (
          <GlassCard className="text-center">
            <p className="mb-4 text-sm opacity-80">No projects yet. Submit a link to get started.</p>
            <Link to="/projects/new">
              <GradientButton>Submit a link</GradientButton>
            </Link>
          </GlassCard>
        )}

        {recentProjects.length > 0 && (
          <AnimatedList className="flex flex-col gap-3">
            {recentProjects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </AnimatedList>
        )}
      </div>
    </PageWrapper>
  );
}
