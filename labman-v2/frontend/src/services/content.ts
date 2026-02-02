import api from './api';
import type { Content } from '../types';

export const contentService = {
    async getContent(groupId?: number, researchPlanId?: number): Promise<Content[]> {
        const response = await api.get<Content[]>('/content/', {
            params: { group_id: groupId, research_plan_id: researchPlanId }
        });
        return response.data;
    },

    async uploadFile(file: File, title?: string, description?: string, groupId?: number): Promise<Content> {
        const formData = new FormData();
        formData.append('file', file);
        if (title) formData.append('title', title);
        if (description) formData.append('description', description);
        if (groupId) formData.append('group_id', groupId.toString());

        const response = await api.post<Content>('/content/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
    },

    async deleteContent(id: number): Promise<void> {
        await api.delete(`/content/${id}`);
    },

    getDownloadUrl(id: number): string {
        return `${api.defaults.baseURL}/content/${id}/download`;
    },
};
