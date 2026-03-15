import { cn } from "@/lib/utils";
import { forwardRef } from "react";

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "w-full bg-surface-raised border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder:text-text-muted resize-none",
        "focus:outline-none focus:ring-1 focus:ring-accent/50 focus:border-accent/50 transition-colors",
        className
      )}
      {...props}
    />
  )
);
Textarea.displayName = "Textarea";
