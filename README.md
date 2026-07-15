## 🛠️ Dotfiles & Configs

* **`bash_aliases.conf`**: My terminal aliases.
* **`bashrc.conf`**: Default `.bashrc` with Kitty color support and startup ASCII art.
* **`cmus.conf`**: Cmus music player setup (keybindings, colors, config).
* **`keybind.conf`**: GNOME global keyboard shortcuts.
* **`kitty.conf`**: Kitty terminal config and keybindings.
* **`vim.conf`**: My Vim configuration.

---

## 🎵 Scripts & Media

* **`copy_file.sh`**: Script to auto-copy music to a server (requires `rsync`).
* **`app.py`**: Turns my laptop into a media server (useful since I mostly use a hotspot).

**Setup Commands for Media Server:**

```bash
sudo apt update && sudo apt install python3-pip -y
python3 -m pip install mutagen Pillow --break-system-packages

```

---

## ✍️ LaTeX Setup

1. **Install LaTeX**: The core engine.
2. **Full LaTeX Package**: The complete package for all fonts and formats.
3. **Zathura**: PDF viewer (instant refresh when saved).
4. **vim-plug**: Vim plugin manager (must install first).
5. **VimTex**: IDE plugin for LaTeX inside Vim.
