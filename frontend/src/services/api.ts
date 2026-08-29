import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

interface RetriableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
}

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}/api/v1`,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableRequestConfig | undefined;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      const { data } = await axios.post<RefreshTokenResponse>(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/refresh`,
        { refresh_token: refreshToken }
      );

      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);

      return api(originalRequest);
    }

    return Promise.reject(error);
  }
);

export default api;
