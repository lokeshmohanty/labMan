import { createSignal, createResource, createMemo, Show, For } from 'solid-js';
import { useNavigate, useSearchParams } from '@solidjs/router';
import { meetingService } from '../services/meetings';
import { groupService } from '../services/groups';
import type { Meeting, MeetingCreate } from '../types';
import MarkdownTextarea from '../components/MarkdownTextarea';
import { formatMeetingDate, formatTime } from '../utils/dateUtils';
import { appConfig } from '../stores/appConfig';
import '../styles/tabs.css';
import '../styles/calendar.css';

export default function Meetings() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const [viewMode, setViewMode] = createSignal<'list' | 'calendar'>(
        searchParams.view === 'calendar' ? 'calendar' : 'list'
    );
    const [currentDate, setCurrentDate] = createSignal(new Date());
    const [meetings, { refetch }] = createResource<Meeting[]>(
        () => meetingService.getMeetings()
    );
    const [groups] = createResource(() => groupService.getGroups());
    const [showCreateModal, setShowCreateModal] = createSignal(false);
    const [formData, setFormData] = createSignal<MeetingCreate>({
        title: '',
        description: '',
        meeting_time: '',
        group_id: undefined,
        is_private: false,
    });

    const openCreateModal = (date?: Date) => {
        // Find default group (group matching lab name or first group)
        let defaultGroupId: number | undefined = undefined;
        const currentGroups = groups() || [];
        if (currentGroups.length > 0) {
            const labGroup = currentGroups.find(g => g.name === appConfig().labName);
            if (labGroup) {
                defaultGroupId = labGroup.id;
            } else {
                defaultGroupId = currentGroups[0].id;
            }
        }

        if (date) {
            // Format date for datetime-local: YYYY-MM-DDTHH:mm
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            setFormData({
                ...formData(),
                meeting_time: `${year}-${month}-${day}T${hours}:${minutes}`,
                group_id: defaultGroupId
            });
        } else {
            setFormData({ title: '', description: '', meeting_time: '', group_id: defaultGroupId, is_private: false });
        }
        setShowCreateModal(true);
    };

    const handleCreate = async (e: Event) => {
        e.preventDefault();
        try {
            await meetingService.createMeeting(formData());
            setShowCreateModal(false);
            refetch();
            setFormData({ title: '', description: '', meeting_time: '', group_id: undefined, is_private: false });
        } catch (error) {
            console.error('Failed to create meeting:', error);
        }
    };

    const handleRSVP = async (meetingId: number, response: string) => {
        try {
            await meetingService.respondToMeeting(meetingId, { response });
            alert(`RSVP recorded: ${response}`);
        } catch (error) {
            console.error('Failed to RSVP:', error);
        }
    };

    // Calendar helper functions
    const getDaysInMonth = (date: Date) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        return new Date(year, month + 1, 0).getDate();
    };

    const getFirstDayOfMonth = (date: Date) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        return new Date(year, month, 1).getDay();
    };

    const getMeetingsForDate = (date: Date) => {
        if (!meetings()) return [];
        // Extract YYYY-MM-DD in UTC for initial check, then refine based on actual time
        const dateStr = date.toISOString().split('T')[0];
        return meetings()!.filter(meeting => {
            const meetingDate = new Date(meeting.meeting_time).toISOString().split('T')[0];
            return meetingDate === dateStr;
        });
    };

    const calendarDays = createMemo(() => {
        const daysInMonth = getDaysInMonth(currentDate());
        const firstDay = getFirstDayOfMonth(currentDate());
        const days = [];

        // Add empty cells for days before the first day of the month
        for (let i = 0; i < firstDay; i++) {
            days.push(null);
        }

        // Add days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            days.push(day);
        }

        return days;
    });

    const previousMonth = () => {
        const newDate = new Date(currentDate());
        newDate.setMonth(newDate.getMonth() - 1);
        setCurrentDate(newDate);
    };

    const nextMonth = () => {
        const newDate = new Date(currentDate());
        newDate.setMonth(newDate.getMonth() + 1);
        setCurrentDate(newDate);
    };

    const monthName = createMemo(() => {
        return currentDate().toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    });

    return (
        <div class="page">
            <div class="page-header">
                <h1>Meetings</h1>
                <button class="btn btn-primary" onClick={() => openCreateModal()}>
                    Schedule Meeting
                </button>
            </div>

            <div class="tabs">
                <button
                    class={viewMode() === 'list' ? 'tab active' : 'tab'}
                    onClick={() => setViewMode('list')}
                >
                    📋 List View
                </button>
                <button
                    class={viewMode() === 'calendar' ? 'tab active' : 'tab'}
                    onClick={() => setViewMode('calendar')}
                >
                    📅 Calendar View
                </button>
            </div>

            <Show when={meetings.loading}>
                <p>Loading meetings...</p>
            </Show>

            <Show when={meetings()}>
                {/* List View */}
                <Show when={viewMode() === 'list'}>
                    <div class="meetings-list">
                        <For each={meetings()}>
                            {(meeting) => (
                                <div class="card meeting-card-clickable" onClick={() => navigate(`/meetings/${meeting.id}`)}>
                                    <div class="meeting-meta">
                                        <span class="meeting-time">{formatMeetingDate(meeting.meeting_time)}</span>
                                        <Show when={meeting.group_name}>
                                            <span class="badge badge-group">{meeting.group_name}</span>
                                        </Show>
                                        <Show when={meeting.is_private}>
                                            <span class="badge badge-private">Private</span>
                                        </Show>
                                    </div>
                                    <h3 class="meeting-title-list">{meeting.title}</h3>
                                    <Show when={meeting.description}>
                                        <p class="meeting-desc line-clamp-2">{meeting.description}</p>
                                    </Show>
                                    <div class="meeting-actions" onClick={(e) => e.stopPropagation()}>
                                        <button class="btn btn-sm btn-outline" onClick={() => handleRSVP(meeting.id, 'yes')}>
                                            Accept
                                        </button>
                                        <button class="btn btn-sm btn-outline" onClick={() => handleRSVP(meeting.id, 'maybe')}>
                                            Maybe
                                        </button>
                                        <button class="btn btn-sm btn-outline" onClick={() => handleRSVP(meeting.id, 'no')}>
                                            Decline
                                        </button>
                                    </div>
                                </div>
                            )}
                        </For>
                    </div>
                </Show>

                {/* Calendar View */}
                <Show when={viewMode() === 'calendar'}>
                    <div class="calendar-container">
                        <div class="calendar-header">
                            <button class="btn btn-sm" onClick={previousMonth}>←</button>
                            <h2>{monthName()}</h2>
                            <button class="btn btn-sm" onClick={nextMonth}>→</button>
                        </div>

                        <div class="calendar-grid">
                            <div class="calendar-day-header">Sun</div>
                            <div class="calendar-day-header">Mon</div>
                            <div class="calendar-day-header">Tue</div>
                            <div class="calendar-day-header">Wed</div>
                            <div class="calendar-day-header">Thu</div>
                            <div class="calendar-day-header">Fri</div>
                            <div class="calendar-day-header">Sat</div>

                            <For each={calendarDays()}>
                                {(day) => (
                                    <div class={day ? 'calendar-day' : 'calendar-day empty'}>
                                        <Show when={day}>
                                            <div class="day-header-row">
                                                <div class="day-number">{day}</div>
                                                <button
                                                    class="add-meeting-btn"
                                                    onClick={() => openCreateModal(new Date(currentDate().getFullYear(), currentDate().getMonth(), day!))}
                                                    title="Schedule meeting on this day"
                                                >
                                                    +
                                                </button>
                                            </div>
                                            <For each={getMeetingsForDate(new Date(currentDate().getFullYear(), currentDate().getMonth(), day!))}>
                                                {(meeting) => (
                                                    <div class="calendar-meeting"
                                                        title={meeting.title}
                                                        onClick={() => navigate(`/meetings/${meeting.id}`)}
                                                    >
                                                        <span class="meeting-time-badge">{formatTime(meeting.meeting_time)}</span>
                                                        <span class="meeting-title">{meeting.title}</span>
                                                    </div>
                                                )}
                                            </For>
                                        </Show>
                                    </div>
                                )}
                            </For>
                        </div>
                    </div>
                </Show>
            </Show>

            <Show when={showCreateModal()}>
                <div class="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div class="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Schedule Meeting</h2>
                        <form onSubmit={handleCreate}>
                            <div class="form-group">
                                <label>Title</label>
                                <input
                                    type="text"
                                    value={formData().title}
                                    onInput={(e) => setFormData({ ...formData(), title: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-group">
                                <label>Description</label>
                                <MarkdownTextarea
                                    value={formData().description || ''}
                                    onChange={(value) => setFormData({ ...formData(), description: value })}
                                    placeholder="Meeting description (Markdown supported)"
                                    rows={4}
                                />
                            </div>
                            <div class="form-group">
                                <label>Date & Time</label>
                                <input
                                    type="datetime-local"
                                    value={formData().meeting_time}
                                    onInput={(e) => setFormData({ ...formData(), meeting_time: e.currentTarget.value })}
                                    required
                                />
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Group</label>
                                    <select
                                        class="form-control"
                                        value={formData().group_id || ''}
                                        onChange={(e) => setFormData({ ...formData(), group_id: e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined })}
                                    >
                                        <Show when={groups()} fallback={<option value="">Loading...</option>}>
                                            <For each={groups()}>
                                                {(group) => (
                                                    <option value={group.id}>{group.name}</option>
                                                )}
                                            </For>
                                        </Show>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Visibility</label>
                                    <div class="visibility-selector" style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
                                        <button
                                            type="button"
                                            class={`btn ${!formData().is_private ? 'btn-primary' : 'btn-outline'}`}
                                            onClick={() => setFormData({ ...formData(), is_private: false })}
                                            style={{ flex: 1, "justify-content": "center" }}
                                        >
                                            🌍 Public
                                        </button>
                                        <button
                                            type="button"
                                            class={`btn ${formData().is_private ? 'btn-danger' : 'btn-outline'}`}
                                            onClick={() => setFormData({ ...formData(), is_private: true })}
                                            style={{ flex: 1, "justify-content": "center" }}
                                        >
                                            🔒 Private
                                        </button>
                                    </div>
                                    <p class="help-text" style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.5rem;">
                                        {formData().is_private
                                            ? 'Only invited members and group members can see this meeting.'
                                            : 'Visible to all lab members on the calendar.'}
                                    </p>
                                </div>
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn" onClick={() => setShowCreateModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    Create
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </Show>
        </div>
    );
}
