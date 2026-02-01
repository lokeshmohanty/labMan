import api from './api';
import type { User, UserCreate, UserUpdate, PasswordUpdate } from '../types';

export const userService = {
    async getUsers(): Promise<User[]> {
        const response = await api.get<User[]>('/users/');
        return response.data;
    },

    async getUser(id: number): Promise<User> {
        const response = await api.get<User>(`/users/${id}`);
        return response.data;
    },

    async createUser(user: UserCreate): Promise<User> {
        const response = await api.post<User>('/users/', user);
        return response.data;
    },

    async updateUser(id: number, user: UserUpdate): Promise<User> {
        const response = await api.put<User>(`/users/${id}`, user);
        return response.data;
    },

    async deleteUser(id: number): Promise<void> {
        await api.delete(`/users/${id}`);
    },

    async updatePassword(id: number, data: PasswordUpdate): Promise<void> {
        await api.put(`/users/${id}/password`, data);
    },

    async resendActivation(id: number): Promise<void> {
        await api.post(`/users/${id}/resend-activation`);
    },
};
