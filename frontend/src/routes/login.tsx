import { createFileRoute, redirect } from "@tanstack/react-router";
import { useUserStore } from "@/lib/state";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { UserAuthForm } from "@/components/auth/UserAuthForm";
import { Icons } from "@/components/icons";

export const Route = createFileRoute("/login")({
  beforeLoad: async ({ location }) => {
    const isLoggedIn = useUserStore.getState().user !== null;

    if (isLoggedIn) {
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
    <>
      <div className="container relative h-[100vh] flex-col items-center grid w-screen lg:max-w-none lg:grid-cols-2 lg:px-0">
        <a
          href="/"
          className={cn(
            buttonVariants({ variant: "ghost" }),
            "absolute right-4 top-4 md:right-8 md:top-8",
          )}
        >
          Linkpulse
        </a>
        <div className="relative hidden h-full flex-col grow bg-muted p-10 text-white dark:border-r lg:flex">
          <div className="absolute inset-0 bg-zinc-900" />
          <div className="relative z-20 flex items-center text-lg font-medium">
            <Icons.linkpulse className="mr-2 h-6 w-6 text-white" />
            Linkpulse
          </div>
          <div className="z-20 mt-auto space-y-2">
            {/* <blockquote className="space-y-2">
              <p className="text-lg">
                &ldquo;This library has saved me countless hours of work and
                helped me deliver stunning designs to my clients faster than
                ever before.&rdquo;
              </p>
              <footer className="text-sm">Sofia Davis</footer>
            </blockquote> */}
            {/* <p className="text-lg"></p>
            <footer className="text-sm"></footer> */}
          </div>
        </div>
        <div className="px-6">
          <div className="mx-auto flex w-full flex-col space-y-6 sm:w-[350px]">
            <div className="flex flex-col space-y-2 text-center">
              <h1 className="text-2xl font-semibold tracking-tight">
                Create an account
              </h1>
              <p className="text-sm text-muted-foreground">
                Enter your email below to create your account
              </p>
            </div>
            <UserAuthForm />
            <p className="text-center text-sm text-muted-foreground">
              By clicking continue, you agree to our{" "}
              <a
                href="/terms"
                className="underline underline-offset-4 hover:text-primary"
              >
                Terms of Service
              </a>{" "}
              and{" "}
              <a
                href="/privacy"
                className="underline underline-offset-4 hover:text-primary"
              >
                Privacy Policy
              </a>
              .
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
