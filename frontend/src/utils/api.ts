import axios from "axios";
import type { ApiErrorPayload } from "@/types/common";

export function getApiErrorMessage(error: unknown) {
  if (axios.isAxiosError<ApiErrorPayload>(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }

    if (detail && typeof detail === "object" && "message" in detail) {
      return String(detail.message);
    }

    if (typeof error.response?.data?.message === "string") {
      return error.response.data.message;
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Не удалось выполнить запрос к API.";
}
