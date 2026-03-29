import { createSignal, createResource } from 'solid-js';
import { authService } from '../services/auth';
import { userService } from '../services/users';
import { useAuth } from '../stores/auth';
import type { User } from '../types';

export default function Account() {
    const { user } = useAuth();
    const [isEditing, setIsEditing] = createSignal(false);
    const [formData, setFormData] = createSignal({
        name: user()?.name || '',
        email: user()?.email || '',
        email_notifications: user()?.email_notifications || true,
    });
    const [showPasswordChange, setShowPasswordChange] = createSignal(false);
    const [passwordData, setPasswordData] = createSignal({
        current_password: '',
        new_password: '',
        confirm_password: '',
    });

    const handleSave = async (e: Event) => {
        e.preventDefault();
        try {
            if (user()?.id) {
                await userService.updateUser(user()!.id, formData());
                setIsEditing(false);
                alert('Account updated successfully');
            }
        } catch (error) {
            console.error('Failed to update account:', error);
            alert('Failed to update account');
        }
    };

    const handlePasswordChange = async (e: Event) => {
        e.preventDefault();
        const pwd = passwordData();
        if (pwd.new_password !== pwd.confirm_password) {
            alert('Passwords do not match');
            return;
        }
        try {
            if (user()?.id) {
                await userService.updatePassword(user()!.id, {
                    current_password: pwd.current_password,
                    new_password: pwd.new_password,
                });
                setShowPasswordChange(false);
                setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
                alert('Password changed successfully');
            }
        } catch (error) {
            console.error('Failed to change password:', error);
            alert('Failed to change password');
        }
    };

    return (
        <div class="page">
            <div class="page-header">
                <h1>Account Details</h1>
            </div>

            <div class="card">
                <h3>Profile Information</h3>
                <form onSubmit={handleSave}>
                    <div class="form-group">
                        <label>Name</label>
                        <input
                            type="text"
                            value={formData().name}
                            onInput={(e) => setFormData({ ...formData(), name: e.currentTarget.value })}
                            disabled={!isEditing()}
                        />
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            value={formData().email}
                            onInput={(e) => setFormData({ ...formData(), email: e.currentTarget.value })}
                            disabled={!isEditing()}
                        />
                    </div>
                    <div class="form-group">
                        <label>
                            <input
                                type="checkbox"
                                checked={formData().email_notifications}
                                onChange={(e) => setFormData({ ...formData(), email_notifications: e.currentTarget.checked })}
                                disabled={!isEditing()}
                            />
                            Enable email notifications
                        </label>
                    </div>
                    <div class="modal-actions">
                        {!isEditing() ? (
                            <button type="button" class="btn btn-primary" onClick={() => setIsEditing(true)}>
                                Edit
                            </button>
                        ) : (
                            <>
                                <button type="button" class="btn" onClick={() => setIsEditing(false)}>
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    Save
                                </button>
                            </>
                        )}
                    </div>
                </form>
            </div>

            <div class="card" style="margin-top: 1.5rem;">
                <h3>Change Password</h3>
                {!showPasswordChange() ? (
                    <button class="btn btn-primary" onClick={() => setShowPasswordChange(true)}>
                        Change Password
                    </button>
                ) : (
                    <form onSubmit={handlePasswordChange}>
                        <div class="form-group">
                            <label>Current Password</label>
                            <input
                                type="password"
                                value={passwordData().current_password}
                                onInput={(e) => setPasswordData({ ...passwordData(), current_password: e.currentTarget.value })}
                                required
                            />
                        </div>
                        <div class="form-group">
                            <label>New Password</label>
                            <input
                                type="password"
                                value={passwordData().new_password}
                                onInput={(e) => setPasswordData({ ...passwordData(), new_password: e.currentTarget.value })}
                                required
                            />
                        </div>
                        <div class="form-group">
                            <label>Confirm New Password</label>
                            <input
                                type="password"
                                value={passwordData().confirm_password}
                                onInput={(e) => setPasswordData({ ...passwordData(), confirm_password: e.currentTarget.value })}
                                required
                            />
                        </div>
                        <div class="modal-actions">
                            <button type="button" class="btn" onClick={() => setShowPasswordChange(false)}>
                                Cancel
                            </button>
                            <button type="submit" class="btn btn-primary">
                                Change Password
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}
