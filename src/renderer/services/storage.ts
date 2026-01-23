import { HistoryEntry, CompanyResearch, GeneratedEmail } from '../types';

const HISTORY_KEY = 'history';

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export async function getHistory(): Promise<HistoryEntry[]> {
  if (window.electronAPI) {
    const history = await window.electronAPI.store.get(HISTORY_KEY);
    return history || [];
  }
  // Fallback to localStorage for development
  const stored = localStorage.getItem(HISTORY_KEY);
  return stored ? JSON.parse(stored) : [];
}

export async function saveToHistory(
  companyName: string,
  websiteUrl: string,
  research: CompanyResearch,
  emails: Record<string, GeneratedEmail>,
  pdfPath: string | null
): Promise<HistoryEntry> {
  const entry: HistoryEntry = {
    id: generateId(),
    companyName,
    websiteUrl,
    research,
    emails,
    pdfPath,
    createdAt: new Date().toISOString(),
  };

  const history = await getHistory();
  history.unshift(entry);

  if (window.electronAPI) {
    await window.electronAPI.store.set(HISTORY_KEY, history);
  } else {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  }

  return entry;
}

export async function deleteFromHistory(id: string): Promise<void> {
  const history = await getHistory();
  const entry = history.find(h => h.id === id);

  // Delete associated PDF if exists
  if (entry?.pdfPath && window.electronAPI) {
    await window.electronAPI.pdf.delete(entry.pdfPath);
  }

  const filtered = history.filter(h => h.id !== id);

  if (window.electronAPI) {
    await window.electronAPI.store.set(HISTORY_KEY, filtered);
  } else {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered));
  }
}

export async function clearHistory(): Promise<void> {
  const history = await getHistory();

  // Delete all associated PDFs
  if (window.electronAPI) {
    for (const entry of history) {
      if (entry.pdfPath) {
        await window.electronAPI.pdf.delete(entry.pdfPath);
      }
    }
    await window.electronAPI.store.set(HISTORY_KEY, []);
  } else {
    localStorage.setItem(HISTORY_KEY, JSON.stringify([]));
  }
}

export async function getHistoryEntry(id: string): Promise<HistoryEntry | null> {
  const history = await getHistory();
  return history.find(h => h.id === id) || null;
}

export async function updateHistoryEntry(
  id: string,
  updates: Partial<HistoryEntry>
): Promise<void> {
  const history = await getHistory();
  const index = history.findIndex(h => h.id === id);

  if (index !== -1) {
    history[index] = { ...history[index], ...updates };

    if (window.electronAPI) {
      await window.electronAPI.store.set(HISTORY_KEY, history);
    } else {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    }
  }
}
