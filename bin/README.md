This folder is used by electron-builder to bundle the backend runtime.

Production strategy options:
1) Embed a prebuilt Python binary + virtual env with the backend server.
2) Embed a small launcher that uses the system Python to run backend/server.py with vendored wheels.

For a quick start during development builds, the Electron app will try to spawn the backend using:
- process.env.PTITCONVERT_PYTHON if set
- otherwise: python3 (macOS/Linux) or python (Windows)

For production, place platform-specific backend bundles:
- macOS: bin/macos/backend
- Windows: bin/win/backend.exe
- Linux:  bin/linux/backend

Electron will prefer these if present.
