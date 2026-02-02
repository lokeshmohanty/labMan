import api from './api';
import type { Inventory, InventoryCreate } from '../types';

export const inventoryService = {
    async getInventory(availableOnly = false): Promise<Inventory[]> {
        const response = await api.get<Inventory[]>('/inventory/', {
            params: { available_only: availableOnly }
        });
        return response.data;
    },

    async createItem(item: InventoryCreate): Promise<Inventory> {
        const response = await api.post<Inventory>('/inventory/', item);
        return response.data;
    },

    async updateItem(id: number, item: Partial<InventoryCreate>): Promise<Inventory> {
        const response = await api.put<Inventory>(`/inventory/${id}`, item);
        return response.data;
    },

    async deleteItem(id: number): Promise<void> {
        await api.delete(`/inventory/${id}`);
    },
};
