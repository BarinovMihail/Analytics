import { apiClient } from "@/api/client";
import { getObject, getString } from "@/utils/parsers";

export interface HealthStatus {
  status: string;
  database: string;
  environment: string;
}

export const healthApi = {
  async getHealth(): Promise<HealthStatus> {
    const response = await apiClient.get("/health");
    const data = getObject(response.data);

    return {
      status: getString(data.status, "unknown"),
      database: getString(data.database, "unknown"),
      environment: getString(data.environment, "unknown"),
    };
  },
};
