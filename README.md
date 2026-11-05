# 🧬 DevReplicant

[![CI](https://github.com/Scempyyy/DevReplicant/actions/workflows/ci.yml/badge.svg)](https://github.com/Scempyyy/DevReplicant/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Zero External Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](#zero-dependencies)

> **Universal developer environment snapshotter, restore script generator, and Docker container re-hydration engine.**

---

## ⚡ What is DevReplicant?

Setting up a new development machine, laptop, or cloud dev container typically takes hours of tedious manual installations, chasing missing packages, reconstructing config files, and reinstalling IDE plugins.

**DevReplicant** automates machine replication into reproducible, single-click artifacts:
- 📦 **Package Manager Discovery**: Inspects APT, Pacman, Pip, NPM global, Cargo, and Flatpak for explicitly installed packages.
- 🛠️ **Runtime & Compiler Auditing**: Detects Git, Node, Python, Docker, Rust, Go, Java, GitHub CLI, and tool versions.
- ⚙️ **Config & Identity Preservation**: Safely captures `.gitconfig`, environment variables, and shell aliases without exposing secrets.
- 💻 **IDE Extensions**: Inventories installed VS Code extensions (`code --list-extensions`) for instant reinstallation.
- 🚀 **1-Click Re-hydration**: Generates an idempotent `restore.sh` bash script, portable `manifest.json`, and an Ubuntu `Dockerfile` that re-creates your exact workspace.
- 🎨 **Local Cyber Console**: Modern dark-mode interface to inspect your machine state and download restore bundles.

---

## 🏗️ Re-hydration Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Target Workstation                   │
│   • Linux OS / Kernel   • Git identity                 │
│   • APT / Pip / NPM     • VS Code Plugins              │
└───────────────────────────┬────────────────────────────┘
                            │
               (devreplicant snapshot)
                            ▼
           ┌──────────────────────────────────┐
           │     DevReplicant Scan Engine     │
           │  • Filters system-installed pkgs │
           │  • Sanitizes secret credentials  │
           └────────────────┬─────────────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
┌──────────────┐     ┌─────────────┐      ┌─────────────┐
│manifest.json │     │ restore.sh  │      │ Dockerfile  │
│Machine Spec  │     │ Bash Script │      │ Container   │
└──────────────┘     └─────────────┘      └─────────────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                            ▼
              [ New Laptop / Cloud Server / VM ]
               Single command restoration!
```

---

## 🚀 Quickstart

### 1. Launch Interactive Studio

```bash
# Clone the repository
git clone https://github.com/Scempyyy/DevReplicant.git
cd DevReplicant

# Start the local studio server
python3 devreplicant.py serve
```

Open your browser to **`http://localhost:8960`**.

### 2. Export via CLI

Capture your machine's environment directly into files:

```bash
# Export JSON manifest, restore script, and Dockerfile
python3 devreplicant.py snapshot \
  --output manifest.json \
  --export-script restore.sh \
  --export-docker Dockerfile
```

### 3. Rehydrate on a New Machine

Transfer `restore.sh` to your target machine and run:

```bash
chmod +x restore.sh
./restore.sh
```

---

## 🧪 Testing

```bash
python3 -m unittest discover tests -v
```

---

## 📄 License

DevReplicant is open-source software licensed under the **[MIT License](LICENSE)**. Created by [Scempyyy](https://github.com/Scempyyy).
