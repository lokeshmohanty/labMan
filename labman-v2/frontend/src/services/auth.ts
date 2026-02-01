import api from './api';
import type { LoginRequest, Token, User } from '../types';

export const authService = {
    async login(credentials: LoginRequest): Promise<Token> {
        const formData = new FormData();
        formData.append('username', credentials.email);
        formData.append('password', credentials.password);

        const response = await api.post<Token>('/auth/login', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    async getCurrentUser(): Promise<User> {
        const response = await api.get<User>('/auth/me');
        return response.data;
    },

    async forgotPassword(email: string): Promise<void> {
        await api.post('/auth/forgot-password', { email });
    },

    async resetPassword(token: string, new_password: string): Promise<void> {
        await api.post('/auth/reset-password', { token, new_password });
    },

    async activateAccount(token: string, password: string): Promise<void> {
        await api.post('/auth/activate', { token, password });
    },
};
