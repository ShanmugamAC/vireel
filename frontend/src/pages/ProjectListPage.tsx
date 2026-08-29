import { Link } from 'react-router-dom';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { GlassCard } from '@/components/ui/GlassCard';
import { GradientButton } from '@/components/ui/GradientButton';
import { AnimatedList } from '@/components/ui/AnimatedList';
import { ProjectCard } from '@/components/projects/ProjectCard';
import { useProjects } from '@/hooks/useProjects';

export function ProjectListPage() {
  const { data: projects, isLoading, isError } = useProjects();

  return (
    <PageWrapper>
      <div className="mx-auto max-w-3xl p-6">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Projects</h1>
          <Link to="/projects/new">
            <GradientButton>New Project</GradientButton>
          </Link>
        </div>

        {isLoading && <p className="text-sm opacity-70">Loading projects...</p>}
        {isError && <p className="text-sm text-red-500">Failed to load projects.</p>}

        {projects && projects.length === 0 && (
          <GlassCard className="text-center">
            <p className="mb-4 text-sm opacity-80">
              You haven&apos;t submitted any videos yet. Paste a link to get your first trailer.
            </p>
            <Link to="/projects/new">
              <GradientButton>Submit a link</GradientButton>
            </Link>
          </GlassCard>
        )}

        {projects && projects.length > 0 && (
          <AnimatedList className="flex flex-col gap-3">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </AnimatedList>
        )}
      </div>
    </PageWrapper>
  );
}
