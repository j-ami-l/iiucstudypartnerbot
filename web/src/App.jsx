import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { api } from './api';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Notes from './pages/Notes';
import NoteDetail from './pages/NoteDetail';
import Settings from './pages/Settings';

export default function App() {
  const [user, setUser] = useState(null);

  const fetchUser = useCallback(async () => {
    try {
      const data = await api.getMe();
      setUser(data);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Magic-link token exchange page */}
        <Route path="/login" element={<Login onLoginSuccess={fetchUser} />} />

        {/* Dashboard page */}
        <Route
          path="/dashboard"
          element={
            <Layout user={user}>
              <Dashboard user={user} />
            </Layout>
          }
        />

        {/* Notes list page */}
        <Route
          path="/notes"
          element={
            <Layout user={user}>
              <Notes user={user} />
            </Layout>
          }
        />

        {/* Note detail page */}
        <Route
          path="/notes/:id"
          element={
            <Layout user={user}>
              <NoteDetail user={user} />
            </Layout>
          }
        />

        {/* Account & Session Settings */}
        <Route
          path="/settings"
          element={
            <Layout user={user}>
              <Settings user={user} onLogout={() => setUser(null)} />
            </Layout>
          }
        />

        {/* Default route */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
