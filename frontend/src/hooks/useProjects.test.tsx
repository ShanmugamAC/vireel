import { QueryClient, QueryClientProvider, type Query } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { projectKeys, useProject, useProjects } from '@/hooks/useProjects';
import { projectService } from '@/services/projectService';
import type { Project, ProjectListItem, ProjectStatus } from '@/types';

vi.mock('@/services/projectService', () => ({
  projectService: {
    listProjects: vi.fn(),
    getProject: vi.fn(),
    createProject: vi.fn(),
    deleteProject: vi.fn(),
    retryProject: vi.fn(),
  },
}));

function makeClientAndWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  return { queryClient, wrapper };
}

interface RefetchIntervalOptions {
  refetchInterval?: (query: Query) => number | false;
}

/** Resolve `useProject`'s live `refetchInterval` callback straight off the cached query. */
function resolveRefetchInterval(queryClient: QueryClient, id: number): number | false {
  const query = queryClient.getQueryCache().find({ queryKey: projectKeys.detail(id) });
  if (!query) throw new Error(`No cached query found for project ${id}`);
  const { refetchInterval } = query.options as RefetchIntervalOptions;
  if (!refetchInterval) throw new Error('useProject query has no refetchInterval configured');
  return refetchInterval(query);
}

function makeProject(status: ProjectStatus): Project {
  return {
    id: 1,
    title: 'My Project',
    source_url: 'https://youtube.com/watch?v=1',
    status,
    error_message: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    outputs: [],
  };
}

describe('useProjects', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches the project list via projectService.listProjects', async () => {
    const items: ProjectListItem[] = [{ id: 1, title: 'A', status: 'completed', created_at: '2024-01-01' }];
    vi.mocked(projectService.listProjects).mockResolvedValue(items);
    const { wrapper } = makeClientAndWrapper();

    const { result } = renderHook(() => useProjects(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(items);
    expect(projectService.listProjects).toHaveBeenCalledTimes(1);
  });
});

describe('useProject polling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('is disabled (does not fetch) when id is undefined', () => {
    const { wrapper } = makeClientAndWrapper();
    const { result } = renderHook(() => useProject(undefined), { wrapper });

    expect(result.current.fetchStatus).toBe('idle');
    expect(projectService.getProject).not.toHaveBeenCalled();
  });

  it('schedules a 3s refetch while the project is in a non-terminal status', async () => {
    vi.mocked(projectService.getProject).mockResolvedValue(makeProject('downloading'));
    const { wrapper, queryClient } = makeClientAndWrapper();

    const { result } = renderHook(() => useProject(1), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(resolveRefetchInterval(queryClient, 1)).toBe(3000);
  });

  it('stops polling once the project reaches a terminal status (completed)', async () => {
    vi.mocked(projectService.getProject).mockResolvedValue(makeProject('completed'));
    const { wrapper, queryClient } = makeClientAndWrapper();

    const { result } = renderHook(() => useProject(1), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(resolveRefetchInterval(queryClient, 1)).toBe(false);
  });

  it('stops polling once the project reaches a terminal status (failed)', async () => {
    vi.mocked(projectService.getProject).mockResolvedValue(makeProject('failed'));
    const { wrapper, queryClient } = makeClientAndWrapper();

    const { result } = renderHook(() => useProject(1), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(resolveRefetchInterval(queryClient, 1)).toBe(false);
  });
});
