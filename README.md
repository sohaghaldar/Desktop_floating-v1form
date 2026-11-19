# 🕷️ Desktop Floating Spider (ডেস্কটপ ফ্লোটিং স্পাইডার)

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.6.0-00f5d4.svg?style=for-the-badge&logo=github" alt="Version 2.6.0" />
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11%20%7C%20Linux%20%7C%20macOS-38bdf8.svg?style=for-the-badge&logo=windows" alt="Platforms" />
  <img src="https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-f59e0b.svg?style=for-the-badge&logo=python" alt="Python Versions" />
  <img src="https://img.shields.io/badge/Release-Standalone%20.EXE%20%26%20Pip-10b981.svg?style=for-the-badge" alt="Standalone EXE" />
  <img src="https://img.shields.io/badge/License-MIT-ef4444.svg?style=for-the-badge" alt="License" />
</p>

An ultra-responsive, physics-driven, living **Desktop Floating Spider** and multi-species desktop companion for **Windows 10/11**, **Linux**, and **macOS**. 

Features **procedural Inverse Kinematics (IK)** leg physics, authentic orb-web weaving, dynamic prey hunting, zero taskbar clutter, 24/7 system tray controls, a sleek dark-glass live settings customizer (`Shift + P`), and an integrated **GitHub Auto-Updater with real-time Megabyte (MB) download progress**!

---

## 🖥️ Desktop Preview & Visual Layout

```text
 ╔══════════════════════════════════════════════════════════════════════════════════╗
 ║  Desktop Wallpaper / Open Apps (100% Click-Through & Non-Blocking)               ║
 ║                                                                                  ║
 ║              \    |    /               [Ceiling Silk Anchor]                     ║
 ║               \   |   /                                                          ║
 ║                \  |  /                                                           ║
 ║            -----[ 🕸️ ]-----            [Procedural Orb-Web]                       ║
 ║                /  |  \                                                           ║
 ║               /   |   \                                                          ║
 ║                   🕷️                    [Living Cyber Spider with IK Legs]        ║
 ║                   |                                                              ║
 ║                   ▼                                                              ║
 ║               🪂 Bungee Silk Drop       🪰 Flying Prey Fly (Shift+F)             ║
 ║                                                                                  ║
 ║  ┌─────────────────────────────────────────────────────────────┐                 ║
 ║  │ ✨ WELCOME: Shift+P: Settings | Shift+F: Prey | Shift+B: Drop│ [Floating Hint] ║
 ║  └─────────────────────────────────────────────────────────────┘                 ║
 ╚══════════════════════════════════════════════════════════════════════════════════╝
    [Windows Taskbar: Clean & Uncluttered]                 [System Tray: 🕷️ 24/7]
```

---

## ⚡ Highlights & Key Features

- **🚀 100% Standalone Portable `.exe`**:
  - Run immediately on any PC without installing Python, Git, or dependencies!
  - Fully persistent settings (`settings.json` stays next to the `.exe`).
- **🪟 Clean Taskbar & 24/7 Tray Integration**:
  - The transparent overlay runs with `WS_EX_TOOLWINDOW`—zero taskbar buttons to clutter your screen.
  - The Taskbar button only appears while the **Live Settings & Customizer** window is open.
  - Dedicated **Cyan Cyber Spider icon** in the Windows System Tray (near the clock) for instant right-click menu controls.
- **🦵 Procedural Inverse Kinematics (IK) Legs**:
  - 8 independently computed jointed legs that grip natural desktop coordinates with realistic stepping phases.
- **🕸️ Authentic Orb-Web Construction**:
  - Procedural anchor placement, radial spoke weaving, and concentric spiral thread construction with dewdrop physics.
- **🎯 Autonomous Curiosity & Interactive Hunting**:
  - Playfully crawls toward idle mouse cursors, playfully headbutts/shoves resting cursors, and captures trapped flies with web vibrations.
- **📊 GitHub Live Auto-Updater with MB Counter**:
  - Automatically notifies users when a new release is available on GitHub.
  - Live progress display with exact download metrics: `Downloading: 12.4 MB / 18.2 MB (68%)`.
  - Atomic update application with syntax validation and instant auto-restart.
- **💡 First-Run Guidance & What's New Notifications**:
  - Displays a sleek on-screen cyber card with key shortcuts upon first launch.
  - Automatically shows a "What's New" changelog card whenever a new update is applied.
- **🛠️ Interactive Self-Installer (`install.bat`)**:
  - Asks permission before installing packages (`Pillow`, `pystray`), creates Desktop shortcuts with cyber icons, and starts the pet.
- **📦 Pip / PyPI Ready**:
  - Installable via standard `pip install .` or `pip install -e .` with CLI commands `desktop-spider` and `desktop-floating`.
- **🌐 Dual Multilingual Support**:
  - Complete English & Bengali (বাংলা) localization with on-the-fly language switching and downloader.

---

## 🎮 Hotkeys Quick Reference (কিবোর্ড শর্টকাট)

All hotkeys are completely customizable in the **Live Settings Customizer** (`Shift + P`).

