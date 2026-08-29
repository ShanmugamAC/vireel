import { isAxiosError } from 'axios';

interface ApiErrorBody {
  detail?: string | { msg?: string }[];
  message?: string;
}

/**
 * Extracts a human-readable message from an unknown error thrown by the
 * `api` axios client (typically a FastAPI error response), falling back to
 * a caller-provided default.
 */
export function getErrorMessage(error: unknown, fallback: string): string {
  if (isAxiosError<ApiErrorBody>(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail) && detail.length > 0 && detail[0]?.msg) {
      return detail[0].msg;
    }
    const message = error.response?.data?.message;
    if (typeof message === 'string') return message;
    if (error.message) return error.message;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
