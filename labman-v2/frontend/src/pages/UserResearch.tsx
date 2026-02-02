import { createSignal, createResource, Show, For } from 'solid-js';
import { useParams } from '@solidjs/router';
import { researchService } from '../services/research';
import { userService } from '../services/users';
import { useAuth } from '../stores/auth';
import type { ResearchPlan, User } from '../types';
import { marked } from 'marked';
import MarkdownTextarea from '../components/MarkdownTextarea';
import '../styles/research.css';

export default function UserResearch() {
    const params = useParams();
    const { isAdmin } = useAuth();
    const userId = () => parseInt(params.userId);

    const [user] = createResource<User>(() => userService.getUser(userId()));
    const [plan, { refetch }] = createResource<ResearchPlan>(() =>
        researchService.getUserResearchPlan(userId())
    );

    const [isEditingComments, setIsEditingComments] = createSignal(false);
    const [comments, setComments] = createSignal('');

    const renderMarkdown = (text?: string) => {
        if (!text) return '<p><em>No content yet.</em></p>';
        return marked.parse(text, { async: false }) as string;
    };

    const startEditComments = () => {
        setComments(plan()?.comments || '');
        setIsEditingComments(true);
    };

    const saveComments = async () => {
        try {
            await researchService.updateUserComments(userId(), comments());
            setIsEditingComments(false);
            refetch();
        } catch (error) {
            console.error('Failed to update comments:', error);
        }
    };

    // Calculate Gantt chart date range (1 week before to 2 weeks future)
    const getGanttDateRange = () => {
        const today = new Date();
        const start = new Date(today);
        start.setDate(start.getDate() - 7); // 1 week before
        const end = new Date(today);
        end.setDate(end.getDate() + 14); // 2 weeks future
        return { start, end };
    };

    const getTaskPosition = (task: any) => {
        const { start: rangeStart, end: rangeEnd } = getGanttDateRange();
        const totalDays = (rangeEnd.getTime() - rangeStart.getTime()) / (1000 * 60 * 60 * 24);

        const taskStart = task.start_date ? new Date(task.start_date) : rangeStart;
        const taskEnd = task.end_date ? new Date(task.end_date) : rangeEnd;

        const startOffset = Math.max(0, (taskStart.getTime() - rangeStart.getTime()) / (1000 * 60 * 60 * 24));
        const duration = (taskEnd.getTime() - taskStart.getTime()) / (1000 * 60 * 60 * 24);

        return {
            left: `${(startOffset / totalDays) * 100}%`,
            width: `${Math.max(1, (duration / totalDays) * 100)}%`
        };
    };

    const getStatusClass = (status: string) => {
        switch (status) {
            case 'completed': return 'status-completed';
            case 'in_progress': return 'status-in-progress';
            default: return 'status-pending';
        }
    };

    return (
        <div class="page research-page">
            <div class="page-header">
                <div>
                    <h1>{user()?.name || 'Loading...'}'s Research</h1>
                    <p class="user-email">{user()?.email}</p>
                </div>
            </div>

            <Show when={plan.loading}>
                <p>Loading research plan...</p>
            </Show>

            <Show when={plan()}>
                <div class="research-content">
                    <div class="card">
                        <h3>Research Proposal</h3>
                        <div class="markdown-content" innerHTML={renderMarkdown(plan()?.problem_statement)} />
                    </div>

                    <div class="card">
                        <h3>Research Progress</h3>
                        <div class="markdown-content" innerHTML={renderMarkdown(plan()?.research_progress)} />
                    </div>

                    {/* Tasks List */}
                    <div class="card">
                        <h3>Tasks</h3>
                        <Show when={plan()?.tasks && plan()!.tasks.length > 0} fallback={<p>No tasks yet.</p>}>
                            <div class="tasks-list">
                                <For each={plan()?.tasks}>
                                    {(task) => (
                                        <div class={`task-item ${getStatusClass(task.status)}`}>
                                            <div class="task-header">
                                                <strong>{task.title}</strong>
                                                <span class={`task-status ${getStatusClass(task.status)}`}>
                                                    {task.status.replace('_', ' ')}
                                                </span>
                                            </div>
                                            <Show when={task.description}>
                                                <p class="task-description">{task.description}</p>
                                            </Show>
                                            <div class="task-dates">
                                                <Show when={task.start_date}>
                                                    <span>Start: {new Date(task.start_date!).toLocaleDateString()}</span>
                                                </Show>
                                                <Show when={task.end_date}>
                                                    <span>End: {new Date(task.end_date!).toLocaleDateString()}</span>
                                                </Show>
                                            </div>
                                        </div>
                                    )}
                                </For>
                            </div>
                        </Show>
                    </div>

                    {/* Gantt Chart */}
                    <div class="card">
                        <h3>Timeline (1 Week Before - 2 Weeks Future)</h3>
                        <Show when={plan()?.tasks && plan()!.tasks.length > 0} fallback={<p>No tasks to display.</p>}>
                            <div class="gantt-chart">
                                <div class="gantt-header">
                                    <div class="gantt-today-marker" style={{ left: `${(7 / 21) * 100}%` }}>
                                        <span>Today</span>
                                    </div>
                                </div>
                                <div class="gantt-tasks">
                                    <For each={plan()?.tasks}>
                                        {(task) => (
                                            <div class="gantt-row">
                                                <div class="gantt-task-label">{task.title}</div>
                                                <div class="gantt-timeline">
                                                    <div
                                                        class={`gantt-bar ${getStatusClass(task.status)}`}
                                                        style={getTaskPosition(task)}
                                                        title={`${task.title}: ${task.start_date} - ${task.end_date}`}
                                                    >
                                                        <span class="gantt-bar-label" style={{
                                                            display: 'block',
                                                            overflow: 'hidden',
                                                            'text-overflow': 'ellipsis',
                                                            'white-space': 'nowrap',
                                                            'font-size': '0.7rem',
                                                            color: 'white',
                                                            'font-weight': '600'
                                                        }}>
                                                            {task.title}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </For>
                                </div>
                            </div>
                        </Show>
                    </div>

                    {/* Links */}
                    <div class="card">
                        <h3>Links</h3>
                        <div class="links-section">
                            <Show when={plan()?.github_link} fallback={<p>No GitHub repository link.</p>}>
                                <div class="link-item">
                                    <strong>GitHub Repository:</strong>{' '}
                                    <a href={plan()!.github_link} target="_blank" rel="noopener noreferrer">
                                        {plan()!.github_link}
                                    </a>
                                </div>
                            </Show>
                            <Show when={plan()?.manuscript_link}>
                                <div class="link-item">
                                    <strong>Research Manuscript:</strong>{' '}
                                    <a href={plan()!.manuscript_link} target="_blank" rel="noopener noreferrer">
                                        {plan()!.manuscript_link}
                                    </a>
                                </div>
                            </Show>
                        </div>
                    </div>

                    {/* Comments */}
                    <Show when={isAdmin()}>
                        <div class="card admin-comments">
                            <div class="card-header">
                                <h3>Comments</h3>
                                <Show when={!isEditingComments()}>
                                    <button class="btn btn-sm btn-primary" onClick={startEditComments}>
                                        Edit Comments
                                    </button>
                                </Show>
                                <Show when={isEditingComments()}>
                                    <div class="edit-actions">
                                        <button class="btn btn-sm" onClick={() => setIsEditingComments(false)}>
                                            Cancel
                                        </button>
                                        <button class="btn btn-sm btn-primary" onClick={saveComments}>
                                            Save
                                        </button>
                                    </div>
                                </Show>
                            </div>
                            <Show when={!isEditingComments()}>
                                <div class="markdown-content" innerHTML={renderMarkdown(plan()?.comments)} />
                            </Show>
                            <Show when={isEditingComments()}>
                                <MarkdownTextarea
                                    value={comments()}
                                    onChange={(value) => setComments(value)}
                                    placeholder="Add comments for this researcher (Markdown supported)..."
                                    rows={6}
                                />
                            </Show>
                        </div>
                    </Show>
                </div>
            </Show>
        </div>
    );
}
