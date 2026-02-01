import { createSignal, createResource, For, Show } from 'solid-js';
import { auditService, type AuditLog } from '../services/audit';
import '../styles/common.css';

export default function ActivityHistory() {
    const [actionFilter, setActionFilter] = createSignal<string>('');
    const [page, setPage] = createSignal(0);
    const pageSize = 50;

    const [logs] = createResource(
        () => ({ filter: actionFilter(), page: page() }),
        async ({ filter, page }) => {
            return await auditService.getAuditLogs({
                action: filter || undefined,
                skip: page * pageSize,
                limit: pageSize
            });
        }
    );

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getActionBadgeClass = (action: string) => {
        if (action.includes('login')) return 'badge-success';
        if (action.includes('delete') || action.includes('remove')) return 'badge-danger';
        if (action.includes('create') || action.includes('add')) return 'badge-primary';
        if (action.includes('update') || action.includes('edit')) return 'badge-warning';
        return 'badge-secondary';
    };

    const handleFilterChange = (e: Event) => {
        const target = e.target as HTMLInputElement;
        setActionFilter(target.value);
        setPage(0); // Reset to first page when filter changes
    };

    return (
        <div class="page">
            <div class="page-header">
                <h1>Activity History</h1>
            </div>

            <div class="card">
                <div class="form-group">
                    <label>Filter by Action</label>
                    <input
                        type="text"
                        placeholder="e.g., login, create, update, delete..."
                        value={actionFilter()}
                        onInput={handleFilterChange}
                    />
                </div>

                <Show when={logs.loading}>
                    <p>Loading activity logs...</p>
                </Show>

                <Show when={logs.error}>
                    <p class="error">Failed to load activity logs</p>
                </Show>

                <Show when={logs() && logs()!.length === 0}>
                    <p>No activity logs found.</p>
                </Show>

                <Show when={logs() && logs()!.length > 0}>
                    <div class="activity-list">
                        <For each={logs()}>
                            {(log: AuditLog) => (
                                <div class="activity-item">
                                    <div class="activity-header">
                                        <span class={`badge ${getActionBadgeClass(log.action)}`}>
                                            {log.action}
                                        </span>
                                        <span class="activity-time">{formatDate(log.created_at)}</span>
                                    </div>
                                    <div class="activity-body">
                                        <strong>{log.user_name || 'System'}</strong>
                                        {log.details && (
                                            <p class="activity-details">{log.details}</p>
                                        )}
                                    </div>
                                </div>
                            )}
                        </For>
                    </div>

                    <div class="pagination">
                        <button
                            class="btn btn-secondary"
                            onClick={() => setPage(p => Math.max(0, p - 1))}
                            disabled={page() === 0}
                        >
                            Previous
                        </button>
                        <span>Page {page() + 1}</span>
                        <button
                            class="btn btn-secondary"
                            onClick={() => setPage(p => p + 1)}
                            disabled={logs()!.length < pageSize}
                        >
                            Next
                        </button>
                    </div>
                </Show>
            </div>
        </div>
    );
}

