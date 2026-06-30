<div align="center">

<p align="center">
<a href="README.md">🇮🇱 עברית</a> | <a href="README.en.md">🇬🇧 English</a>
</p>

# 🌵 CoreELEC-IL

### The Israeli Repository for Kodi / CoreELEC
![CoreELEC-IL](icon.png)


**Home to addons written out of love for stability, performance, and clean code.**


[![GitHub](https://img.shields.io/badge/GitHub-Repo-181717?logo=github&logoColor=white)](https://github.com/kicking-bird-py/coreelec-il)
[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](#)
[![Kodi](https://img.shields.io/badge/Kodi-19%20%7C%2020%20%7C%2021-17B2E7?logo=kodi&logoColor=white)](#)
[![XML](https://img.shields.io/badge/XML-FF6600)](#)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue)](#)

</div>

---

<p align="center">
<img src="https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&label=" width="24"/> About Me <img src="https://img.shields.io/badge/-Kodi-17B2E7?logo=kodi&logoColor=white&label=" width="24"/>

I'm an independent developer — One-Man Show 🎬 — a technology enthusiast and part of the Kodi community. It all started simply with curiosity: "how does this actually work behind the scenes?" That curiosity led me to start exploring Kodi — first with skin/interface customization, then digging deeper into how Kodi actually works under the hood. I taught myself Python, and I haven't stopped building since.

Everything you'll find here was born out of a real need — not a feature for the sake of a feature, but a solution to a problem that genuinely bothered me day to day. I started this repository because I wanted one reliable, up-to-date place that gathers all the tools I've built for the Israeli Kodi community — no marketing, no empty promises, just code that works.
</p>

**Three words that guide me:**

🧘 **Stability** — A good addon is one you don't even notice is there

🛠️ **From Scratch** — No unnecessary dependencies, no third-party bugs

⚡ **Performance** — Runs smoothly even on modest hardware

---

## 🎯 The Vision

No updates just to "bump the version number." Every release that goes out has been tested, verified, and proven to improve the experience. Period.

💡 Why is there no <img src="https://img.shields.io/badge/-Build-17B2E7?logo=kodi&logoColor=white&label=" height="20"/> here?
> Because builds tend to be heavy, bloated, and prone to breaking after every update. I'd rather give you stable, modular tools — and you build the experience you want on top of a clean, fast foundation.

---

## 📥 How to Download

**Via Kodi (recommended):**
Add the repository URL as a new Source in Kodi → Add-ons → Install from repository, copy the link, confirm — then go to Install from zip file, the repo will appear, and install it. Once installed, you're connected to the repository ✅

**The Repo:** [kicking-bird-py.github.io/ce-il](https://kicking-bird-py.github.io/ce-il/)

**Option B — Browse the website:**
Browse to [kicking-bird-py.github.io/ce-il](https://kicking-bird-py.github.io/ce-il/) and download the repo as a ZIP file.

**Option C — Via Git:**
```bash
git clone https://github.com/kicking-bird-py/ce-il.git
```

---

## 🧩 Addons I've Built

### 🔍 AutoCompletion `[CoreELEC-IL Edition]`
> A search autocomplete addon that makes searching in Kodi smarter and more accurate.

`v3.0.1` 🟢 · [📦 Download ZIP](https://github.com/kicking-bird-py/coreelec-il/tree/main/zips/plugin.program.autocompletion) · [📂 Source Code](https://github.com/kicking-bird-py/coreelec-il/tree/main/src/plugin.program.autocompletion)

<p>
<img src="https://img.shields.io/badge/Python%203-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python 3"/>
<img src="https://img.shields.io/badge/Kodi%2019+-17B2E7?style=for-the-badge&logo=kodi&logoColor=white" alt="Kodi 19+"/>
<img src="https://img.shields.io/badge/RTL%20Ready-2CA5E0?style=for-the-badge" alt="RTL Ready"/>
<img src="https://img.shields.io/badge/Zero%20Dependencies-00C853?style=for-the-badge" alt="Zero Dependencies"/>
</p>

- **Full Compatibility:** Works perfectly on Kodi version 21 and above, and is fully adapted to work with the latest versions.

- **Smart Search (Clean Search):** The system automatically strips redundant words from the search (like "season," "episode," "quality," "movie," etc.). For example, if you search "The Bidder Season 1," the system understands you're looking for "The Bidder" and performs an accurate search without the noise words, in both Hebrew and English.

> 💡 **User Experience:** When you start typing and use autocomplete, you might notice the text stops updating in the search bar — no need to worry! That means the system has already "caught" the term and is performing the search for you behind the scenes, instantly.

🗂️ **Local Cache:** Quick access to recent searches.

🔄 **Tailored Interface:** Full RTL (right-to-left writing direction) support.

⏱️ **Stability:** Timeout management to prevent freezes.

#### ⚙️ Technical Specs & Improvements (CoreELEC-IL Rewrite)

The addon is originally based on the work of Philipp Temminghoff 🌱, but underwent a comprehensive, in-depth rewrite to meet the modern standards of Kodi and CoreELEC:

**Full Migration to <img src="https://img.shields.io/badge/-Python%203-3776AB?logo=python&logoColor=white&label=" height="20"/>:** Full adaptation to modern working environments (starting from <img src="https://img.shields.io/badge/-Kodi%2019+-17B2E7?logo=kodi&logoColor=white&label=" height="20"/> and above), ensuring compatibility with all current versions.

**Independent Search Engine 🔍:** Unlike Philipp's original extension — which relied on external libraries (like `requests` and third-party dependencies) suffering from a lack of updates and an old Python 2 codebase — the CoreELEC-IL version is built on a fully independent engine.

**"All-in-One" Experience 📦:** The beauty of this addon is that everything lives under one roof. Unlike the original version, which required installing cumbersome external dependencies, here the system relies on the libraries already built into your Kodi.

**Cross-Platform Compatibility 🌐:** Thanks to its independent architecture, the addon guarantees full support and great performance on any platform (📦 CoreELEC, 🤖 Android, 🪟 Windows, 🐧 Linux) or any other OS running Kodi.

**The Result ✨:** The built-in search slowness and the wrong-results issue that characterized the previous version have both been eliminated. The system is now lighter, more stable, and significantly faster.

**Requires a Supporting Skin 🎨:** The addon requires a skin that supports custom search to display autocomplete results properly (such as Estuary or skins based on it).

> ⚠️ **Important Note:** On some skins, make sure in the skin settings that the "AutoCompletion" addon option is enabled, and that the correct Provider for "CoreELEC-IL" is selected.

🆕 **What's new in `v3.0.1`:** Resolved a bug in search-term cleaning and a leftover-character issue.

---

### 🛡️ Safe Boot Manager `[CoreELEC-IL Exclusive]`
> The addon that keeps your system smooth and stable — from the moment it boots up until the moment it shuts down.

`v1.0.5` 🟢 · [📦 Download ZIP](https://github.com/kicking-bird-py/coreelec-il/tree/main/zips/service.safeboot.manager) · [📂 Source Code](https://github.com/kicking-bird-py/coreelec-il/tree/main/src/service.safeboot.manager)

<p>
<img src="https://img.shields.io/badge/Python%203-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python 3"/>
<img src="https://img.shields.io/badge/Kodi%20Service-17B2E7?style=for-the-badge&logo=kodi&logoColor=white" alt="Kodi Service"/>
<img src="https://img.shields.io/badge/Token%20Masking-FF3D3D?style=for-the-badge&logo=shieldsdotio&logoColor=white" alt="Token Masking"/>
<img src="https://img.shields.io/badge/English%20UI-2CA5E0?style=for-the-badge" alt="English UI"/>
</p>

Safe Boot Manager 🧠: is an original, exclusive project of mine, written from scratch. The need for it arose from dealing with "lightweight" operating systems (Lightweight OS) such as LibreELEC and CoreELEC, known for their high sensitivity to even the smallest system changes. On these systems, excessive remote button presses or momentary load spikes during boot can lead to freezes or crashes, so I built this addon as an active protection mechanism that ensures the system stays stable at every moment.

> ⚖️ **More importantly:** The addon solves the well-known dilemma with "heavy" skins — no matter which skin you use, Safe Boot Manager knows how to manage your streamer's resources optimally, so the user experience stays smooth, fast, and stutter-free even under graphical load.

#### ⚙️ Technical Specs & Improvements

**Boot Protection Mechanism**

🔒 Prevents unnecessary remote presses while the system is booting by displaying a blocking interface until loading is complete.

🧹 Automatically cleans temporary files on every boot, while preserving critical system files like logs and UI assets.

⏳ Automatically waits for system stability (preventing load during library or PVR scans) before releasing the lock to the user.

**Maintaining Stability 🧘**

📡 Continuous system monitoring; when load is detected (video library scan, PVR scan, or a "Busy" window), the system automatically activates a blocking interface to prevent disruptions.

**Enhanced Playback Experience 🎬**

🔙 A background-based mechanism that detects 3 presses of the "Back" button within one second. The system performs a controlled, independent exit from the player — you can see the player close smoothly. This feature saves you the unnecessary effort of hunting for the "stop" button every time to stop playback.

🌀 Smart loading messages that appear when starting a movie/show and when playback ends, creating a seamless visual experience.

**🔐 Security, Privacy & Provider Sync Management**

🔗 **Smart Sync:** From the moment you install the addon, it scans and automatically detects your service providers (Trakt, TorBox, AllDebrid, Real-Debrid, Premiumize, EasyNews). Instead of manually searching for how to set up each provider, the addon actively offers you the provider connections in the addon's settings, which open automatically once installation finishes. You can easily enable or disable each provider in the settings window, but you must restart Kodi for the changes to take effect.

> 🔴💡 **Note:** The addon is built to work alongside the POV addon and uses it to send searches to the scrapers. It's recommended to install POV so the addon functions optimally.

🥷 **Token Masking Mechanism:** A unique implementation that ensures no full access Token (API Token) is ever written to the log file. Only the last 4 characters are shown for identification purposes, preventing exposure of credentials when sharing logs (Log Sharing).

✅ **Connection Check:** For each provider you've selected, the addon automatically checks on every boot whether you're connected, and shows you a clear visual indicator — connected or not connected — with a quick-connect prompt if a Token is missing.

#### 🎨 User Interface

🪶 **Lightweight Design:** Graphic elements are created dynamically, ensuring proper operation on any skin.

🚫 **Active Blocking:** A built-in mechanism that prevents remote button presses from reaching the system while the interface is active.

📊 **Progress Indicators:** Displays progress percentages and process names (provider checks, temp cleanup, waiting for system) in English (full localization).

#### 🛡️ Quality Assurance & Development

🔬 Over two months of intensive development and from-scratch coding went into this addon. Every line went through rigorous lab testing on a Homatics 4K Box streamer to ensure flawless performance and full hardware compatibility. Every update released to the GitHub repository goes through a comprehensive, thorough performance test suite before being released to the public. This policy is meant to ensure the addon is stable and reliable, with no compromises. That's why there's no rushed or aggressive update cadence — I choose an approach of absolute stability and long-term reliability over frequent changes.

🆕 **What's new in `v1.0.5`:** Translation bug fixes and a settings file update.

Originally built from scratch — no external dependencies, stable and fast.

---

## 🌱 Open Source, Open Heart

Every addon here is released under **GPL-3.0**. Learn from it, share it, use it — and if my code helped you, fair credit is the fuel that keeps me building 🔥

🐛 Found a bug? Open an **Issue** on <a href="https://github.com/kicking-bird-py/coreelec-il/issues"><img src="https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white&label=" height="20"/></a>

⭐ Enjoyed it? Give the project a **star**

☕ Want to treat me? Buy me a virtual coffee on [Ko-fi](https://ko-fi.com/kicking_bird_py)

<div align="center">

**Originally built from scratch — simple, stable, clean.** 🌵

</div>
