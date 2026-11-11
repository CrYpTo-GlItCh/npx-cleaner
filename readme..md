# 🛠️ npx-cleaner

An open-source, automated Windows utility designed to safely clean **FiveM (Legacy)** and **FiveM Enhanced (Gen9)** cache directories, terminate conflicting processes, and resolve client stability issues without deleting core game files.

**Author:** CICADA

---

## ✨ Key Features

* **Dual Build Support:** Dedicated tabs to manage and clean **FiveM (Legacy)** and **FiveM Enhanced (Gen9)** installations independently or simultaneously.
* **Custom Path Configuration:** Auto-detects standard `AppData` directories and includes manual path entry, a **Browse** picker, and persistent saving (`npx_cleaner_config.json`) for custom drive installations.
* **Process Environment Watchdog:** Continuously monitors background tasks for `FiveM.exe`, `FiveM_Enhanced.exe`, `GTA5.exe`, `GTA5_Enhanced.exe`, and `CitizenFX.exe` to prevent file lock errors, with one-click process termination.
* **Granular Component Selection:** Toggle specific folders per build (`cache`, `server-cache`, `server-cache-priv`, `nui-storage`, and `logs`/`crashes`), plus a shared toggle for `DigitalEntitlements`.
* **100% Reversible Safe Recycling:** Routes all deleted folders to the Windows Recycle Bin via `send2trash` so data can be restored anytime.
* **Real-Time Diagnostics:** Displays live file counts, megabyte totals across profiles, directory validation status, and a built-in console log.

---

## 📥 Download (Pre-Built Executable)

If you do not have Python installed, you can download the compiled Windows executable directly from GitHub:
1. Open the **Actions** tab (or **Releases**) in this repository.
2. Select the latest successful **Build npx-cleaner Executable** run.
3. Download **`npx-cleaner-windows.zip`**, extract it, and run **`npx-cleaner.exe`**.

---

## 🚀 Running from Source

1. Clone the repository:
   ```bash
   git clone https://github.com
   cd npx-cleaner
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```bash
   python npx_cleaner.py
   ```

---

## 📦 Building the Standalone Executable

To compile `npx_cleaner.py` into a single standalone `.exe` locally:

```bash
pyinstaller --onefile --noconsole --name="npx-cleaner" npx_cleaner.py
```

The compiled executable will be placed inside the **`dist/`** folder as `npx-cleaner.exe`.

---

## 📄 License

This project is open-source and licensed under the **MIT License**.
