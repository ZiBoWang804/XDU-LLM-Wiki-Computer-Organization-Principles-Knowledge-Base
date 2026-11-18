# -*- coding: utf-8 -*-
# 多模态解析层：附件（图片/文档）→ 文本块（转写 + 图形描述）。
# 政策：解析失败明确报错（ParseError→API 502），识别不确定处标注 [未能识别]；
#       不静默忽略附件。入库流水线复用本模块。
import base64
import io
import os
import re

from . import config
from .adapters.llm_adapter import LLMError, chat_vision

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
DOC_EXTS = {'.txt', '.md', '.docx', '.pdf', '.pptx'}
ALLOWED_EXTS = IMAGE_EXTS | DOC_EXTS
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_TEXT = 20000

VISION_SYSTEM = (
    '你是文档/图片转写助手。任务：①转写图中全部文字（含表格，表格转 markdown；公式用行内记法）；'
    '②图形/流程图/结构图用文字描述结构与走向；③看不清、无法识别之处一律标注 [未能识别]，不猜测。'
    '只输出转写与描述，不要评论。')


class ParseError(RuntimeError):
    pass


# ---------- 存储 ----------
def _safe_name(name: str) -> str:
    name = os.path.basename(name or 'file')
    return re.sub(r'[^\w.\-()一-鿿]', '_', name)[:120]


def save_upload(data: bytes, filename: str, course_id: str, user_id) -> dict:
    """保存上传文件到 uploads/<course>/<user_id>/，返回元信息（file_id 用于后续解析）。"""
    if not data:
        raise ParseError('文件为空')
    if len(data) > MAX_UPLOAD_BYTES:
        raise ParseError('文件超过 25MB 上限')
    fn = _safe_name(filename)
    ext = os.path.splitext(fn)[1].lower()
    if ext not in ALLOWED_EXTS:
        raise ParseError('不支持的格式：%s（支持 图片 jpg/png/webp/gif、文档 txt/md/docx/pdf/pptx）' % ext)
    sub = os.path.join(config.UPLOAD_DIR, _safe_name(str(course_id)), _safe_name(str(user_id)))
    os.makedirs(sub, exist_ok=True)
    import time
    path = os.path.join(sub, '%d_%s' % (int(time.time()), fn))
    with open(path, 'wb') as f:
        f.write(data)
    return {'file_id': os.path.relpath(path, config.UPLOAD_DIR).replace('\\', '/'),
            'name': fn, 'type': ext.lstrip('.'), 'size': len(data)}


def _resolve(file_id: str) -> str:
    path = os.path.normpath(os.path.join(config.UPLOAD_DIR, file_id))
    if not path.startswith(os.path.normpath(config.UPLOAD_DIR)):
        raise ParseError('非法文件路径')
    if not os.path.isfile(path):
        raise ParseError('附件不存在或已过期：%s' % file_id)
    return path


# ---------- 分格式解析 ----------
def _img_payload(path: str) -> dict:
    ext = os.path.splitext(path)[1].lower()
    mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
            'webp': 'image/webp', 'gif': 'image/gif'}.get(ext.lstrip('.'), 'image/png')
    with open(path, 'rb') as f:
        return {'mime': mime, 'b64': base64.b64encode(f.read()).decode()}


def _mineru_markdown(path: str, name: str) -> str:
    """MinerU 云端 OCR/精准解析（上传 → 轮询 → Markdown）。OCR 统一走 MinerU。"""
    import time
    import zipfile
    import httpx
    token = os.environ.get('MINERU_API_TOKEN', '')
    if not token:
        raise ParseError('MINERU_API_TOKEN 未配置（见 .env），无法执行 OCR 解析')
    base = 'https://mineru.net/api/v4'
    hdrs = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    fn = os.path.basename(path)
    try:
        r = httpx.post(base + '/file-urls/batch', headers=hdrs, timeout=90, trust_env=False, json={
            'enable_formula': True, 'enable_table': True, 'enable_ocr': True,
            'language': 'ch', 'files': [{'name': fn, 'is_ocr': True}]})
        r.raise_for_status()
        data = r.json()
        if data.get('code') != 0:
            raise ParseError('MinerU 申请上传失败：%s' % data.get('msg'))
        batch_id = data['data']['batch_id']
        url = data['data']['file_urls'][0]
        with open(path, 'rb') as f:
            # 注意：OSS 预签名对请求头敏感，PUT 不能带 Content-Type（会 403 SignatureDoesNotMatch）
            up = httpx.put(url, content=f.read(), timeout=300, trust_env=False)
            up.raise_for_status()
        deadline = time.time() + 300
        entry = None
        while time.time() < deadline:
            g = httpx.get(base + '/extract-results/batch/' + batch_id,
                          headers=hdrs, timeout=60, trust_env=False)
            g.raise_for_status()
            res = (g.json().get('data') or {}).get('extract_result') or []
            if res and res[0].get('state') in ('done', 'failed'):
                entry = res[0]
                break
            time.sleep(5)
        if entry is None:
            raise ParseError('MinerU 解析超时（%s）' % name)
        if entry.get('state') != 'done':
            raise ParseError('MinerU 解析失败（%s）：%s' % (name, entry.get('err_msg', '未知错误')))
        md_url = entry.get('full_zip_url') or (entry.get('result_urls') or {}).get('markdown') or ''
        if not md_url:
            raise ParseError('MinerU 未返回结果内容（%s）' % name)
        blob = httpx.get(md_url, timeout=120, trust_env=False).content
        try:
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                for member in z.namelist():
                    if member.endswith('.md'):
                        return z.read(member).decode('utf-8', errors='ignore')
        except zipfile.BadZipFile:
            return blob.decode('utf-8', errors='ignore')
        raise ParseError('MinerU 结果包中无 Markdown（%s）' % name)
    except ParseError:
        raise
    except Exception as e:
        raise ParseError('MinerU 调用失败（%s）：%s' % (name, e))


