import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  description?: string;
  icon: LucideIcon;
}

export function StatCard({ title, value, description, icon: Icon }: StatCardProps) {
  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-5 shadow-panel">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{value}</p>
          {description ? <p className="mt-2 text-sm text-slate-500">{description}</p> : null}
        </div>
        <div className="rounded-2xl bg-accent-soft p-3 text-accent">
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </article>
  );
}
