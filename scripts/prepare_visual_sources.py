from __future__ import annotations

import argparse
import json
import math
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image
import pypdfium2 as pdfium


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
PDF_SUFFIXES = {".pdf"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare local PDF/image sources for visual interpretation."
    )
    parser.add_argument("inputs", nargs="+", help="PDF or image files to prepare")
    parser.add_argument(
        "--output-dir",
        help="Output directory. Defaults to 渲染缓存/<source-stem>",
    )
    parser.add_argument(
        "--pages",
        help="1-based page list for PDFs, for example 31 or 31-35 or 31,33,35-36",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="Render scale for PDF pages. 2.0 is usually enough for OCR and vision.",
    )
    parser.add_argument(
        "--vertical-slices",
        type=int,
        default=1,
        help="Split each rendered image into N vertical slices. Use 2-4 for dense pages.",
    )
    parser.add_argument(
        "--ocr-markdown",
        action="store_true",
        help="Run PaddleOCR on each prepared base image and write page-level markdown sidecars.",
    )
    return parser.parse_args()


def parse_page_spec(spec: str | None, page_count: int) -> list[int]:
    if not spec:
        return list(range(page_count))
    selected: set[int] = set()
    for part in spec.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            if start > end:
                raise ValueError(f"Invalid page range: {token}")
            for page_no in range(start, end + 1):
                if 1 <= page_no <= page_count:
                    selected.add(page_no - 1)
            continue
        page_no = int(token)
        if 1 <= page_no <= page_count:
            selected.add(page_no - 1)
    if not selected:
        raise ValueError("No valid pages selected.")
    return sorted(selected)


def default_output_dir(source: Path) -> Path:
    return Path.cwd() / "渲染缓存" / source.stem


def ensure_output_dir(source: Path, configured: str | None, multi_input: bool) -> Path:
    if configured:
        base_dir = Path(configured)
        out_dir = base_dir / source.stem if multi_input else base_dir
    else:
        out_dir = default_output_dir(source)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def save_image(image: Image.Image, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)


def create_vertical_slices(image: Image.Image, base_path: Path, slices: int) -> list[str]:
    if slices <= 1:
        return []
    width, height = image.size
    step = math.ceil(height / slices)
    rel_paths: list[str] = []
    for idx in range(slices):
        top = idx * step
        bottom = min(height, (idx + 1) * step)
        if top >= bottom:
            continue
        cropped = image.crop((0, top, width, bottom))
        slice_path = base_path.with_name(f"{base_path.stem}-s{idx + 1:02d}-of{slices:02d}{base_path.suffix}")
        cropped.save(slice_path)
        rel_paths.append(slice_path.name)
    return rel_paths


def get_ocr_engine() -> Any:
    os.environ.setdefault("DISABLE_MODEL_SOURCE_CHECK", "True")
    from paddleocr import PaddleOCR

    return PaddleOCR(lang="ch")


def run_ocr_markdown(ocr: Any, image_path: Path) -> dict[str, Any]:
    result = ocr.predict(str(image_path))[0]
    lines = [text.strip() for text in result.get("rec_texts", []) if text.strip()]
    scores = [float(score) for score in result.get("rec_scores", []) if score is not None]
    avg_score = round(sum(scores) / len(scores), 4) if scores else 0.0
    md_path = image_path.with_suffix(".ocr.md")
    json_path = image_path.with_suffix(".ocr.json")
    md_lines = [
        f"# OCR for {image_path.name}",
        "",
        f"- SourceImage: {image_path.name}",
        f"- OCRLineCount: {len(lines)}",
        f"- AvgScore: {avg_score}",
        "",
        "## Lines",
    ]
    if lines:
        md_lines.extend(f"- {line}" for line in lines)
    else:
        md_lines.append("- (empty after OCR filtering)")
    md_path.write_text("\n".join(md_lines).rstrip() + "\n", encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "source_image": image_path.name,
                "line_count": len(lines),
                "avg_score": avg_score,
                "rec_texts": lines,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "ocr_markdown": md_path.name,
        "ocr_json": json_path.name,
        "ocr_line_count": len(lines),
        "ocr_avg_score": avg_score,
    }


