import { createSignal, createResource, Show, For } from 'solid-js';
import { serverService } from '../services/servers';
import { useAuth } from '../stores/auth';
import type { Server, ServerCreate } from '../types';

export default function Servers() {
    const { isAdmin } = useAuth();
    const [servers, { refetch }] = createResource<Server[]>(serverService.getServers);
    const [showModal, setShowModal] = createSignal(false);
    const [editingServer, setEditingServer] = createSignal<Server | null>(null);
    const [formData, setFormData] = createSignal<ServerCreate>({
        name: '',
        status: 'active',
    });

    const handleSubmit = async (e: Event) => {
        e.preventDefault();
        try {
            if (editingServer()) {
                await serverService.updateServer(editingServer()!.id, formData());
            } else {
                await serverService.createServer(formData());
            }
            setShowModal(false);
            setEditingServer(null);
            refetch();
            setFormData({ name: '', status: 'active' });
        } catch (error) {
            console.error('Failed to save server:', error);
        }
    };

    const handleEdit = (server: Server) => {
        setEditingServer(server);
        setFormData({
            name: server.name,
            hostname: server.hostname,
            ip_address: server.ip_address,
            description: server.description,
            specs: server.specs,
            status: server.status,
            notes: server.notes,
        });
        setShowModal(true);
    };

    return (
        <div class="page">
            <div class="page-header">
                <h1>Servers</h1>
                <Show when={isAdmin()}>
                    <button class="btn btn-primary" onClick={() => setShowModal(true)}>
                        Add Server
                    </button>
                </Show>
            </div>

            <Show when={servers.loading}>
                <p>Loading servers...</p>
            </Show>

            <Show when={servers()}>
                <div class="servers-grid">
                    <For each={servers()}>
                        {(server) => (
                            <div class="card server-card">
                                <div class="server-header">
                                    <h3>{server.name}</h3>
                                    <span class={`badge badge-${server.status}`}>{server.status}</span>
                                </div>
                                <Show when={server.hostname}>
                                    <p><strong>Hostname:</strong> {server.hostname}</p>
                                </Show>
                                <Show when={server.ip_address}>
                                    <p><strong>IP:</strong> {server.ip_address}</p>
                                </Show>
                                <Show when={server.specs}>
                                    <p><strong>Specs:</strong> {server.specs}</p>
                                </Show>
                                <Show when={server.description}>
                                    <p class="text-muted">{server.description}</p>
                                </Show>
                                <div class="server-actions">
                                    <button class="btn btn-sm" onClick={() => handleEdit(server)}>
                                        Edit
                                    </button>
                                </div>
                            </div>
                        )}
                    </For>
                </div>
            </Show>

            <Show when={showModal()}>
                <div class="modal-overlay" onClick={() => { setShowModal(false); setEditingServer(null); }}>
                    <div class="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>{editingServer() ? 'Edit Server' : 'Add Server'}</h2>
                        <form onSubmit={handleSubmit}>
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
                                <label>Hostname</label>
                                <input
                                    type="text"
                                    value={formData().hostname || ''}
                                    onInput={(e) => setFormData({ ...formData(), hostname: e.currentTarget.value })}
                                />
                            </div>
                            <div class="form-group">
                                <label>IP Address</label>
                                <input
                                    type="text"
                                    value={formData().ip_address || ''}
                                    onInput={(e) => setFormData({ ...formData(), ip_address: e.currentTarget.value })}
                                />
                            </div>
                            <div class="form-group">
                                <label>Specs</label>
                                <input
                                    type="text"
                                    value={formData().specs || ''}
                                    onInput={(e) => setFormData({ ...formData(), specs: e.currentTarget.value })}
                                    placeholder="e.g., 32GB RAM, 8 cores"
                                />
                            </div>
                            <div class="form-group">
                                <label>Status</label>
                                <select
                                    value={formData().status}
                                    onChange={(e) => setFormData({ ...formData(), status: e.currentTarget.value })}
                                >
                                    <option value="active">Active</option>
                                    <option value="maintenance">Maintenance</option>
                                    <option value="offline">Offline</option>
                                </select>
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn" onClick={() => { setShowModal(false); setEditingServer(null); }}>
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    Save
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </Show>
        </div>
    );
}
