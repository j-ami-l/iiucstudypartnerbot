import React from 'react';
import { NavLink, Link } from 'react-router-dom';

export default function Layout({ children, user }) {
  return (
    <div className="app-container">
      {/* Top Navbar */}
      <header className="navbar">
        <div className="nav-inner">
          <Link to="/dashboard" className="brand">
            <span style={{ fontSize: '1.4rem' }}>⚡</span>
            <span>SnapStudy AI</span>
            <span className="brand-badge">PORTAL</span>
          </Link>

          <nav className="nav-links">
            <NavLink
              to="/dashboard"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/notes"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              Notes
            </NavLink>
            <NavLink
              to="/settings"
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              Settings
            </NavLink>
            {user?.name && (
              <span
                style={{
                  fontSize: '0.82rem',
                  color: 'var(--text-secondary)',
                  marginLeft: '0.75rem',
                  paddingLeft: '0.75rem',
                  borderLeft: '1px solid var(--border-color)',
                }}
              >
                👤 {user.name}
              </span>
            )}
          </nav>
        </div>
      </header>

      {/* Main Page Content */}
      <main className="main-content">{children}</main>

      {/* Mobile Bottom Tab Bar */}
      <nav className="bottom-bar" aria-label="Mobile Navigation">
        <NavLink
          to="/dashboard"
          className={({ isActive }) => `bottom-tab ${isActive ? 'active' : ''}`}
        >
          <span style={{ fontSize: '1.2rem' }}>📊</span>
          <span>Dashboard</span>
        </NavLink>
        <NavLink
          to="/notes"
          className={({ isActive }) => `bottom-tab ${isActive ? 'active' : ''}`}
        >
          <span style={{ fontSize: '1.2rem' }}>📖</span>
          <span>Notes</span>
        </NavLink>
        <NavLink
          to="/settings"
          className={({ isActive }) => `bottom-tab ${isActive ? 'active' : ''}`}
        >
          <span style={{ fontSize: '1.2rem' }}>⚙️</span>
          <span>Settings</span>
        </NavLink>
      </nav>
    </div>
  );
}
