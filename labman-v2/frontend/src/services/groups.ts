import api from './api';
import type { Group, GroupTreeNode, GroupCreate, GroupUpdate, UserGroupCreate, GroupProject, GroupTaskCreate } from '../types';

export const groupService = {
    async getGroups(): Promise<Group[]> {
        const response = await api.get<Group[]>('/groups/');
        return response.data;
    },

    async getGroupTree(): Promise<GroupTreeNode[]> {
        const response = await api.get<GroupTreeNode[]>('/groups/tree');
        return response.data;
    },

    async getGroup(id: number): Promise<Group> {
        const response = await api.get<Group>(`/groups/${id}`);
        return response.data;
    },

    async createGroup(group: GroupCreate): Promise<Group> {
        const response = await api.post<Group>('/groups/', group);
        return response.data;
    },

    async updateGroup(id: number, group: GroupUpdate): Promise<Group> {
        const response = await api.put<Group>(`/groups/${id}`, group);
        return response.data;
    },

    async deleteGroup(id: number): Promise<void> {
        await api.delete(`/groups/${id}`);
    },

    async getGroupMembers(groupId: number): Promise<any[]> {
        const response = await api.get(`/groups/${groupId}/members`);
        return response.data;
    },

    async addMember(groupId: number, data: UserGroupCreate): Promise<void> {
        await api.post(`/groups/${groupId}/members`, data);
    },

    async removeMember(groupId: number, userId: number): Promise<void> {
        await api.delete(`/groups/${groupId}/members/${userId}`);
    },

    async getGroupProject(groupId: number): Promise<GroupProject> {
        const response = await api.get<GroupProject>(`/groups/${groupId}/project`);
        return response.data;
    },

    async updateGroupProject(groupId: number, data: Partial<GroupProject>): Promise<GroupProject> {
        const response = await api.put<GroupProject>(`/groups/${groupId}/project`, data);
        return response.data;
    },

    async createGroupTask(groupId: number, task: GroupTaskCreate): Promise<void> {
        await api.post(`/groups/${groupId}/project/tasks`, task);
    },

    async updateGroupTask(groupId: number, taskId: number, data: Partial<GroupTaskCreate>): Promise<void> {
        await api.put(`/groups/${groupId}/project/tasks/${taskId}`, data);
    },

    async deleteGroupTask(groupId: number, taskId: number): Promise<void> {
        await api.delete(`/groups/${groupId}/project/tasks/${taskId}`);
    },
};
