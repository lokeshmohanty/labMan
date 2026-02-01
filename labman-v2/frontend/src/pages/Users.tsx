import { createSignal, createResource, Show, For } from 'solid-js';
import { userService } from '../services/users';
import { useAuth } from '../stores/auth';
import type { User, UserCreate } from '../types';
import '../styles/users.css';

export default function Users() {
    const { isAdmin } = useAuth();
    const [users, { refetch }] = createResource<User[]>(userService.getUsers);
    const [showCreateModal, setShowCreateModal] = createSignal(false);
    const [formData, setFormData] = createSignal<UserCreate>({
        name: '',
        email: '',
        is_admin: false,
        email_notifications: true,
    });

    const handleCreate = async (e: Event) => {
        e.preventDefault();
        try {
            await userService.createUser(formData());
            setShowCreateModal(false);
            refetch();
            setFormData({
                name: '',
                email: '',
                is_admin: false,
                email_notifications: true,
            });
        } catch (error) {
            console.error('Failed to create user:', error);
        }
    };

    const handleDelete = async (id: number) => {
        if (confirm('Are you sure you want to delete this user?')) {
            try {
                await userService.deleteUser(id);
                refetch();
            } catch (error) {
                console.error('Failed to delete user:', error);
            }
        }
    };

    return (
        <div class="users-page">
            <div class="page-header">
                <h1>Users</h1>
                <Show when={isAdmin()}>
                    <button class="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                        Add User
                    </button>
                </Show>
            </div>

            <Show when={users.loading}>
                <p>Loading users...</p>
            </Show>

            <Show when={users.error}>
                <div class="alert alert-error">Failed to load users</div>
            </Show>

            <Show when={users()}>
                <div class="users-grid">
                    <For each={users()}>
                        {(user) => (
                            <div class="user-card">
                                <h3>{user.name}</h3>
                                <p>{user.email}</p>
                                <div class="user-badges">
                                    <Show when={user.is_admin}>
                                        <span class="badge badge-admin">Admin</span>
                                    </Show>
                                    <Show when={!user.password_hash}>
                                        <span class="badge badge-pending">Pending</span>
                                    </Show>
                                </div>
                                <Show when={isAdmin()}>
                                    <div class="user-actions">
                                        <button class="btn btn-sm btn-danger" onClick={() => handleDelete(user.id)}>
                                            Delete
                                        </button>
                                    </div>
                                </Show>
                            </div>
                        )}
                    </For>
                </div>
            </Show>

            <Show when={showCreateModal()}>
                <div class="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div class="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Create User</h2>
                        <form onSubmit={handleCreate}>
                            <div class="form-group">
                                <label>Name</label>
                                <input
                                    type="text"
                                    value={formData().name}
                                    onInput={(e) => setFormData({ ...formData(), name: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>Email</label>
                                <input
                                    type="email"
                                    value={formData().email}
                                    onInput={(e) => setFormData({ ...formData(), email: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={formData().is_admin}
                                        onChange={(e) => setFormData({ ...formData(), is_admin: e.currentTarget.checked })}
                                    />
                                    Admin
                                </label>
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn" onClick={() => setShowCreateModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    Create
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </Show>
        </div>
    );
}
