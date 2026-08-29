import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { projectService } from '@/services/projectService';
import type { Project, ProjectListItem } from '@/types';

const TERMINAL_STATUSES = new Set(['completed', 'failed']);

export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  detail: (id: number) => [...projectKeys.all, 'detail', id] as const,
};

export function useProjects() {
  return useQuery<ProjectListItem[]>({
    queryKey: projectKeys.lists(),
    queryFn: projectService.listProjects,
  });
}

export function useProject(id: number | undefined) {
  return useQuery<Project>({
    queryKey: projectKeys.detail(id ?? -1),
    queryFn: () => projectService.getProject(id as number),
    enabled: id !== undefined,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status || TERMINAL_STATUSES.has(status)) return false;
      return 3000;
    },
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: projectService.createProject,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: projectService.deleteProject,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}

export function useRetryProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: projectService.retryProject,
    onSuccess: (project) => {
      void queryClient.invalidateQueries({ queryKey: projectKeys.detail(project.id) });
      void queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
    },
  });
}
