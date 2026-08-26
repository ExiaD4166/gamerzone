import "server-only";

/**
 * The one place the frontend talks to the FastAPI backend.
 *
 * `server-only` makes this a build error if a Client Component ever imports it.
 * That matters: everything here runs with the user's access token, and the token
 * must never be bundled into code that reaches a browser.
 */

const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

/** The error shape every endpoint returns — see the backend's error handlers. */
export type ApiError = {
  detail: string;
  code: string;
  request_id: string;
};

export type ApiResult<T> = { ok: true; data: T } | { ok: false; error: ApiError; status: number };

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  /** Sent as JSON. */
  json?: unknown;
  /** Sent as an HTML form body, which the OAuth2 login endpoint requires. */
  form?: Record<string, string>;
  /** The caller's access token, when the endpoint needs one. */
  token?: string;
  /** Opt out of caching for anything user-specific. */
  cache?: RequestCache;
};

/**
 * Calls the API and always resolves — never throws — so callers handle failure
 * as a value rather than wrapping everything in try/catch.
 */
export async function api<T>(path: string, options: RequestOptions = {}): Promise<ApiResult<T>> {
  const { method = "GET", json, form, token, cache = "no-store" } = options;

  const headers: Record<string, string> = {};
  let body: string | undefined;

  if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(json);
  } else if (form !== undefined) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    body = new URLSearchParams(form).toString();
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { method, headers, body, cache });
  } catch {
    // The API is unreachable — usually it simply isn't running in development.
    return {
      ok: false,
      status: 0,
      error: {
        detail: "Could not reach the server. Please try again in a moment.",
        code: "network_error",
        request_id: "none",
      },
    };
  }

  if (response.status === 204) {
    return { ok: true, data: undefined as T };
  }

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const error = (payload ?? {}) as Partial<ApiError>;
    return {
      ok: false,
      status: response.status,
      error: {
        detail: error.detail ?? "Something went wrong.",
        code: error.code ?? `http_${response.status}`,
        request_id: error.request_id ?? "none",
      },
    };
  }

  return { ok: true, data: payload as T };
}

/** The user shape the API returns (matches UserRead on the backend). */
export type User = {
  id: number;
  email: string;
  username: string;
  is_verified: boolean;
  is_superuser: boolean;
  created_at: string;
};

export type DownloadItem = {
  id: number;
  title: string;
  category: string;
  url: string;
  description: string | null;
  created_at: string;
};
