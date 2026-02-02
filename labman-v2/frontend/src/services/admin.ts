import apiClient from './api';

export interface AdminConfig {
    content: string;
}

export const adminService = {
    async getConfig(): Promise<AdminConfig> {
        const response = await apiClient.get<AdminConfig>('/admin/config');
        return response.data;
    },

    async updateConfig(content: string): Promise<void> {
        await apiClient.put('/admin/config', { content });
    },

    async getStructuredConfig(): Promise<any> {
        const response = await apiClient.get<any>('/admin/config/structured');
        return response.data;
    },

    async updateStructuredConfig(data: any): Promise<void> {
        await apiClient.put('/admin/config/structured', data);
    },

    async reloadConfig(): Promise<void> {
        await apiClient.post('/admin/config/reload', {});
    },

    async createBackup(): Promise<void> {
        await apiClient.post('/admin/config/backup', {});
    },

    async listBackups(): Promise<{ filename: string; created_at: string; size: number }[]> {
        const response = await apiClient.get('/admin/config/backups');
        return response.data;
    },



    async getBackupContent(filename: string): Promise<{ content: string }> {
        const response = await apiClient.get(`/admin/config/backups/${filename}`);
        return response.data;
    },

    async restoreBackup(filename: string): Promise<void> {
        await apiClient.post(`/admin/config/restore/${filename}`, {});
    }
};
