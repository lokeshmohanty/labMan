import { createSignal, createResource, Show, For } from 'solid-js';
import { useParams, useNavigate } from '@solidjs/router';
import { groupService } from '../services/groups';
import { useAuth } from '../stores/auth';
import '../styles/common.css';

export default function GroupDetail() {
    const params = useParams();
    const navigate = useNavigate();
    const { isAdmin, user } = useAuth();
    const [group, { refetch: refetchGroup }] = createResource(() => groupService.getGroup(parseInt(params.id)));
    const [members, { refetch: refetchMembers }] = createResource(() =>
        groupService.getGroupMembers(parseInt(params.id))
    );
    const [showAddMemberModal, setShowAddMemberModal] = createSignal(false);
    const [allUsers, setAllUsers] = createSignal<any[]>([]);
    const [selectedUserId, setSelectedUserId] = createSignal<number | null>(null);

    const canManageMembers = () => {
        return isAdmin() || group()?.lead_id === user()?.id;
    };

    const handleDelete = async () => {
        if (confirm('Are you sure you want to delete this group?')) {
            try {
                await groupService.deleteGroup(parseInt(params.id));
                navigate('/groups');
            } catch (error) {
                console.error('Failed to delete group:', error);
            }
        }
    };

    const handleAddMember = async () => {
        if (!selectedUserId()) {
            alert('Please select a user');
            return;
        }

        try {
            await groupService.addMember(parseInt(params.id), {
                user_id: selectedUserId()!
            });
            setShowAddMemberModal(false);
            setSelectedUserId(null);
            refetchMembers();
        } catch (error) {
            console.error('Failed to add member:', error);
            alert('Failed to add member. They may already be in the group.');
        }
    };

    const handleRemoveMember = async (userId: number) => {
        if (confirm('Are you sure you want to remove this member?')) {
            try {
                await groupService.removeMember(parseInt(params.id), userId);
                refetchMembers();
            } catch (error) {
                console.error('Failed to remove member:', error);
            }
        }
    };

    const openAddMemberModal = async () => {
        try {
            const response = await fetch('/api/v1/users/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const users = await response.json();
            setAllUsers(users);
            setShowAddMemberModal(true);
        } catch (error) {
            console.error('Failed to fetch users:', error);
        }
    };

    const [showEditModal, setShowEditModal] = createSignal(false);
    const [editFormData, setEditFormData] = createSignal({
        name: '',
        description: '',
        parent_id: undefined as number | undefined,
        lead_id: undefined as number | undefined,
    });
    const [allGroups, setAllGroups] = createSignal<any[]>([]);

    const openEditModal = async () => {
        // Fetch Users
        if (allUsers().length === 0) {
            try {
                const response = await fetch('/api/v1/users/', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                const users = await response.json();
                setAllUsers(users);
            } catch (error) {
                console.error('Failed to fetch users:', error);
            }
        }

        // Fetch Groups for Parent Selection
        if (allGroups().length === 0) {
            try {
                const tree = await groupService.getGroupTree();
                const flatten = (nodes: any[]): any[] => {
                    let res: any[] = [];
                    for (const n of nodes) {
                        res.push(n);
                        if (n.children && n.children.length > 0) res = res.concat(flatten(n.children));
                    }
                    return res;
                };
                setAllGroups(flatten(tree));
            } catch (error) {
                console.error('Failed to fetch groups:', error);
            }
        }

        const g = group();
        if (g) {
            setEditFormData({
                name: g.name,
                description: g.description || '',
                parent_id: g.parent_id,
                lead_id: g.lead_id,
            });
            setShowEditModal(true);
        }
    };


    const handleUpdate = async (e: Event) => {
        e.preventDefault();
        try {
            await groupService.updateGroup(parseInt(params.id), editFormData());
            setShowEditModal(false);
            refetchGroup();
        } catch (error) {
            console.error('Failed to update group:', error);
        }
    };

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    return (
        <div class="page">
            <Show when={group.loading}>
                <p>Loading group...</p>
            </Show>

            <Show when={group()}>
                <div class="page-header">
                    <h1>{group()?.name}</h1>
                    <div style="display: flex; gap: 0.5rem;">
                        <button
                            class="btn btn-primary"
                            onClick={() => navigate(`/groups/${params.id}/project`)}
                        >
                            View Project
                        </button>
                        <Show when={isAdmin()}>
                            <button class="btn btn-secondary" onClick={openEditModal}>
                                Edit Group
                            </button>
                            <button class="btn btn-danger" onClick={handleDelete}>
                                Delete Group
                            </button>
                        </Show>
                    </div>
                </div>

                <div class="card">
                    <h3>Group Information</h3>
                    <div class="form-group">
                        <label>Description</label>
                        <p>{group()?.description || 'No description provided'}</p>
                    </div>
                    <div class="form-group">
                        <label>Lead</label>
                        <p>{group()?.lead_name || 'No lead assigned'}</p>
                    </div>
                    <div class="form-group">
                        <label>Parent Group</label>
                        <p>{group()?.parent_id ? `Group #${group()?.parent_id}` : 'Top-level group'}</p>
                    </div>
                </div>

                <div class="card" style="margin-top: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h3>Members</h3>
                        <Show when={canManageMembers()}>
                            <button class="btn btn-primary" onClick={openAddMemberModal}>
                                Add Member
                            </button>
                        </Show>
                    </div>

                    <Show when={members.loading}>
                        <p>Loading members...</p>
                    </Show>

                    <Show when={members() && members()!.length === 0}>
                        <p>No members in this group yet.</p>
                    </Show>

                    <Show when={members() && members()!.length > 0}>
                        <div class="table-container">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Joined</th>
                                        <Show when={canManageMembers()}>
                                            <th>Actions</th>
                                        </Show>
                                    </tr>
                                </thead>
                                <tbody>
                                    <For each={members()}>
                                        {(member: any) => (
                                            <tr>
                                                <td>{member.user_name || 'Unknown'}</td>
                                                <td>{member.user_email || '-'}</td>
                                                <td>{formatDate(member.joined_at)}</td>
                                                <Show when={canManageMembers()}>
                                                    <td>
                                                        <button
                                                            class="btn btn-danger"
                                                            style="padding: 0.25rem 0.5rem; font-size: 0.875rem;"
                                                            onClick={() => handleRemoveMember(member.user_id)}
                                                        >
                                                            Remove
                                                        </button>
                                                    </td>
                                                </Show>
                                            </tr>
                                        )}
                                    </For>
                                </tbody>
                            </table>
                        </div>
                    </Show>
                </div>
            </Show>



            {/* Edit Group Modal */}
            {/* Edit Group Modal */}
            <Show when={showEditModal()}>
                <div class="modal-overlay" onClick={() => setShowEditModal(false)}>
                    <div class="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Edit Research Group</h2>
                        <form onSubmit={handleUpdate}>
                            <div class="form-group">
                                <label>Name</label>
                                <input
                                    type="text"
                                    value={editFormData().name}
                                    onInput={(e) => setEditFormData({ ...editFormData(), name: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>Description</label>
                                <textarea
                                    value={editFormData().description}
                                    onInput={(e) => setEditFormData({ ...editFormData(), description: e.currentTarget.value })}
                                    rows={3}
                                />
                            </div>
                            <div class="form-group">
                                <label>Parent Group</label>
                                <select
                                    value={editFormData().parent_id || ''}
                                    onChange={(e) => setEditFormData({ ...editFormData(), parent_id: e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined })}
                                >
                                    <option value="">Top-level group</option>
                                    <For each={allGroups()}>
                                        {(group) => (
                                            <Show when={group.id !== parseInt(params.id)}>
                                                <option value={group.id}>{group.name}</option>
                                            </Show>
                                        )}
                                    </For>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Group Lead</label>
                                <select
                                    value={editFormData().lead_id || ''}
                                    onChange={(e) => setEditFormData({ ...editFormData(), lead_id: e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined })}
                                >
                                    <option value="">None</option>
                                    <For each={allUsers()}>
                                        {(user) => <option value={user.id}>{user.name}</option>}
                                    </For>
                                </select>
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn" onClick={() => setShowEditModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    Update
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </Show>

            {/* Add Member Modal */}
            <Show when={showAddMemberModal()}>
                <div class="modal-overlay" onClick={() => setShowAddMemberModal(false)}>
                    <div class="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Add Member</h2>
                        <div class="form-group">
                            <label>Select User</label>
                            <select
                                value={selectedUserId() || ''}
                                onChange={(e) => setSelectedUserId(parseInt(e.target.value))}
                            >
                                <option value="">-- Select a user --</option>
                                <For each={allUsers()}>
                                    {(user) => (
                                        <option value={user.id}>{user.name} ({user.email})</option>
                                    )}
                                </For>
                            </select>
                        </div>
                        <div class="modal-actions">
                            <button class="btn btn-secondary" onClick={() => setShowAddMemberModal(false)}>
                                Cancel
                            </button>
                            <button class="btn btn-primary" onClick={handleAddMember}>
                                Add Member
                            </button>
                        </div>
                    </div>
                </div>
            </Show>
        </div >
    );
}