| Hotkey | Action (English) | বিবরণ (বাংলা) |
| :--- | :--- | :--- |
| **`Shift + P`** | **Open Live Settings Customizer** | **লাইভ সেটিংস ও কাস্টমাইজার প্যানেল খুলুন** |
| **`Shift + F`** | **Spawn Tasty Insect Prey** | **শিকারযোগ্য উড়ন্ত পোকা তৈরি করুন** |
| **`Shift + B`** | **Bungee Jump / Rappel Drop** | **সিল্কের সুতো দিয়ে বাঞ্জি ড্রপ দিন** |
| **`Shift + T`** | **Cycle Cyber Color Themes** | **সাইবার রঙের থিম পরিবর্তন করুন** |
| **`Shift + W`** | **Cycle Spider Model / Anatomy** | **মাকড়সার শারীরিক গঠন/মডেল পরিবর্তন** |
| **`Shift + M`** | **Cycle Creature Species** | **পরবর্তী প্রাণী পরিবর্তন (প্রজাপতি, টিকটিকি ইত্যাদি)** |
| **`Shift + \``** | **Move Web / Anchor Position** | **মাউস দিয়ে জাল বা বাসা নতুন জায়গায় সরান** |
| **`Shift + C`** | **Restart Ceiling Entrance** | **নতুন করে সিলিং থেকে নেমে জাল তৈরি শুরু** |
| **`Shift + Q`** | **Set Ceiling Entry Point** | **সিলিং এন্ট্রি পয়েন্ট নির্ধারণ করুন** |
| **`Shift + H`** | **Hatch Spiderling Babies** | **ডিম ফুটে পিঠে মাকড়সার বাচ্চা বের করুন** |
| **`Shift + R`** | **Trigger Instant Health Break** | **স্বাস্থ্য সচেতনতা বিরতি কার্ড প্রদর্শন** |
| **`Shift + S`** | **Toggle Sound Effects (ON/OFF)** | **শব্দ বা সাউন্ড চালু/বন্ধ করুন** |
| **`Shift + ESC`** | **Safely Exit Application** | **অ্যাপ্লিকেশনটি সম্পূর্ণ বন্ধ করুন** |

---

## 📥 Installation & Running (ইনস্টলেশন ও চালনা)

Choose any of the following 4 easy methods:

### Option 1: Standalone Portable `.exe` (Recommended for Any PC)
> **No Python, Git, or command line required!**
1. Download `DesktopFloatingSpider.exe` from the [Releases](https://github.com/sohaghaldar/desktop-pet-ecosystem/releases) page (or `Desktop-Floating-Spider-v2.6.0-Portable.zip`).
2. Double-click `DesktopFloatingSpider.exe` to run immediately!
3. All your customized settings are automatically saved in `settings.json` next to the executable.

---

### Option 2: Interactive Installer (`install.bat`)
1. Clone or download this repository.
2. Double-click **`install.bat`** (or run `python setup_interactive.py` in CMD).
3. The interactive installer will:
   - Check your Python environment.
   - Ask: `"Do you want to automatically install missing dependencies (Pillow, pystray) via pip? [Y/n]"`
   - Ask: `"Do you want to create a 'Desktop Floating' shortcut on your Desktop? [Y/n]"`
   - Ask: `"Do you want to launch Desktop Floating Spider now? [Y/n]"`

---

### Option 3: Install via `pip`
You can install it directly into your Python environment as a standard CLI package:

```bash
# Clone the repository
git clone https://github.com/sohaghaldar/desktop-pet-ecosystem.git
cd desktop-pet-ecosystem

# Install package
pip install .

# Launch anywhere from CMD / Terminal:
desktop-spider
# or
desktop-floating
```

---

### Option 4: Traditional Source Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run silently in background (Windows)
run_spider.bat
# or
pythonw desktop_spider.py
```

---

## ⚙️ Configuration & Customization (`settings.json`)

All settings persist in `settings.json`. You can modify them directly from the in-app **Live Settings Control Panel** (`Shift + P`) or manually in the JSON file:

```json
{
  "LANGUAGE": "en",
  "CREATURE_SPECIES": "spider",
  "SPIDER_MODEL_INDEX": 0,
  "SPIDER_SIZE_SCALE": 0.5,
  "SPIDER_SPEED": 6.0,
  "THEME_INDEX": 1,
  "SOUND_ENABLED": false,
  "BUNGEE_AUTO_ENABLED": true,
  "HOTKEYS": {
    "SETTINGS": "Shift+P",
    "BUG": "Shift+F",
    "BUNGEE": "Shift+B"
  }
}
```

---

## 🔄 Built-in GitHub Auto-Updater

Desktop Floating Spider includes a native updater engine:
1. When you open the Settings panel (`Shift + P`), it silently queries the latest GitHub release.
2. If an update is available, you will see a notification and the **Update Now** button will illuminate.
3. Clicking **Update Now** downloads the release with a **live MB counter** (`Downloading: 14.2 MB / 18.5 MB (76%)`).
4. Once verified, it applies the update atomically and seamlessly restarts the application.

---

## 🤝 Contributing

Contributions, bug reports, and pull requests are warmly welcomed!
- Fork the repository.
- Create a new feature branch (`git checkout -b feature/CoolNewFeature`).
- Commit your improvements (`git commit -m "Add CoolNewFeature"`).
- Push to the branch (`git push origin feature/CoolNewFeature`).
- Open a Pull Request on GitHub.

---

## 📄 License & Credits

- **Author**: Sohag Haldar ([@sohaghaldar](https://github.com/sohaghaldar))
- **License**: Released under the **MIT License**. Free for personal and educational use.
