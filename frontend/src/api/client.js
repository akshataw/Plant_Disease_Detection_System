// Thin fetch wrapper: attaches the JWT, refreshes it once on 401, and normalises errors.
const BASE = "/api/v1";
const ACCESS = "pd_access_token";
const REFRESH = "pd_refresh_token";

export const tokens = {
  get access() { return localStorage.getItem(ACCESS); },
  get refresh() { return localStorage.getItem(REFRESH); },
  set({ access_token, refresh_token }) {
    if (access_token) localStorage.setItem(ACCESS, access_token);
    if (refresh_token) localStorage.setItem(REFRESH, refresh_token);
  },
  clear() {
    localStorage.removeItem(ACCESS);
    localStorage.removeItem(REFRESH);
  },
};

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

let onAuthLost = () => {};
export function setAuthLostHandler(fn) { onAuthLost = fn; }

async function tryRefresh() {
  if (!tokens.refresh) return false;
  const res = await fetch(`${BASE}/auth/refresh`, {
    method: "POST",
    headers: { Authorization: `Bearer ${tokens.refresh}` },
  });
  if (!res.ok) return false;
  tokens.set(await res.json());
  return true;
}

async function rawRequest(path, { method = "GET", body, json, auth = true } = {}) {
  const headers = {};
  if (auth && tokens.access) headers.Authorization = `Bearer ${tokens.access}`;
  if (json !== undefined) headers["Content-Type"] = "application/json";
  return fetch(`${BASE}${path}`, { method, headers, body: json !== undefined ? JSON.stringify(json) : body });
}

export async function request(path, options = {}) {
  let res = await rawRequest(path, options);
  if (res.status === 401 && options.auth !== false && (await tryRefresh())) {
    res = await rawRequest(path, options);
  }
  if (res.status === 401 && options.auth !== false) {
    tokens.clear();
    onAuthLost();
  }
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      message = (await res.json()).error || message;
    } catch { /* non-JSON error body */ }
    throw new ApiError(message, res.status);
  }
  if (res.status === 204) return null;
  const type = res.headers.get("content-type") || "";
  return type.includes("application/json") ? res.json() : res.blob();
}

export const api = {
  register: (data) => request("/auth/register", { method: "POST", json: data, auth: false }),
  login: (data) => request("/auth/login", { method: "POST", json: data, auth: false }),
  me: () => request("/auth/me"),
  health: () => request("/health", { auth: false }),
  predict: (file) => {
    const form = new FormData();
    form.append("image", file);
    return request("/predict", { method: "POST", body: form });
  },
  history: (page = 1, perPage = 10) => request(`/history?page=${page}&per_page=${perPage}`),
  historyItem: (id) => request(`/history/${id}`),
  deleteHistoryItem: (id) => request(`/history/${id}`, { method: "DELETE" }),
  imageBlob: (url) => request(url.replace(BASE, "")),
};
