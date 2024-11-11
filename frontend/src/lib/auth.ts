import Result, { ok, err } from "true-myth/result";
import { useUserStore } from "@/lib/state";

// Authentication on the frontend is managed by Zustand's state.
// Upon application load, a single request is made to acquire session state.
// Any route that requires authentication will redirect if a valid session is not acquired.
// The session state is stored in the user store.
// If any protected API call suddenly fails with a 401 status code, the user store is reset, a logout message is displayed, and the user is redirected to the login page.
// All redirects to the login page will carry a masked URL parameter that can be used to redirect the user back to the page they were on after logging in.

const TARGET = !import.meta.env.DEV
  ? `http://${import.meta.env.VITE_BACKEND_TARGET}`
  : "";

type ErrorResponse = {
  detail: string;
};

type SessionResponse = {
  user: {};
};

/**
 * Retrieves the current session from the server.
 *
 * An Ok result will contain the session data, implying that the session is valid and the user is authenticated.
 * An Err result will contain an error response, implying that the session is invalid or non-existent, and the user is not authenticated.
 *
 * @returns {Promise<Result<SessionResponse, ErrorResponse>>} A promise that resolves to a Result object containing either the session data or an error response.
 */
export const getSession = async (): Promise<
  Result<SessionResponse, ErrorResponse>
> => {
  const response = await fetch(TARGET + "/api/session");
  if (response.ok) {
    const user = await response.json();
    useUserStore.getState().setUser(user);
    return ok({ user });
  } else {
    useUserStore.getState().logout();
    const error = await response.json();
    return err({ detail: error.detail });
  }
};

export const isAuthenticated = async (): Promise<boolean> => {
  let state = useUserStore.getState();

  if (state.initialized) return state.user !== null;
  else {
    const result = await getSession();
    return result.isOk;
  }
};

type LoginResponse = {
  email: string;
  expiry: string;
};

export const login = async (
  email: string,
  password: string,
): Promise<Result<LoginResponse, ErrorResponse>> => {
  const response = await fetch(TARGET + "/api/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (response.ok) {
    const user = await response.json();
    useUserStore.getState().setUser(user);
    return ok(user);
  } else {
    const error = await response.json();
    return err({ detail: error.detail });
  }
};
