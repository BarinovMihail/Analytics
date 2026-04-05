export interface UploadBatch {
  id: number;
  fileName: string;
  uploadedAt: string | null;
  status: string;
  rowsTotal: number;
  rowsSuccess: number;
  rowsError: number;
}

export interface UploadResult {
  batchId: number;
  fileName: string;
  status: string;
  rowsTotal: number;
  rowsSuccess: number;
  rowsError: number;
}

export interface UploadErrorItem {
  id: number;
  batchId: number;
  rowNumber: number;
  errorMessage: string;
  rawRowJson: Record<string, unknown>;
  createdAt: string | null;
}
