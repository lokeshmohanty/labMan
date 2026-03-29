import { createSignal, createContext, useContext, JSX, onMount } from 'solid-js';
import type { User } from '../types';
import { authService } from '../services/auth';

interface AuthContextType {
    user: () => User | null;
    isAuthenticated: () => boolean;
    isAdmin: () => boolean;
    login: (token: string) => Promise<void>;
    logout: () => void;
    loading: () => boolean;
}

const AuthContext = createContext<AuthContextType>();

export function AuthProvider(props: { children: JSX.Element }) {
    const [user, setUser] = createSignal<User | null>(null);
    const [loading, setLoading] = createSignal(true);

    const isAuthenticated = () => user() !== null;
    const isAdmin = () => user()?.is_admin ?? false;

    const login = async (token: string) => {
        localStorage.setItem('token', token);
        try {
            const userData = await authService.getCurrentUser();
            setUser(userData);
        } catch (error) {
            localStorage.removeItem('token');
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
        window.location.href = '/login';
    };

    onMount(async () => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const userData = await authService.getCurrentUser();
                setUser(userData);
            } catch (error) {
                localStorage.removeItem('token');
            }
        }
        setLoading(false);
    });

    return (
        <AuthContext.Provider value={{ user, isAuthenticated, isAdmin, login, logout, loading }}>
            {props.children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}
