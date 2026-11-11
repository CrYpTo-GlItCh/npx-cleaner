import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
from send2trash import send2trash

TARGET_PROCESSES = [
    "FiveM.exe",
    "FiveM_Enhanced.exe",
    "CitizenFX.exe",
    "GTA5.exe",
    "GTA5_Enhanced.exe"
]

CONFIG_FILE = "npx_cleaner_config.json"


class NPXCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("npx-cleaner | FiveM & Enhanced Optimizer")
        self.root.geometry("580x730")
        self.root.resizable(False, False)

        local_app = os.environ.get("LOCALAPPDATA", "")
        self.default_paths = {
            "legacy": self.detect_legacy_path(local_app),
            "enhanced": self.detect_enhanced_path(local_app)
        }

        self.custom_paths = self.load_config()
        self.targets = {"legacy": {}, "enhanced": {}}

        legacy_init = self.custom_paths.get("legacy") or self.default_paths["legacy"]
        enhanced_init = self.custom_paths.get("enhanced") or self.default_paths["enhanced"]

        self.path_vars = {
            "legacy": tk.StringVar(value=str(legacy_init)),
            "enhanced": tk.StringVar(value=str(enhanced_init))
        }
        self.path_status_lbls = {}

        self.setup_ui()
        self.scan_all_caches()
        self.check_running_processes()

    def detect_legacy_path(self, local_app):
        """Checks standard AppData paths for FiveM Legacy."""
        candidates = [
            os.path.join(local_app, "FiveM", "FiveM.app", "data"),
            os.path.join(local_app, "FiveM", "data")
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return candidates[0]

    def detect_enhanced_path(self, local_app):
        """Checks common AppData folder names used by FiveM Enhanced."""
        candidates = [
            os.path.join(local_app, "FiveM Enhanced", "FiveM.app", "data"),
            os.path.join(local_app, "FiveM_Enhanced", "FiveM.app", "data"),
            os.path.join(local_app, "FiveM", "FiveM Enhanced.app", "data"),
            os.path.join(local_app, "FiveM Enhanced", "data")
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return candidates[0]

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                return {}
        return {}

    def save_config(self):
        data = {
            "legacy": self.path_vars["legacy"].get().strip(),
            "enhanced": self.path_vars["enhanced"].get().strip()
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.log(f"Warning: Could not save path settings ({e})")

    def setup_ui(self):
        # Header Banner
        header = tk.Label(self.root, text="npx-cleaner", font=("Arial", 16, "bold"), fg="#1e90ff")
        header.pack(pady=(8, 0))

        author_lbl = tk.Label(
            self.root,
            text="Created by CICADA | Dual Legacy & Enhanced Edition",
            font=("Arial", 9, "italic"),
            fg="gray"
        )
        author_lbl.pack(pady=(0, 8))

        # Process Watchdog Frame
        self.proc_frame = tk.LabelFrame(self.root, text=" Process Environment Watchdog ", padx=10, pady=5)
        self.proc_frame.pack(fill="x", padx=15, pady=5)

        self.proc_status_lbl = tk.Label(
            self.proc_frame,
            text="Checking active tasks...",
            fg="orange",
            font=("Arial", 9, "bold")
        )
        self.proc_status_lbl.pack(anchor="w")

        self.kill_btn = ttk.Button(
            self.proc_frame,
            text="Force Close Running FiveM / GTA Processes",
            command=self.kill_processes
        )
        self.kill_btn.pack(fill="x", pady=5)

        # Notebook Tabs for Legacy vs Enhanced
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="x", padx=15, pady=8)

        self.tab_legacy = ttk.Frame(self.notebook)
        self.tab_enhanced = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_legacy, text="  FiveM (Legacy)  ")
        self.notebook.add(self.tab_enhanced, text="  FiveM Enhanced (Gen9)  ")

        self.build_client_tab(self.tab_legacy, "legacy")
        self.build_client_tab(self.tab_enhanced, "enhanced")

        # Shared Account / Entitlements Option
        self.shared_frame = tk.LabelFrame(
            self.root,
            text=" Shared Account Data (Applies to Both Builds) ",
            padx=10,
            pady=5
        )
        self.shared_frame.pack(fill="x", padx=15, pady=5)

        ent_row = tk.Frame(self.shared_frame)
        ent_row.pack(fill="x", pady=2)

        self.entitlement_var = tk.BooleanVar(value=False)
        self.entitlement_path = os.path.join(os.environ.get("APPDATA", ""), "CitizenFX", "ros_entitlements")

        chk = ttk.Checkbutton(
            ent_row,
            text="DigitalEntitlements (Forces Rockstar Re-login)",
            variable=self.entitlement_var,
            command=self.scan_all_caches
        )
        chk.pack(side="left")

        self.entitlement_lbl = tk.Label(ent_row, text="Calculating...", fg="gray", font=("Arial", 9))
        self.entitlement_lbl.pack(side="right")

        # Total Size Readout
        self.total_lbl = tk.Label(
            self.root,
            text="Total Selected Across All Profiles: 0.00 MB",
            font=("Arial", 11, "bold"),
            fg="#2ed573"
        )
        self.total_lbl.pack(pady=8)

        # Console Logger
        self.log_text = tk.Text(
            self.root,
            height=8,
            width=66,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#ffffff"
        )
        self.log_text.pack(padx=15, pady=5)
        self.log("npx-cleaner initialized. Edit paths manually or use Browse if auto-detect misses.")

        # Action Buttons Row
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=15, pady=12)

        self.rescan_btn = ttk.Button(btn_frame, text="Rescan Directories", command=self.scan_all_caches)
        self.rescan_btn.pack(side="left", ipadx=10, ipady=6)

        self.clean_btn = tk.Button(
            btn_frame,
            text="CLEAN SELECTED CACHES (SAFE RECYCLE)",
            bg="#ff4757",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.confirm_and_clean
        )
        self.clean_btn.pack(side="right", fill="x", expand=True, padx=(10, 0), ipady=5)

    def build_client_tab(self, parent, mode):
        # Custom Directory Bar
        dir_frame = tk.Frame(parent, pady=6, padx=8)
        dir_frame.pack(fill="x")

        tk.Label(dir_frame, text="Data Path:", font=("Arial", 8, "bold")).pack(side="left")

        entry = ttk.Entry(dir_frame, textvariable=self.path_vars[mode], font=("Arial", 8))
        entry.pack(side="left", fill="x", expand=True, padx=5)
        entry.bind("<Return>", lambda e, m=mode: self.apply_manual_path(m))
        entry.bind("<FocusOut>", lambda e, m=mode: self.apply_manual_path(m))

        browse_btn = ttk.Button(
            dir_frame,
            text="Browse...",
            width=8,
            command=lambda m=mode: self.browse_folder(m)
        )
        browse_btn.pack(side="left", padx=(0, 3))

        reset_btn = ttk.Button(
            dir_frame,
            text="Reset",
            width=6,
            command=lambda m=mode: self.reset_folder(m)
        )
        reset_btn.pack(side="right")

        # Directory Status Indicator
        status_bar = tk.Frame(parent, padx=10)
        status_bar.pack(fill="x")

        path_status = tk.Label(status_bar, text="Checking directory...", font=("Arial", 8), fg="gray")
        path_status.pack(anchor="w")
        self.path_status_lbls[mode] = path_status

        # Cache Folder Checkboxes
        list_frame = tk.Frame(parent, pady=4, padx=10)
        list_frame.pack(fill="x")

        folders = [
            ("cache", "Main Client Cache (cache)", True),
            ("server-cache", "Server Assets Cache (server-cache)", True),
            ("server-cache-priv", "Private Server Cache (server-cache-priv)", True),
            ("nui-storage", "NUI Browser & UI Storage (nui-storage)", True),
            ("logs", "Crash & Client Logs (logs / crashes)", False)
        ]

        for folder_key, label_text, default_checked in folders:
            row = tk.Frame(list_frame)
            row.pack(fill="x", pady=3)

            var = tk.BooleanVar(value=default_checked)
            chk = ttk.Checkbutton(row, text=label_text, variable=var, command=self.scan_all_caches)
            chk.pack(side="left")

            status_lbl = tk.Label(row, text="Scanning...", fg="gray", font=("Arial", 9))
            status_lbl.pack(side="right")

            self.targets[mode][folder_key] = {
                "var": var,
                "label": f"[{mode.upper()}] {label_text}",
                "status_lbl": status_lbl
            }

    def normalize_data_path(self, raw_path):
        """Normalizes user-selected or typed paths to point to the 'data' folder."""
        cleaned = os.path.normpath(raw_path.strip().strip('"'))
        if os.path.exists(os.path.join(cleaned, "FiveM.app", "data")):
            return os.path.join(cleaned, "FiveM.app", "data")
        if os.path.exists(os.path.join(cleaned, "data")):
            return os.path.join(cleaned, "data")
        return cleaned

    def apply_manual_path(self, mode):
        raw = self.path_vars[mode].get().strip()
        if not raw:
            return
        normalized = self.normalize_data_path(raw)
        if normalized != raw:
            self.path_vars[mode].set(normalized)
        self.save_config()
        self.scan_all_caches()

    def browse_folder(self, mode):
        selected = filedialog.askdirectory(title=f"Select FiveM {mode.capitalize()} Folder")
        if selected:
            normalized = self.normalize_data_path(selected)
            self.path_vars[mode].set(normalized)
            self.save_config()
            self.log(f"Updated {mode.capitalize()} path: {normalized}")
            self.scan_all_caches()

    def reset_folder(self, mode):
        default_dir = self.default_paths[mode]
        self.path_vars[mode].set(default_dir)
        self.save_config()
        self.log(f"Reset {mode.capitalize()} path to default: {default_dir}")
        self.scan_all_caches()

    def log(self, text):
        self.log_text.insert(tk.END, f">> {text}\n")
        self.log_text.see(tk.END)

    def get_dir_size(self, path):
        if not os.path.exists(path):
            return 0, 0
        total_size = 0
        file_count = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    try:
                        total_size += os.path.getsize(fp)
                        file_count += 1
                    except OSError:
                        pass
        return total_size, file_count

    def scan_all_caches(self):
        def worker():
            total_selected_bytes = 0

            for mode in ["legacy", "enhanced"]:
                base_data_dir = self.path_vars[mode].get().strip()
                parent_app_dir = os.path.dirname(base_data_dir)

                if os.path.exists(base_data_dir):
                    self.path_status_lbls[mode].config(
                        text="Directory Found: Ready to clean",
                        fg="#2ed573"
                    )
                else:
                    self.path_status_lbls[mode].config(
                        text="Directory Not Found: Type path above or click Browse...",
                        fg="#ff4757"
                    )

                for folder_key, info in self.targets[mode].items():
                    if folder_key == "logs":
                        target_paths = [
                            os.path.join(parent_app_dir, "logs"),
                            os.path.join(parent_app_dir, "crashes")
                        ]
                    else:
                        target_paths = [os.path.join(base_data_dir, folder_key)]

                    size_bytes = 0
                    files = 0
                    found_any = False

                    for p in target_paths:
                        if os.path.exists(p):
                            found_any = True
                            b, f = self.get_dir_size(p)
                            size_bytes += b
                            files += f

                    if found_any:
                        size_mb = size_bytes / (1024 * 1024)
                        info["status_lbl"].config(text=f"{files} files ({size_mb:.2f} MB)", fg="black")
                        if info["var"].get():
                            total_selected_bytes += size_bytes
                    else:
                        info["status_lbl"].config(text="Not Found / Empty", fg="gray")

            # Scan DigitalEntitlements
            if os.path.exists(self.entitlement_path):
                b, f = self.get_dir_size(self.entitlement_path)
                self.entitlement_lbl.config(text=f"{f} files ({b / (1024 * 1024):.2f} MB)", fg="black")
                if self.entitlement_var.get():
                    total_selected_bytes += b
            else:
                self.entitlement_lbl.config(text="Not Found / Empty", fg="gray")

            total_mb = total_selected_bytes / (1024 * 1024)
            self.total_lbl.config(text=f"Total Selected Across All Profiles: {total_mb:.2f} MB")

        threading.Thread(target=worker, daemon=True).start()

    def check_running_processes(self):
        active = []
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info.get('name')
                if name and (name in TARGET_PROCESSES or "FiveM" in name or "GTA5" in name):
                    if name.endswith(".exe"):
                        active.append(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if active:
            self.proc_status_lbl.config(text=f"CONFLICT DETECTED: {', '.join(set(active))}", fg="#ff4757")
            self.clean_btn.config(state="disabled")
        else:
            self.proc_status_lbl.config(text="Environment Safe: No active FiveM or GTA processes.", fg="#2ed573")
            self.clean_btn.config(state="normal")

        self.root.after(2000, self.check_running_processes)

    def kill_processes(self):
        killed = False
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                name = proc.info.get('name')
                if name and (name in TARGET_PROCESSES or "FiveM" in name or "GTA5" in name):
                    psutil.Process(proc.info['pid']).terminate()
                    self.log(f"Terminated: {name} (PID: {proc.info['pid']})")
                    killed = True
            except Exception:
                pass
        if killed:
            self.log("Background processes cleared.")
        else:
            self.log("No conflicting processes running.")

    def confirm_and_clean(self):
        if self.entitlement_var.get():
            ans = messagebox.askyesno(
                "Rockstar Re-login Required",
                "You selected DigitalEntitlements. Cleaning this will require you to log back into Rockstar Social Club.\n\nContinue?"
            )
            if not ans:
                return

        confirm = messagebox.askyesno(
            "Confirm Safe Clean",
            "All selected cache folders across Legacy and Enhanced profiles will be moved to your Windows Recycle Bin. Proceed?"
        )
        if confirm:
            self.execute_cleaning()

    def execute_cleaning(self):
        self.clean_btn.config(state="disabled")

        def worker():
            cleaned_count = 0
            for mode in ["legacy", "enhanced"]:
                base_data_dir = self.path_vars[mode].get().strip()
                parent_app_dir = os.path.dirname(base_data_dir)

                for folder_key, info in self.targets[mode].items():
                    if not info["var"].get():
                        continue

                    if folder_key == "logs":
                        target_paths = [
                            os.path.join(parent_app_dir, "logs"),
                            os.path.join(parent_app_dir, "crashes")
                        ]
                    else:
                        target_paths = [os.path.join(base_data_dir, folder_key)]

                    for path in target_paths:
                        if os.path.exists(path):
                            try:
                                self.log(f"Recycling {info['label']}...")
                                send2trash(path)
                                cleaned_count += 1
                            except Exception as e:
                                self.log(f"Error cleaning {path}: {e}")

            if self.entitlement_var.get() and os.path.exists(self.entitlement_path):
                try:
                    self.log("Recycling Shared DigitalEntitlements...")
                    send2trash(self.entitlement_path)
                    cleaned_count += 1
                except Exception as e:
                    self.log(f"Error cleaning DigitalEntitlements: {e}")

            self.log(f"Cleanup complete. {cleaned_count} target directories moved to Recycle Bin.")
            self.scan_all_caches()
            messagebox.showinfo(
                "npx-cleaner",
                f"Optimization complete! {cleaned_count} directories safely moved to the Recycle Bin."
            )

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = NPXCleanerApp(root)
    root.mainloop()
