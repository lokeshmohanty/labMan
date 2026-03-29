import { createResource, For, Show } from 'solid-js';
import { useAuth } from '../stores/auth';
import { groupService } from '../services/groups';
import { meetingService } from '../services/meetings';
import { auditService } from '../services/audit';
import { inventoryService } from '../services/inventory';
import { A } from '@solidjs/router';
import { formatDashboardDate, formatDateTime } from '../utils/dateUtils';
import '../styles/dashboard.css';

export default function Dashboard() {
    const { user } = useAuth();

    const [groups] = createResource(groupService.getGroups);
    const [meetings] = createResource(() => meetingService.getMeetings()); // Get all for stats, filter in UI
    const [auditLogs] = createResource(() => auditService.getAuditLogs({ limit: 5 }));
    const [inventory] = createResource(() => inventoryService.getInventory());

    const upcomingMeetings = () => {
        const now = new Date();
        return (meetings() || [])
            .filter(m => new Date(m.meeting_time) > now)
            .sort((a, b) => new Date(a.meeting_time).getTime() - new Date(b.meeting_time).getTime())
            .slice(0, 3);
    };

    return (
        <div class="dashboard">
            <div class="page-header">
                <h1>Welcome, {user()?.name || 'Researcher'}!</h1>
                <p class="dashboard-subtitle">Here is what's happening in your lab today.</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-label">My Groups</span>
                    <span class="stat-value">{groups()?.length || 0}</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Upcoming Meetings</span>
                    <span class="stat-value">{upcomingMeetings().length}</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label">Inventory Items</span>
                    <span class="stat-value">{inventory()?.length || 0}</span>
                </div>
            </div>

            <div class="dashboard-grid">
                <div class="card main-span">
                    <div class="card-header">
                        <h2>Upcoming Meetings</h2>
                        <A href="/meetings?view=calendar" class="view-all">View Calendar</A>
                    </div>
                    <Show when={upcomingMeetings().length > 0} fallback={<p class="empty-state">No upcoming meetings scheduled.</p>}>
                        <div class="meeting-list-mini">
                            <For each={upcomingMeetings()}>
                                {(meeting) => (
                                    <A href={`/meetings/${meeting.id}`} class="meeting-item-mini">
                                        <div class="meeting-info">
                                            <span class="meeting-title">{meeting.title}</span>
                                            <span class="meeting-time">{formatDashboardDate(meeting.meeting_time)}</span>
                                        </div>
                                        <Show when={meeting.group_name}>
                                            <span class="meeting-tag">{meeting.group_name}</span>
                                        </Show>
                                    </A>
                                )}
                            </For>
                        </div>
                    </Show>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2>Your Groups</h2>
                        <A href="/groups" class="view-all">Manage</A>
                    </div>
                    <Show when={groups()?.length && groups()!.length > 0} fallback={<p class="empty-state">Not assigned to any groups.</p>}>
                        <div class="group-list-mini">
                            <For each={groups()?.slice(0, 5)}>
                                {(group) => (
                                    <A href={`/groups/${group.id}`} class="group-item-mini">
                                        <span class="group-name">{group.name}</span>
                                        <span class="group-role">{group.lead_name || 'Research Group'}</span>
                                    </A>
                                )}
                            </For>
                        </div>
                    </Show>
                </div>

                <div class="card full-width">
                    <div class="card-header">
                        <h2>Recent Activity</h2>
                        <A href="/activity" class="view-all">Activity History</A>
                    </div>
                    <Show when={auditLogs()?.length && auditLogs()!.length > 0} fallback={<p class="empty-state">No recent activity logged.</p>}>
                        <div class="activity-feed">
                            <For each={auditLogs()}>
                                {(log) => (
                                    <div class="activity-log-item">
                                        <div class="log-marker"></div>
                                        <div class="log-content">
                                            <p><strong>{log.user_name}</strong> {log.action}</p>
                                            <Show when={log.details}>
                                                <span class="log-details">{log.details}</span>
                                            </Show>
                                            <span class="log-time">{formatDateTime(log.created_at)}</span>
                                        </div>
                                    </div>
                                )}
                            </For>
                        </div>
                    </Show>
                </div>
            </div>
        </div>
    );
}

