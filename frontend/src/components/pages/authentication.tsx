import { Icons } from "@/components/icons";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Link } from "@tanstack/react-router";
import { ReactNode } from "react";

export function AgreementText() {
  return (
    <p className="text-center text-sm text-muted-foreground">
      By clicking continue, you agree to our{" "}
      <Link
        href="/terms"
        className="underline underline-offset-4 hover:text-primary"
      >
        Terms of Service
      </Link>{" "}
      and{" "}
      <Link
        href="/privacy"
        className="underline underline-offset-4 hover:text-primary"
      >
        Privacy Policy
      </Link>
      .
    </p>
  );
}

export default function AuthenticationPage({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="container relative h-[100vh] flex-col items-center grid w-screen lg:max-w-none lg:grid-cols-2 lg:px-0">
      <Link
        href="/"
        className={cn(
          buttonVariants({ variant: "ghost" }),
          "absolute right-4 top-4 md:right-8 md:top-8",
        )}
      >
        Linkpulse
      </Link>
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
      <div className="px-6">{children}</div>
    </div>
  );
}
