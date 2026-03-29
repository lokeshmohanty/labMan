import { createSignal, createResource, Show, For } from 'solid-js';
import { researchService } from '../services/research';
import type { ResearchPlan, ResearchTaskCreate } from '../types';
import { marked } from 'marked';
import MarkdownTextarea from '../components/MarkdownTextarea';

export default function MyResearch() {
    const [plan, { refetch }] = createResource<ResearchPlan>(researchService.getMyResearchPlan);
    const [isEditing, setIsEditing] = createSignal(false);
    const [formData, setFormData] = createSignal<Partial<ResearchPlan>>({});

    // Task management state
    const [showTaskModal, setShowTaskModal] = createSignal(false);
    const [editingTask, setEditingTask] = createSignal<any | null>(null);
    const [taskForm, setTaskForm] = createSignal({
        title: '',
        description: '',
        start_date: '',
        end_date: '',
        status: 'pending'
    });

    const renderMarkdown = (text?: string) => {
        if (!text) return '<p><em>No content yet.</em></p>';
        return marked(text);
    };

    const startEdit = () => {
        setFormData(plan() || {});
        setIsEditing(true);
    };

    const saveChanges = async () => {
        try {
            await researchService.updateMyResearchPlan(formData());
            setIsEditing(false);
            refetch();
        } catch (error) {
            console.error('Failed to update research plan:', error);
        }
    };

    // Task management functions
    const openTaskModal = (task?: any) => {
        if (task) {
            setEditingTask(task);
            setTaskForm({
                title: task.title || '',
                description: task.description || '',
                start_date: task.start_date || '',
                end_date: task.end_date || '',
                status: task.status || 'pending'
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
            const taskData: any = {
                title: taskForm().title,
                description: taskForm().description,
                status: taskForm().status
            };

            // Only include dates if they have values
            if (taskForm().start_date) {
                taskData.start_date = taskForm().start_date;
            }
            if (taskForm().end_date) {
                taskData.end_date = taskForm().end_date;
            }

            if (editingTask()) {
                await researchService.updateTask(editingTask().id, taskData);
            } else {
                await researchService.createTask(taskData);
            }
            closeTaskModal();
            refetch();
        } catch (error) {
            console.error('Failed to save task:', error);
        }
    };

    const deleteTask = async (taskId: number) => {
        if (confirm('Are you sure you want to delete this task?')) {
            try {
                await researchService.deleteTask(taskId);
                refetch();
            } catch (error) {
                console.error('Failed to delete task:', error);
            }
        }
    };

    return (
        <div class="page">
            <div class="page-header">
                <h1>My Research</h1>
                <Show when={!isEditing()}>
                    <button class="btn btn-primary" onClick={startEdit}>
                        Edit
                    </button>
                </Show>
                <Show when={isEditing()}>
                    <div class="edit-actions">
                        <button class="btn" onClick={() => setIsEditing(false)}>Cancel</button>
                        <button class="btn btn-primary" onClick={saveChanges}>Save</button>
                    </div>
                </Show>
            </div>

            <Show when={plan.loading}>
                <p>Loading research plan...</p>
            </Show>

            <Show when={plan()}>
                <div class="research-content">
                    <div class="card">
                        <h3>Research Problem</h3>
                        <Show when={!isEditing()}>
                            <div class="markdown-content" innerHTML={renderMarkdown(plan()?.problem_statement)} />
                        </Show>
                        <Show when={isEditing()}>
                            <MarkdownTextarea
                                value={formData().problem_statement || ''}
                                onChange={(value) => setFormData({ ...formData(), problem_statement: value })}
                                placeholder="Describe your research problem (Markdown supported)..."
                                rows={6}
                            />
                        </Show>
                    </div>

                    <div class="card">
                        <h3>Research Progress</h3>
                        <Show when={!isEditing()}>
                            <div class="markdown-content" innerHTML={renderMarkdown(plan()?.research_progress)} />
                        </Show>
                        <Show when={isEditing()}>
                            <MarkdownTextarea
                                value={formData().research_progress || ''}
                                onChange={(value) => setFormData({ ...formData(), research_progress: value })}
                                placeholder="Document your research progress (Markdown supported)..."
                                rows={10}
                            />
                        </Show>
                    </div>

                    {/* Tasks Section */}
                    <div class="card">
                        <div class="card-header">
                            <h3>Tasks</h3>
                            <button class="btn btn-sm btn-primary" onClick={() => openTaskModal()}>
                                + Add Task
                            </button>
                        </div>
                        <Show when={plan()?.tasks && plan()!.tasks.length > 0} fallback={<p>No tasks yet.</p>}>
                            <div class="tasks-list">
                                <For each={plan()?.tasks}>
                                    {(task) => (
                                        <div class="task-item">
                                            <div class="task-header">
                                                <strong>{task.title}</strong>
                                                <div class="task-actions">
                                                    <span class={`task-status status-${task.status}`}>
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
                    </div>

                    <div class="card">
                        <h3>Links</h3>
                        <Show when={!isEditing()}>
                            <Show when={plan()?.github_link}>
                                <p><strong>GitHub:</strong> <a href={plan()!.github_link} target="_blank">{plan()!.github_link}</a></p>
                            </Show>
                            <Show when={plan()?.manuscript_link}>
                                <p><strong>Manuscript:</strong> <a href={plan()!.manuscript_link} target="_blank">{plan()!.manuscript_link}</a></p>
                            </Show>
                        </Show>
                        <Show when={isEditing()}>
                            <div class="form-group">
                                <label>GitHub Link</label>
                                <input
                                    type="url"
                                    value={formData().github_link || ''}
                                    onInput={(e) => setFormData({ ...formData(), github_link: e.currentTarget.value })}
                                />
                            </div>
                            <div class="form-group">
                                <label>Manuscript Link</label>
                                <input
                                    type="url"
                                    value={formData().manuscript_link || ''}
                                    onInput={(e) => setFormData({ ...formData(), manuscript_link: e.currentTarget.value })}
                                />
                            </div>
                        </Show>
                    </div>
                </div>
            </Show>

            {/* Task Modal */}
            <Show when={showTaskModal()}>
                <div class="modal-overlay" onClick={closeTaskModal}>
                    <div class="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>{editingTask() ? 'Edit Task' : 'Add Task'}</h2>
                        <form onSubmit={(e) => { e.preventDefault(); saveTask(); }}>
                            <div class="form-group">
                                <label>Title *</label>
                                <input
                                    type="text"
                                    class="form-control"
                                    value={taskForm().title}
                                    onInput={(e) => setTaskForm({ ...taskForm(), title: e.currentTarget.value })}
                                    placeholder="Task title"
                                    required
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
                            <div class="modal-actions">
                                <button type="button" class="btn" onClick={closeTaskModal}>
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    {editingTask() ? 'Update' : 'Create'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </Show>
        </div>
    );
}
