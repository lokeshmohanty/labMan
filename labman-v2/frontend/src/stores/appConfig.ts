import { createSignal } from 'solid-js';

export const [appConfig, setAppConfig] = createSignal({
    labName: 'Lab Manager',
    timezone: 'Asia/Kolkata' // Default
});

export const updateAppConfig = (config: Partial<ReturnType<typeof appConfig>>) => {
    setAppConfig(prev => ({ ...prev, ...config }));
};
