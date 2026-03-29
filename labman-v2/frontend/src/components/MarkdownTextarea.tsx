import { createSignal, Show } from 'solid-js';
import { marked } from 'marked';
import '../styles/markdown.css';

interface MarkdownTextareaProps {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    rows?: number;
    label?: string;
    disabled?: boolean;
}

export default function MarkdownTextarea(props: MarkdownTextareaProps) {
    const [mode, setMode] = createSignal<'edit' | 'preview'>('edit');

    const renderMarkdown = (text: string) => {
        if (!text) return '<p><em>No content yet.</em></p>';
        return marked(text);
    };

    return (
        <div class="markdown-textarea">
            <Show when={props.label}>
                <label class="form-label">{props.label}</label>
            </Show>

            <div class="markdown-tabs">
                <button
                    type="button"
                    class={`markdown-tab ${mode() === 'edit' ? 'active' : ''}`}
                    onClick={() => setMode('edit')}
                >
                    ✏️ Edit
                </button>
                <button
                    type="button"
                    class={`markdown-tab ${mode() === 'preview' ? 'active' : ''}`}
                    onClick={() => setMode('preview')}
                >
                    👁️ Preview
                </button>
            </div>

            <Show when={mode() === 'edit'}>
                <textarea
                    class="form-control markdown-editor"
                    value={props.value}
                    onInput={(e) => props.onChange(e.currentTarget.value)}
                    placeholder={props.placeholder || 'Enter text (Markdown supported)...'}
                    rows={props.rows || 6}
                    disabled={props.disabled}
                />
            </Show>

            <Show when={mode() === 'preview'}>
                <div
                    class="markdown-preview"
                    innerHTML={renderMarkdown(props.value)}
                />
            </Show>
        </div>
    );
}
