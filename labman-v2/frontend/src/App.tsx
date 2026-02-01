import { Router, Route, Navigate } from '@solidjs/router';
import { Show } from 'solid-js';
import { AuthProvider, useAuth } from './stores/auth';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Groups from './pages/Groups';
import GroupDetail from './pages/GroupDetail';
import GroupProject from './pages/GroupProject';
import Meetings from './pages/Meetings';
import Inventory from './pages/Inventory';
import MyResearch from './pages/MyResearch';
import UserResearch from './pages/UserResearch';
import MeetingDetail from './pages/MeetingDetail';
import Admin from './pages/Admin';
import Account from './pages/Account';
import ActivityHistory from './pages/ActivityHistory';

function ProtectedRoute(props: any) {
    const { isAuthenticated, loading } = useAuth();

    return (
        <Show when={!loading()} fallback={<div>Loading...</div>}>
            <Show when={isAuthenticated()} fallback={<Navigate href="/login" />}>
                <Layout>{props.children}</Layout>
            </Show>
        </Show>
    );
}

export default function App() {
    return (
        <AuthProvider>
            <Router>
                <Route path="/login" component={Login} />
                <Route path="/dashboard" component={() => <ProtectedRoute><Dashboard /></ProtectedRoute>} />
                <Route path="/groups" component={() => <ProtectedRoute><Groups /></ProtectedRoute>} />
                <Route path="/groups/:id" component={() => <ProtectedRoute><GroupDetail /></ProtectedRoute>} />
                <Route path="/groups/:id/project" component={() => <ProtectedRoute><GroupProject /></ProtectedRoute>} />
                <Route path="/meetings" component={() => <ProtectedRoute><Meetings /></ProtectedRoute>} />
                <Route path="/meetings/:id" component={() => <ProtectedRoute><MeetingDetail /></ProtectedRoute>} />
                <Route path="/inventory" component={() => <ProtectedRoute><Inventory /></ProtectedRoute>} />
                <Route path="/my-research" component={() => <ProtectedRoute><MyResearch /></ProtectedRoute>} />
                <Route path="/research/:userId" component={() => <ProtectedRoute><UserResearch /></ProtectedRoute>} />
                <Route path="/admin" component={() => <ProtectedRoute><Admin /></ProtectedRoute>} />
                <Route path="/account" component={() => <ProtectedRoute><Account /></ProtectedRoute>} />
                <Route path="/activity" component={() => <ProtectedRoute><ActivityHistory /></ProtectedRoute>} />
                <Route path="/" component={() => <Navigate href="/dashboard" />} />
            </Router>
        </AuthProvider>
    );
}
