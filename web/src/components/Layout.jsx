import React, { useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import Icon from './Icon';

/**
 * Layout component following UI_PORTAL.md Section 4:
 * - Phone (<768px): Top bar with bolt logo, title, PORTAL badge, truncated username;
 *   Fixed glass bottom tab bar with safe-area-inset-bottom.
 * - Desktop (>=768px): Floating glass pill navbar centered at top (max 960px).
 *   Active link has --accent-soft background and --text color. No bottom tab bar.
 */
export default function Layout({ children, user }) {
  useEffect(() => {
    if (user?.language) {
      document.documentElement.lang = user.language;
    }
  }, [user?.language]);

  const firstName = user?.name ? user.name.split(' ')[0] : 'Student';

  return (
    <div className="portal-app-wrapper">
      {/* Desktop Floating Glass Pill Navbar */}
      <header className="portal-desktop-nav-container">
        <nav className="portal-pill-navbar" aria-label="Desktop Navigation">
          <Link to="/dashboard" className="portal-brand">
            <span className="brand-icon-wrap" aria-hidden="true">
              <Icon name="bolt" size={16} />
            </span>
            <span className="brand-text">SnapStudy AI</span>
            <span className="brand-portal-badge">PORTAL</span>
          </Link>

          <div className="pill-nav-links">
            <NavLink
              to="/dashboard"
              className={({ isActive }) => `pill-nav-item ${isActive ? 'active' : ''}`}
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/notes"
              className={({ isActive }) => `pill-nav-item ${isActive ? 'active' : ''}`}
            >
              Notes
            </NavLink>
            <NavLink
              to="/weak"
              className={({ isActive }) => `pill-nav-item ${isActive ? 'active' : ''}`}
            >
              Weak Topics
            </NavLink>
            <NavLink
              to="/mistakes"
              className={({ isActive }) => `pill-nav-item ${isActive ? 'active' : ''}`}
            >
              Mistakes
            </NavLink>
            <NavLink
              to="/history"
              className={({ isActive }) => `pill-nav-item ${isActive ? 'active' : ''}`}
            >
              History
            </NavLink>
            <NavLink
              to="/leaderboard"
              className={({ isActive }) => `pill-nav-item ${isActive ? 'active' : ''}`}
            >
              League
            </NavLink>
            <NavLink
              to="/settings"
              className={({ isActive }) => `pill-nav-item ${isActive ? 'active' : ''}`}
            >
              Settings
            </NavLink>
          </div>

          <div className="pill-user-slot" title={user?.name || ''}>
            <span className="pill-user-dot" aria-hidden="true" />
            <span className="pill-user-name">{firstName}</span>
          </div>
        </nav>
      </header>

      {/* Mobile Top Bar */}
      <header className="portal-mobile-topbar">
        <Link to="/dashboard" className="portal-brand">
          <span className="brand-icon-wrap" aria-hidden="true">
            <Icon name="bolt" size={16} />
          </span>
          <span className="brand-text">SnapStudy AI</span>
          <span className="brand-portal-badge">PORTAL</span>
        </Link>
        <div className="mobile-user-name" title={user?.name || ''}>
          {firstName}
        </div>
      </header>

      {/* Main Page Body */}
      <main className="portal-main-container">
        {children}
      </main>

      {/* Mobile Bottom Tab Bar (Fixed, Glass, env(safe-area-inset-bottom)) */}
      <nav className="portal-mobile-bottom-bar" aria-label="Mobile Navigation">
        <NavLink
          to="/dashboard"
          className={({ isActive }) => `bottom-tab-link ${isActive ? 'active' : ''}`}
        >
          <Icon name="home" size={19} />
          <span>Home</span>
        </NavLink>
        <NavLink
          to="/notes"
          className={({ isActive }) => `bottom-tab-link ${isActive ? 'active' : ''}`}
        >
          <Icon name="notes" size={19} />
          <span>Notes</span>
        </NavLink>
        <NavLink
          to="/weak"
          className={({ isActive }) => `bottom-tab-link ${isActive ? 'active' : ''}`}
        >
          <Icon name="target" size={19} />
          <span>Weak</span>
        </NavLink>
        <NavLink
          to="/leaderboard"
          className={({ isActive }) => `bottom-tab-link ${isActive ? 'active' : ''}`}
        >
          <Icon name="trophy" size={19} />
          <span>League</span>
        </NavLink>
        <NavLink
          to="/settings"
          className={({ isActive }) => `bottom-tab-link ${isActive ? 'active' : ''}`}
        >
          <Icon name="settings" size={19} />
          <span>Settings</span>
        </NavLink>
      </nav>
    </div>
  );
}
