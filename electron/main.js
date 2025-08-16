const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = process.env.ELECTRON_START_URL || !app.isPackaged;

let pyProc = null;

function startBackend() {
  const cwd = path.resolve(__dirname, '..');
  const env = Object.assign({}, process.env, { PTITCONVERT_PORT: '8787' });

  if (!isDev) {
    // Try packaged backend binary
    let binPath;
    if (process.platform === 'darwin') {
      binPath = path.join(process.resourcesPath, 'backend', 'macos', 'backend');
    } else if (process.platform === 'win32') {
      binPath = path.join(process.resourcesPath, 'backend', 'win', 'backend.exe');
    } else {
      binPath = path.join(process.resourcesPath, 'backend', 'linux', 'backend');
    }
    pyProc = spawn(binPath, [], { env });
  } else {
    // Dev: spawn python script
    let pythonCmd = process.env.PTITCONVERT_PYTHON;
    if (!pythonCmd) {
      const venvPosix = path.join(cwd, '.venv', 'bin', 'python');
      const venvWin = path.join(cwd, '.venv', 'Scripts', 'python.exe');
      try {
        const fs = require('fs');
        if (process.platform === 'win32' && fs.existsSync(venvWin)) pythonCmd = venvWin;
        else if (fs.existsSync(venvPosix)) pythonCmd = venvPosix;
      } catch (_) {}
    }
    if (!pythonCmd) pythonCmd = (process.platform === 'win32' ? 'python' : 'python3');
    const args = [path.join('backend', 'server.py')];
    pyProc = spawn(pythonCmd, args, { cwd, env });
  }

  pyProc.stdout.on('data', (data) => {
    console.log(`[backend] ${data}`.toString());
  });
  pyProc.stderr.on('data', (data) => {
    console.error(`[backend] ${data}`.toString());
  });
  pyProc.on('exit', (code) => {
    console.log(`[backend] exited with code ${code}`);
  });
}

function stopBackend() {
  if (pyProc) {
    try { pyProc.kill(); } catch (e) {}
    pyProc = null;
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 720,
    minWidth: 900,
    minHeight: 600,
    title: 'PtitConvert',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  });

  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  stopBackend();
});

// IPC for dialogs
ipcMain.handle('pickFiles', async (event) => {
  const res = await dialog.showOpenDialog({
    properties: ['openFile', 'multiSelections']
  });
  return res.canceled ? [] : res.filePaths;
});

ipcMain.handle('pickFolder', async (event) => {
  const res = await dialog.showOpenDialog({
    properties: ['openDirectory']
  });
  return res.canceled ? '' : res.filePaths[0];
});
