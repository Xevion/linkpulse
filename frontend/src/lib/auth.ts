import Result, { ok, err } from "true-myth/result";
import { useUserStore } from "./state";

// Authentication on the frontend is managed by Zustand's state.
// Upon application load, a single request is made to acquire session state.
// Any route that requires authentication will redirect if a valid session is not acquired.
// The session state is stored in the user store.
// If any protected API call suddenly fails with a 401 status code, the user store is reset, a logout message is displayed, and the user is redirected to the login page.
// All redirects to the login page will carry a masked URL parameter that can be used to redirect the user back to the page they were on after logging in.

const TARGET = import.meta.env.DEV
  ? `http://${import.meta.env.VITE_BACKEND_TARGET}`
  : "";

console.log({ env: import.meta.env, target: TARGET });
type ErrorResponse = {
  detail: string;
};

type SessionResponse = {
  user: {};
};

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
