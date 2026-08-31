# RealmsLauncher

A modern Minecraft launcher for Medieval RP servers with a beautiful medieval-themed UI.

## Features

- **Medieval-themed Design**: Beautiful gold and brown color scheme perfect for RP servers
- **One-Click Installation**: Download Minecraft 1.21.1 with a single button
- **Auto Mod Management**: Automatically downloads and updates mods from repository
- **NeoForge Support**: Built-in NeoForge installation for modded gameplay
- **Mod Verification**: Checks installed mods against repository and updates if needed
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.8 or higher
- Java (for running Minecraft)

## Installation

### From Source

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install customtkinter requests pyinstaller
   ```

3. Run the launcher:
   ```bash
   python realmslauncher.py
   ```

### Build EXE (Windows)

Run the build script:
```bash
build.bat
```

Or manually:
```bash
pyinstaller --onefile --windowed --name RealmsLauncher realmslauncher.py
```

The executable will be in the `dist` folder.

## Usage

1. **Download Minecraft**: Click "📥 Download Minecraft" to install Minecraft 1.21.1
2. **Install Mods**: Click "🔧 Install NeoForge & Mods" to install NeoForge and required mods
3. **Play**: Click "⚔️ PLAY" to launch the game with all mods

## Configuration

### Mod List

Edit `modlist.json` to customize which mods are installed:

```json
{
  "version": 1,
  "mods": [
    {
      "filename": "mod-name.jar",
      "url": "https://example.com/mod-url"
    }
  ]
}
```

### Remote Repository

Update `MODLIST_URL` in `realmslauncher.py` to point to your remote modlist.json:

```python
MODLIST_URL = "https://raw.githubusercontent.com/your-repo/main/modlist.json"
```

## File Structure

```
RealmsLauncher/
├── realmslauncher.py    # Main launcher application
├── modlist.json         # Mod configuration file
├── build.bat           # Windows build script
├── README.md           # This file
└── dist/               # Built executables
    └── RealmsLauncher  # Compiled launcher
```

## License

This project is open source and available for modification.

## Support

For issues or questions, please contact your server administrator.