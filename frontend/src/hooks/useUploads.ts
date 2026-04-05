import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/api/queryKeys";
import { uploadApi } from "@/api/uploadApi";

export function useUploads() {
  return useQuery({
    queryKey: queryKeys.uploads,
    queryFn: () => uploadApi.getUploads(),
  });
}
