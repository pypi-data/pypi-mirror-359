# crackify

**Terminal-based Spotify artist autostreamer (headless, requires librespot).**

Stream any Spotify artist’s entire catalog in an infinite loop, directly from your terminal, with no need for the Spotify client. Built for automation, bots, or hands-free music streaming.

---

## 🚨 Legal Notice

> **This project is UNOFFICIAL and not affiliated with Spotify.**
>
> By using `crackify`, you accept that it utilizes reverse-engineered streaming with [`librespot`](https://github.com/librespot-org/librespot), which may violate Spotify's Terms of Service. Use at your own risk, for educational or demonstration purposes only.

---

## Features

- Headless/terminal-based audio streaming—no Spotify app needed
- Autostreams all public tracks for any artist (loops forever)
- Minimal Python API: `import crackify; crackify.autostream(...)`
- Requires only Python and the [librespot](https://github.com/librespot-org/librespot) binary

---

## Installation

**1. Install crackify from PyPI:**
```sh
pip install crackify