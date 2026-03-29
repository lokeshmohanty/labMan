import { Book, BookCreate, BookUpdate } from '../types';

export const bookService = {
    getBooks: async (): Promise<Book[]> => {
        const response = await fetch('/api/v1/books/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch books');
        return response.json();
    },

    getBook: async (id: number): Promise<Book> => {
        const response = await fetch(`/api/v1/books/${id}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch book');
        return response.json();
    },

    createBook: async (data: BookCreate): Promise<Book> => {
        const response = await fetch('/api/v1/books/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Failed to create book');
        return response.json();
    },

    updateBook: async (id: number, data: BookUpdate): Promise<Book> => {
        const response = await fetch(`/api/v1/books/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Failed to update book');
        return response.json();
    },

    deleteBook: async (id: number): Promise<void> => {
        const response = await fetch(`/api/v1/books/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) throw new Error('Failed to delete book');
    }
};
