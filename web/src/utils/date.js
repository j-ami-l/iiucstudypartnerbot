/**
 * Safe date formatting helper for SnapStudy Portal.
 * Handles ISO strings with or without trailing Z, SQLite timestamps, and invalid fallbacks.
 */
export function formatLocalDate(dateStr, options = { month: 'short', day: 'numeric', year: 'numeric' }) {
  if (!dateStr) return 'Recent';
  try {
    let clean = dateStr.trim();
    if (!clean.endsWith('Z') && !clean.includes('+')) {
      clean = clean.replace(' ', 'T') + 'Z';
    }
    const d = new Date(clean);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString(undefined, options);
  } catch {
    return dateStr;
  }
}

export function formatLocalDateTime(dateStr) {
  if (!dateStr) return '';
  try {
    let clean = dateStr.trim();
    if (!clean.endsWith('Z') && !clean.includes('+')) {
      clean = clean.replace(' ', 'T') + 'Z';
    }
    const d = new Date(clean);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  } catch {
    return dateStr;
  }
}
