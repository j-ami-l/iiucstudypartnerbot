import React from 'react';

/**
 * ShinyButton: The one animated primary CTA with a slow rotating conic border highlight.
 * UI_PORTAL.md Section 4 & 5.1.
 * Renders an <a> (external or deep link) or a <button>.
 */
export default function ShinyButton({
  children,
  href,
  onClick,
  target,
  rel,
  className = '',
  icon,
  type = 'button',
}) {
  const content = (
    <span className="shiny-inner">
      {icon && <span className="shiny-icon">{icon}</span>}
      <span className="shiny-text">{children}</span>
    </span>
  );

  if (href) {
    return (
      <a
        href={href}
        target={target}
        rel={rel}
        className={`portal-shiny-btn ${className}`.trim()}
      >
        {content}
      </a>
    );
  }

  return (
    <button
      type={type}
      onClick={onClick}
      className={`portal-shiny-btn ${className}`.trim()}
    >
      {content}
    </button>
  );
}
