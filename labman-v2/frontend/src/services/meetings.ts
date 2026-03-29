import api from './api';
import type { Meeting, MeetingCreate, MeetingResponse } from '../types';

export const meetingService = {
    async getMeetings(upcoming = false): Promise<Meeting[]> {
        const response = await api.get<Meeting[]>('/meetings/', { params: { upcoming } });
        return response.data;
    },

    async getMeeting(id: number): Promise<Meeting> {
        const response = await api.get<Meeting>(`/meetings/${id}`);
        return response.data;
    },

    async createMeeting(meeting: MeetingCreate): Promise<Meeting> {
        const response = await api.post<Meeting>('/meetings/', meeting);
        return response.data;
    },

    async updateMeeting(id: number, meeting: Partial<MeetingCreate>): Promise<Meeting> {
        const response = await api.put<Meeting>(`/meetings/${id}`, meeting);
        return response.data;
    },

    async deleteMeeting(id: number): Promise<void> {
        await api.delete(`/meetings/${id}`);
    },

    async respondToMeeting(id: number, response: MeetingResponse): Promise<void> {
        await api.post(`/meetings/${id}/respond`, response);
    },

    async getMeetingResponses(id: number): Promise<any[]> {
        const response = await api.get(`/meetings/${id}/responses`);
        return response.data;
    },
};
