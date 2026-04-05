import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/api/queryKeys";
import { uploadApi } from "@/api/uploadApi";

export function useUploadErrors(batchId: number) {
  return useQuery({
    queryKey: queryKeys.uploadErrors(batchId),
    queryFn: () => uploadApi.getUploadErrors(batchId),
    enabled: Number.isFinite(batchId) && batchId > 0,
  });
}
