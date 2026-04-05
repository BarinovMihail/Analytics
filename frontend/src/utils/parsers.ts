function asRecord(value: unknown) {
  return typeof value === "object" && value !== null ? (value as Record<string, unknown>) : null;
}

export function getString(value: unknown, fallback = "") {
  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  return fallback;
}

export function getNullableString(value: unknown) {
  const stringValue = getString(value);
  return stringValue || null;
}

export function getNumber(value: unknown, fallback = 0) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const normalized = Number(value);
    return Number.isFinite(normalized) ? normalized : fallback;
  }

  return fallback;
}

export function getObject(value: unknown) {
  return asRecord(value) ?? {};
}

export function getArray(value: unknown) {
  return Array.isArray(value) ? value : [];
}
