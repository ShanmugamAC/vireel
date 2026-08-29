import { Link } from 'react-router-dom';
import { GlassCard } from '@/components/ui/GlassCard';
import { StatusBadge } from '@/components/projects/StatusBadge';
import type { ProjectListItem } from '@/types';

interface ProjectCardProps {
  project: ProjectListItem;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link to={`/projects/${project.id}`}>
      <GlassCard className="flex items-center justify-between gap-4">
        <div className="min-w-0">
          <p className="truncate font-medium">{project.title ?? `Project #${project.id}`}</p>
          <p className="text-xs opacity-60">{new Date(project.created_at).toLocaleString()}</p>
        </div>
        <StatusBadge status={project.status} />
      </GlassCard>
    </Link>
  );
}
