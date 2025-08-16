const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('ptitconvert', {
  pickFiles: () => ipcRenderer.invoke('pickFiles'),
  pickFolder: () => ipcRenderer.invoke('pickFolder')
});
