import api from '@/services/api';
import type { AuthTokens, User } from '@/types';

interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
}

interface UpdateMePayload {
  full_name?: string;
}

const setTokens = (tokens: AuthTokens): void => {
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
};

const clearTokens = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

const register = async (payload: RegisterPayload): Promise<User> => {
  const { data } = await api.post<User>('/auth/register', payload);
  return data;
};

const login = async (email: string, password: string): Promise<AuthTokens> => {
  const body = new URLSearchParams();
  body.append('username', email);
  body.append('password', password);

  const { data } = await api.post<AuthTokens>('/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  setTokens(data);
  return data;
};

const logout = async (): Promise<void> => {
  const refreshToken = localStorage.getItem('refresh_token');
  try {
    if (refreshToken) {
      await api.post('/auth/logout', { refresh_token: refreshToken });
    }
  } finally {
    clearTokens();
  }
};

const getMe = async (): Promise<User> => {
  const { data } = await api.get<User>('/auth/me');
  return data;
};

const updateMe = async (payload: UpdateMePayload): Promise<User> => {
  const { data } = await api.put<User>('/auth/me', payload);
  return data;
};

const refresh = async (refreshToken: string): Promise<AuthTokens> => {
  const { data } = await api.post<AuthTokens>('/auth/refresh', { refresh_token: refreshToken });
  setTokens(data);
  return data;
};

export const authService = {
  register,
  login,
  logout,
  getMe,
  updateMe,
  refresh,
  setTokens,
  clearTokens,
};
