interface LoadingStateProps {
  lines?: number;
  className?: string;
}

export function LoadingState({ lines = 3, className = "" }: LoadingStateProps) {
  return (
    <div className={`rounded-3xl border border-slate-200 bg-white p-6 shadow-panel ${className}`}>
      <div className="animate-pulse space-y-4">
        {Array.from({ length: lines }).map((_, index) => (
          <div key={index} className="h-4 rounded-full bg-slate-200" />
        ))}
      </div>
    </div>
  );
}
