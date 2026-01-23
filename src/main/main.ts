import { app, BrowserWindow, ipcMain, shell } from 'electron';
import * as path from 'path';
import * as fs from 'fs';

// Use dynamic import for electron-store (ES Module)
let Store: any;

const isDev = !app.isPackaged;

let mainWindow: BrowserWindow | null = null;
let store: any = null;

async function initStore() {
  const StoreModule = await import('electron-store');
  Store = StoreModule.default;
  store = new Store({
    name: 'eai-dealflow-data',
    defaults: {
      history: [],
      userSettings: {
        userName: '',
        defaultTone: 'formal',
        companyName: 'EAI Capital',
        aiProvider: 'openrouter',
        apiKey: '',
      },
    },
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1100,
    minHeight: 700,
    backgroundColor: '#0E1117',
    titleBarStyle: 'hiddenInset',
    trafficLightPosition: { x: 20, y: 20 },
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    show: false,
  });

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Failed to load:', errorCode, errorDescription);
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    const indexPath = path.join(__dirname, '../renderer/index.html');
    console.log('Loading production file:', indexPath);
    mainWindow.loadFile(indexPath).catch(err => {
      console.error('Failed to load index.html:', err);
    });
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  await initStore();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// IPC Handlers for storage
ipcMain.handle('store:get', (_, key: string) => {
  if (!store) return null;
  return store.get(key);
});

ipcMain.handle('store:set', (_, key: string, value: any) => {
  if (!store) return false;
  store.set(key, value);
  return true;
});

ipcMain.handle('store:delete', (_, key: string) => {
  if (!store) return false;
  store.delete(key);
  return true;
});

// Get app data path for PDF storage
ipcMain.handle('app:getDataPath', () => {
  const dataPath = path.join(app.getPath('userData'), 'reports');
  if (!fs.existsSync(dataPath)) {
    fs.mkdirSync(dataPath, { recursive: true });
  }
  return dataPath;
});

// Save PDF to disk
ipcMain.handle('pdf:save', async (_, filename: string, data: string) => {
  const dataPath = path.join(app.getPath('userData'), 'reports');
  if (!fs.existsSync(dataPath)) {
    fs.mkdirSync(dataPath, { recursive: true });
  }
  const filePath = path.join(dataPath, filename);
  const buffer = Buffer.from(data, 'base64');
  fs.writeFileSync(filePath, buffer);
  return filePath;
});

// Read PDF from disk
ipcMain.handle('pdf:read', async (_, filePath: string) => {
  if (fs.existsSync(filePath)) {
    const buffer = fs.readFileSync(filePath);
    return buffer.toString('base64');
  }
  return null;
});

// Open PDF in default viewer
ipcMain.handle('pdf:open', async (_, filePath: string) => {
  if (fs.existsSync(filePath)) {
    shell.openPath(filePath);
    return true;
  }
  return false;
});

// Delete PDF from disk
ipcMain.handle('pdf:delete', async (_, filePath: string) => {
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
    return true;
  }
  return false;
});

// AI API call handler - runs in main process to avoid CORS issues
ipcMain.handle('ai:call', async (_, config: { provider: string; apiKey: string; prompt: string }) => {
  const { provider, apiKey, prompt } = config;

  const API_ENDPOINTS: Record<string, string> = {
    openrouter: 'https://openrouter.ai/api/v1/chat/completions',
    openai: 'https://api.openai.com/v1/chat/completions',
    anthropic: 'https://api.anthropic.com/v1/messages',
    gemini: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent',
  };

  const DEFAULT_MODELS: Record<string, string> = {
    openrouter: 'google/gemini-2.0-flash-001',
    openai: 'gpt-4o',
    anthropic: 'claude-3-5-sonnet-20241022',
    gemini: 'gemini-1.5-flash',
  };

  try {
    let response: Response;
    let result: string;

    if (provider === 'openrouter') {
      response = await fetch(API_ENDPOINTS.openrouter, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'https://eai-dealflow.app',
          'X-Title': 'EAI DealFlow',
        },
        body: JSON.stringify({
          model: DEFAULT_MODELS.openrouter,
          messages: [{ role: 'user', content: prompt }],
          temperature: 0.7,
          max_tokens: 4096,
        }),
      });
      if (!response.ok) {
        const errorData: any = await response.json().catch(() => ({}));
        throw new Error(errorData?.error?.message || `OpenRouter API error: ${response.status}`);
      }
      const data: any = await response.json();
      result = data.choices[0]?.message?.content || '';
    } else if (provider === 'openai') {
      response = await fetch(API_ENDPOINTS.openai, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: DEFAULT_MODELS.openai,
          messages: [{ role: 'user', content: prompt }],
          temperature: 0.7,
          max_tokens: 4096,
        }),
      });
      if (!response.ok) {
        const errorData: any = await response.json().catch(() => ({}));
        throw new Error(errorData?.error?.message || `OpenAI API error: ${response.status}`);
      }
      const data: any = await response.json();
      result = data.choices[0]?.message?.content || '';
    } else if (provider === 'anthropic') {
      response = await fetch(API_ENDPOINTS.anthropic, {
        method: 'POST',
        headers: {
          'x-api-key': apiKey,
          'Content-Type': 'application/json',
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify({
          model: DEFAULT_MODELS.anthropic,
          max_tokens: 4096,
          messages: [{ role: 'user', content: prompt }],
        }),
      });
      if (!response.ok) {
        const errorData: any = await response.json().catch(() => ({}));
        throw new Error(errorData?.error?.message || `Anthropic API error: ${response.status}`);
      }
      const data: any = await response.json();
      result = data.content[0]?.text || '';
    } else if (provider === 'gemini') {
      const url = `${API_ENDPOINTS.gemini}?key=${apiKey}`;
      response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 4096,
          },
        }),
      });
      if (!response.ok) {
        const errorData: any = await response.json().catch(() => ({}));
        throw new Error(errorData?.error?.message || `Gemini API error: ${response.status}`);
      }
      const data: any = await response.json();
      result = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
    } else {
      throw new Error(`Unknown provider: ${provider}`);
    }

    return { success: true, data: result };
  } catch (error: any) {
    return { success: false, error: error.message || 'Unknown error' };
  }
});
