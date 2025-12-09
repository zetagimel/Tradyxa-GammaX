import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

interface RefreshButtonProps {
  isLoading?: boolean;
  onClick: () => void;
  className?: string;
}

export function RefreshButton({ isLoading = false, onClick, className }: RefreshButtonProps) {
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={onClick}
      disabled={isLoading}
      className={cn("sm:w-auto sm:px-4", className)}
      data-testid="button-refresh"
      aria-label="Refresh data"
    >
      <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin", "sm:mr-2")} />
      <span className="hidden sm:inline">Refresh</span>
    </Button>
  );
}
