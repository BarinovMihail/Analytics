import type { UploadBatch, UploadErrorItem, UploadResult } from "@/types/uploads";
import { getArray, getNullableString, getNumber, getObject, getString } from "@/utils/parsers";

export function adaptUploadResult(payload: unknown): UploadResult {
  const data = getObject(payload);

  return {
    batchId: getNumber(data.batch_id),
    fileName: getString(data.file_name),
    status: getString(data.status, "processed"),
    rowsTotal: getNumber(data.rows_total),
    rowsSuccess: getNumber(data.rows_success),
    rowsError: getNumber(data.rows_error),
    rowsDuplicate: getNumber(data.rows_duplicate),
  };
}

export function adaptUploads(payload: unknown): UploadBatch[] {
  return getArray(payload).map((item) => {
    const row = getObject(item);

    return {
      id: getNumber(row.id),
      fileName: getString(row.file_name),
      uploadedAt: getNullableString(row.uploaded_at),
      status: getString(row.status, "processed"),
      rowsTotal: getNumber(row.rows_total),
      rowsSuccess: getNumber(row.rows_success),
      rowsError: getNumber(row.rows_error),
      rowsDuplicate: getNumber(row.rows_duplicate),
    };
  });
}

export function adaptUploadErrors(payload: unknown): UploadErrorItem[] {
  return getArray(payload).map((item) => {
    const row = getObject(item);

    return {
      id: getNumber(row.id),
      batchId: getNumber(row.batch_id),
      rowNumber: getNumber(row.row_number),
      errorMessage: getString(row.error_message),
      rawRowJson: getObject(row.raw_row_json),
      createdAt: getNullableString(row.created_at),
    };
  });
}
