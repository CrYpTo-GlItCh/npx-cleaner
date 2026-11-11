```text
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                           ║
║  ███╗   ██╗██████╗ ██╗  ██╗      ██████╗██╗     ███████╗ █████╗ ███╗   ██╗███████╗██████╗ ║
║  ████╗  ██║██╔══██╗╚██╗██╔╝     ██╔════╝██║     ██╔════╝██╔══██╗████╗  ██║██╔════╝██╔══██╗║
║  ██╔██╗ ██║██████╔╝ ╚███╔╝█████╗██║     ██║     █████╗  ███████║██╔██╗ ██║█████╗  ██████╔╝║
║  ██║╚██╗██║██╔═══╝  ██╔██╗╚════╝██║     ██║     ██╔══╝  ██╔══██║██║╚██╗██║██╔══╝  ██╔══██╗║
║  ██║ ╚████║██║     ██╔╝ ██╗     ╚██████╗███████╗███████╗██║  ██║██║ ╚████║███████╗██║  ██║║
║  ╚═╝  ╚═══╝╚═╝     ╚═╝  ╚═╝      ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝║
║                                                                                           ║
║             [ NUPIXEL // NEXT-GEN FIVEM CACHE PURGE & OPTIMIZER // CICADA ]               ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
```

<div align="center">

### `SYS.ARCHITECT: CICADA` &nbsp;//&nbsp; `BUILD: LEGACY + ENHANCED (GEN9)`

| 💠 `PLATFORM` | 🐍 `RUNTIME` | 🎨 `THEME` | 📜 `LICENSE` |
| :---: | :---: | :---: | :---: |
| **Windows 10 / 11** | **Python 3.11+** | **[NuPixel Cyberpunk](https://nupixel.xyz)** | **[MIT License](./LICENSE)** |

*A high-contrast, neon-infused Windows utility engineered to purge corrupted FiveM caches, terminate locked client threads, and boost frame stability across both **FiveM Legacy** and **FiveM Enhanced (Gen9)**.*

</div>

---

## ⚡ SYSTEM CAPABILITIES

| MODULE | PROTOCOL | DESCRIPTION |
| :--- | :--- | :--- |
| **`[DUAL_CORE_ENGINE]`** | **Legacy + Gen9** | Dedicated tabs to manage and purge **FiveM (Legacy)** and **FiveM Enhanced (Gen9)** independently or simultaneously. |
| **`[PATH_OVERRIDE]`** | **Custom Drive Ready** | Auto-probes `AppData` or lets you type/browse custom installation folders, saving overrides to `npx_cleaner_config.json`. |
| **`[THREAD_WATCHDOG]`** | **Anti-Lock Guard** | Actively scans for `FiveM.exe`, `FiveM_Enhanced.exe`, `GTA5.exe`, `GTA5_Enhanced.exe`, and `CitizenFX.exe` with one-click termination. |
| **`[SAFE_RECYCLE]`** | **100% Reversible** | Routes purged directories directly to the Windows Recycle Bin via `send2trash`—zero permanent data loss. |
| **`[MATRIX_TERMINAL]`** | **Live Telemetry** | Real-time monospace diagnostics calculating file counts, MB payload sizes, and live purge execution logs. |

---

## 🎯 TARGET PURGE NODES

```text
> PROBE_TARGETS // SELECTABLE CACHE PARTITIONS
  ├── [✓] cache               :: Core client streaming & temporary shaders
  ├── [✓] server-cache        :: Downloaded server scripts & map assets
  ├── [✓] server-cache-priv   :: Encrypted server resource caches
  ├── [✓] nui-storage         :: Chromium NUI browser cache & stuck HUDs
  ├── [ ] logs / crashes      :: Client crash dumps & diagnostic logs
  └── [ ] DigitalEntitlements :: Shared CitizenFX auth node (Forces Rockstar re-login)
```

---

## 📥 QUICK DEPLOY (STANDALONE `.EXE`)

No Python installation required. Grab the pre-compiled Windows binary straight from the automated build pipeline:

1. Navigate to the **[Actions](../../actions)** tab (or **[Releases](../../releases)**) at the top of this repository.
2. Click the latest green **`Build npx-cleaner Executable`** workflow run.
3. Scroll down to **Artifacts** and download **`npx-cleaner-windows.zip`**.
4. Extract **`npx-cleaner.exe`** and launch.

---

## 💻 RUN FROM SOURCE

```bash
# 1. Clone the repository
git clone https://github.com
cd npx-cleaner

# 2. Install dependencies
pip install -r requirements.txt

# 3. Boot the NuPixel Cyberpunk UI
python npx_cleaner.py
```

---

## 🛠️ COMPILE STANDALONE BINARY

To package **`npx-cleaner`** into a single, console-free Windows executable locally:

```bash
pyinstaller --onefile --noconsole --name="npx-cleaner" npx_cleaner.py
```

Your compiled binary will be generated at **`dist/npx-cleaner.exe`**.

---

<div align="center">

**ENGINEERED BY `CICADA` FOR THE `NUPIXEL` COMMUNITY**  
*Licensed under the MIT License*

</div>
