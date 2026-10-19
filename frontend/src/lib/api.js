// Minimal JSON API client for the demo UI (increment 1.10).
//
// Same-origin in dev (Vite proxies /api to Django on :8000); cross-origin in
// UAT via VITE_API_URL (baked in at build time) plus CORS on the backend.
// Every request carries credentials (the session cookie) and the X-Tenant
// header naming the tenant schema. POSTs send the CSRF token from the
// /api/auth/csrf/ JSON response as X-CSRFToken — the CSRF cookie itself
// lives on the API's origin, so document.cookie cannot see it cross-origin.

const API_BASE = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');

let tenant = 'acme';

export function setTenant(schemaName) {
  tenant = schemaName;
}

export function getTenant() {
  return tenant;
}

export class ApiError extends Error {
  constructor(detail, status) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
  }
}

// CSRF token for POSTs, taken from the /api/auth/csrf/ JSON response (the
// cookie itself is on the API's origin and unreadable cross-origin).
let csrfToken = '';

async function request(path, { method = 'GET', body } = {}) {
  const headers = { 'X-Tenant': tenant };
  const init = { method, credentials: 'include', headers };
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    if (csrfToken) headers['X-CSRFToken'] = csrfToken;
    init.body = JSON.stringify(body);
  }
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, init);
  } catch {
    throw new ApiError('Could not reach the server. Check your connection.', 0);
  }
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }
  if (!res.ok) {
    throw new ApiError((data && data.detail) || `Request failed (${res.status})`, res.status);
  }
  return data;
}

export const api = {
  csrf: async () => {
    const data = await request('/api/auth/csrf/');
    csrfToken = data.csrf_token ?? '';
    return data;
  },
  login: (username, password) =>
    request('/api/auth/login/', { method: 'POST', body: { username, password } }),
  mfa: (token) => request('/api/auth/mfa/', { method: 'POST', body: { token } }),
  logout: () => request('/api/auth/logout/', { method: 'POST', body: {} }),
  me: () => request('/api/auth/me/'),
  funds: () => request('/api/funds/'),
  fund: (id) => request(`/api/funds/${id}/`),
};

/** The three seeded demo tenants, in the order the seed command creates them. */
export const DEMO_TENANTS = [
  { schema: 'acme', label: 'Acme Community Loan Fund' },
  { schema: 'harbor', label: 'Harbor Community Capital' },
  { schema: 'mesa', label: 'Mesa Verde Loan Fund' },
];
