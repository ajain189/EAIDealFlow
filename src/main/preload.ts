import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  // Store operations
  store: {
    get: (key: string) => ipcRenderer.invoke('store:get', key),
    set: (key: string, value: any) => ipcRenderer.invoke('store:set', key, value),
    delete: (key: string) => ipcRenderer.invoke('store:delete', key),
  },
  // App operations
  app: {
    getDataPath: () => ipcRenderer.invoke('app:getDataPath'),
  },
  // PDF operations
  pdf: {
    save: (filename: string, data: string) => ipcRenderer.invoke('pdf:save', filename, data),
    read: (filePath: string) => ipcRenderer.invoke('pdf:read', filePath),
    open: (filePath: string) => ipcRenderer.invoke('pdf:open', filePath),
    delete: (filePath: string) => ipcRenderer.invoke('pdf:delete', filePath),
  },
  // AI operations
  ai: {
    call: (config: { provider: string; apiKey: string; prompt: string }) =>
      ipcRenderer.invoke('ai:call', config),
  },
});
