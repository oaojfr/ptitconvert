PtitConvert Electron
====================

Development
- Ensure Python backend deps are installed in your environment (see project README)
- Start UI: npm install && npm start
- Env var PTITCONVERT_PYTHON can point to your venv Python

Build installers (cross-platform from each OS)
- macOS: npm run build:mac → dist/PtitConvert-*.dmg
- Windows: npm run build:win → dist/PtitConvert Setup *.exe
- Linux: npm run build:linux → dist/PtitConvert-*.AppImage

Packaging the backend
- Place platform-specific backend binaries under ../bin/{macos|win|linux}/
- electron-builder copies them into the app resources
- In dev, Electron spawns backend/server.py using system/venv Python
