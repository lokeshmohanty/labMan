import { A, useNavigate } from '@solidjs/router';
import { useAuth } from '../stores/auth';
import { appConfig, updateAppConfig } from '../stores/appConfig';
import { createSignal, Show, onMount } from 'solid-js';
import '../styles/layout.css';
import '../styles/settings.css';
import apiClient from '../services/api';

export default function Layout(props: any) {
    const { isAuthenticated, isAdmin, logout } = useAuth();
    const navigate = useNavigate();
    const [showSettings, setShowSettings] = createSignal(false);
    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // Sync app config on mount
    onMount(async () => {
        try {
            const response = await apiClient.get('/auth/system-info');
            const data = response.data;
            updateAppConfig({
                labName: data.lab_name || 'LabMan v2',
                timezone: data.timezone || 'Asia/Kolkata'
            });
        } catch (error) {
            console.error('Failed to fetch system info:', error);
        }
    });

    return (
        <div class="app-layout">
            <Show when={isAuthenticated()}>
                <nav class="sidebar">
                    <div class="sidebar-header">
                        <h2>{appConfig().labName}</h2>
                    </div>
                    <div class="nav-links">
                        <A href="/dashboard" activeClass="active">Dashboard</A>
                        <A href="/groups" activeClass="active">Groups</A>
                        <A href="/meetings" activeClass="active">Meetings</A>
                        <A href="/inventory" activeClass="active">Inventory</A>
                        <A href="/my-research" activeClass="active">My Research</A>
                    </div>
                    <div class="nav-footer">
                        <div class="settings-dropdown">
                            <button
                                class="settings-trigger"
                                onClick={() => setShowSettings(!showSettings())}
                            >
                                ⚙️ Settings
                            </button>
                            <Show when={showSettings()}>
                                <div class="settings-menu">
                                    <Show when={isAdmin()}>
                                        <A href="/admin" onClick={() => setShowSettings(false)}>
                                            👤 Administration
                                        </A>
                                    </Show>
                                    <A href="/account" onClick={() => setShowSettings(false)}>
                                        🔧 Account Details
                                    </A>
                                    <A href="/activity" onClick={() => setShowSettings(false)}>
                                        📊 Activity History
                                    </A>
                                    <button class="logout-btn" onClick={handleLogout}>
                                        🚪 Logout
                                    </button>
                                </div>
                            </Show>
                        </div>
                    </div>
                </nav>
            </Show>
            <main class="main-content">
                {props.children}
            </main>
        </div>
    );
}
