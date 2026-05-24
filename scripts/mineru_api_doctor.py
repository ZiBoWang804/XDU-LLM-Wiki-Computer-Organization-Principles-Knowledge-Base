from __future__ import annotations

import json
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / ".env"


def load_simple_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip().lstrip("\ufeff")] = value.strip()
    return data


env_data = load_simple_env(ENV_FILE)
for key, value in env_data.items():
    os.environ.setdefault(key, value)

report = {
    "env_file": str(ENV_FILE),
    "env_file_exists": ENV_FILE.exists(),
    "mineru_token_present": bool(os.environ.get("MINERU_TOKEN")),
    "mineru_model": os.environ.get("MINERU_MODEL", "pipeline"),
    "mineru_language": os.environ.get("MINERU_LANGUAGE", "zh"),
    "mineru_enable_formula": os.environ.get("MINERU_ENABLE_FORMULA", "true"),
    "mineru_enable_table": os.environ.get("MINERU_ENABLE_TABLE", "true"),
}

try:
    from mineru import MinerU  # type: ignore
    from mineru.exceptions import AuthError, TaskNotFoundError, MinerUError  # type: ignore

    client = MinerU(token=os.environ.get("MINERU_TOKEN"))
    report["sdk_import"] = "ok"
    report["sdk_class"] = "MinerU"
    report["base_mode"] = "auth" if os.environ.get("MINERU_TOKEN") else "flash-only"
    if os.environ.get("MINERU_TOKEN"):
        try:
            client.get_task("codex-auth-probe")
            report["auth_probe"] = {"status": "unexpected-success"}
        except TaskNotFoundError as exc:
            report["auth_probe"] = {"status": "ok", "detail": str(exc)}
        except AuthError as exc:
            report["auth_probe"] = {"status": "auth_failed", "detail": str(exc)}
        except MinerUError as exc:
            report["auth_probe"] = {"status": "api_reached", "detail": str(exc)}
    client.close()
except Exception as exc:  # pragma: no cover
    report["sdk_import"] = "failed"
    report["error"] = str(exc)

print(json.dumps(report, ensure_ascii=False, indent=2))
