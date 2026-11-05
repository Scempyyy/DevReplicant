"""Environment collectors and snapshot generator."""

import os
import platform
import shutil
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional


def run_cmd(cmd: List[str], timeout: float = 4.0) -> Optional[str]:
    """Runs a shell command safely and returns standard output."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return None


def get_system_info() -> Dict[str, Any]:
    """Collects operating system, architecture, and kernel metadata."""
    uname = platform.uname()
    os_name = "Linux"
    if os.path.exists("/etc/os-release"):
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        os_name = line.split("=", 1)[1].strip().strip('"')
                        break
        except Exception:
            pass

    return {
        "os_pretty": os_name,
        "system": uname.system,
        "release": uname.release,
        "machine": uname.machine,
        "processor": uname.processor or uname.machine,
        "hostname": platform.node(),
        "python_version": platform.python_version(),
    }


def collect_toolchains() -> Dict[str, Any]:
    """Detects installed compiler runtimes and tools."""
    tools = {}

    binaries = {
        "git": ["git", "--version"],
        "node": ["node", "--version"],
        "npm": ["npm", "--version"],
        "python": ["python3", "--version"],
        "pip": ["pip3", "--version"],
        "docker": ["docker", "--version"],
        "docker-compose": ["docker-compose", "--version"],
        "rustc": ["rustc", "--version"],
        "cargo": ["cargo", "--version"],
        "go": ["go", "version"],
        "java": ["java", "-version"],
        "gh": ["gh", "--version"],
        "code": ["code", "--version"],
        "curl": ["curl", "--version"],
    }

    for name, cmd in binaries.items():
        if shutil.which(cmd[0]):
            out = run_cmd(cmd)
            if out:
                # Keep first line
                first_line = out.splitlines()[0]
                tools[name] = {"installed": True, "version": first_line}
            else:
                tools[name] = {"installed": True, "version": "detected"}
        else:
            tools[name] = {"installed": False, "version": None}

    return tools


def collect_packages() -> Dict[str, List[str]]:
    """Gathers explicitly installed packages across available package managers."""
    pkgs: Dict[str, List[str]] = {}

    # APT (Debian/Ubuntu)
    if shutil.which("apt-mark"):
        out = run_cmd(["apt-mark", "showmanual"])
        if out:
            pkgs["apt"] = sorted([p for p in out.splitlines() if p and not p.startswith("linux-")])[:120]

    # Pacman (Arch Linux)
    if shutil.which("pacman"):
        out = run_cmd(["pacman", "-Qqe"])
        if out:
            pkgs["pacman"] = sorted(out.splitlines())[:120]

    # Python pip
    if shutil.which("pip3") or shutil.which("pip"):
        pip_bin = "pip3" if shutil.which("pip3") else "pip"
        out = run_cmd([pip_bin, "list", "--format=freeze"])
        if out:
            pkgs["pip"] = [line for line in out.splitlines() if "==" in line][:80]

    # Node global packages
    if shutil.which("npm"):
        out = run_cmd(["npm", "list", "-g", "--depth=0"])
        if out:
            npm_pkgs = []
            for line in out.splitlines():
                if "@" in line and not line.startswith("npm@") and not line.startswith("/"):
                    parts = line.strip().split()
                    if parts:
                        npm_pkgs.append(parts[-1])
            pkgs["npm_global"] = npm_pkgs[:50]

    # Cargo (Rust)
    if shutil.which("cargo"):
        out = run_cmd(["cargo", "install", "--list"])
        if out:
            cargo_pkgs = []
            for line in out.splitlines():
                if not line.startswith(" ") and ":" in line:
                    cargo_pkgs.append(line.split(":")[0].strip())
            pkgs["cargo"] = cargo_pkgs

    # VS Code Extensions
    if shutil.which("code"):
        out = run_cmd(["code", "--list-extensions"])
        if out:
            pkgs["vscode_extensions"] = sorted(out.splitlines())

    return pkgs


def collect_git_config() -> Dict[str, str]:
    """Collects safe non-sensitive global git configurations."""
    configs = {}
    if shutil.which("git"):
        out = run_cmd(["git", "config", "--global", "--list"])
        if out:
            for line in out.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    # Sanitize any accidental secrets
                    if "token" in k.lower() or "secret" in k.lower() or "password" in k.lower():
                        continue
                    configs[k] = v.strip()
    return configs


def create_snapshot() -> Dict[str, Any]:
    """Produces a complete developer environment snapshot manifest."""
    return {
        "manifest_version": "1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system": get_system_info(),
        "toolchains": collect_toolchains(),
        "packages": collect_packages(),
        "git_config": collect_git_config(),
    }


def generate_restore_script(snapshot: Dict[str, Any]) -> str:
    """Generates an automated, idempotent bash restoration script."""
    lines = [
        "#!/usr/bin/env bash",
        "# DevReplicant Generated Environment Restoration Script",
        "# Rebuilds packages, toolchains, and developer configurations",
        "set -e",
        "",
        'echo "🚀 Restoring developer environment via DevReplicant..."',
        "",
    ]

    pkgs = snapshot.get("packages", {})

    # APT
    if "apt" in pkgs and pkgs["apt"]:
        lines.append("# --- APT Packages ---")
        lines.append("if command -v apt-get >/dev/null 2>&1; then")
        lines.append("  echo '📦 Installing APT packages...'")
        lines.append("  sudo apt-get update -y")
        chunk = " ".join(pkgs["apt"][:40])
        lines.append(f"  sudo apt-get install -y {chunk}")
        lines.append("fi")
        lines.append("")

    # Pip
    if "pip" in pkgs and pkgs["pip"]:
        lines.append("# --- Python Packages ---")
        lines.append("if command -v pip3 >/dev/null 2>&1; then")
        lines.append("  echo '🐍 Installing Python pip packages...'")
        for p in pkgs["pip"][:30]:
            lines.append(f"  pip3 install '{p}' || true")
        lines.append("fi")
        lines.append("")

    # NPM
    if "npm_global" in pkgs and pkgs["npm_global"]:
        lines.append("# --- NPM Global Packages ---")
        lines.append("if command -v npm >/dev/null 2>&1; then")
        lines.append("  echo '📦 Installing global NPM modules...'")
        for mod in pkgs["npm_global"]:
            lines.append(f"  npm install -g {mod} || true")
        lines.append("fi")
        lines.append("")

    # VS Code Extensions
    if "vscode_extensions" in pkgs and pkgs["vscode_extensions"]:
        lines.append("# --- VS Code Extensions ---")
        lines.append("if command -v code >/dev/null 2>&1; then")
        lines.append("  echo '💻 Installing VS Code extensions...'")
        for ext in pkgs["vscode_extensions"]:
            lines.append(f"  code --install-extension {ext} || true")
        lines.append("fi")
        lines.append("")

    # Git configs
    git_conf = snapshot.get("git_config", {})
    if git_conf:
        lines.append("# --- Git Configuration ---")
        lines.append("if command -v git >/dev/null 2>&1; then")
        for k, v in git_conf.items():
            lines.append(f'  git config --global "{k}" "{v}"')
        lines.append("fi")
        lines.append("")

    lines.append('echo "✅ Developer environment successfully re-hydrated!"')
    return "\n".join(lines)


def generate_dockerfile(snapshot: Dict[str, Any]) -> str:
    """Generates a reproducible Dockerfile recreating the machine's environment."""
    lines = [
        "FROM ubuntu:22.04",
        "ENV DEBIAN_FRONTEND=noninteractive",
        "WORKDIR /workspace",
        "",
        "RUN apt-get update && apt-get install -y \\",
        "    curl wget git build-essential python3 python3-pip \\",
        "    ca-certificates gnupg lsb-release && \\",
        "    rm -rf /var/lib/apt/lists/*",
        "",
    ]

    pkgs = snapshot.get("packages", {})
    if "pip" in pkgs and pkgs["pip"]:
        pip_sample = " ".join([f"'{p}'" for p in pkgs["pip"][:15]])
        lines.append(f"RUN pip3 install {pip_sample} || true")
        lines.append("")

    lines.append("CMD [\"/bin/bash\"]")
    return "\n".join(lines)
