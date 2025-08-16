const { app, BrowserWindow, ipcMain, dialog, nativeImage } = require('electron');
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
  // Resolve an app icon for the window (Linux/Windows). On macOS the bundle icon is used.
  let windowIcon = undefined;
  try {
    // Prefer 512x512 PNG generated from SVG
    const iconPng = path.join(__dirname, 'assets', 'icon.png');
    if (require('fs').existsSync(iconPng)) {
      windowIcon = nativeImage.createFromPath(iconPng);
    }
  } catch (_) {}

  const win = new BrowserWindow({
    width: 1100,
    height: 720,
    minWidth: 900,
    minHeight: 600,
    title: 'PtitConvert',
    icon: process.platform === 'darwin' ? undefined : windowIcon, // macOS ignores this
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  });

  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

app.whenReady().then(() => {
  startBackend();

  // In dev on macOS, set the dock icon explicitly from PNG so it matches the bundle icon.
  try {
    if (process.platform === 'darwin' && isDev) {
      const dockPng = path.join(__dirname, 'assets', 'icon.png');
      if (require('fs').existsSync(dockPng)) {
        app.dock.setIcon(nativeImage.createFromPath(dockPng));
      }
    }
  } catch (_) {}

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
