from __future__ import annotations

import json
import os
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

from mineru import MinerU

RUNTIME_PYTHON_SITE = Path(
    r"C:\Users\Zibo wang\.cache\codex-runtimes\codex-primary-runtime\dependencies\python"
)
if RUNTIME_PYTHON_SITE.exists():
    sys.path.append(str(RUNTIME_PYTHON_SITE))

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None


REPO_ROOT = Path(__file__).resolve().parents[1]
KB_ROOT = REPO_ROOT / "知识库"
DRAFT_ROOT = KB_ROOT / "资料整理稿"
ENV_FILE = REPO_ROOT / ".env"

MARKDOWN_EXTS = {".md", ".txt"}
DOCX_EXTS = {".docx"}
PPTX_EXTS = {".pptx"}
PDF_EXTS = {".pdf"}
SUPPORTED_EXTS = MARKDOWN_EXTS | DOCX_EXTS | PPTX_EXTS | PDF_EXTS
IMAGE_MD_RE = re.compile(r"!\[\]\((images/[^)]+)\)")
ZERO_WIDTH_CHARS = ("\ufeff", "\u200b", "\u200c", "\u200d", "\u2060")


@dataclass
class CategorySpec:
    name: str
    source_dirs: list[Path]
    output_dir: Path
    draft_type: str


CATEGORIES: list[CategorySpec] = [
    CategorySpec(
        name="课件",
        source_dirs=[REPO_ROOT / "资料" / "课件"],
        output_dir=DRAFT_ROOT / "课件",
        draft_type="courseware_draft",
    ),
    CategorySpec(
        name="笔记",
        source_dirs=[REPO_ROOT / "资料" / "笔记"],
        output_dir=DRAFT_ROOT / "笔记",
        draft_type="note_draft",
    ),
    CategorySpec(
        name="作业",
        source_dirs=[REPO_ROOT / "作业", REPO_ROOT / "资料" / "部分作业题"],
        output_dir=DRAFT_ROOT / "作业",
        draft_type="homework_draft",
    ),
    CategorySpec(
        name="试卷",
        source_dirs=[REPO_ROOT / "资料" / "历年考试卷"],
        output_dir=DRAFT_ROOT / "试卷",
        draft_type="exam_draft",
    ),
]


def load_simple_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip().lstrip("\ufeff")] = value.strip()
    return data


