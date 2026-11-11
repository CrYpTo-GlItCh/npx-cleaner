import os
import json
import random
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

# NuPixel Cyberpunk Theme Palette
BG_DARK = "#07070c"
BG_PANEL = "#0e0e18"
BG_INPUT = "#151524"
NEON_CYAN = "#00f3ff"
NEON_CYAN_DIM = "#007a80"
NEON_PINK = "#ff007f"
NEON_PINK_DIM = "#800040"
MATRIX_GREEN = "#00ff41"
TEXT_LIGHT = "#e2e8f0"
TEXT_MUTED = "#64748b"

class NPXCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NPX-CLEANER // NUPIXEL CYBERPUNK OPTIMIZER")
        self.root.geometry("620x780")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)

        local_app = os.environ.get("LOCALAPPDATA") or os.path.expanduser(os.path.join("~", "AppData", "Local"))
        
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

        self.configure_styles()
        self.setup_ui()
        self.start_neon_flicker()
        self.scan_all_caches()
        self.check_running_processes()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Notebook & Tab Styling
        style.configure("TNotebook", background=BG_DARK, borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure("TNotebook.Tab", background=BG_PANEL, foreground=TEXT_MUTED, padding=[16, 8], font=("Consolas", 10, "bold"), borderwidth=1)
        style.map("TNotebook.Tab", 
            background=[("selected", BG_INPUT)], 
            foreground=[("selected", NEON_CYAN)], 
            expand=[("selected", [1, 1, 1, 0])]
        )

        style.configure("Dark.TFrame", background=BG_PANEL)
        style.configure("Cyber.TCheckbutton", background=BG_PANEL, foreground=TEXT_LIGHT, font=("Consolas", 9), indicatorcolor=BG_INPUT, indicatorrelief="flat")
        style.map("Cyber.TCheckbutton", 
            background=[("active", BG_PANEL)], 
            foreground=[("active", NEON_CYAN), ("selected", NEON_CYAN)], 
            indicatorcolor=[("selected", NEON_PINK), ("active", NEON_CYAN)]
        )

    def detect_legacy_path(self, local_app):
        """Checks standard AppData paths for FiveM Legacy."""
        candidates = [
            os.path.join(local_app, "FiveM", "FiveM.app", "data"),
            os.path.join(local_app, "FiveM", "data"),
            os.path.join(local_app, "FiveM")
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
            os.path.join(local_app, "FiveM Enhanced", "data"),
            os.path.join(local_app, "FiveM for GTAV Enhanced", "FiveM.app", "data")
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
            self.log(f"[WARN] Could not save path settings: {e}", tag="pink")

    def setup_ui(self):
        # Top Neon Banner Frame
        banner_frame = tk.Frame(self.root, bg=BG_PANEL, highlightbackground=NEON_CYAN, highlightthickness=1, pady=10)
        banner_frame.pack(fill="x", padx=16, pady=(14, 8))

        title_row = tk.Frame(banner_frame, bg=BG_PANEL)
        title_row.pack()

        self.neon_prefix = tk.Label(title_row, text="[ NUPIXEL // ", font=("Consolas", 16, "bold"), bg=BG_PANEL, fg=NEON_PINK)
        self.neon_prefix.pack(side="left")
        self.neon_title = tk.Label(title_row, text="NPX-CLEANER", font=("Consolas", 18, "bold"), bg=BG_PANEL, fg=NEON_CYAN)
        self.neon_title.pack(side="left")
        self.neon_suffix = tk.Label(title_row, text=" ]", font=("Consolas", 16, "bold"), bg=BG_PANEL, fg=NEON_PINK)
        self.neon_suffix.pack(side="left")

        self.sub_banner = tk.Label(banner_frame, text="SYS.ARCHITECT: CICADA  |  DUAL LEGACY & GEN9 CACHE PROTOCOL", font=("Consolas", 8, "bold"), bg=BG_PANEL, fg=TEXT_MUTED)
        self.sub_banner.pack(pady=(3, 0))

        # Process Watchdog Panel
        self.proc_frame = tk.Frame(self.root, bg=BG_PANEL, highlightbackground=NEON_PINK, highlightthickness=1, padx=12, pady=8)
        self.proc_frame.pack(fill="x", padx=16, pady=6)

        proc_header = tk.Label(self.proc_frame, text=">> PROCESS ENVIRONMENT WATCHDOG", font=("Consolas", 9, "bold"), bg=BG_PANEL, fg=NEON_PINK)
        proc_header.pack(anchor="w")

        self.proc_status_lbl = tk.Label(self.proc_frame, text="SCANNING ACTIVE PROCESSES...", fg=NEON_CYAN, bg=BG_PANEL, font=("Consolas", 9, "bold"))
        self.proc_status_lbl.pack(anchor="w", pady=(2, 6))

        self.kill_btn = tk.Button(self.proc_frame, text="[ TERMINATE RUNNING FIVEM / GTA PROCESSES ]", bg=BG_INPUT, fg=NEON_PINK, activebackground=NEON_PINK, activeforeground=BG_DARK, font=("Consolas", 9, "bold"), relief="flat", highlightbackground=NEON_PINK, highlightthickness=1, cursor="hand2", command=self.kill_processes)
        self.kill_btn.pack(fill="x", ipady=3)

        # Notebook Tabs for Legacy vs Enhanced
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="x", padx=16, pady=8)

        self.tab_legacy = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.tab_enhanced = ttk.Frame(self.notebook, style="Dark.TFrame")

        self.notebook.add(self.tab_legacy, text="  FIVEM // LEGACY  ")
        self.notebook.add(self.tab_enhanced, text="  FIVEM // ENHANCED (GEN9)  ")

        self.build_client_tab(self.tab_legacy, "legacy")
        self.build_client_tab(self.tab_enhanced, "enhanced")

        # Shared Account / Entitlements Panel
        self.shared_frame = tk.Frame(self.root, bg=BG_PANEL, highlightbackground=NEON_CYAN_DIM, highlightthickness=1, padx=12, pady=7)
        self.shared_frame.pack(fill="x", padx=16, pady=4)

        shared_hdr = tk.Label(self.shared_frame, text=">> SHARED CITIZENFX AUTHENTICATION NODE", font=("Consolas", 8, "bold"), bg=BG_PANEL, fg=NEON_CYAN)
        shared_hdr.pack(anchor="w", pady=(0, 3))

        ent_row = tk.Frame(self.shared_frame, bg=BG_PANEL)
        ent_row.pack(fill="x")

        self.entitlement_var = tk.BooleanVar(value=False)
        self.entitlement_path = os.path.join(os.environ.get("APPDATA", ""), "CitizenFX", "ros_entitlements")

        chk = ttk.Checkbutton(ent_row, text="DigitalEntitlements (Forces Rockstar Re-Auth)", variable=self.entitlement_var, style="Cyber.TCheckbutton", command=self.scan_all_caches)
        chk.pack(side="left")

        self.entitlement_lbl = tk.Label(ent_row, text="CALCULATING...", fg=TEXT_MUTED, bg=BG_PANEL, font=("Consolas", 9))
        self.entitlement_lbl.pack(side="right")

        # Total Payload Size Readout
        self.total_lbl = tk.Label(self.root, text="PAYLOAD SELECTED: 0.00 MB", font=("Consolas", 11, "bold"), bg=BG_DARK, fg=NEON_CYAN)
        self.total_lbl.pack(pady=6)

        # Matrix Terminal Logger
        term_border = tk.Frame(self.root, bg=BG_DARK, highlightbackground=MATRIX_GREEN, highlightthickness=1)
        term_border.pack(fill="x", padx=16, pady=4)

        term_top = tk.Label(term_border, text=" MATRIX_TERMINAL // NPX_SYS_LOG", font=("Consolas", 8, "bold"), bg="#031206", fg=MATRIX_GREEN, anchor="w")
        term_top.pack(fill="x")

        self.log_text = tk.Text(term_border, height=8, width=72, font=("Consolas", 9), bg="#030804", fg=MATRIX_GREEN, insertbackground=MATRIX_GREEN, relief="flat", padx=6, pady=4)
        self.log_text.pack(fill="x")
        self.log_text.tag_configure("green", foreground=MATRIX_GREEN)
        self.log_text.tag_configure("cyan", foreground=NEON_CYAN)
        self.log_text.tag_configure("pink", foreground=NEON_PINK)

        self.log("BOOT SEQUENCE COMPLETE // NUPIXEL UI LOADED.", tag="cyan")
        self.log("READY FOR CACHE PURGE. CUSTOMIZE PATHS OR EXECUTE.", tag="green")

        # Bottom Action Controls
        btn_frame = tk.Frame(self.root, bg=BG_DARK)
        btn_frame.pack(fill="x", padx=16, pady=(10, 14))

        self.rescan_btn = tk.Button(btn_frame, text="[ RESCAN ]", bg=BG_PANEL, fg=NEON_CYAN, activebackground=NEON_CYAN, activeforeground=BG_DARK, font=("Consolas", 10, "bold"), relief="flat", highlightbackground=NEON_CYAN, highlightthickness=1, cursor="hand2", command=self.scan_all_caches)
        self.rescan_btn.pack(side="left", ipadx=12, ipady=6)

        self.clean_btn = tk.Button(btn_frame, text=">> EXECUTE SAFE RECYCLE PURGE <<", bg=NEON_PINK, fg="#ffffff", activebackground=NEON_CYAN, activeforeground=BG_DARK, font=("Consolas", 11, "bold"), relief="flat", cursor="hand2", command=self.confirm_and_clean)
        self.clean_btn.pack(side="right", fill="x", expand=True, padx=(10, 0), ipady=6)

    def build_client_tab(self, parent, mode):
        container = tk.Frame(parent, bg=BG_PANEL, highlightbackground=NEON_CYAN, highlightthickness=1, padx=10, pady=8)
        container.pack(fill="both", expand=True)

        # Custom Directory Bar
        dir_frame = tk.Frame(container, bg=BG_PANEL, pady=4)
        dir_frame.pack(fill="x")

        tk.Label(dir_frame, text="PATH:", font=("Consolas", 9, "bold"), bg=BG_PANEL, fg=NEON_CYAN).pack(side="left")

        entry = tk.Entry(dir_frame, textvariable=self.path_vars[mode], font=("Consolas", 8), bg=BG_INPUT, fg=TEXT_LIGHT, insertbackground=NEON_CYAN, relief="flat", highlightbackground=NEON_CYAN_DIM, highlightthickness=1)
        entry.pack(side="left", fill="x", expand=True, padx=6, ipady=3)
        entry.bind("<Return>", lambda e, m=mode: self.apply_manual_path(m))
        entry.bind("<FocusOut>", lambda e, m=mode: self.apply_manual_path(m))

        browse_btn = tk.Button(dir_frame, text="BROWSE", bg=BG_INPUT, fg=NEON_CYAN, activebackground=NEON_CYAN, activeforeground=BG_DARK, font=("Consolas", 8, "bold"), relief="flat", highlightbackground=NEON_CYAN, highlightthickness=1, cursor="hand2", command=lambda m=mode: self.browse_folder(m))
        browse_btn.pack(side="left", padx=(0, 4), ipadx=6, ipady=1)

        reset_btn = tk.Button(dir_frame, text="RESET", bg=BG_INPUT, fg=NEON_PINK, activebackground=NEON_PINK, activeforeground=BG_DARK, font=("Consolas", 8, "bold"), relief="flat", highlightbackground=NEON_PINK, highlightthickness=1, cursor="hand2", command=lambda m=mode: self.reset_folder(m))
        reset_btn.pack(side="right", ipadx=6, ipady=1)

        # Directory Status Indicator
        path_status = tk.Label(container, text="PROBING DIRECTORY...", font=("Consolas", 8, "bold"), bg=BG_PANEL, fg=TEXT_MUTED)
        path_status.pack(anchor="w", pady=(2, 6))
        self.path_status_lbls[mode] = path_status

        # Cache Folder Checkboxes
        folders = [
            ("cache", "Main Client Cache [cache]", True),
            ("server-cache", "Server Assets Cache [server-cache]", True),
            ("server-cache-priv", "Private Server Cache [server-cache-priv]", True),
            ("nui-storage", "NUI Browser & UI Storage [nui-storage]", True),
            ("logs", "Crash & Client Logs [logs / crashes]", False)
        ]

        for folder_key, label_text, default_checked in folders:
            row = tk.Frame(container, bg=BG_PANEL)
            row.pack(fill="x", pady=3)

            var = tk.BooleanVar(value=default_checked)
            chk = ttk.Checkbutton(row, text=label_text, variable=var, style="Cyber.TCheckbutton", command=self.scan_all_caches)
            chk.pack(side="left")

            status_lbl = tk.Label(row, text="SCANNING...", fg=TEXT_MUTED, bg=BG_PANEL, font=("Consolas", 9))
            status_lbl.pack(side="right")

            self.targets[mode][folder_key] = {
                "var": var,
                "label": f"[{mode.upper()}] {folder_key}",
                "status_lbl": status_lbl
            }

    def start_neon_flicker(self):
        """Creates a subtle cyberpunk neon sign flicker effect on the header."""
        def flicker_step():
            roll = random.random()
            if roll < 0.08:
                self.neon_title.config(fg=NEON_CYAN_DIM)
                self.neon_prefix.config(fg=NEON_PINK_DIM)
                self.neon_suffix.config(fg=NEON_PINK_DIM)
                delay = random.randint(60, 130)
            elif roll < 0.14:
                self.neon_title.config(fg=NEON_PINK)
                self.neon_prefix.config(fg=NEON_CYAN)
                self.neon_suffix.config(fg=NEON_CYAN)
                delay = random.randint(80, 150)
            else:
                self.neon_title.config(fg=NEON_CYAN)
                self.neon_prefix.config(fg=NEON_PINK)
                self.neon_suffix.config(fg=NEON_PINK)
                delay = random.randint(400, 1600)
            self.root.after(delay, flicker_step)
        flicker_step()

    def normalize_data_path(self, raw_path):
        cleaned = os.path.normpath(raw_path.strip().strip('"'))
        for sub in ["data", os.path.join("FiveM.app", "data"), os.path.join("FiveM Application Data", "data")]:
            candidate = os.path.join(cleaned, sub)
            if os.path.exists(candidate):
                return candidate
        if os.path.exists(cleaned):
            for entry in os.listdir(cleaned):
                sub_data = os.path.join(cleaned, entry, "data")
                if os.path.exists(sub_data):
                    return sub_data
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
            self.log(f"[{mode.upper()}] TARGET OVERRIDE -> {normalized}", tag="cyan")
            self.scan_all_caches()

    def reset_folder(self, mode):
        default_dir = self.default_paths[mode]
        self.path_vars[mode].set(default_dir)
        self.save_config()
        self.log(f"[{mode.upper()}] PATH RESTORED -> {default_dir}", tag="cyan")
        self.scan_all_caches()

    def log(self, text, tag="green"):
        self.log_text.insert(tk.END, f"> {text}\n", tag)
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
                    self.path_status_lbls[mode].config(text="[ONLINE] DIRECTORY LOCKED & VERIFIED", fg=MATRIX_GREEN)
                else:
                    self.path_status_lbls[mode].config(text="[OFFLINE] DIRECTORY NOT FOUND // EDIT PATH OR CLICK BROWSE", fg=NEON_PINK)

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
                        info["status_lbl"].config(text=f"{files} files ({size_mb:.2f} MB)", fg=NEON_CYAN if info["var"].get() else TEXT_LIGHT)
                        if info["var"].get():
                            total_selected_bytes += size_bytes
                    else:
                        info["status_lbl"].config(text="EMPTY / NOT FOUND", fg=TEXT_MUTED)

            # Scan DigitalEntitlements
            if os.path.exists(self.entitlement_path):
                b, f = self.get_dir_size(self.entitlement_path)
                self.entitlement_lbl.config(text=f"{f} files ({b / (1024 * 1024):.2f} MB)", fg=NEON_PINK if self.entitlement_var.get() else TEXT_LIGHT)
                if self.entitlement_var.get():
                    total_selected_bytes += b
            else:
                self.entitlement_lbl.config(text="EMPTY / NOT FOUND", fg=TEXT_MUTED)

            total_mb = total_selected_bytes / (1024 * 1024)
            self.total_lbl.config(text=f"PAYLOAD SELECTED: {total_mb:.2f} MB")

        threading.Thread(target=worker, daemon=True).start()

    def check_running_processes(self):
        def worker():
            running_names = []
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name']
                    if name in TARGET_PROCESSES:
                        if name not in running_names:
                            running_names.append(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if running_names:
                self.proc_status_lbl.config(text=f"[ALERT] RUNNING TARGETS DETECTED: {', '.join(running_names)}", fg=NEON_PINK)
            else:
                self.proc_status_lbl.config(text="[CLEAR] NO CONFLICTING FIVEM / GTA PROCESSES DETECTED", fg=MATRIX_GREEN)
            
            self.root.after(5000, self.check_running_processes)

        threading.Thread(target=worker, daemon=True).start()

    def kill_processes(self):
        killed_count = 0
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                name = proc.info['name']
                if name in TARGET_PROCESSES:
                    psutil.Process(proc.info['pid']).terminate()
                    killed_count += 1
                    self.log(f"TERMINATED PROCESS -> {name} (PID: {proc.info['pid']})", tag="pink")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_count > 0:
            messagebox.showinfo("PROCESS WATCHDOG", f"Successfully terminated {killed_count} active target process(es).")
        else:
            messagebox.showinfo("PROCESS WATCHDOG", "No active target processes found to terminate.")
        self.scan_all_caches()

    def confirm_and_clean(self):
        if not messagebox.askyesno("CONFIRM PURGE", "Are you sure you want to recycle/purge the selected cache directories?"):
            return
        
        def worker():
            purged_bytes = 0
            purged_files = 0

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

                    for p in target_paths:
                        if os.path.exists(p):
                            b, f = self.get_dir_size(p)
                            try:
                                send2trash(p)
                                purged_bytes += b
                                purged_files += f
                                self.log(f"[{mode.upper()}] RECYCLED -> {folder_key}", tag="pink")
                            except Exception as e:
                                self.log(f"[{mode.upper()}] FAILED TO TRASH {folder_key}: {e}", tag="pink")

            # Purge DigitalEntitlements if selected
            if self.entitlement_var.get() and os.path.exists(self.entitlement_path):
                b, f = self.get_dir_size(self.entitlement_path)
                try:
                    send2trash(self.entitlement_path)
                    purged_bytes += b
                    purged_files += f
                    self.log("[AUTH] RECYCLED -> ros_entitlements (DigitalEntitlements)", tag="pink")
                except Exception as e:
                    self.log(f"[AUTH] FAILED TO TRASH ros_entitlements: {e}", tag="pink")

            mb_saved = purged_bytes / (1024 * 1024)
            self.log(f"PURGE COMPLETE // RECYCLED {purged_files} FILES ({mb_saved:.2f} MB FREED).", tag="green")
            messagebox.showinfo("PURGE COMPLETE", f"Successfully moved {purged_files} items to Recycle Bin.\nFreed space: {mb_saved:.2f} MB")
            self.scan_all_caches()

        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = NPXCleanerApp(root)
    root.mainloop()
