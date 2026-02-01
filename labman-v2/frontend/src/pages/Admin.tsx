import { createSignal, onMount, For, createMemo } from 'solid-js';
import { adminService } from '../services/admin';
import { useAuth } from '../stores/auth';
import { appConfig } from '../stores/appConfig';
import Users from './Users';
import { getTimezoneOptions } from '../utils/dateUtils';
import '../styles/admin.css';

export default function Admin() {
    const { isAdmin } = useAuth();
    const [activeTab, setActiveTab] = createSignal<'users' | 'settings'>('users');
    const [mode, setMode] = createSignal<'simple' | 'advanced'>('simple');
    const [configContent, setConfigContent] = createSignal('');
    const [initialConfigContent, setInitialConfigContent] = createSignal('');
    const [configData, setConfigData] = createSignal<any>({});
    const [initialConfigData, setInitialConfigData] = createSignal<any>({});
    const [loading, setLoading] = createSignal(false);
    const [message, setMessage] = createSignal<{ text: string, type: 'success' | 'error' } | null>(null);

    // Timezone filtering
    const [tzSearch, setTzSearch] = createSignal('');
    const tzOptions = getTimezoneOptions();
    const filteredTzOptions = createMemo(() => {
        const search = tzSearch().toLowerCase();
        if (!search) return tzOptions;
        return tzOptions.filter((opt: any) => opt.label.toLowerCase().includes(search));
    });

    // Redirect if not admin
    if (!isAdmin()) {
        window.location.href = '/dashboard';
        return null;
    }

    const loadConfig = async () => {
        try {
            setLoading(true);
            if (mode() === 'advanced') {
                const data = await adminService.getConfig();
                setConfigContent(data.content);
                setInitialConfigContent(data.content);
            } else {
                const data = await adminService.getStructuredConfig();
                setConfigData(data);
                setInitialConfigData(JSON.parse(JSON.stringify(data)));
            }
        } catch (error) {
            console.error('Error loading config:', error);
            setMessage({ text: 'Failed to load configuration', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const getStructuredDiff = () => {
        const diff: string[] = [];
        const current = configData();
        const initial = initialConfigData();

        // Check for changes in all keys from both current and initial
        const allKeys = new Set([...Object.keys(current), ...Object.keys(initial)]);

        allKeys.forEach(key => {
            const val1 = current[key];
            const val2 = initial[key];

            // Use JSON.stringify for deep comparison of arrays/objects
            if (JSON.stringify(val1) !== JSON.stringify(val2)) {
                const label = key.replace(/_/g, ' ').toLowerCase()
                    .replace(/\b\w/g, c => c.toUpperCase());

                const fmt = (v: any) => {
                    if (v === undefined || v === null || v === '') return 'None';
                    if (typeof v === 'object') return JSON.stringify(v);
                    return String(v);
                };

                diff.push(`${label}: ${fmt(val2)} -> ${fmt(val1)}`);
            }
        });
        return diff;
    };

    const handleSaveRaw = async () => {
        if (configContent() === initialConfigContent()) {
            setMessage({ text: 'No changes detected.', type: 'error' });
            return;
        }

        if (!window.confirm(`Are you sure you want to apply these raw configuration changes?`)) {
            return;
        }

        try {
            setLoading(true);
            setMessage(null);
            await adminService.updateConfig(configContent());
            setInitialConfigContent(configContent());
            setMessage({ text: 'Configuration applied successfully!', type: 'success' });
        } catch (error: any) {
            console.error('Error saving config:', error);
            setMessage({ text: error.response?.data?.detail || 'Failed to save configuration', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleSaveStructured = async () => {
        const diff = getStructuredDiff();
        if (diff.length === 0) {
            setMessage({ text: 'No changes detected.', type: 'error' });
            return;
        }

        if (!window.confirm(`Confirm Changes:\n\n${diff.join('\n')}\n\nApply these settings?`)) {
            return;
        }

        try {
            setLoading(true);
            setMessage(null);
            const data = { ...configData() };
            // Ensure numbers are numbers for backend
            if (data.SMTP_PORT) data.SMTP_PORT = parseInt(data.SMTP_PORT);

            await adminService.updateStructuredConfig(data);

            // Sync the structured data back to current and initial to ensure types match
            setConfigData(data);
            setInitialConfigData(JSON.parse(JSON.stringify(data)));

            setMessage({ text: 'Configuration applied successfully!', type: 'success' });
        } catch (error: any) {
            console.error('Error saving config:', error);
            setMessage({ text: error.response?.data?.detail || 'Failed to save configuration', type: 'error' });
        } finally {
            setLoading(false);
        }
    };


    onMount(() => {
        if (activeTab() === 'settings') {
            loadConfig();
        }
    });

    const toggleMode = () => {
        setMode(m => m === 'simple' ? 'advanced' : 'simple');
        loadConfig(); // Reload data in new format
    };

    return (
        <div class="page">
            <div class="page-header">
                <h1>Administration</h1>
            </div>

            <div class="tabs">
                <button
                    class={activeTab() === 'users' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('users')}
                >
                    Users
                </button>
                <button
                    class={activeTab() === 'settings' ? 'tab active' : 'tab'}
                    onClick={() => {
                        setActiveTab('settings');
                        loadConfig();
                    }}
                >
                    Settings
                </button>
            </div>

            <div class="tab-content">
                {activeTab() === 'users' && <Users />}
                {activeTab() === 'settings' && (
                    <div class="card settings-card">
                        <div class="card-header">
                            <h3>System Configuration</h3>
                            <div class="header-actions">
                                <button class="btn btn-sm btn-secondary" onClick={toggleMode}>
                                    Switch to {mode() === 'simple' ? 'Advanced' : 'Simple'}
                                </button>
                            </div>
                        </div>

                        {message() && (
                            <div class={`alert alert-${message()?.type}`}>
                                {message()?.text}
                            </div>
                        )}

                        {mode() === 'advanced' ? (
                            <>
                                <div class="form-group">
                                    <label>Config File (data/config.toml)</label>
                                    <textarea
                                        class="config-editor"
                                        value={configContent()}
                                        onInput={(e) => setConfigContent(e.currentTarget.value)}
                                        rows={20}
                                    />
                                </div>
                                <div class="actions">
                                    <button
                                        class="btn btn-primary"
                                        onClick={handleSaveRaw}
                                        disabled={loading()}
                                    >
                                        {loading() ? 'Applying...' : 'Apply'}
                                    </button>
                                </div>
                            </>
                        ) : (
                            <div class="settings-form">
                                <h4>General Settings</h4>
                                <div class="form-group">
                                    <label>Lab Name</label>
                                    <input
                                        type="text"
                                        value={configData().LAB_NAME || ''}
                                        onInput={(e) => setConfigData({ ...configData(), LAB_NAME: e.currentTarget.value })}
                                    />
                                </div>
                                <div class="form-group">
                                    <label>Frontend URL</label>
                                    <input
                                        type="text"
                                        value={configData().FRONTEND_URL || ''}
                                        onInput={(e) => setConfigData({ ...configData(), FRONTEND_URL: e.currentTarget.value })}
                                    />
                                </div>
                                <div class="form-group">
                                    <label>Timezone</label>
                                    <input
                                        type="text"
                                        class="form-control"
                                        style="margin-bottom: 0.5rem; height: 32px; font-size: 0.9rem;"
                                        placeholder="🔍 Type to filter..."
                                        value={tzSearch()}
                                        onInput={(e) => setTzSearch(e.currentTarget.value)}
                                    />
                                    <select
                                        class="form-control"
                                        value={configData().TIMEZONE || appConfig().timezone || 'Asia/Kolkata'}
                                        onChange={(e) => setConfigData({ ...configData(), TIMEZONE: e.currentTarget.value })}
                                    >
                                        <For each={filteredTzOptions()}>
                                            {(tz) => (
                                                <option value={tz.value}>{tz.label}</option>
                                            )}
                                        </For>
                                    </select>
                                </div>

                                <h4>Security</h4>
                                <div class="form-group">
                                    <label>Secret Key</label>
                                    <input
                                        type="password"
                                        value={configData().SECRET_KEY || ''}
                                        onInput={(e) => setConfigData({ ...configData(), SECRET_KEY: e.currentTarget.value })}
                                    />
                                    <small>Changing this invalidates all sessions.</small>
                                </div>

                                <h4>Email Configuration (SMTP)</h4>
                                <div class="form-group">
                                    <label>SMTP Host</label>
                                    <input
                                        type="text"
                                        value={configData().SMTP_HOST || ''}
                                        onInput={(e) => setConfigData({ ...configData(), SMTP_HOST: e.currentTarget.value })}
                                        placeholder="smtp.gmail.com"
                                    />
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label>SMTP Port</label>
                                        <input
                                            type="number"
                                            value={configData().SMTP_PORT || ''}
                                            onInput={(e) => setConfigData({ ...configData(), SMTP_PORT: e.currentTarget.value })}
                                            placeholder="587"
                                        />
                                    </div>
                                    <div class="form-group">
                                        <label>SMTP User</label>
                                        <input
                                            type="text"
                                            value={configData().SMTP_USER || ''}
                                            onInput={(e) => setConfigData({ ...configData(), SMTP_USER: e.currentTarget.value })}
                                            placeholder="user@example.com"
                                        />
                                    </div>
                                </div>
                                <div class="actions">
                                    <button
                                        class="btn btn-primary"
                                        onClick={handleSaveStructured}
                                        disabled={loading()}
                                    >
                                        {loading() ? 'Applying...' : 'Apply'}
                                    </button>
                                </div>
                            </div>
                        )}

                        <div class="info-box">
                            <p><strong>Note:</strong> Changes to the configuration will require a backend restart to take effect.</p>
                        </div>
                    </div>
                )}

                {activeTab() === 'settings' && <BackupManager />}
            </div>
        </div>
    );
}

function BackupManager() {
    const [backups, setBackups] = createSignal<{ filename: string; created_at: string; size: number }[]>([]);
    const [loading, setLoading] = createSignal(false);
    const [message, setMessage] = createSignal<{ text: string, type: 'success' | 'error' } | null>(null);
    const [viewingBackup, setViewingBackup] = createSignal<{ filename: string, content: string } | null>(null);

    const loadBackups = async () => {
        try {
            const data = await adminService.listBackups();
            setBackups(data);
        } catch (error) {
            console.error('Error loading backups:', error);
        }
    };

    const handleCreateBackup = async () => {
        try {
            setLoading(true);
            await adminService.createBackup();
            setMessage({ text: 'Backup created successfully!', type: 'success' });
            loadBackups();
        } catch (error) {
            console.error('Error creating backup:', error);
            setMessage({ text: 'Failed to create backup', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleViewBackup = async (filename: string) => {
        try {
            setLoading(true);
            const data = await adminService.getBackupContent(filename);
            setViewingBackup({ filename, content: data.content });
        } catch (error) {
            console.error('Error viewing backup:', error);
            setMessage({ text: 'Failed to load backup content', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleRestore = async (filename: string) => {
        if (!confirm(`Are you sure you want to restore ${filename}? This will overwrite current settings.`)) return;

        try {
            setLoading(true);
            await adminService.restoreBackup(filename);
            setMessage({ text: 'Configuration restored! Backend refresh triggered.', type: 'success' });
            setViewingBackup(null);
            // Reload page or re-fetch settings?
            // In a real app we might want to signal the parent component to reload config.
            // For now, the user can hit Refresh Config or Refresh Page.
        } catch (error) {
            console.error('Error restoring backup:', error);
            setMessage({ text: 'Failed to restore backup', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    onMount(() => {
        loadBackups();
    });

    return (
        <div class="card settings-card" style={{ "margin-top": "2rem" }}>
            <div class="card-header">
                <h3>Configuration Backups</h3>
                <button class="btn btn-sm btn-primary" onClick={handleCreateBackup} disabled={loading()}>
                    Create Backup
                </button>
            </div>

            {message() && (
                <div class={`alert alert-${message()?.type}`}>
                    {message()?.text}
                </div>
            )}

            <div class="backup-list">
                {backups().length === 0 ? (
                    <p class="text-secondary">No backups found.</p>
                ) : (
                    <table class="w-full">
                        <thead>
                            <tr>
                                <th class="text-left">Date</th>
                                <th class="text-left">Filename</th>
                                <th class="text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {backups().map(backup => (
                                <tr>
                                    <td>{new Date(backup.created_at).toLocaleString()}</td>
                                    <td class="text-secondary text-sm">{backup.filename}</td>
                                    <td class="text-right">
                                        <button
                                            class="btn btn-sm btn-secondary"
                                            onClick={() => handleViewBackup(backup.filename)}
                                            disabled={loading()}
                                        >
                                            View
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {viewingBackup() && (
                <div class="modal-overlay" onClick={() => setViewingBackup(null)}>
                    <div class="modal" onClick={(e) => e.stopPropagation()} style={{ "max-width": "800px", "width": "90%" }}>
                        <h2>Backup Content: {viewingBackup()?.filename}</h2>
                        <div class="form-group">
                            <textarea
                                class="config-editor"
                                style={{ "height": "400px" }}
                                readOnly
                                value={viewingBackup()?.content}
                            />
                        </div>
                        <div class="modal-actions">
                            <button class="btn btn-secondary" onClick={() => setViewingBackup(null)}>
                                Close
                            </button>
                            <button
                                class="btn btn-primary"
                                onClick={() => handleRestore(viewingBackup()!.filename)}
                            >
                                Restore This Version
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
