const dash = "—";

export function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return dash;
  }

  return new Intl.NumberFormat("ru-RU").format(value);
}

export function formatCurrency(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return dash;
  }

  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatDate(value: string | null | undefined) {
  if (!value) {
    return dash;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  }).format(parsed);
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return dash;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(parsed);
}

export function formatEmpty(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") {
    return dash;
  }

  return String(value);
}

export function formatMonthLabel(value: string) {
  const parsed = new Date(`${value}-01`);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ru-RU", {
    month: "short",
    year: "numeric",
  }).format(parsed);
}

export function prettyJson(value: Record<string, unknown>) {
  return JSON.stringify(value, null, 2);
}
