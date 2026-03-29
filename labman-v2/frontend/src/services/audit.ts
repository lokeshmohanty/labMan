import apiClient from './api';

export interface AuditLog {
    id: number;
    user_id: number | null;
    user_name: string | null;
    action: string;
    details: string | null;
    created_at: string;
}

export const auditService = {
    async getAuditLogs(params?: {
        user_id?: number;
        action?: string;
        skip?: number;
        limit?: number;
    }): Promise<AuditLog[]> {
        const queryParams = new URLSearchParams();
        if (params?.user_id) queryParams.append('user_id', params.user_id.toString());
        if (params?.action) queryParams.append('action', params.action);
        if (params?.skip) queryParams.append('skip', params.skip.toString());
        if (params?.limit) queryParams.append('limit', params.limit.toString());

        const query = queryParams.toString();
        const url = `/audit/logs${query ? `?${query}` : ''}`;

        const response = await apiClient.get<AuditLog[]>(url);
        return response.data;
    }
};