def _parse_image(path: str, name: str) -> str:
    """图片解析：优先模型自身读图能力（转写+图形描述一步到位）；
    OCR（MinerU）留给长文档/扫描件。"""
    try:
        return chat_vision(VISION_SYSTEM, '转写这张图片的内容：', [_img_payload(path)],
                           thinking=False, temperature=0.1)
    except LLMError as e:
        raise ParseError('图片解析失败（%s）：%s' % (name, e))


def _parse_docx(path: str, name: str) -> str:
    try:
        import docx
    except ImportError:
        raise ParseError('docx 解析组件（python-docx）未安装')
    try:
        d = docx.Document(path)
    except Exception as e:
        raise ParseError('docx 文件损坏或格式不符（%s）：%s' % (name, e))
    parts = [p.text for p in d.paragraphs if p.text.strip()]
    for t in d.tables:
        rows = ['| ' + ' | '.join(c.text.replace('\n', ' ') for c in row.cells) + ' |'
                for row in t.rows]
        if rows:
            parts.append('\n'.join(rows))
    text = '\n'.join(parts).strip()
    if not text:
        raise ParseError('docx 未提取到文本内容（%s）' % name)
    return text


def _parse_pdf(path: str, name: str) -> str:
    try:
        import fitz
    except ImportError:
        raise ParseError('pdf 解析组件（PyMuPDF）未安装')
    try:
        doc = fitz.open(path)
    except Exception as e:
        raise ParseError('pdf 打开失败（%s）：%s' % (name, e))
    texts = [page.get_text() for page in doc]
    text = '\n'.join(texts).strip()
    # 扫描型 PDF（无文本层）→ MinerU OCR 精准解析
    if len(text) < 50:
        return _mineru_markdown(path, name)
    return text


def _parse_pptx(path: str, name: str) -> str:
    try:
        from pptx import Presentation
    except ImportError:
        raise ParseError('pptx 解析组件（python-pptx）未安装')
    try:
        prs = Presentation(path)
    except Exception as e:
        raise ParseError('pptx 文件损坏或格式不符（%s）：%s' % (name, e))
    parts = []
    for i, slide in enumerate(prs.slides, 1):
        chunks = ['[第%d页]' % i]
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                chunks.append(shape.text_frame.text)
            if getattr(shape, 'has_table', False) and shape.has_table:
                rows = ['| ' + ' | '.join(c.text.replace('\n', ' ') for c in row.cells) + ' |'
                        for row in shape.table.rows]
                chunks.append('\n'.join(rows))
        if len(chunks) > 1:
            parts.append('\n'.join(chunks))
    text = '\n\n'.join(parts).strip()
    if not text:
        raise ParseError('pptx 未提取到文本内容（%s）' % name)
    return text


def _parse_text(path: str, name: str) -> str:
    try:
        with open(path, encoding='utf-8', errors='ignore') as f:
            text = f.read().strip()
    except Exception as e:
        raise ParseError('文本读取失败（%s）：%s' % (name, e))
    if not text:
        raise ParseError('文件内容为空（%s）' % name)
    return text


# ---------- 统一入口 ----------
def _dispatch(path: str) -> str:
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower()
    if ext in IMAGE_EXTS:
        text = _parse_image(path, name)
    elif ext == '.docx':
        text = _parse_docx(path, name)
    elif ext == '.pdf':
        text = _parse_pdf(path, name)
    elif ext == '.pptx':
        text = _parse_pptx(path, name)
    elif ext in {'.txt', '.md'}:
        text = _parse_text(path, name)
    else:
        raise ParseError('不支持的格式：%s' % ext)
    if len(text) > MAX_TEXT:
        text = text[:MAX_TEXT] + '\n…（附件过长，已截断至 %d 字）' % MAX_TEXT
    return '【附件解析：%s（%s）】\n%s' % (name, ext.lstrip('.'), text)


def parse_file(file_id: str) -> str:
    """解析上传附件为文本块。失败抛 ParseError（明确报错，不静默忽略）。"""
    return _dispatch(_resolve(file_id))


def parse_kb(kb_name: str) -> str:
    """解析知识库内文件（如 原始资料/xxx.pdf）。路径限定在课程知识库目录内。"""
    root = os.path.normpath(config.kb_dir())
    path = os.path.normpath(os.path.join(root, kb_name))
    if not path.startswith(root):
        raise ParseError('非法知识库路径')
    if not os.path.isfile(path):
        raise ParseError('知识库文件不存在：%s' % kb_name)
    return _dispatch(path)


def parse_attachments(file_ids: list) -> str:
    """多个附件 → 一块上下文；任一失败即整体报错（不跳过）。"""
    if not file_ids:
        return ''
    blocks = [parse_file(fid) for fid in file_ids]
    return '\n\n'.join(blocks)
