import { createSignal, createResource, Show, For } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { groupService } from '../services/groups';
import { userService } from '../services/users';
import { useAuth } from '../stores/auth';
import type { GroupTreeNode, User } from '../types';
import '../styles/groups.css';
import '../styles/tabs.css';

export default function Groups() {
    const { isAdmin } = useAuth();
    const navigate = useNavigate();
    const [viewMode, setViewMode] = createSignal<'list' | 'research'>('research');
    const [groups, { refetch: refetchGroups }] = createResource<GroupTreeNode[]>(
        () => groupService.getGroupTree()
    );
    const [users] = createResource<User[]>(
        () => userService.getUsers()
    );
    const [showCreateModal, setShowCreateModal] = createSignal(false);
    const [formData, setFormData] = createSignal({
        name: '',
        description: '',
        parent_id: undefined as number | undefined,
        lead_id: undefined as number | undefined,
    });

    const [editingId, setEditingId] = createSignal<number | null>(null);

    const handleSave = async (e: Event) => {
        e.preventDefault();
        try {
            if (editingId()) {
                await groupService.updateGroup(editingId()!, formData());
            } else {
                await groupService.createGroup(formData());
            }
            setShowCreateModal(false);
            setEditingId(null);
            refetchGroups();
            setFormData({ name: '', description: '', parent_id: undefined, lead_id: undefined });
        } catch (error) {
            console.error('Failed to save group:', error);
        }
    };



    const openCreateModal = () => {
        setEditingId(null);
        setFormData({ name: '', description: '', parent_id: undefined, lead_id: undefined });
        setShowCreateModal(true);
    };

    const handleDelete = async (id: number) => {
        if (confirm('Are you sure you want to delete this group?')) {
            try {
                await groupService.deleteGroup(id);
                refetchGroups();
            } catch (error) {
                console.error('Failed to delete group:', error);
            }
        }
    };

    const flattenGroups = (nodes: GroupTreeNode[]): GroupTreeNode[] => {
        let result: GroupTreeNode[] = [];
        for (const node of nodes) {
            result.push(node);
            if (node.children && node.children.length > 0) {
                result = result.concat(flattenGroups(node.children));
            }
        }
        return result;
    };

    const renderTree = (nodes: GroupTreeNode[]) => {
        return (
            <div class="tree">
                <ul>
                    <For each={nodes}>
                        {(node) => (
                            <li>
                                <div class="group-card-node">
                                    <h3 class="group-title" onClick={() => navigate(`/groups/${node.id}`)}>
                                        {node.name}
                                    </h3>
                                    <Show when={node.lead_name}>
                                        <div class="group-lead">👑 {node.lead_name}</div>
                                    </Show>
                                </div>

                                <Show when={(node.children && node.children.length > 0) || (node.members && node.members.length > 0)}>
                                    <ul>
                                        {/* Render Members as Leaf Nodes */}
                                        <Show when={node.members}>
                                            <For each={node.members}>
                                                {(member) => (
                                                    <li>
                                                        <div class="member-node" onClick={() => navigate(`/research/${member.user_id}`)}>
                                                            <span class="member-avatar">{member.user_name.charAt(0)}</span>
                                                            <span class="member-name">{member.user_name}</span>
                                                        </div>
                                                    </li>
                                                )}
                                            </For>
                                        </Show>

                                        {/* Render Subgroups recursively */}
                                        <Show when={node.children && node.children.length > 0}>
                                            <For each={node.children}>
                                                {(childNode) => (
                                                    <li>
                                                        <div class="group-card-node">
                                                            <h3 class="group-title" onClick={() => navigate(`/groups/${childNode.id}`)}>
                                                                {childNode.name}
                                                            </h3>
                                                            <Show when={childNode.lead_name}>
                                                                <div class="group-lead">👑 {childNode.lead_name}</div>
                                                            </Show>
                                                        </div>

                                                        <Show when={(childNode.children && childNode.children.length > 0) || (childNode.members && childNode.members.length > 0)}>
                                                            <ul>
                                                                {/* Grandchildren Members */}
                                                                <Show when={childNode.members}>
                                                                    <For each={childNode.members}>
                                                                        {(member) => (
                                                                            <li>
                                                                                <div class="member-node" onClick={() => navigate(`/research/${member.user_id}`)}>
                                                                                    <span class="member-avatar">{member.user_name.charAt(0)}</span>
                                                                                    <span class="member-name">{member.user_name}</span>
                                                                                </div>
                                                                            </li>
                                                                        )}
                                                                    </For>
                                                                </Show>

                                                                {/* Grandchildren Subgroups (Recursive via renderTree internal logic if needed, but here we just need to recurse for children's children) */}
                                                                {/* Actually, correct recursion is calling a RenderNode function. Let's make a recursive component or function. */}
                                                                {/* SolidJS recursion is best done with a component or a self-calling function. I'll use a recursive function content. */}
                                                                {renderTree(childNode.children).children[0].children}
                                                                {/* Wait, calling renderTree again returns a div with ul. I need just the LIs or a way to embed. */}
                                                            </ul>
                                                        </Show>
                                                    </li>
                                                )}
                                            </For>
                                        </Show>
                                    </ul>
                                </Show>
                            </li>
                        )}
                    </For>
                </ul>
            </div>
        );
    };

    // Better Recursive Component approach for SolidJS
    const TreeNode = (props: { node: GroupTreeNode }) => {
        return (
            <li>
                <div class="group-card-node">
                    <div class="group-node-header">
                        <h3 class="group-title" onClick={() => navigate(`/groups/${props.node.id}`)}>
                            {props.node.name}
                        </h3>

                    </div>
                    <Show when={props.node.lead_name}>
                        <div class="group-lead">👑 {props.node.lead_name}</div>
                    </Show>

                    {/* Members as Pills */}
                    <Show when={props.node.members && props.node.members.length > 0}>
                        <div class="members-container">
                            <For each={props.node.members}>
                                {(member) => (
                                    <div
                                        class="member-pill"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            navigate(`/research/${member.user_id}`);
                                        }}
                                        title={member.user_name}
                                    >
                                        <span class="member-pill-avatar">{member.user_name.charAt(0)}</span>
                                        {member.user_name.split(' ')[0]}
                                    </div>
                                )}
                            </For>
                        </div>
                    </Show>
                </div>

                <Show when={props.node.children && props.node.children.length > 0}>
                    <ul>
                        <For each={props.node.children}>
                            {(child) => <TreeNode node={child} />}
                        </For>
                    </ul>
                </Show>
            </li>
        );
    };

    return (
        <div class="groups-page">
            <div class="page-header">
                <h1>Research Groups</h1>
                <div style="display: flex; gap: 0.5rem;">
                    <Show when={isAdmin()}>
                        <button class="btn btn-primary" onClick={openCreateModal}>
                            Create Group
                        </button>
                    </Show>
                </div>
            </div>

            <div class="tabs">
                <button
                    class={viewMode() === 'research' ? 'tab active' : 'tab'}
                    onClick={() => setViewMode('research')}
                >
                    📊 Research View
                </button>
                <button
                    class={viewMode() === 'list' ? 'tab active' : 'tab'}
                    onClick={() => setViewMode('list')}
                >
                    📋 List View
                </button>
            </div>

            <Show when={groups.loading}>
                <p>Loading groups...</p>
            </Show>

            <Show when={groups.error}>
                <div class="alert alert-error">Failed to load groups</div>
            </Show>

            <Show when={groups()}>
                {/* Research View - Tree Structure */}
                <Show when={viewMode() === 'research'}>
                    <div class="group-tree-container">
                        <div class="tree">
                            <ul>
                                <For each={groups() || []}>
                                    {(node) => <TreeNode node={node} />}
                                </For>
                            </ul>
                        </div>
                    </div>
                </Show>

                {/* List View - Flat Table */}
                <Show when={viewMode() === 'list'}>
                    <div class="table-container">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Description</th>
                                    <th>Lead</th>
                                    <th>Members</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <For each={flattenGroups(groups() || [])}>
                                    {(group) => (
                                        <tr>
                                            <td>
                                                <strong onClick={() => navigate(`/groups/${group.id}`)} style="cursor: pointer;">
                                                    {group.name}
                                                </strong>
                                            </td>
                                            <td>{group.description || '-'}</td>
                                            <td>{group.lead_name || '-'}</td>
                                            <td>{group.member_count}</td>
                                            <td>
                                                <Show when={group.has_project}>
                                                    <button class="btn btn-sm" onClick={() => navigate(`/groups/${group.id}/project`)}>
                                                        Project
                                                    </button>
                                                </Show>
                                                <Show when={isAdmin()}>
                                                    <button class="btn btn-sm btn-danger" onClick={() => handleDelete(group.id)}>
                                                        Delete
                                                    </button>
                                                </Show>
                                            </td>
                                        </tr>
                                    )}
                                </For>
                            </tbody>
                        </table>
                    </div>
                </Show>
            </Show>

            <Show when={showCreateModal()}>
                <div class="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div class="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>{editingId() ? 'Edit Research Group' : 'Create Research Group'}</h2>
                        <form onSubmit={handleSave}>
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
                                <label>Description</label>
                                <textarea
                                    value={formData().description}
                                    onInput={(e) => setFormData({ ...formData(), description: e.currentTarget.value })}
                                    rows={3}
                                />
                            </div>
                            <Show when={!editingId()}>
                                <div class="form-group">
                                    <label>Parent Group (optional)</label>
                                    <select
                                        value={formData().parent_id || ''}
                                        onChange={(e) => setFormData({ ...formData(), parent_id: e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined })}
                                    >
                                        <option value="">None (Top-level group)</option>
                                        <Show when={groups()}>
                                            <For each={groups()}>
                                                {(group) => <option value={group.id}>{group.name}</option>}
                                            </For>
                                        </Show>
                                    </select>
                                </div>
                            </Show>
                            <div class="form-group">
                                <label>Group Lead (optional)</label>
                                <select
                                    value={formData().lead_id || ''}
                                    onChange={(e) => setFormData({ ...formData(), lead_id: e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined })}
                                >
                                    <option value="">None</option>
                                    <Show when={users()}>
                                        <For each={users()}>
                                            {(user) => <option value={user.id}>{user.name}</option>}
                                        </For>
                                    </Show>
                                </select>
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn" onClick={() => setShowCreateModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    {editingId() ? 'Update' : 'Create'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </Show>
        </div>
    );
}
