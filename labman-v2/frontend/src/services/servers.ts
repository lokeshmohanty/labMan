import api from './api';
import type { Server, ServerCreate } from '../types';

export const serverService = {
    async getServers(): Promise<Server[]> {
        const response = await api.get<Server[]>('/servers/');
        return response.data;
    },

    async createServer(server: ServerCreate): Promise<Server> {
        const response = await api.post<Server>('/servers/', server);
        return response.data;
    },

    async updateServer(id: number, server: Partial<ServerCreate>): Promise<Server> {
        const response = await api.put<Server>(`/servers/${id}`, server);
        return response.data;
    },

    async deleteServer(id: number): Promise<void> {
        await api.delete(`/servers/${id}`);
    },
};
