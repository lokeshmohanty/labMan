import { A, useNavigate } from '@solidjs/router';
import { useAuth } from '../stores/auth';
import { createSignal, Show } from 'solid-js';
import '../styles/layout.css';
import '../styles/settings.css';

export default function Layout(props: any) {
    const { isAuthenticated, isAdmin, logout } = useAuth();
    const navigate = useNavigate();
    const [showSettings, setShowSettings] = createSignal(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div class="app-layout">
            <Show when={isAuthenticated()}>
                <nav class="sidebar">
                    <div class="sidebar-header">
                        <h2>LabMan v2</h2>
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
