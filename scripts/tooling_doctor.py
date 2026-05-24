from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parents[1]


def module_status(name: str) -> dict[str, str]:
    try:
        mod = importlib.import_module(name)
        version = getattr(mod, "__version__", "unknown")
        return {"status": "ok", "version": str(version)}
    except Exception as exc:
        return {"status": "missing", "detail": str(exc)}


def file_status(path: Path) -> dict[str, str]:
    return {"status": "ok" if path.exists() else "missing", "path": str(path)}


def resolve_windows_shortcut(path: Path) -> Optional[str]:
    try:
        import win32com.client  # type: ignore

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(path))
        target = shortcut.TargetPath
        return str(target) if target else None
    except Exception:
        return None


def find_obsidian() -> str | None:
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Obsidian" / "Obsidian.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Obsidian" / "Obsidian.exe",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Obsidian" / "Obsidian.exe",
        Path("D:/Obsidian/Obsidian.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    shortcut_candidates = [
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Obsidian.lnk",
        Path(os.environ.get("ProgramData", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Obsidian.lnk",
    ]
    for shortcut in shortcut_candidates:
        if shortcut.exists():
            target = resolve_windows_shortcut(shortcut)
            if target and Path(target).exists():
                return target
    return None


def global_module_status(python_cmd: str, module_name: str) -> dict[str, str]:
    try:
        completed = subprocess.run(
            [python_cmd, "-c", f"import {module_name}; print(getattr({module_name}, '__version__', 'unknown'))"],
            capture_output=True,
            text=True,
            timeout=20,
            check=True,
        )
        return {"status": "ok", "version": completed.stdout.strip() or "unknown", "python": python_cmd}
    except Exception as exc:
        return {"status": "missing", "detail": str(exc), "python": python_cmd}


obsidian_path = find_obsidian()
report = {
    "python": sys.version.split()[0],
    "repo_root": str(REPO_ROOT),
    "venv": file_status(REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
    "core_modules": {
        "yaml": module_status("yaml"),
        "markdown": module_status("markdown"),
        "markitdown": module_status("markitdown"),
        "mineru": module_status("mineru"),
    },
    "optional_modules": {
        "magic_pdf": module_status("magic_pdf"),
        "paddleocr": module_status("paddleocr"),
        "paddleocr_global": global_module_status("python", "paddleocr"),
    },
    "obsidian": {"status": "ok", "path": obsidian_path} if obsidian_path else {"status": "missing"},
    "files": {
        "AGENTS.md": file_status(REPO_ROOT / "AGENTS.md"),
        "CODEX.md": file_status(REPO_ROOT / "CODEX.md"),
        "architecture-overview.md": file_status(REPO_ROOT / "architecture-overview.md"),
    },
}

print(json.dumps(report, ensure_ascii=False, indent=2))
