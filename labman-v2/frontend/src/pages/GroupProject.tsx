import { createSignal, createResource, Show, For } from 'solid-js';
import { useParams, useNavigate } from '@solidjs/router';
import { groupService } from '../services/groups';
import { marked } from 'marked';
import type { GroupProject, GroupTask } from '../types';
import MarkdownTextarea from '../components/MarkdownTextarea';
import '../styles/project.css';

export default function GroupProjectPage() {
    const params = useParams();
    const navigate = useNavigate();
    const groupId = () => parseInt(params.id);

    const [project, { refetch }] = createResource(groupId, groupService.getGroupProject);
    const [isEditing, setIsEditing] = createSignal(false);
    const [formData, setFormData] = createSignal<Partial<GroupProject>>({});

    // Task management state
    const [showTaskModal, setShowTaskModal] = createSignal(false);
    const [editingTask, setEditingTask] = createSignal<GroupTask | null>(null);
    const [taskForm, setTaskForm] = createSignal({
        title: '',
        description: '',
        start_date: '',
        end_date: '',
        status: 'pending'
    });

    const startEdit = () => {
        setFormData(project() || {});
        setIsEditing(true);
    };

    const cancelEdit = () => {
        setIsEditing(false);
        setFormData({});
    };

    const saveChanges = async () => {
        try {
            await groupService.updateGroupProject(groupId(), formData());
            setIsEditing(false);
            refetch();
        } catch (error) {
            console.error('Failed to update project:', error);
            alert('Failed to update project. Make sure you are a member of this group.');
        }
    };

    const renderMarkdown = (text?: string) => {
        if (!text) return '<p><em>No content yet.</em></p>';
        return marked.parse(text, { async: false }) as string;
    };

    // Task management functions
    const openTaskModal = (task?: GroupTask) => {
        if (task) {
            setEditingTask(task);
            setTaskForm({
                title: task.title,
                description: task.description || '',
                start_date: task.start_date || '',
                end_date: task.end_date || '',
                status: task.status
            });
        } else {
            setEditingTask(null);
            setTaskForm({
                title: '',
                description: '',
                start_date: '',
                end_date: '',
                status: 'pending'
            });
        }
        setShowTaskModal(true);
    };

    const closeTaskModal = () => {
        setShowTaskModal(false);
        setEditingTask(null);
        setTaskForm({
            title: '',
            description: '',
            start_date: '',
            end_date: '',
            status: 'pending'
        });
    };

    const saveTask = async () => {
        try {
            const task = editingTask();
            const formValues = taskForm();

            // Prepare task data, excluding empty dates
            const taskData: any = {
                title: formValues.title,
                status: formValues.status
            };

            if (formValues.description) {
                taskData.description = formValues.description;
            }
            if (formValues.start_date) {
                taskData.start_date = formValues.start_date;
            }
            if (formValues.end_date) {
                taskData.end_date = formValues.end_date;
            }

            if (task) {
                await groupService.updateGroupTask(groupId(), task.id, taskData);
            } else {
                await groupService.createGroupTask(groupId(), taskData);
            }
            closeTaskModal();
            refetch();
        } catch (error) {
            console.error('Failed to save task:', error);
            alert('Failed to save task');
        }
    };

    const deleteTask = async (taskId: number) => {
        if (!confirm('Are you sure you want to delete this task?')) return;
        try {
            await groupService.deleteGroupTask(groupId(), taskId);
            refetch();
        } catch (error) {
            console.error('Failed to delete task:', error);
            alert('Failed to delete task');
        }
    };

    return (
        <div class="project-page">
            <div class="page-header">
                <button class="btn btn-secondary" onClick={() => navigate('/groups')}>
                    ← Back to Groups
                </button>
                <h1>Group Project Page</h1>
                <Show when={!isEditing()}>
                    <button class="btn btn-primary" onClick={startEdit}>
                        Edit Project
                    </button>
                </Show>
                <Show when={isEditing()}>
                    <div class="edit-actions">
                        <button class="btn" onClick={cancelEdit}>Cancel</button>
                        <button class="btn btn-primary" onClick={saveChanges}>Save</button>
                    </div>
                </Show>
            </div>

            <Show when={project.loading}>
                <p>Loading project...</p>
            </Show>

            <Show when={project.error}>
                <div class="alert alert-error">Failed to load project</div>
            </Show>

            <Show when={project()}>
                <div class="project-content">
                    {/* Main Content Grid */}
                    <div class="content-grid project-grid">
                        {/* Left Column - Main Research Info */}
                        <div class="content-column main-column">
                            <div class="card section-card">
                                <h3>Research Problem</h3>
                                <Show when={!isEditing()}>
                                    <div class="markdown-content" innerHTML={renderMarkdown(project()?.problem_statement)} />
                                </Show>
                                <Show when={isEditing()}>
                                    <MarkdownTextarea
                                        value={formData().problem_statement || ''}
                                        onChange={(value) => setFormData({ ...formData(), problem_statement: value })}
                                        placeholder="Describe the research problem (Markdown supported)..."
                                        rows={8}
                                    />
                                </Show>
                            </div>

                            <div class="card section-card">
                                <h3>Research Progress</h3>
                                <Show when={!isEditing()}>
                                    <div class="markdown-content" innerHTML={renderMarkdown(project()?.research_progress)} />
                                </Show>
                                <Show when={isEditing()}>
                                    <MarkdownTextarea
                                        value={formData().research_progress || ''}
                                        onChange={(value) => setFormData({ ...formData(), research_progress: value })}
                                        placeholder="Document research progress (Markdown supported)..."
                                        rows={12}
                                    />
                                </Show>
                            </div>

                            <div class="card section-card">
                                <h3>Comments</h3>
                                <Show when={!isEditing()}>
                                    <div class="markdown-content" innerHTML={renderMarkdown(project()?.comments)} />
                                </Show>
                                <Show when={isEditing()}>
                                    <MarkdownTextarea
                                        value={formData().comments || ''}
                                        onChange={(value) => setFormData({ ...formData(), comments: value })}
                                        placeholder="Add comments (Markdown supported)..."
                                        rows={6}
                                    />
                                </Show>
                            </div>
                        </div>

                        {/* Right Column - Meta, Links, Tasks */}
                        <div class="content-column sidebar-column">
                            {/* Links Section */}
                            <Show when={project()?.github_link || project()?.manuscript_link || isEditing()}>
                                <div class="card section-card links-card">
                                    <h3>Project Links</h3>
                                    <Show when={!isEditing()}>
                                        <div class="links-grid">
                                            <Show when={project()?.github_link}>
                                                <a href={project()!.github_link} target="_blank" class="link-item github">
                                                    <span class="link-icon">G</span>
                                                    <span class="link-text">GitHub Repository</span>
                                                    <span class="link-arrow">↗</span>
                                                </a>
                                            </Show>
                                            <Show when={project()?.manuscript_link}>
                                                <a href={project()!.manuscript_link} target="_blank" class="link-item manuscript">
                                                    <span class="link-icon">M</span>
                                                    <span class="link-text">Research Manuscript</span>
                                                    <span class="link-arrow">↗</span>
                                                </a>
                                            </Show>
                                        </div>
                                    </Show>
                                    <Show when={isEditing()}>
                                        <div class="form-group">
                                            <label>GitHub Link</label>
                                            <input
                                                type="url"
                                                value={formData().github_link || ''}
                                                onInput={(e) => setFormData({ ...formData(), github_link: e.currentTarget.value })}
                                                placeholder="https://github.com/..."
                                            />
                                        </div>
                                        <div class="form-group">
                                            <label>Manuscript Link</label>
                                            <input
                                                type="url"
                                                value={formData().manuscript_link || ''}
                                                onInput={(e) => setFormData({ ...formData(), manuscript_link: e.currentTarget.value })}
                                                placeholder="https://..."
                                            />
                                        </div>
                                    </Show>
                                </div>
                            </Show>
                            <div class="card">
                                <div class="card-header">
                                    <h3>Tasks Timeline</h3>
                                    <button class="btn btn-sm btn-primary" onClick={() => openTaskModal()}>
                                        + Add Task
                                    </button>
                                </div>
                                <Show when={project()?.tasks && project()!.tasks.length > 0}>
                                    <div class="tasks-list">
                                        <For each={project()!.tasks}>
                                            {(task) => (
                                                <div class={`task-item task-${task.status}`}>
                                                    <div class="task-header">
                                                        <strong>{task.title}</strong>
                                                        <div class="task-actions">
                                                            <span class={`badge badge-${task.status}`}>
                                                                {task.status.replace('_', ' ')}
                                                            </span>
                                                            <button class="btn btn-sm" onClick={() => openTaskModal(task)}>
                                                                Edit
                                                            </button>
                                                            <button class="btn btn-sm btn-danger" onClick={() => deleteTask(task.id)}>
                                                                Delete
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <Show when={task.description}>
                                                        <p class="task-description">{task.description}</p>
                                                    </Show>
                                                    <div class="task-dates">
                                                        <Show when={task.start_date}>
                                                            <span>Start: {task.start_date}</span>
                                                        </Show>
                                                        <Show when={task.end_date}>
                                                            <span>Due: {task.end_date}</span>
                                                        </Show>
                                                    </div>
                                                </div>
                                            )}
                                        </For>
                                    </div>
                                </Show>
                                <Show when={!project()?.tasks || project()!.tasks.length === 0}>
                                    <p class="text-muted">No tasks added yet.</p>
                                </Show>

                                {/* Gantt Chart */}
                                <Show when={project()?.tasks && project()!.tasks.length > 0}>
                                    <div class="gantt-chart">
                                        <h4>Timeline View</h4>
                                        <div class="gantt-container">
                                            {(() => {
                                                const allTasks = project()!.tasks;

                                                // Fixed timeline: last week to next 2 weeks
                                                const today = new Date();
                                                const startDate = new Date(today);
                                                startDate.setDate(startDate.getDate() - 7); // 1 week ago
                                                const endDate = new Date(today);
                                                endDate.setDate(endDate.getDate() + 14); // 2 weeks ahead

                                                const todayPosition = ((today.getTime() - startDate.getTime()) / (endDate.getTime() - startDate.getTime())) * 100;

                                                return (
                                                    <>
                                                        <div class="gantt-timeline">
                                                            <For each={allTasks}>
                                                                {(task) => {
                                                                    // Calculate position and width
                                                                    let left = 0;
                                                                    let width = 100;
                                                                    let hasValidDates = false;

                                                                    if (task.start_date && task.end_date) {
                                                                        hasValidDates = true;
                                                                        const taskStart = new Date(task.start_date);
                                                                        const taskEnd = new Date(task.end_date);
                                                                        left = ((taskStart.getTime() - startDate.getTime()) / (endDate.getTime() - startDate.getTime())) * 100;
                                                                        width = ((taskEnd.getTime() - taskStart.getTime()) / (endDate.getTime() - startDate.getTime())) * 100;

                                                                        // Clamp to visible range
                                                                        if (left < 0) {
                                                                            width += left;
                                                                            left = 0;
                                                                        }
                                                                        if (left + width > 100) {
                                                                            width = 100 - left;
                                                                        }
                                                                    }

                                                                    // Build tooltip content
                                                                    const tooltipContent = `${task.title}
Status: ${task.status.replace('_', ' ')}
${task.description ? `Description: ${task.description}\n` : ''}${task.start_date ? `Start: ${task.start_date}\n` : ''}${task.end_date ? `Due: ${task.end_date}` : ''}`;

                                                                    return (
                                                                        <div class="gantt-row-full">
                                                                            <div class="gantt-bar-container">
                                                                                <Show when={hasValidDates}>
                                                                                    <div
                                                                                        class={`gantt-bar gantt-bar-pill gantt-bar-${task.status}`}
                                                                                        style={{
                                                                                            left: `${left}%`,
                                                                                            width: `${Math.max(width, 2)}%`
                                                                                        }}
                                                                                        title={tooltipContent}
                                                                                    >
                                                                                        <span class="gantt-bar-label">{task.title}</span>
                                                                                    </div>
                                                                                </Show>
                                                                                <Show when={!hasValidDates}>
                                                                                    <div class="gantt-no-dates" title={tooltipContent}>
                                                                                        {task.title} - No dates set
                                                                                    </div>
                                                                                </Show>
                                                                            </div>
                                                                        </div>
                                                                    );
                                                                }}
                                                            </For>
                                                        </div>
                                                        <Show when={todayPosition >= 0 && todayPosition <= 100}>
                                                            <div class="gantt-today-marker" style={{ left: `${todayPosition}%` }}>
                                                                <div class="gantt-today-line"></div>
                                                                <div class="gantt-today-label">Today</div>
                                                            </div>
                                                        </Show>
                                                    </>
                                                );
                                            })()}
                                        </div>
                                    </div>
                                </Show>
                            </div>
                        </div>
                    </div>

                    {/* Comments Section */}
                    <div class="card">
                        <h3>Comments</h3>
                        <Show when={!isEditing()}>
                            <div class="markdown-content" innerHTML={renderMarkdown(project()?.comments)} />
                        </Show>
                        <Show when={isEditing()}>
                            <MarkdownTextarea
                                value={formData().comments || ''}
                                onChange={(value) => setFormData({ ...formData(), comments: value })}
                                placeholder="Add comments (Markdown supported)..."
                                rows={6}
                            />
                        </Show>
                    </div>
                </div>
            </Show>

            {/* Task Modal */}
            <Show when={showTaskModal()}>
                <div class="modal-overlay" onClick={closeTaskModal}>
                    <div class="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div class="modal-header">
                            <h2>{editingTask() ? 'Edit Task' : 'Add New Task'}</h2>
                            <button class="btn-close" onClick={closeTaskModal}>×</button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label>Title *</label>
                                <input
                                    type="text"
                                    class="form-control"
                                    value={taskForm().title}
                                    onInput={(e) => setTaskForm({ ...taskForm(), title: e.currentTarget.value })}
                                    placeholder="Task title"
                                />
                            </div>
                            <div class="form-group">
                                <label>Description</label>
                                <MarkdownTextarea
                                    value={taskForm().description}
                                    onChange={(value) => setTaskForm({ ...taskForm(), description: value })}
                                    placeholder="Task description (Markdown supported)"
                                    rows={4}
                                />
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Start Date</label>
                                    <input
                                        type="date"
                                        class="form-control"
                                        value={taskForm().start_date}
                                        onInput={(e) => setTaskForm({ ...taskForm(), start_date: e.currentTarget.value })}
                                    />
                                </div>
                                <div class="form-group">
                                    <label>End Date</label>
                                    <input
                                        type="date"
                                        class="form-control"
                                        value={taskForm().end_date}
                                        onInput={(e) => setTaskForm({ ...taskForm(), end_date: e.currentTarget.value })}
                                    />
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Status</label>
                                <select
                                    class="form-control"
                                    value={taskForm().status}
                                    onChange={(e) => setTaskForm({ ...taskForm(), status: e.currentTarget.value })}
                                >
                                    <option value="pending">Pending</option>
                                    <option value="in_progress">In Progress</option>
                                    <option value="completed">Completed</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-actions">
                            <button class="btn" onClick={closeTaskModal}>Cancel</button>
                            <button class="btn btn-primary" onClick={saveTask}>
                                {editingTask() ? 'Update Task' : 'Create Task'}
                            </button>
                        </div>
                    </div>
                </div>
            </Show>
        </div>
    );
}
