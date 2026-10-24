/**
 * Formatting helpers for dates and titles in SnapStudy Portal (feature P3b).
 * Solves "Invalid Date" and "Study Note #N" issues per UI_PORTAL.md Section 6.
 */

export function parseDbDate(value) {
  if (!value) return null;
  const iso = String(value).includes("T") ? String(value) : String(value).replace(" ", "T");
  const d = new Date(/[zZ]|[+-]\d{2}:?\d{2}$/.test(iso) ? iso : iso + "Z");
  return Number.isNaN(d.getTime()) ? null : d;
}

export function timeAgo(value, locale = navigator.language) {
  const d = parseDbDate(value);
  if (!d) return "—";
  const diff = (d.getTime() - Date.now()) / 1000;
  const units = [
    ["day", 86400],
    ["hour", 3600],
    ["minute", 60],
  ];
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: "auto" });
  for (const [unit, secs] of units) {
    if (Math.abs(diff) >= secs) return rtf.format(Math.round(diff / secs), unit);
  }
  return rtf.format(0, "minute");
}

export function fullDate(value, locale = navigator.language) {
  const d = parseDbDate(value);
  return d ? d.toLocaleString(locale, { dateStyle: "medium", timeStyle: "short" }) : "—";
}

export function noteTitle(note) {
  if (!note) return "Untitled note";
  if (note.title && note.title.trim()) return note.title.trim();
  if (note.summary_text) {
    const lines = note.summary_text.split("\n").map((l) => l.trim()).filter(Boolean);
    for (const line of lines) {
      const cleaned = line.replace(/^[\p{Emoji}\s#*-]+(Summary|সারসংক্ষেপ)?[:\s-]*/iu, "").trim();
      if (cleaned) {
        return cleaned.length > 60 ? cleaned.slice(0, 57) + "…" : cleaned;
      }
    }
  }
  return "Untitled note";
}
