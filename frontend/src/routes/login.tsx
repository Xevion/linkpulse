import { createFileRoute, redirect } from "@tanstack/react-router";

import { LoginForm } from "@/components/auth/form";
import AuthenticationPage from "@/components/pages/authentication";
import { isAuthenticated } from "@/lib/auth";

export const Route = createFileRoute("/login")({
  beforeLoad: async ({ location }) => {
    const authenticated = await isAuthenticated();

    if (authenticated) {
      return redirect({
        to: "/dashboard",
        search: { redirect: location.href },
      });
    }
  },
  component: Login,
});

function Login() {
  return (
    <AuthenticationPage>
      <div className="mx-auto flex w-full flex-col space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">Sign In</h1>
          <p className="text-sm text-muted-foreground">
            Enter your email & password below to login
          </p>
        </div>
        <LoginForm />
      </div>
    </AuthenticationPage>
  );
}
