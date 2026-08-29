export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type ProjectStatus =
  | 'pending'
  | 'downloading'
  | 'transcribing'
  | 'analyzing'
  | 'scripting'
  | 'rendering'
  | 'completed'
  | 'failed';

export type OutputType = 'trailer_30s' | 'trailer_1min' | 'summary_3min';

export type OutputCategory = 'Cinematic' | 'Energetic' | 'Educational' | 'Dramatic';

export type OutputStatus = 'pending' | 'rendering' | 'completed' | 'failed';

export interface Output {
  id: number;
  output_type: OutputType;
  category: OutputCategory;
  file_path: string;
  duration_seconds: number;
  status: OutputStatus;
  created_at: string;
}

export interface ProjectListItem {
  id: number;
  title: string | null;
  status: ProjectStatus;
  created_at: string;
}

export interface Project {
  id: number;
  title: string | null;
  source_url: string;
  status: ProjectStatus;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  outputs: Output[];
}
