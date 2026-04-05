import { Link } from "react-router-dom";
import { EmptyState } from "@/components/EmptyState";

export function NotFoundPage() {
  return (
    <div className="space-y-6">
      <EmptyState
        title="Страница не найдена"
        description="Проверьте адрес или вернитесь на главную страницу панели аналитики."
      />
      <Link
        to="/"
        className="inline-flex rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-white transition hover:bg-accent-dark"
      >
        На главную
      </Link>
    </div>
  );
}
