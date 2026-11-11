# 🛠️ Open Source FiveM Cache Fixer & Cleaner

A lightweight, automated Windows utility designed to clean up FiveM cache directories, terminate conflicting processes, and fix common client issues safely without deleting core data.

## ✨ Features
* **Process Watchdog:** Automatically monitors and stops background instances of GTA V and FiveM to avoid file write locks.
* **Component Selection:** Choose exactly what to clear (Main Cache, Server Assets, NUI Browser Storage, or DigitalEntitlements).
* **Safe Recycling:** Deletes files using the Windows Recycle Bin (`send2trash`), making all operations 100% reversible.
* **Real-time Diagnostics:** Instantly calculates folder sizes and shows a live activity log.

## 🚀 How to Run from Source

1. Clone the repository:
   ```bash
   git clone https://github.com
   cd FiveM-Cache-Fixer
   ```
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python fivem_cleaner.py
   ```

## 📦 How to Build the Standalone `.exe`
To compile the script into a single executable file that your player base can use without needing Python installed, run:
```bash
pyinstaller --onefile --noconsole fivem_cleaner.py
```
The standalone executable will be generated inside the `/dist` directory.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
