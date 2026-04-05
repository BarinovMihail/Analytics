import { useQuery } from "@tanstack/react-query";
import { healthApi } from "@/api/healthApi";
import { queryKeys } from "@/api/queryKeys";

export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => healthApi.getHealth(),
    staleTime: 60_000,
  });
}
