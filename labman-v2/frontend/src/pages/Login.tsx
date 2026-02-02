import { createSignal, Show } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { authService } from '../services/auth';
import { useAuth } from '../stores/auth';
import '../styles/auth.css';

export default function Login() {
    const [email, setEmail] = createSignal('');
    const [password, setPassword] = createSignal('');
    const [error, setError] = createSignal('');
    const [loading, setLoading] = createSignal(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: Event) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const token = await authService.login({
                email: email(),
                password: password(),
            });
            await login(token.access_token);
            navigate('/dashboard');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div class="auth-container">
            <div class="auth-card">
                <h1>LabMan</h1>
                <h2>Lab Management System</h2>

                <form onSubmit={handleSubmit} class="auth-form">
                    <Show when={error()}>
                        <div class="alert alert-error">{error()}</div>
                    </Show>

                    <div class="form-group">
                        <label for="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            value={email()}
                            onInput={(e) => setEmail(e.currentTarget.value)}
                            required
                            placeholder="your@email.com"
                        />
                    </div>

                    <div class="form-group">
                        <label for="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password()}
                            onInput={(e) => setPassword(e.currentTarget.value)}
                            required
                            placeholder="••••••••"
                        />
                    </div>

                    <button type="submit" class="btn btn-primary" disabled={loading()}>
                        {loading() ? 'Logging in...' : 'Login'}
                    </button>

                    <div class="auth-links">
                        <a href="/forgot-password">Forgot password?</a>
                    </div>
                </form>
            </div>
        </div>
    );
}
