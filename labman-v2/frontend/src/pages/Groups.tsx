import { createSignal, createResource, Show, For, onMount } from 'solid-js';
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
        // Find default parent (group matching lab name or first group)
        let defaultParentId: number | undefined = undefined;
        const currentGroups = flattenGroups(groups() || []);
        if (currentGroups.length > 0) {
            const labGroup = currentGroups.find(g => g.name === labName());
            if (labGroup) {
                defaultParentId = labGroup.id;
            } else {
                // Fallback to first group if exact match not found
                defaultParentId = currentGroups[0].id;
            }
        }

        setFormData({ name: '', description: '', parent_id: defaultParentId, lead_id: undefined });
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

    const [labName, setLabName] = createSignal('Lab Manager');

    onMount(async () => {
        try {
            const response = await fetch('/api/v1/auth/system-info');
            const data = await response.json();
            if (data.lab_name) {
                setLabName(data.lab_name);
            }
        } catch (error) {
            console.error('Failed to fetch system info:', error);
        }
    });

    const renderTree = (nodes: GroupTreeNode[]) => {
        // Find if there's an actual group that matches the Lab Name
        const labGroup = nodes.find(n => n.name === labName());
        const otherGroups = nodes.filter(n => n.name !== labName());

        // Base properties for the root
        let rootNode: GroupTreeNode = {
            id: 0, // Virtual ID by default
            name: labName(),
            description: 'Lab Root',
            lead_id: undefined,
            lead_name: undefined,
            member_count: 0,
            members: [],
            children: []
        };

        if (labGroup) {
            // If we found a matching group, use its details as the root
            // and dissolve it (promote its children to root children)
            rootNode = {
                ...rootNode,
                ...labGroup, // Overwrite with real data (id, description, members, etc.)
                member_count: labGroup.member_count,
                // Merge children: Real children of LabGroup + Other top-level groups
                children: [...(labGroup.children || []), ...otherGroups]
            };
        } else {
            // No matching group, just wrap everything
            rootNode.children = nodes;
            rootNode.member_count = nodes.reduce((acc, curr) => acc + (curr.member_count || 0), 0);
        }

        return (
            <div class="group-tree-wrapper">
                <TreeNode node={rootNode} isRoot={true} />
            </div>
        );
    };

    const TreeNode = (props: { node: GroupTreeNode; isRoot?: boolean }) => {
        const hasChildren = props.node.children && props.node.children.length > 0;

        // Disable navigation for virtual root
        const handleClick = () => {
            if (!props.isRoot) {
                navigate(`/groups/${props.node.id}`);
            }
            // Optional: Toggle collapse if we add collapsing later
        };

        return (
            <div class={`group-card-node ${props.isRoot ? 'root-node' : ''}`}>
                <div class="group-header-content">
                    <div class="group-node-header">
                        <h3
                            class="group-title"
                            onClick={handleClick}
                            style={{ cursor: props.isRoot ? 'default' : 'pointer' }}
                        >
                            {props.node.name}
                        </h3>
                    </div>
                </div>

                {/* Members Section - Skip for root if empty */}
                <Show when={props.node.members && props.node.members.length > 0}>
                    <div class="members-container">
                        <For each={props.node.members}>
                            {(member) => {
                                const isLead = member.user_id === props.node.lead_id;
                                return (
                                    <div
                                        class={`member-pill ${isLead ? 'is-lead' : ''}`}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            navigate(`/research/${member.user_id}`);
                                        }}
                                        title={isLead ? `${member.user_name} (Group Lead)` : member.user_name}
                                    >
                                        <div class="member-info">
                                            <span class="member-name">{member.user_name}</span>
                                            <Show when={isLead}>
                                                <span class="member-role">group lead</span>
                                            </Show>
                                        </div>
                                    </div>
                                );
                            }}
                        </For>
                    </div>
                </Show>

                {/* Nested Subgroups */}
                <Show when={hasChildren}>
                    <div class="subgroups-container">
                        {/* Only show label for non-root nodes, or customize for root */}
                        <Show when={!props.isRoot}>
                            <h4 class="subgroups-label">Subgroups</h4>
                        </Show>
                        <div class="subgroups-list">
                            <For each={props.node.children}>
                                {(child) => <TreeNode node={child} />}
                            </For>
                        </div>
                    </div>
                </Show>
            </div>
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
                        {renderTree(groups() || [])}
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
                                    <label>Parent Group</label>
                                    <select
                                        value={formData().parent_id || ''}
                                        onChange={(e) => setFormData({ ...formData(), parent_id: e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined })}
                                    >
                                        <Show when={groups()} fallback={<option value="">Loading...</option>}>
                                            <For each={flattenGroups(groups() || [])}>
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