def read_text_flexible(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def slugify_relative(path: Path) -> str:
    raw = path.as_posix().replace("/", "-")
    cleaned = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", raw, flags=re.UNICODE)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or "untitled"


def sanitize_markdown_text(text: str) -> str:
    text = normalize_extracted_text(text)
    # 保留正文文本，去掉内嵌图片行，避免源 markdown 中相对路径失效。
    lines = []
    for line in text.splitlines():
        if line.strip().startswith("![](") or line.strip().startswith("!["):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def normalize_extracted_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    for ch in ZERO_WIDTH_CHARS:
        text = text.replace(ch, "")
    text = text.replace("\xa0", " ")
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def polish_reviewed_markdown(text: str) -> str:
    text = normalize_extracted_text(text)
    lines = text.splitlines()
    cleaned: list[str] = []
    in_code_block = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            cleaned.append(line)
            continue
        if in_code_block:
            cleaned.append(line)
            continue

        line = re.sub(r"^\\-\s*", "- ", line)
        line = re.sub(r"^•\s*", "- ", line)
        line = re.sub(r"^#\s+-\s*", "# ", line)
        line = re.sub(r"^#\s+一(指令系统|CPU设计|数制表示|绪论|运算方法|存储系统)", r"# \1", line)
        line = line.replace("# 温故 一关于", "# 温故 — 关于")
        line = line.replace("\\~", "~")
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def bool_env(key: str, default: bool) -> bool:
    return os.environ.get(key, str(default).lower()).strip().lower() == "true"


def count_cjk(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def markdown_quality_signals(text: str) -> dict[str, int]:
    cleaned = sanitize_markdown_text(text)
    non_empty_lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    return {
        "char_count": len(cleaned),
        "line_count": len(non_empty_lines),
        "cjk_count": count_cjk(cleaned),
        "image_ref_count": len(IMAGE_MD_RE.findall(text)),
        "replacement_char_count": text.count("\ufffd"),
        "formula_token_count": text.count("$$") + text.count("\\(") + text.count("\\["),
        "heading_count": len([line for line in non_empty_lines if line.startswith("#")]),
        "short_line_count": len([line for line in non_empty_lines if len(line) <= 2]),
    }


def assess_extracted_markdown(text: str, image_count: int = 0) -> tuple[str, list[str], dict[str, int]]:
    signals = markdown_quality_signals(text)
    effective_image_count = max(image_count, signals["image_ref_count"])
    reasons: list[str] = []

    if signals["char_count"] < 400:
        reasons.append("正文字符数过低")
    if signals["line_count"] < 20:
        reasons.append("非空行数过低")
    if signals["replacement_char_count"] >= 1:
        reasons.append("出现 replacement character，疑似乱码或截断")
    if effective_image_count >= 20 and signals["char_count"] < 1500:
        reasons.append("图片很多但正文过短")
    if effective_image_count >= 50 and signals["cjk_count"] < 200:
        reasons.append("图片型文档中文正文过少")
    if signals["heading_count"] <= 2 and signals["char_count"] < 1200:
        reasons.append("标题层级稀少且正文不足，疑似只抽到模板头")

    if reasons:
        return "reject", reasons, signals

    warnings: list[str] = []
    if effective_image_count >= 80 and signals["char_count"] < 6000:
        warnings.append("图片密集型文档，建议后续重点抽检")
    if signals["short_line_count"] >= max(20, signals["line_count"] // 3):
        warnings.append("短行比例较高，可能存在版式碎裂")

    if warnings:
        return "warn", warnings, signals
    return "pass", [], signals


def should_reextract_existing(draft_path: Path, raw_md_path: Path, assets_dir: Path | None) -> tuple[bool, str]:
    draft_text = read_text_flexible(draft_path) if draft_path.exists() else ""
    raw_text = read_text_flexible(raw_md_path) if raw_md_path.exists() else ""
    image_count = len(list(assets_dir.glob("*"))) if assets_dir and assets_dir.exists() else 0
    if "MinerU 云端提取失败" in raw_text:
        return True, "existing_raw_contains_failure_marker"
    verdict, reasons, _signals = assess_extracted_markdown(raw_text or draft_text, image_count=image_count)
    if verdict == "reject":
        return True, f"existing_extract_quality_reject:{'|'.join(reasons)}"
    return False, "existing_extract_accepted"


def inspect_pdf_binary_signals(path: Path, sample_bytes: int = 2_000_000) -> dict[str, int]:
    with path.open("rb") as fh:
        data = fh.read(sample_bytes)
    return {
        "image_obj_count": data.count(b"/Subtype /Image") + data.count(b"/Subtype/Image"),
        "font_obj_count": data.count(b"/Font"),
        "text_op_count": data.count(b" Tj") + data.count(b" TJ") + data.count(b"BT") + data.count(b"ET"),
        "to_unicode_count": data.count(b"/ToUnicode"),
    }


def infer_pdf_ocr_mode(path: Path, target_dir: Path) -> tuple[bool, str, dict[str, int]]:
    raw_md_path = target_dir / "raw-extract.md"
    if raw_md_path.exists():
        prior_text = read_text_flexible(raw_md_path)
        prior = markdown_quality_signals(prior_text)
        if "MinerU 云端提取失败" in prior_text:
            return True, "prior_mineru_failed", prior
        if prior["replacement_char_count"] >= 20:
            return True, "prior_extract_garbled", prior
        if prior["char_count"] >= 1200 and prior["cjk_count"] >= 200:
            return False, "prior_extract_text_ok", prior
        if prior["image_ref_count"] >= 8 and prior["char_count"] <= 400:
            return True, "prior_extract_image_heavy", prior

    binary = inspect_pdf_binary_signals(path)
    if binary["image_obj_count"] >= 8 and binary["font_obj_count"] <= 1 and binary["text_op_count"] <= 4:
        return True, "binary_signals_image_pdf", binary
    if binary["font_obj_count"] >= 3 or binary["to_unicode_count"] >= 1 or binary["text_op_count"] >= 6:
        return False, "binary_signals_text_pdf", binary
    return False, "default_editable_pdf", binary


def iter_source_files(source_dir: Path) -> Iterable[Path]:
    if not source_dir.exists():
        return []
    files: list[Path] = []
    for path in source_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.parts):
            continue
        if "_assets" in path.parts:
            continue
        if path.suffix.lower() not in SUPPORTED_EXTS:
            continue
        if path.stat().st_size == 0:
            continue
        files.append(path)
    return sorted(files)


def extract_docx_text(path: Path) -> str:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    paragraphs: list[str] = []
    for para in root.findall(".//w:p", ns):
        texts = [node.text or "" for node in para.findall(".//w:t", ns)]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return "\n\n".join(paragraphs).strip()


def extract_pptx_text(path: Path) -> str:
    ns = {
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    }
    slides: list[tuple[int, str]] = []
    with zipfile.ZipFile(path) as zf:
        slide_names = sorted(
            [name for name in zf.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml")],
            key=lambda name: int(re.search(r"slide(\d+)\.xml", name).group(1)),
        )
        for slide_name in slide_names:
            slide_no = int(re.search(r"slide(\d+)\.xml", slide_name).group(1))
            root = ET.fromstring(zf.read(slide_name))
            texts = [node.text or "" for node in root.findall(".//a:t", ns)]
            body = "\n".join([text.strip() for text in texts if text.strip()]).strip()
            if body:
                slides.append((slide_no, body))
    parts = [f"## Slide {slide_no}\n\n{body}" for slide_no, body in slides]
    return "\n\n".join(parts).strip()


def classify_extension(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in PDF_EXTS:
        return "pdf"
    if ext in DOCX_EXTS:
        return "docx"
    if ext in PPTX_EXTS:
        return "pptx"
    return "markdown"


def ensure_root_index() -> None:
    DRAFT_ROOT.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 资料整理稿索引",
        "",
        "## 子目录",
        "- [教材](./教材/index.md)",
        "- [课件](./课件/index.md)",
        "- [笔记](./笔记/index.md)",
        "- [作业](./作业/index.md)",
        "- [试卷](./试卷/index.md)",
    ]
    (DRAFT_ROOT / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def wrap_draft(
    *,
    title: str,
    draft_type: str,
    category: str,
    source_file: str,
    source_relative: str,
    source_path: str,
    raw_markdown: str,
    assets_dir: str | None,
    status: str,
    extracted_markdown: str,
    extract_meta: dict[str, Any] | None,
) -> str:
    assets_line = f"assets_dir: {assets_dir}\n" if assets_dir else ""
    extract_lines = ""
    if extract_meta:
        for key, value in extract_meta.items():
            yaml_key = f"extract_{key}"
            if isinstance(value, bool):
                rendered = "true" if value else "false"
            else:
                rendered = str(value)
            extract_lines += f"{yaml_key}: {rendered}\n"
    polished_markdown = polish_reviewed_markdown(extracted_markdown)
    return f"""---
title: {title}
type: {draft_type}
category: {category}
source_file: {source_file}
source_relative: {source_relative}
source_path: {source_path}
raw_markdown: {raw_markdown}
{assets_line}status: {status}
{extract_lines}---

# {title}

## 来源

- 分类：`{category}`
- 原始文件：`{source_file}`
- 原始相对路径：`{source_relative}`
- 原始绝对路径：`{source_path}`

## 后续处理建议

- 从本整理稿中提取稳定知识点
- 检查公式、表格、结构图的提取效果
- 必要时补单独图像解读稿
- 如发现资料错误，转入勘误或分歧

## 提取结果

{polished_markdown}
"""


def write_category_outputs(spec: CategorySpec, records: list[dict]) -> None:
    manifest_path = spec.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps({"records": records}, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# {spec.name}资料整理稿索引",
        "",
        "## 已入库资料",
    ]
    for record in records:
        draft_abs = Path(record["draft_md"])
        rel = draft_abs.relative_to(spec.output_dir).as_posix()
        lines.append(f"- [{record['source_file']}](./{rel}) | `{record['source_relative']}`")
    lines.extend(
        [
            "",
            "## 说明",
            "- 本层是证据层，不是知识点规范层。",
            "- 默认先读知识点页；知识点不够时，再回读这些整理稿。",
        ]
    )
    (spec.output_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def ingest_pdf(path: Path, target_dir: Path, client: MinerU) -> tuple[str, str, str | None, dict[str, Any]]:
    raw_md_path = target_dir / "raw-extract.md"
    force_ocr, ocr_reason, ocr_evidence = infer_pdf_ocr_mode(path, target_dir)
    model = os.environ.get("MINERU_MODEL", "vlm")
    language = os.environ.get("MINERU_LANGUAGE", "ch")
    formula = bool_env("MINERU_ENABLE_FORMULA", True)
    table = bool_env("MINERU_ENABLE_TABLE", True)
    timeout_sec = int(os.environ.get("MINERU_TIMEOUT_SEC", "900"))
    attempts = [
        {
            "attempt_name": "primary",
            "model": model,
            "ocr": force_ocr,
            "language": language,
            "formula": formula,
            "table": table,
        }
    ]
    if model != "pipeline" or force_ocr:
        attempts.append(
            {
                "attempt_name": "pipeline_text_retry",
                "model": "pipeline",
                "ocr": False,
                "language": language,
                "formula": formula,
                "table": table,
            }
        )
    if not force_ocr:
        attempts.append(
            {
                "attempt_name": "pipeline_ocr_retry",
                "model": "pipeline",
                "ocr": True,
                "language": language,
                "formula": formula,
                "table": table,
            }
        )

    last_error: Exception | None = None
    for index, attempt in enumerate(attempts):
        try:
            result = client.extract(
                str(path),
                model=attempt["model"],
                ocr=attempt["ocr"],
                language=attempt["language"],
                formula=attempt["formula"],
                table=attempt["table"],
                timeout=timeout_sec,
            )
            markdown = normalize_extracted_text(result.markdown or "")
            if not markdown:
                raise RuntimeError("No markdown content available (state != done)")
            temp_images_dir = target_dir / "images"
            image_count = len(list(temp_images_dir.glob("*"))) if temp_images_dir.exists() else 0
            quality_verdict, quality_reasons, quality_signals = assess_extracted_markdown(markdown, image_count=image_count)
            if quality_verdict == "reject":
                continue
            result.save_markdown(str(raw_md_path), with_images=True)
            return (
                sanitize_markdown_text(markdown),
                str(raw_md_path.resolve()),
                str((target_dir / "images").resolve()),
                {
                    "backend": "mineru",
                    "model": attempt["model"],
                    "language": attempt["language"],
                    "formula": attempt["formula"],
                    "table": attempt["table"],
                    "is_ocr": attempt["ocr"],
                    "ocr_reason": ocr_reason,
                    "timeout_sec": timeout_sec,
                    "attempt_name": attempt["attempt_name"],
                    "fallback_used": index > 0,
                    "quality_verdict": quality_verdict,
                    "quality_notes": json.dumps(quality_reasons, ensure_ascii=False),
                    "quality_signal_summary": json.dumps(quality_signals, ensure_ascii=False),
                    "ocr_signal_summary": json.dumps(ocr_evidence, ensure_ascii=False),
                },
            )
        except Exception as exc:
            last_error = exc

    if last_error is None:  # pragma: no cover
        raise RuntimeError("MinerU extract failed without an explicit exception.")
    raise last_error


def fallback_pdf_text(path: Path, target_dir: Path, error_message: str) -> tuple[str, str, None, str, dict[str, Any]]:
    extracted = ""
    if PdfReader is not None:
        try:
            reader = PdfReader(str(path))
            texts: list[str] = []
            for page in reader.pages:
                text = page.extract_text() or ""
                text = text.strip()
                if text:
                    texts.append(text)
            extracted = "\n\n".join(texts).strip()
        except Exception:
            extracted = ""

    if extracted:
        status = "fallback_text_only"
        content = (
            "## 说明\n\n"
            "- 该 PDF 的 MinerU 云端提取失败，已回退为本地文本提取。\n"
            f"- 云端错误：`{error_message}`\n\n"
            "## 本地提取结果\n\n"
            f"{extracted}"
        )
    else:
        status = "manual_review_required"
        content = (
            "## 说明\n\n"
            "- 该 PDF 的 MinerU 云端提取失败，本地文本提取也未获得稳定结果。\n"
            f"- 云端错误：`{error_message}`\n"
            "- 建议后续优先做 OCR 强化或单独图像解读。\n"
        )

    raw_md_path = target_dir / "raw-extract.md"
    raw_md_path.write_text(content + "\n", encoding="utf-8")
    return (
        content,
        str(raw_md_path.resolve()),
        None,
        status,
        {
            "backend": "mineru_fallback",
            "model": os.environ.get("MINERU_MODEL", "vlm"),
            "language": os.environ.get("MINERU_LANGUAGE", "ch"),
            "formula": bool_env("MINERU_ENABLE_FORMULA", True),
            "table": bool_env("MINERU_ENABLE_TABLE", True),
            "is_ocr": True,
            "ocr_reason": "fallback_after_extract_error",
        },
    )


def ingest_non_pdf(path: Path, target_dir: Path) -> tuple[str, str, None, dict[str, Any]]:
    ext = path.suffix.lower()
    if ext in MARKDOWN_EXTS:
        text = sanitize_markdown_text(read_text_flexible(path))
    elif ext in DOCX_EXTS:
        text = extract_docx_text(path)
    elif ext in PPTX_EXTS:
        text = extract_pptx_text(path)
    else:
        raise ValueError(f"Unsupported extension: {ext}")
    raw_md_path = target_dir / "raw-extract.md"
    normalized_text = normalize_extracted_text(text)
    raw_md_path.write_text(normalized_text + ("\n" if normalized_text else ""), encoding="utf-8")
    quality_verdict, quality_reasons, quality_signals = assess_extracted_markdown(normalized_text, image_count=0)
    return normalized_text, str(raw_md_path.resolve()), None, {
        "backend": ext.lstrip("."),
        "quality_verdict": quality_verdict,
        "quality_notes": json.dumps(quality_reasons, ensure_ascii=False),
        "quality_signal_summary": json.dumps(quality_signals, ensure_ascii=False),
    }


def build_category(spec: CategorySpec, client: MinerU) -> dict:
    spec.output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    seen: set[Path] = set()
    used_slugs: set[str] = set()
    force = os.environ.get("COMPORG_FORCE_REINGEST", "false").lower() == "true"

    for source_dir in spec.source_dirs:
        for source_file in iter_source_files(source_dir):
            if source_file in seen:
                continue
            seen.add(source_file)

            rel_path = source_file.relative_to(source_dir)
            slug = slugify_relative(Path(source_dir.name) / rel_path.with_suffix(""))
            if slug in used_slugs:
                slug = f"{slug}-{source_file.suffix.lower().lstrip('.')}"
            used_slugs.add(slug)
            target_dir = spec.output_dir / slug
            target_dir.mkdir(parents=True, exist_ok=True)
            draft_path = target_dir / f"{slug}.md"
            raw_md_path = target_dir / "raw-extract.md"

            kind = classify_extension(source_file)
            status = "imported"
            assets_dir: str | None = None
            extract_meta: dict[str, Any] = {"backend": kind}
            if not force and draft_path.exists() and raw_md_path.exists():
                images_dir = target_dir / "images"
                should_reextract, reuse_reason = should_reextract_existing(draft_path, raw_md_path, images_dir)
                if should_reextract:
                    force_current = True
                else:
                    force_current = False
                if images_dir.exists():
                    assets_dir = str(images_dir.resolve())
                if not force_current:
                    extracted = sanitize_markdown_text(read_text_flexible(raw_md_path))
                    raw_markdown = str(raw_md_path.resolve())
                    status = "reused"
                    extract_meta["reuse_reason"] = reuse_reason
            else:
                force_current = True
            if force_current:
                if kind == "pdf":
                    try:
                        extracted, raw_markdown, assets_dir, extract_meta = ingest_pdf(source_file, target_dir, client)
                        status = "extracted"
                    except Exception as exc:
                        extracted, raw_markdown, assets_dir, status, extract_meta = fallback_pdf_text(
                            source_file, target_dir, str(exc)
                        )
                else:
                    extracted, raw_markdown, assets_dir, extract_meta = ingest_non_pdf(source_file, target_dir)

            wrapped = wrap_draft(
                title=slug,
                draft_type=spec.draft_type,
                category=spec.name,
                source_file=source_file.name,
                source_relative=str(source_file.relative_to(REPO_ROOT)).replace("\\", "/"),
                source_path=str(source_file.resolve()),
                raw_markdown=raw_markdown,
                assets_dir=assets_dir,
                status=status,
                extracted_markdown=extracted,
                extract_meta=extract_meta,
            )
            draft_path.write_text(wrapped, encoding="utf-8")
            records.append(
                {
                    "slug": slug,
                    "source_file": source_file.name,
                    "source_relative": str(source_file.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "draft_md": str(draft_path.resolve()),
                    "raw_markdown": raw_markdown,
                    "assets_dir": assets_dir,
                    "type": spec.draft_type,
                    "status": status,
                    "extract_meta": extract_meta,
                }
            )
            write_category_outputs(spec, records)

    return {"category": spec.name, "count": len(records), "output": str(spec.output_dir)}


def main() -> None:
    env_data = load_simple_env(ENV_FILE)
    for key, value in env_data.items():
        os.environ.setdefault(key, value)

    token = os.environ.get("MINERU_TOKEN")
    if not token:
        raise SystemExit("MINERU_TOKEN 未配置，无法开始资料入库。")

    only = {item.strip() for item in sys.argv[1:] if item.strip()}

    ensure_root_index()
    results: list[dict] = []
    with MinerU(token=token) as client:
        for spec in CATEGORIES:
            if only and spec.name not in only:
                continue
            results.append(build_category(spec, client))

    print(json.dumps({"status": "ok", "categories": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
