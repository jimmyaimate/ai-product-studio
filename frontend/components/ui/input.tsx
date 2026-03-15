import { cn } from "@/lib/utils";
import { forwardRef } from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "w-full bg-surface-raised border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder:text-text-muted",
        "focus:outline-none focus:ring-1 focus:ring-accent/50 focus:border-accent/50 transition-colors",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";
