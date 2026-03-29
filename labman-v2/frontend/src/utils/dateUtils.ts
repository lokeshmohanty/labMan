import { appConfig } from '../stores/appConfig';

export const formatDate = (date: string | Date, timezone?: string) => {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        timeZone: timezone || appConfig().timezone || 'Asia/Kolkata',
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
};

export const formatDateTime = (date: string | Date, timezone?: string) => {
    const d = new Date(date);
    return d.toLocaleString('en-US', {
        timeZone: timezone || appConfig().timezone || 'Asia/Kolkata',
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
};

export const formatTime = (date: string | Date, timezone?: string) => {
    const d = new Date(date);
    return d.toLocaleTimeString('en-US', {
        timeZone: timezone || appConfig().timezone || 'Asia/Kolkata',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
};

// Custom format for Dashboard: "time day month (weekday)"
export const formatDashboardDate = (date: string | Date, timezone?: string) => {
    const d = new Date(date);
    const tz = timezone || appConfig().timezone || 'Asia/Kolkata';
    const time = d.toLocaleTimeString('en-US', { timeZone: tz, hour: '2-digit', minute: '2-digit', hour12: true });
    const day = d.toLocaleDateString('en-US', { timeZone: tz, day: 'numeric' });
    const month = d.toLocaleDateString('en-US', { timeZone: tz, month: 'short' });
    const weekday = d.toLocaleDateString('en-US', { timeZone: tz, weekday: 'short' });
    return `${time} ${day} ${month} (${weekday})`;
};

// Custom format for Meetings: "time   day month (weekday)"
export const formatMeetingDate = (date: string | Date, timezone?: string) => {
    const d = new Date(date);
    const tz = timezone || appConfig().timezone || 'Asia/Kolkata';
    const time = d.toLocaleTimeString('en-US', { timeZone: tz, hour: '2-digit', minute: '2-digit', hour12: true });
    const day = d.toLocaleDateString('en-US', { timeZone: tz, day: 'numeric' });
    const month = d.toLocaleDateString('en-US', { timeZone: tz, month: 'short' });
    const weekday = d.toLocaleDateString('en-US', { timeZone: tz, weekday: 'short' });
    return `${time}\u00A0\u00A0\u00A0${day} ${month} (${weekday})`;
};

export const getTimezoneOptions = () => {
    const timezones = (Intl as any).supportedValuesOf('timeZone');
    const date = new Date();

    return timezones.map((tz: string) => {
        try {
            const formatter = new Intl.DateTimeFormat('en-US', {
                timeZone: tz,
                timeZoneName: 'shortOffset'
            });
            const parts = formatter.formatToParts(date);
            const offset = parts.find(p => p.type === 'timeZoneName')?.value || 'UTC';

            return {
                value: tz,
                label: `${tz.replace(/_/g, ' ')} (${offset})`
            };
        } catch (e) {
            return { value: tz, label: tz };
        }
    }).sort((a: any, b: any) => {
        // Sort by offset primarily, then name
        const getOffsetValue = (label: string) => {
            const match = label.match(/GMT([+-])(\d+):?(\d+)?/);
            if (!match) return 0;
            const sign = match[1] === '+' ? 1 : -1;
            const hours = parseInt(match[2]);
            const minutes = match[3] ? parseInt(match[3]) : 0;
            return sign * (hours * 60 + minutes);
        };

        const offsetA = getOffsetValue(a.label);
        const offsetB = getOffsetValue(b.label);

        if (offsetA !== offsetB) return offsetA - offsetB;
        return a.value.localeCompare(b.value);
    });
};
