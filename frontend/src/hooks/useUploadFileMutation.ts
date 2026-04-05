import { useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/api/queryKeys";
import { uploadApi } from "@/api/uploadApi";

export function useUploadFileMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => uploadApi.uploadFile(file),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.uploads }),
        queryClient.invalidateQueries({ queryKey: ["analytics"] }),
      ]);
    },
  });
}
