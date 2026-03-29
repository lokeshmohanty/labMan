import api from './api';
import type { ResearchPlan, ResearchTaskCreate } from '../types';

export const researchService = {
    async getMyResearchPlan(): Promise<ResearchPlan> {
        const response = await api.get<ResearchPlan>('/research/me');
        return response.data;
    },

    async getUserResearchPlan(userId: number): Promise<ResearchPlan> {
        const response = await api.get<ResearchPlan>(`/research/${userId}`);
        return response.data;
    },

    async updateMyResearchPlan(plan: Partial<ResearchPlan>): Promise<ResearchPlan> {
        const response = await api.put<ResearchPlan>('/research/me', plan);
        return response.data;
    },

    async updateUserComments(userId: number, comments: string): Promise<ResearchPlan> {
        const response = await api.put<ResearchPlan>(`/research/${userId}/comments`, { comments });
        return response.data;
    },

    async createTask(task: ResearchTaskCreate): Promise<void> {
        await api.post('/research/me/tasks', task);
    },

    async updateTask(taskId: number, task: Partial<ResearchTaskCreate>): Promise<void> {
        await api.put(`/research/tasks/${taskId}`, task);
    },

    async deleteTask(taskId: number): Promise<void> {
        await api.delete(`/research/tasks/${taskId}`);
    },
};
