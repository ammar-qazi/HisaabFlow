/**
 * Backend API location, shared by every module that calls the API.
 * Relative: the backend serves the UI (Docker), and in development the CRA
 * dev server proxies /api to the backend (src/setupProxy.js).
 */
export const API_V1_BASE = '/api/v1';
