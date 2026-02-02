import { createResource, Show, For } from 'solid-js';
import { useParams, useNavigate } from '@solidjs/router';
import { meetingService } from '../services/meetings';
import { useAuth } from '../stores/auth';
import type { Meeting } from '../types';
import { marked } from 'marked';
import { formatMeetingDate } from '../utils/dateUtils';
import '../styles/project.css';

export default function MeetingDetail() {
    const params = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [meeting] = createResource<Meeting>(() => meetingService.getMeeting(parseInt(params.id)));
    const [responses, { refetch: refetchResponses }] = createResource(() => meetingService.getMeetingResponses(parseInt(params.id)));


    const handleRSVP = async (response: string) => {
        try {
            await meetingService.respondToMeeting(parseInt(params.id), { response });
            refetchResponses();
            alert(`RSVP recorded: ${response}`);
        } catch (error) {
            console.error('Failed to RSVP:', error);
        }
    };

    const renderMarkdown = (text: string) => {
        return { __html: marked.parse(text, { async: false }) as string };
    };

    const isCreator = () => meeting() && user() && meeting()?.created_by === user()?.id;
    const isAdmin = () => user()?.is_admin;

    return (
        <div class="page page-full">
            <Show when={meeting.loading}>
                <p>Loading meeting details...</p>
            </Show>

            <Show when={meeting()} keyed>
                {(m) => (
                    <div class="meeting-detail-container">
                        <div class="page-header">
                            <div>
                                <button class="btn btn-sm" onClick={() => navigate('/meetings')}>← Back to Meetings</button>
                                <h1>{m.title}</h1>
                            </div>
                            <Show when={isCreator() || isAdmin()}>
                                <button class="btn btn-primary" onClick={() => alert('Edit functionality placeholder')}>
                                    Edit Meeting
                                </button>
                            </Show>
                        </div>

                        <div class="meeting-detail-grid">
                            <div class="meeting-detail-main">
                                <div class="card meeting-info-card">
                                    <div class="meeting-meta-large">
                                        <div class="meta-item">
                                            <span class="meta-label">Date & Time</span>
                                            <span class="meta-value">{formatMeetingDate(m.meeting_time)}</span>
                                        </div>
                                        <Show when={m.group_name}>
                                            <div class="meta-item">
                                                <span class="meta-label">Group</span>
                                                <span class="meta-value">{m.group_name}</span>
                                            </div>
                                        </Show>
                                        <Show when={m.is_private}>
                                            <div class="meta-item">
                                                <span class="meta-label">Visibility</span>
                                                <span class="badge badge-private">Private</span>
                                            </div>
                                        </Show>
                                        <div class="meta-item">
                                            <span class="meta-label">Organizer</span>
                                            <span class="meta-value">{m.creator_name || 'Unknown'}</span>
                                        </div>
                                    </div>

                                    <Show when={m.description}>
                                        <div class="meeting-description-section">
                                            <h3>Description</h3>
                                            <div class="markdown-body" innerHTML={renderMarkdown(m.description || '').__html} />
                                        </div>
                                    </Show>
                                </div>

                                <div class="card rsvp-card">
                                    <h3>Your Response</h3>
                                    <div class="rsvp-actions">
                                        <button class="btn btn-success" onClick={() => handleRSVP('yes')}>Accept</button>
                                        <button class="btn btn-warning" onClick={() => handleRSVP('maybe')}>Maybe</button>
                                        <button class="btn btn-danger" onClick={() => handleRSVP('no')}>Decline</button>
                                    </div>
                                </div>
                            </div>

                            <div class="meeting-detail-sidebar">
                                <div class="card attendance-card">
                                    <h3>Attendees</h3>
                                    <div class="attendance-list">
                                        <Show when={responses.loading}>
                                            <p>Loading attendance...</p>
                                        </Show>
                                        <For each={responses()}>
                                            {(resp) => (
                                                <div class="attendance-item">
                                                    <span class="attendee-name">{resp.user_name}</span>
                                                    <span class={`rsvp-badge rsvp-${resp.response}`}>
                                                        {resp.response}
                                                    </span>
                                                </div>
                                            )}
                                        </For>
                                        <Show when={responses()?.length === 0}>
                                            <p class="empty-state">No responses yet.</p>
                                        </Show>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </Show>
        </div>
    );
}
