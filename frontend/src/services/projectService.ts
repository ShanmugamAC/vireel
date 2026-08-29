import api from '@/services/api';
import type { Project, ProjectListItem } from '@/types';

interface CreateProjectPayload {
  source_url: string;
  title?: string;
}

const createProject = async (payload: CreateProjectPayload): Promise<Project> => {
  const { data } = await api.post<Project>('/projects', payload);
  return data;
};

const listProjects = async (): Promise<ProjectListItem[]> => {
  const { data } = await api.get<ProjectListItem[]>('/projects');
  return data;
};

const getProject = async (id: number): Promise<Project> => {
  const { data } = await api.get<Project>(`/projects/${id}`);
  return data;
};

const deleteProject = async (id: number): Promise<void> => {
  await api.delete(`/projects/${id}`);
};

const retryProject = async (id: number): Promise<Project> => {
  const { data } = await api.post<Project>(`/projects/${id}/retry`);
  return data;
};

/**
 * Downloads an output file via the authenticated `api` client (bearer token
 * attached automatically), fetching it as a blob and triggering a browser
 * download through a temporary object URL. This avoids exposing the access
 * token in a URL query string.
 */
const downloadOutput = async (
  projectId: number,
  outputId: number,
  filename: string
): Promise<void> => {
  const response = await api.get<Blob>(`/projects/${projectId}/outputs/${outputId}/download`, {
    responseType: 'blob',
  });

  const objectUrl = window.URL.createObjectURL(response.data);
  const link = document.createElement('a');
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(objectUrl);
};

export const projectService = {
  createProject,
  listProjects,
  getProject,
  deleteProject,
  retryProject,
  downloadOutput,
};
