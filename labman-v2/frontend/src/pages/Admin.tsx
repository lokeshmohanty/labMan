import { createSignal } from 'solid-js';
import { userService } from '../services/users';
import { useAuth } from '../stores/auth';
import type { User } from '../types';
import Users from './Users';

export default function Admin() {
    const { isAdmin } = useAuth();
    const [activeTab, setActiveTab] = createSignal<'users' | 'settings'>('users');

    // Redirect if not admin
    if (!isAdmin()) {
        window.location.href = '/dashboard';
        return null;
    }

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
                    onClick={() => setActiveTab('settings')}
                >
                    Settings
                </button>
            </div>

            <div class="tab-content">
                {activeTab() === 'users' && <Users />}
                {activeTab() === 'settings' && (
                    <div class="card">
                        <h3>System Settings</h3>
                        <p>System configuration options will be available here.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
