import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
from send2trash import send2trash

# Target FiveM Background Processes to Safely Terminate
TARGET_PROCESSES = ["FiveM.exe", "FiveM_b2699_GTAProcess.exe", "FiveM_b3095_GTAProcess.exe", "CitizenFX.exe", "GTA5.exe"]

class NPXCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("npx-cleaner | Open Source FiveM Optimizer")
        self.root.geometry("520x640")
        self.root.resizable(False, False)
        
        # Default local AppData target path for FiveM
        self.fivem_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "FiveM", "FiveM.app")
        self.data_path = os.path.join(self.fivem_path, "data")
        
        self.setup_ui()
        self.scan_cache()

    def setup_ui(self):
        # Header Info Banner
        header = tk.Label(self.root, text="npx-cleaner", font=("Arial", 16, "bold"), fg="#1e90ff")
        header.pack(pady=5)
        
        author_lbl = tk.Label(self.root, text="Created by CICADA", font=("Arial", 9, "italic"), fg="gray")
        author_lbl.pack(pady=2)
        
        path_lbl = tk.Label(self.root, text=f"Target: {self.data_path}", font=("Arial", 8), fg="gray")
        path_lbl.pack(pady=2)

        # Status & System Processes Area
        self.proc_frame = tk.LabelFrame(self.root, text=" Process Environment Status ", padx=10, pady=5)
        self.proc_frame.pack(fill="x", padx=15, pady=5)
        
        self.proc_status_lbl = tk.Label(self.proc_frame, text="Checking active tasks...", fg="orange", font=("Arial", 9, "bold"))
        self.proc_status_lbl.pack(anchor="w")
        
        self.kill_btn = ttk.Button(self.proc_frame, text="Force Close Running Conflict Processes", command=self.kill_processes)
        self.kill_btn.pack(fill="x", pady=5)

        # Target Cleaning Directory Toggles
        self.clean_frame = tk.LabelFrame(self.root, text=" Component Selection & Scan Diagnostics ", padx=10, pady=5)
        self.clean_frame.pack(fill="x", padx=15, pady=5)

        self.targets = {
            "cache": {"var": tk.BooleanVar(value=True), "label": "Main Cache Folder", "path": os.path.join(self.data_path, "cache")},
            "server-cache": {"var": tk.BooleanVar(value=True), "label": "Server Assets Cache", "path": os.path.join(self.data_path, "server-cache")},
            "server-cache-priv": {"var": tk.BooleanVar(value=True), "label": "Private Server Cache", "path": os.path.join(self.data_path, "server-cache-priv")},
            "nui-storage": {"var": tk.BooleanVar(value=True), "label": "NUI Browser Storage / UI Cache", "path": os.path.join(self.data_path, "nui-storage")},
            "digital-entitlements": {"var": tk.BooleanVar(value=False), "label": "DigitalEntitlements (Triggers Re-auth)", "path": os.path.join(os.environ.get("APPDATA", ""), "CitizenFX", "ros_entitlements")}
        }

        for key, info in self.targets.items():
            f = tk.Frame(self.clean_frame)
            f.pack(fill="x", pady=3)
            
            chk = ttk.Checkbutton(f, text=info["label"], variable=info["var"], command=self.scan_cache)
            chk.pack(side="left")
            
            info["status_lbl"] = tk.Label(f, text="Calculating...", fg="gray", font=("Arial", 9))
            info["status_lbl"].pack(side="right")

        # Total Aggregated Size
        self.total_lbl = tk.Label(self.root, text="Total Selected Size: 0.00 MB", font=("Arial", 11, "bold"), fg="#2ed573")
        self.total_lbl.pack(pady=10)

        # Operations Console Logger
        self.log_text = tk.Text(self.root, height=8, width=58, font=("Consolas", 9), bg="#1e1e1e", fg="#ffffff")
        self.log_text.pack(padx=15, pady=5)
        self.log("npx-cleaner initialized. Ready to optimize FiveM storage.")

        # Clean Button Execution Action
        self.clean_btn = tk.Button(self.root, text="EXECUTE SAFE CLEANING", bg="#ff4757", fg="white", font=("Arial", 11, "bold"), command=self.confirm_and_clean)
        self.clean_btn.pack(fill="x", padx=15, pady=15)
        
        # Periodic check for active processes
        self.check_running_processes()

    def log(self, text):
        self.log_text.insert(tk.END, f">> {text}\n")
        self.log_text.see(tk.END)

    def get_dir_size(self, path):
        if not os.path.exists(path):
            return 0, 0
        total_size = 0
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
                    file_count += 1
        return total_size, file_count

    def scan_cache(self):
        def worker():
            total_selected_bytes = 0
            for key, info in self.targets.items():
                if os.path.exists(info["path"]):
                    size_bytes, files = self.get_dir_size(info["path"])
                    size_mb = size_bytes / (1024 * 1024)
                    info["status_lbl"].config(text=f"{files} files ({size_mb:.2f} MB)", fg="black")
                    if info["var"].get():
                        total_selected_bytes += size_bytes
                else:
                    info["status_lbl"].config(text="Directory Empty / Not Found", fg="gray")
            
            total_mb = total_selected_bytes / (1024 * 1024)
            self.total_lbl.config(text=f"Total Selected Size: {total_mb:.2f} MB")
        
        threading.Thread(target=worker, daemon=True).start()

    def check_running_processes(self):
        active = []
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in TARGET_PROCESSES:
                active.append(proc.info['name'])
        
        if active:
            self.proc_status_lbl.config(text=f"CONFLICT DETECTED: {', '.join(set(active))}", fg="#ff4757")
            self.clean_btn.config(state="disabled")
        else:
            self.proc_status_lbl.config(text="Environment Safe: No active conflicting processes.", fg="#2ed573")
            self.clean_btn.config(state="normal")
            
        self.root.after(2000, self.check_running_processes)

    def kill_processes(self):
        killed = False
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] in TARGET_PROCESSES:
                try:
                    psutil.Process(proc.info['pid']).terminate()
                    self.log(f"Terminated conflicting instance: {proc.info['name']} (PID: {proc.info['pid']})")
                    killed = True
                except Exception:
                    pass
        if killed:
            self.log("Environment cleanup finalized.")
        else:
            self.log("No conflicting background environments discovered.")

    def confirm_and_clean(self):
        if self.targets["digital-entitlements"]["var"].get():
            ans = messagebox.askyesno("Advanced Area Flagged", "You have selected DigitalEntitlements. This will require you to sign back into Rockstar/SocialClub upon launching FiveM.\n\nAre you sure you want to proceed?")
            if not ans:
                return
                
        confirm = messagebox.askyesno("Confirm Task Execution", "Selected targeted folders will be safely moved to your Windows Recycle Bin. Proceed?")
        if confirm:
            self.execute_cleaning()

    def execute_cleaning(self):
        self.clean_btn.config(state="disabled")
        def worker():
            for key, info in self.targets.items():
                if info["var"].get() and os.path.exists(info["path"]):
                    try:
                        self.log(f"Staging target for recycling: {info['label']}...")
                        send2trash(info["path"])
                        self.log(f"Successfully cleaned: {info['label']}")
                    except Exception as e:
                        self.log(f"Error accessing target {info['label']}: {str(e)}")
            self.log("All cleaning operations completed successfully.")
            self.scan_cache()
            messagebox.showinfo("Success", "FiveM Cache optimization task finalized successfully by npx-cleaner!")
        
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = NPXCleanerApp(root)
    root.mainloop()
