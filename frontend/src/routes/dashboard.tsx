import { useUserStore } from "@/lib/state";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { isAuthenticated } from "@/lib/auth";

export const Route = createFileRoute("/dashboard")({
  component: RouteComponent,
  beforeLoad: async ({ location }) => {
    const authenticated = await isAuthenticated();

    if (!authenticated) {
      return redirect({
        to: "/login",
        search: { redirect: location.href },
      });
    }
  },
});

function RouteComponent() {
  const { user } = useUserStore();

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, {user?.email || "null"}</p>
    </div>
  );
}
