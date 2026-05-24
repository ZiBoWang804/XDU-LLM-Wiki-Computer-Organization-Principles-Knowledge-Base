from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from mineru import MinerU


REPO_ROOT = Path(__file__).resolve().parents[1]
TEXTBOOK_DIR = REPO_ROOT / "资料" / "教材"
KB_ROOT = REPO_ROOT / "知识库"
TEXTBOOK_DRAFT_DIR = KB_ROOT / "资料整理稿" / "教材"
TEXTBOOK_INDEX = TEXTBOOK_DRAFT_DIR / "index.md"
ENV_FILE = REPO_ROOT / ".env"
MANIFEST_FILE = TEXTBOOK_DRAFT_DIR / "manifest.json"


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


def slugify(name: str) -> str:
    stem = Path(name).stem
    cleaned = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", stem, flags=re.UNICODE)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or "untitled"


def chapter_hint(filename: str) -> str:
    match = re.search(r"第(\d+)章", filename)
    if match:
        return f"第{match.group(1)}章"
    match = re.search(r"-(\d{3})-(\d{3})", filename)
    if match:
        return "附录/后续章节"
    return "待归类"


@dataclass
class SourceRecord:
    filename: str
    slug: str
    chapter: str
    draft_md: str
    raw_markdown: str
    assets_dir: str
    source_pdf: str
    task_id: str


def ensure_dirs() -> None:
    for path in [
        KB_ROOT,
        KB_ROOT / "资料整理稿",
        TEXTBOOK_DRAFT_DIR,
        KB_ROOT / "知识点",
        KB_ROOT / "图像解读",
        KB_ROOT / "勘误",
        KB_ROOT / "分歧",
        KB_ROOT / "个人演化",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def write_root_indexes() -> None:
    files: dict[Path, str] = {
        KB_ROOT / "index.md": """# 计算机组成原理知识库

## 主入口
- [资料整理稿](./资料整理稿/index.md)
- [知识点](./知识点/index.md)
- [图像解读](./图像解读/index.md)
- [勘误](./勘误/index.md)
- [分歧](./分歧/index.md)
- [个人演化](./个人演化/index.md)
""",
        KB_ROOT / "资料整理稿" / "index.md": """# 资料整理稿索引

## 子目录
- [教材](./教材/index.md)
""",
        KB_ROOT / "知识点" / "index.md": """# 知识点索引

当前尚未正式抽取知识点正文。后续应从资料整理稿中稳定沉淀。
""",
        KB_ROOT / "图像解读" / "index.md": """# 图像解读索引

存放复杂图、结构图、模糊页、表格页的单独解释稿。
""",
        KB_ROOT / "勘误" / "index.md": """# 勘误索引

记录原始资料中的已确认错误及其影响范围。
""",
        KB_ROOT / "分歧" / "index.md": """# 分歧索引

记录不同资料之间的说法差异与当前采用依据。
""",
        KB_ROOT / "个人演化" / "index.md": """# 个人演化索引

记录个人理解、类比、替代解法、追问与待确认质疑。
""",
    }
    for path, content in files.items():
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def wrap_draft(record: SourceRecord, extracted_markdown: str) -> str:
    return f"""---
title: {record.slug}
type: textbook_draft
chapter: {record.chapter}
source_pdf: {record.source_pdf}
raw_markdown: {record.raw_markdown}
assets_dir: {record.assets_dir}
task_id: {record.task_id}
status: extracted
---

# {record.slug}

## 来源

- 原始文件：`{record.filename}`
- 对应章节：`{record.chapter}`
- 原始 PDF：`{record.source_pdf}`
- 抽取任务：`{record.task_id}`

## 后续处理建议

- 从本整理稿中抽取稳定知识点
- 检查公式、表格、结构图抽取质量
- 对复杂图页补单独图像解读稿
- 如发现错误，转入勘误或分歧

## MinerU 抽取结果

{extracted_markdown}
"""


def save_manifest(records: list[SourceRecord]) -> None:
    payload = {
        "records": [
            {
                "filename": r.filename,
                "slug": r.slug,
                "chapter": r.chapter,
                "draft_md": r.draft_md,
                "raw_markdown": r.raw_markdown,
                "assets_dir": r.assets_dir,
                "source_pdf": r.source_pdf,
                "task_id": r.task_id,
            }
            for r in records
        ]
    }
    MANIFEST_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_index(records: list[SourceRecord]) -> None:
    lines = [
        "# 教材资料整理稿索引",
        "",
        "## 已入库教材",
    ]
    for record in records:
        rel = Path(record.draft_md).relative_to(TEXTBOOK_DRAFT_DIR).as_posix()
        lines.append(f"- [{record.filename}](./{rel}) | {record.chapter}")
    lines.append("")
    lines.append("## 说明")
    lines.append("- 本层是证据层，不是知识点规范层。")
    lines.append("- 默认先读知识点页；知识点不够时，再回读这些整理稿。")
    TEXTBOOK_INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    env_data = load_simple_env(ENV_FILE)
    for key, value in env_data.items():
        os.environ.setdefault(key, value)

    token = os.environ.get("MINERU_TOKEN")
    if not token:
        raise SystemExit("MINERU_TOKEN 未配置，无法开始教材入库。")

    ensure_dirs()
    write_root_indexes()

    model = os.environ.get("MINERU_MODEL", "pipeline")
    language = os.environ.get("MINERU_LANGUAGE", "zh")
    enable_formula = os.environ.get("MINERU_ENABLE_FORMULA", "true").lower() == "true"
    enable_table = os.environ.get("MINERU_ENABLE_TABLE", "true").lower() == "true"

    records: list[SourceRecord] = []
    with MinerU(token=token) as client:
        pdf_files = sorted(TEXTBOOK_DIR.glob("*.pdf"))
        for pdf_path in pdf_files:
            slug = slugify(pdf_path.name)
            target_dir = TEXTBOOK_DRAFT_DIR / slug
            target_dir.mkdir(parents=True, exist_ok=True)

            extract_kwargs = {
                "model": model,
                "formula": enable_formula,
                "table": enable_table,
                "timeout": 1800,
            }
            if language and language.lower() not in {"auto", "none", "default", "zh"}:
                extract_kwargs["language"] = language

            result = client.extract(str(pdf_path), **extract_kwargs)

            raw_md_path = target_dir / "raw-extract.md"
            result.save_markdown(str(raw_md_path), with_images=True)

            record = SourceRecord(
                filename=pdf_path.name,
                slug=slug,
                chapter=chapter_hint(pdf_path.name),
                draft_md=str((target_dir / f"{slug}.md").resolve()),
                raw_markdown=str(raw_md_path.resolve()),
                assets_dir=str((target_dir / "images").resolve()),
                source_pdf=str(pdf_path.resolve()),
                task_id=result.task_id,
            )
            wrapped = wrap_draft(record, result.markdown or "")
            Path(record.draft_md).write_text(wrapped, encoding="utf-8")
            records.append(record)

    save_manifest(records)
    save_index(records)
    print(json.dumps({"status": "ok", "processed": len(records), "index": str(TEXTBOOK_INDEX)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
