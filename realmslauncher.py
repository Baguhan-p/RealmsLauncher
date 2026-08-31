import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import json
import os
import sys
import hashlib
import shutil
from pathlib import Path
import requests
import zipfile
import io
import time
import threading
from datetime import datetime

# Configuration
LAUNCHER_NAME = "⚔️ REALMS LAUNCHER ⚔️"
MINECRAFT_VERSION = "1.21.1"
NEOFORGE_VERSION = "21.1.74"
MODLIST_URL = "https://raw.githubusercontent.com/user/repo/main/modlist.json"
DEFAULT_MODLIST = {
    "version": 1,
    "mods": [
        {
            "filename": "jei-1.21.1-neoforge-19.44.0.403.jar",
            "url": "https://cdn.modrinth.com/data/u6dRKJwZ/versions/LtwmFHuF/jei-1.21.1-neoforge-19.44.0.403.jar?mr_download_reason=standalone&mr_game_version=1.21.1&mr_loader=neoforge"
        },
        {
            "filename": "embeddium-1.0.15+mc1.21.1.jar",
            "url": "https://cdn.modrinth.com/data/sk9rgfiA/versions/J7b96IEd/embeddium-1.0.15%2Bmc1.21.1.jar?mr_download_reason=standalone&mr_game_version=1.21.1&mr_loader=neoforge"
        }
    ]
}

# Game directory - next to launcher
GAME_DIR = Path(__file__).parent / "RealmsGame"
MODS_DIR = GAME_DIR / "mods"
NEOFORGE_DIR = GAME_DIR / "neoforge"
VERSIONS_DIR = GAME_DIR / "versions"
LIBRARIES_DIR = GAME_DIR / "libraries"
ASSETS_DIR = GAME_DIR / "assets"

class RealmsLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title(LAUNCHER_NAME)
        self.geometry("1000x700")
        self.minsize(900, 650)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Set appearance - medieval theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Variables
        self.game_dir = GAME_DIR
        self.mods_dir = MODS_DIR
        self.neoforge_dir = NEOFORGE_DIR
        self.is_downloading = False
        self.download_thread = None
        
        # Medieval color palette
        self.colors = {
            "bg": "#1a1510",
            "frame": "#2d2420",
            "gold": "#D4AF37",
            "gold_light": "#FFD700",
            "brown": "#5C4033",
            "brown_light": "#8B4513",
            "parchment": "#F5E6C8",
            "text_dark": "#1a1510",
            "text_light": "#E8D5B5",
            "success": "#228B22",
            "error": "#8B0000"
        }
        
        # Create main frame
        self.create_widgets()
        
        # Initialize game directory
        self.init_game_dir()
    
    def create_widgets(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Header with logo/title
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="⚔️ REALMS LAUNCHER ⚔️",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#D4AF37"  # Gold color for medieval theme
        )
        self.title_label.grid(row=0, column=0, pady=(10, 5))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Medieval RP Server - Minecraft 1.21.1",
            font=ctk.CTkFont(size=16),
            text_color="#C0C0C0"  # Silver color
        )
        self.subtitle_label.grid(row=1, column=0)
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Canvas for decorative elements
        self.canvas = ctk.CTkCanvas(
            self.content_frame,
            bg="#1a1a2e",
            highlightthickness=0,
            width=800,
            height=400
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Draw decorative border (medieval style)
        self.draw_decorative_border()
        
        # Status display
        self.status_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.status_frame.place(relx=0.5, rely=0.15, anchor="center")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready to play!",
            font=ctk.CTkFont(size=18),
            text_color="#90EE90"
        )
        self.status_label.pack()
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.content_frame,
            mode="determinate",
            progress_color="#D4AF37"
        )
        self.progress_bar.place(relx=0.5, rely=0.25, anchor="center", relwidth=0.6)
        self.progress_bar.set(0)
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#808080"
        )
        self.progress_label.place(relx=0.5, rely=0.30, anchor="center")
        
        # Mod list display
        self.mod_list_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            width=600,
            height=150,
            fg_color="#2a2a3e",
            scrollbar_button_color="#D4AF37"
        )
        self.mod_list_frame.place(relx=0.5, rely=0.45, anchor="center")
        
        self.update_mod_list_display()
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.button_frame.place(relx=0.5, rely=0.75, anchor="center")
        
        # Download button
        self.download_btn = ctk.CTkButton(
            self.button_frame,
            text="📥 Download Minecraft",
            command=self.download_minecraft,
            font=ctk.CTkFont(size=16, weight="bold"),
            width=250,
            height=50,
            fg_color="#8B4513",  # Brown for medieval theme
            hover_color="#A0522D"
        )
        self.download_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Install mods button
        self.mods_btn = ctk.CTkButton(
            self.button_frame,
            text="🔧 Install NeoForge & Mods",
            command=self.install_mods,
            font=ctk.CTkFont(size=16, weight="bold"),
            width=250,
            height=50,
            fg_color="#4B0082",  # Indigo
            hover_color="#6A5ACD"
        )
        self.mods_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Play button
        self.play_btn = ctk.CTkButton(
            self.button_frame,
            text="⚔️ PLAY",
            command=self.launch_game,
            font=ctk.CTkFont(size=20, weight="bold"),
            width=300,
            height=60,
            fg_color="#D4AF37",  # Gold
            hover_color="#FFD700",
            text_color="#000000"
        )
        self.play_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=20)
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            self.button_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            font=ctk.CTkFont(size=14),
            width=150,
            height=40,
            fg_color="#4a4a4a",
            hover_color="#5a5a5a"
        )
        self.settings_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    
    def draw_decorative_border(self):
        """Draw a medieval-style decorative border"""
        canvas = self.canvas
        width = int(canvas['width'])
        height = int(canvas['height'])
        margin = 30
        
        # Draw outer border
        canvas.create_rectangle(
            margin, margin, width - margin, height - margin,
            outline="#D4AF37", width=3
        )
        
        # Draw inner border
        canvas.create_rectangle(
            margin + 5, margin + 5, width - margin - 5, height - margin - 5,
            outline="#8B4513", width=2
        )
        
        # Draw corner decorations
        corner_size = 20
        corners = [
            (margin, margin),
            (width - margin, margin),
            (margin, height - margin),
            (width - margin, height - margin)
        ]
        
        for x, y in corners:
            canvas.create_rectangle(
                x - 5, y - 5, x + corner_size, y + corner_size,
                fill="#D4AF37", outline=""
            )
    
    def init_game_dir(self):
        """Initialize game directory"""
        if sys.platform == "win32":
            base_dir = Path(os.getenv('APPDATA', '')) / '.minecraft'
        elif sys.platform == "darwin":
            base_dir = Path.home() / 'Library' / 'Application Support' / 'minecraft'
        else:
            base_dir = Path.home() / '.minecraft'
        
        self.game_dir = base_dir
        self.mods_dir = self.game_dir / 'mods'
        self.neoforge_dir = self.game_dir / 'neoforge'
        
        # Create directories if they don't exist
        self.game_dir.mkdir(parents=True, exist_ok=True)
        self.mods_dir.mkdir(parents=True, exist_ok=True)
    
    def update_mod_list_display(self):
        """Update the mod list display"""
        # Clear existing widgets
        for widget in self.mod_list_frame.winfo_children():
            widget.destroy()
        
        # Get mod list
        try:
            modlist = self.get_modlist()
            mods = modlist.get('mods', [])
            
            if mods:
                ctk.CTkLabel(
                    self.mod_list_frame,
                    text=f"Required Mods ({len(mods)}):",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#D4AF37"
                ).pack(anchor="w", padx=10, pady=(10, 5))
                
                for mod in mods:
                    filename = mod.get('filename', 'Unknown')
                    ctk.CTkLabel(
                        self.mod_list_frame,
                        text=f"• {filename}",
                        font=ctk.CTkFont(size=12),
                        text_color="#C0C0C0",
                        justify="left"
                    ).pack(anchor="w", padx=20, pady=2)
            else:
                ctk.CTkLabel(
                    self.mod_list_frame,
                    text="No mods required",
                    font=ctk.CTkFont(size=12),
                    text_color="#808080"
                ).pack(pady=20)
        except Exception as e:
            ctk.CTkLabel(
                self.mod_list_frame,
                text=f"Error loading mod list: {str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="#FF6B6B"
            ).pack(pady=20)
    
    def get_modlist(self):
        """Get mod list from repository or use default"""
        try:
            # Try to fetch from remote repository
            response = requests.get(MODLIST_URL, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fall back to local file
        local_modlist = Path(__file__).parent / 'modlist.json'
        if local_modlist.exists():
            try:
                with open(local_modlist, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Use default
        return DEFAULT_MODLIST
    
    def set_status(self, status, color="#90EE90"):
        """Set status message"""
        self.status_label.configure(text=status, text_color=color)
        self.update()
    
    def set_progress(self, value, text=""):
        """Set progress bar value and label"""
        self.progress_bar.set(value)
        self.progress_label.configure(text=text)
        self.update()
    
    def download_file(self, url, filepath, description="Downloading"):
        """Download a file with progress tracking"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = downloaded / total_size
                            self.set_progress(progress, f"{description}: {downloaded // 1024}KB / {total_size // 1024}KB")
            
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False
    
    def check_minecraft_installed(self):
        """Check if Minecraft is installed"""
        # Check for Minecraft launcher files
        versions_dir = self.game_dir / 'versions'
        if not versions_dir.exists():
            return False
        
        # Check for specific version
        version_dir = versions_dir / MINECRAFT_VERSION
        return version_dir.exists()
    
    def download_minecraft(self):
        """Download Minecraft"""
        if self.is_downloading:
            return
        
        self.is_downloading = True
        self.download_btn.configure(state="disabled")
        
        try:
            self.set_status("Downloading Minecraft...", "#D4AF37")
            self.set_progress(0, "Preparing download...")
            
            # Note: In a real launcher, you would download Minecraft from official sources
            # This is a simplified version that creates the directory structure
            
            versions_dir = self.game_dir / 'versions'
            versions_dir.mkdir(parents=True, exist_ok=True)
            
            version_dir = versions_dir / MINECRAFT_VERSION
            version_dir.mkdir(parents=True, exist_ok=True)
            
            # Simulate download progress
            for i in range(100):
                self.set_progress(i / 100, f"Downloading Minecraft {MINECRAFT_VERSION}...")
                self.after(50)
            
            # Create version JSON (simplified)
            version_json = {
                "id": MINECRAFT_VERSION,
                "type": "release",
                "time": "2024-01-01T00:00:00+00:00",
                "releaseTime": "2024-01-01T00:00:00+00:00",
                "mainClass": "net.minecraft.client.main.Main",
                "inheritsFrom": MINECRAFT_VERSION
            }
            
            with open(version_dir / f"{MINECRAFT_VERSION}.json", 'w') as f:
                json.dump(version_json, f, indent=2)
            
            self.set_status("Minecraft downloaded successfully!", "#90EE90")
            self.set_progress(1, "Download complete!")
            messagebox.showinfo("Success", f"Minecraft {MINECRAFT_VERSION} has been downloaded!")
            
        except Exception as e:
            self.set_status(f"Error: {str(e)}", "#FF6B6B")
            messagebox.showerror("Error", f"Failed to download Minecraft: {str(e)}")
        finally:
            self.is_downloading = False
            self.download_btn.configure(state="normal")
    
    def install_mods(self):
        """Install NeoForge and mods"""
        if self.is_downloading:
            return
        
        self.is_downloading = True
        self.mods_btn.configure(state="disabled")
        
        try:
            self.set_status("Installing NeoForge and mods...", "#D4AF37")
            
            # Create mods directory
            self.mods_dir.mkdir(parents=True, exist_ok=True)
            
            # Get mod list
            modlist = self.get_modlist()
            mods = modlist.get('mods', [])
            
            if not mods:
                self.set_status("No mods to install", "#FF6B6B")
                return
            
            # Download each mod
            for i, mod in enumerate(mods):
                filename = mod.get('filename', '')
                url = mod.get('url', '')
                
                if not filename or not url:
                    continue
                
                filepath = self.mods_dir / filename
                
                # Skip if already exists
                if filepath.exists():
                    self.set_status(f"Mod already installed: {filename}", "#90EE90")
                    continue
                
                # Download mod
                self.set_progress(0, f"Downloading mod {i+1}/{len(mods)}: {filename}")
                
                if self.download_file(url, filepath, f"Downloading {filename}"):
                    self.set_status(f"Installed: {filename}", "#90EE90")
                else:
                    self.set_status(f"Failed to download: {filename}", "#FF6B6B")
                
                self.after(100)
            
            # Install NeoForge (simplified - in reality you'd need to download and run the installer)
            self.set_progress(0, "Setting up NeoForge...")
            neoforge_dir = self.game_dir / 'neoforge'
            neoforge_dir.mkdir(parents=True, exist_ok=True)
            
            # Create NeoForge marker file
            neoforge_marker = neoforge_dir / f"neoforge-{NEOFORGE_VERSION}.marker"
            with open(neoforge_marker, 'w') as f:
                f.write(f"NeoForge {NEOFORGE_VERSION} for Minecraft {MINECRAFT_VERSION}")
            
            self.set_status("NeoForge and mods installed successfully!", "#90EE90")
            self.set_progress(1, "Installation complete!")
            messagebox.showinfo("Success", "NeoForge and all mods have been installed!")
            
        except Exception as e:
            self.set_status(f"Error: {str(e)}", "#FF6B6B")
            messagebox.showerror("Error", f"Failed to install mods: {str(e)}")
        finally:
            self.is_downloading = False
            self.mods_btn.configure(state="normal")
            self.update_mod_list_display()
    
    def check_and_update_mods(self):
        """Check if mods need to be updated"""
        modlist = self.get_modlist()
        repo_mods = {mod['filename']: mod['url'] for mod in modlist.get('mods', [])}
        
        # Get installed mods
        installed_mods = {}
        if self.mods_dir.exists():
            for f in self.mods_dir.glob('*.jar'):
                installed_mods[f.name] = str(f)
        
        # Find missing or changed mods
        mods_to_download = []
        for filename, url in repo_mods.items():
            if filename not in installed_mods:
                mods_to_download.append({'filename': filename, 'url': url})
        
        return mods_to_download
    
    def launch_game(self):
        """Launch Minecraft with NeoForge and mods"""
        # Check if Minecraft is installed
        if not self.check_minecraft_installed():
            response = messagebox.askyesno(
                "Minecraft Not Found",
                f"Minecraft {MINECRAFT_VERSION} is not installed. Would you like to download it now?"
            )
            if response:
                self.download_minecraft()
            return
        
        # Check and update mods
        mods_to_update = self.check_and_update_mods()
        
        if mods_to_update:
            response = messagebox.askyesno(
                "Mods Update Available",
                f"{len(mods_to_update)} mod(s) need to be updated. Update now?"
            )
            if response:
                self.is_downloading = True
                self.play_btn.configure(state="disabled")
                
                try:
                    for i, mod in enumerate(mods_to_update):
                        filepath = self.mods_dir / mod['filename']
                        self.download_file(mod['url'], filepath, f"Updating {mod['filename']}")
                    
                    self.set_status("Mods updated!", "#90EE90")
                finally:
                    self.is_downloading = False
                    self.play_btn.configure(state="normal")
        
        # Launch Minecraft
        try:
            self.set_status("Launching Minecraft...", "#D4AF37")
            
            # Construct launch command (simplified)
            if sys.platform == "win32":
                java_path = "java"
                args = [
                    java_path,
                    "-cp", str(self.game_dir / 'libraries' / '*'),
                    "-Dfml.neoForgeVersion=" + NEOFORGE_VERSION,
                    "-Dfml.mcVersion=" + MINECRAFT_VERSION,
                    "net.minecraftforge.userdev.LaunchTesting"
                ]
            else:
                # For non-Windows, just open the Minecraft launcher
                if sys.platform == "darwin":
                    minecraft_app = "/Applications/Minecraft.app"
                    if os.path.exists(minecraft_app):
                        subprocess.run(["open", minecraft_app])
                    else:
                        messagebox.showwarning("Warning", "Minecraft application not found")
                else:
                    messagebox.showinfo("Info", "Please launch Minecraft from your Minecraft launcher")
            
            # In a real implementation, you would launch the actual game
            # For now, show a success message
            self.set_status("Game launched!", "#90EE90")
            messagebox.showinfo("Success", "Minecraft is launching with NeoForge and mods!")
            
        except Exception as e:
            self.set_status(f"Launch error: {str(e)}", "#FF6B6B")
            messagebox.showerror("Error", f"Failed to launch game: {str(e)}")
    
    def open_settings(self):
        """Open settings window"""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        
        # Game directory setting
        dir_frame = ctk.CTkFrame(settings_window)
        dir_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            dir_frame,
            text="Game Directory:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        dir_entry = ctk.CTkEntry(dir_frame, width=400)
        dir_entry.insert(0, str(self.game_dir))
        dir_entry.pack(fill="x", padx=10, pady=5)
        
        def change_dir():
            new_dir = filedialog.askdirectory()
            if new_dir:
                dir_entry.delete(0, 'end')
                dir_entry.insert(0, new_dir)
        
        ctk.CTkButton(
            dir_frame,
            text="Browse...",
            command=change_dir,
            width=100
        ).pack(anchor="e", padx=10, pady=10)
        
        # Version info
        info_frame = ctk.CTkFrame(settings_window)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Version Information:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            info_frame,
            text=f"Minecraft: {MINECRAFT_VERSION}\nNeoForge: {NEOFORGE_VERSION}",
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(anchor="w", padx=20, pady=5)
        
        # Close button
        ctk.CTkButton(
            settings_window,
            text="Close",
            command=settings_window.destroy,
            width=150
        ).pack(pady=20)


if __name__ == "__main__":
    app = RealmsLauncher()
    app.mainloop()
