import { apiClient } from "@/api/client";
import { adaptUploadErrors, adaptUploadResult, adaptUploads } from "@/features/uploads/adapters";

export const uploadApi = {
  async uploadFile(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post("/api/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return adaptUploadResult(response.data);
  },

  async getUploads() {
    const response = await apiClient.get("/api/uploads");
    return adaptUploads(response.data);
  },

  async getUploadErrors(batchId: number) {
    const response = await apiClient.get(`/api/uploads/${batchId}/errors`);
    return adaptUploadErrors(response.data);
  },
};