def prepare_pdf(source: Path, output_dir: Path, pages: str | None, scale: float, slices: int, ocr: Any | None) -> list[dict[str, Any]]:
    document = pdfium.PdfDocument(str(source))
    selected_pages = parse_page_spec(pages, len(document))
    items: list[dict[str, Any]] = []
    for page_index in selected_pages:
        page = document[page_index]
        image = page.render(scale=scale).to_pil()
        image_path = output_dir / f"page-{page_index + 1:03d}.png"
        save_image(image, image_path)
        item: dict[str, Any] = {
            "kind": "pdf_page",
            "page_number": page_index + 1,
            "image": image_path.name,
            "width": image.width,
            "height": image.height,
            "vertical_slices": create_vertical_slices(image, image_path, slices),
        }
        if ocr is not None:
            item.update(run_ocr_markdown(ocr, image_path))
        items.append(item)
    return items


def prepare_image(source: Path, output_dir: Path, slices: int, ocr: Any | None) -> list[dict[str, Any]]:
    image = Image.open(source)
    target_path = output_dir / source.name
    save_image(image, target_path)
    item: dict[str, Any] = {
        "kind": "image",
        "image": target_path.name,
        "width": image.width,
        "height": image.height,
        "vertical_slices": create_vertical_slices(image, target_path, slices),
    }
    if ocr is not None:
        item.update(run_ocr_markdown(ocr, target_path))
    return [item]


def write_index(output_dir: Path, source: Path, prepared_items: list[dict[str, Any]], args: argparse.Namespace) -> None:
    lines = [
        f"# {source.name} Visual Prep",
        "",
        f"- Source: {source}",
        f"- PreparedAt: {datetime.now(UTC).isoformat()}",
        f"- Scale: {args.scale}",
        f"- VerticalSlices: {args.vertical_slices}",
        f"- OCRMarkdown: {args.ocr_markdown}",
        "",
        "## Items",
    ]
    for item in prepared_items:
        title = item["image"]
        lines.append(f"### {title}")
        lines.append(f"- Kind: {item['kind']}")
        if "page_number" in item:
            lines.append(f"- PageNumber: {item['page_number']}")
        lines.append(f"- Image: [{item['image']}]({item['image']})")
        if item.get("vertical_slices"):
            lines.append("- VerticalSlices:")
            for slice_name in item["vertical_slices"]:
                lines.append(f"  - [{slice_name}]({slice_name})")
        if item.get("ocr_markdown"):
            lines.append(f"- OCRMarkdown: [{item['ocr_markdown']}]({item['ocr_markdown']})")
        if item.get("ocr_json"):
            lines.append(f"- OCRJson: [{item['ocr_json']}]({item['ocr_json']})")
        lines.append("")
    (output_dir / "index.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_manifest(output_dir: Path, source: Path, prepared_items: list[dict[str, Any]], args: argparse.Namespace) -> None:
    manifest = {
        "source": str(source),
        "generated_at": datetime.now(UTC).isoformat(),
        "scale": args.scale,
        "vertical_slices": args.vertical_slices,
        "ocr_markdown": args.ocr_markdown,
        "items": prepared_items,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def resolve_source(raw_input: str) -> Path:
    source = Path(raw_input)
    if not source.is_absolute():
        source = Path.cwd() / source
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(f"Missing source: {source}")
    return source


def main() -> None:
    args = parse_args()
    ocr = get_ocr_engine() if args.ocr_markdown else None
    multi_input = len(args.inputs) > 1
    for raw_input in args.inputs:
        source = resolve_source(raw_input)
        output_dir = ensure_output_dir(source, args.output_dir, multi_input=multi_input)
        suffix = source.suffix.lower()
        if suffix in PDF_SUFFIXES:
            prepared_items = prepare_pdf(source, output_dir, args.pages, args.scale, args.vertical_slices, ocr)
        elif suffix in IMAGE_SUFFIXES:
            prepared_items = prepare_image(source, output_dir, args.vertical_slices, ocr)
        else:
            raise ValueError(f"Unsupported source type: {source}")
        write_manifest(output_dir, source, prepared_items, args)
        write_index(output_dir, source, prepared_items, args)
        print(output_dir)


if __name__ == "__main__":
    main()
