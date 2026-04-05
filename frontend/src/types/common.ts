import type { ReactNode } from "react";

export interface ApiErrorPayload {
  detail?: string | { message?: string };
  message?: string;
}

export interface TableColumn<T> {
  key: string;
  title: string;
  className?: string;
  render: (row: T) => ReactNode;
}
