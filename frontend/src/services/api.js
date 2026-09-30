/**
 * Backend API location, shared by every module that calls the API.
 */
export const API_BASE = window.BACKEND_URL || 'http://127.0.0.1:8000';
export const API_V1_BASE = `${API_BASE}/api/v1`;
