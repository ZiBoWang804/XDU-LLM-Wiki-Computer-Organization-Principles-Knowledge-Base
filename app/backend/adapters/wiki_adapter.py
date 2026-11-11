# -*- coding: utf-8 -*-
# wiki_adapter：LLM Wiki 层——直读本地知识库 md（权威答案层，防编造出处）
import os
import re

import yaml

from .. import config


def _load_page(path: str) -> dict:
    text = open(path, encoding='utf-8', errors='ignore').read()
    fm = {}
    body = text
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            body = parts[2]
    return {'frontmatter': fm, 'body': body.strip()}


def list_pages() -> list:
    out = []
    for root, _dirs, files in os.walk(config.kb_dir()):
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(root, fn), config.kb_dir()).replace('\\', '/')
            # PDF/附件也入列表（type: 文档附件），供浏览器预览
            if fn.lower().endswith('.pdf'):
                out.append({'file': rel, 'type': '文档附件', 'chapter': '',
                            'knowledge_points': [], 'is_pdf': True})
                continue
            if not fn.endswith('.md'):
                continue
            p = _load_page(os.path.join(root, fn))
            fm = p['frontmatter']
            out.append({'file': rel, 'type': fm.get('type', ''), 'chapter': fm.get('chapter', ''),
                        'knowledge_points': fm.get('knowledge_points', [])})
    return out


def get_page(name: str) -> dict:
    """按相对路径（可省略 .md）取整页。"""
    fn = name if name.endswith('.md') else name + '.md'
    path = os.path.join(config.kb_dir(), fn)
    if not os.path.exists(path):
        raise FileNotFoundError(fn)
    p = _load_page(path)
    p['file'] = fn
    return p


def search(keyword: str, limit: int = 5) -> list:
    """混合检索：embedding 语义检索（优先）+ 关键词/frontmatter 加权（补充）。"""
    scored = []
    kw = keyword.lower()
    pages_cache = {}
    for page in list_pages():
        if page.get('is_pdf'):
            continue
        p = _load_page(os.path.join(config.kb_dir(), page['file']))
        pages_cache[page['file']] = p
        fm = p['frontmatter']
        score = 0
        if kw in page['file'].lower():
            score += 10
        for kp in fm.get('knowledge_points', []):
            if kw in kp.lower():
                score += 6
        for epd in fm.get('exam_points', []):
            if kw in str(epd.get('name', '')).lower():
                score += 4
        score += min(p['body'].lower().count(kw), 5)
        if score > 0:
            cnt, snips = _snippets(p['body'], keyword)
            scored.append({'file': page['file'], 'score': score, 'type': fm.get('type', ''),
                           'chapter': fm.get('chapter', ''),
                           'excerpt': _excerpt(p['body'], keyword),
                           'anchor': _anchor(p['body'], keyword),
                           'match_count': cnt or 1, 'snippets': snips or [_excerpt(p['body'], keyword)]})
    # 语义检索增强（向量模型可用时）
    try:
        from . import embed_adapter
        candidates = {f: (p['frontmatter'].get('chapter', '') + ' ' +
                          ' '.join(p['frontmatter'].get('knowledge_points', [])) + ' ' +
                          p['body'][:600]) for f, p in pages_cache.items()}
        sem = embed_adapter.semantic_search(keyword, candidates, top_k=limit)
        if sem:
            seen = {s['file'] for s in scored}
            for f, sc in sem:
                if f not in seen and sc > 0.35:
                    p = pages_cache[f]
                    cnt, snips = _snippets(p['body'], keyword)
                    scored.append({'file': f, 'score': round(sc * 12, 1),
                                   'type': p['frontmatter'].get('type', ''),
                                   'chapter': p['frontmatter'].get('chapter', ''),
                                   'excerpt': _excerpt(p['body'], keyword),
                                   'anchor': _anchor(p['body'], keyword),
                                   'match_count': cnt or 0, 'snippets': snips or [_excerpt(p['body'], keyword)]})
    except Exception:
        pass
    scored.sort(key=lambda x: -x['score'])
    return scored[:limit]


def _excerpt(body: str, keyword: str, width: int = 160) -> str:
    m = re.search(re.escape(keyword), body, re.I)
    if not m:
        return body[:width]
    s = max(m.start() - width // 2, 0)
    return body[s:s + width].replace('\n', ' ')


def _snippets(body: str, keyword: str, n: int = 3) -> tuple:
    """返回 (匹配次数, [最多 n 段命中摘录])。"""
    kwl = keyword.lower()
    count = body.lower().count(kwl)
    out = []
    start = 0
    while len(out) < n:
        i = body.lower().find(kwl, start)
        if i < 0:
            break
        s = max(0, i - 32)
        e = min(len(body), i + len(keyword) + 48)
        out.append(body[s:e].replace(chr(10), ' ').strip())
        start = i + max(len(keyword), 1)
    return count, out


def _anchor(body: str, keyword: str) -> str:
    """找 query 与正文的最长公共子串，作为高亮锚点（语义命中时也能定位）。"""
    import difflib
    clean = re.sub(r'[#*>`|\-\n]', ' ', body[:6000])
    m = difflib.SequenceMatcher(None, keyword, clean).find_longest_match(0, len(keyword), 0, len(clean))
    if m.size >= 4:
        return clean[m.b:m.b + m.size].strip()
    # 兜底：摘录前 12 字（去掉 markdown 符号）
    seg = re.sub(r'[#*>`|\-\n]', '', body[:200]).strip()[:12]
    return seg


def kp_context(kp: str) -> str:
    """给定知识点，拼出其权威上下文（知识点页+对应专题页正文摘要），供 LLM 引用。"""
    chunks = []
    for page in list_pages():
        if page.get('is_pdf'):
            continue
        p = _load_page(os.path.join(config.kb_dir(), page['file']))
        fm = p['frontmatter']
        if kp in fm.get('knowledge_points', []) or any(kp in str(e.get('kp', '')) for e in fm.get('exam_points', [])):
            chunks.append('【来源：%s（%s）】\n%s' % (page['file'], fm.get('chapter', ''), p['body'][:1200]))
    return '\n\n'.join(chunks[:3])


# ---------- Smart Connections：本地向量关联（字符 bigram 向量 + 余弦相似度） ----------
from collections import Counter


def _bigram_vec(text: str) -> Counter:
    t = ''.join(ch for ch in text if ch.strip())
    return Counter(t[i:i + 2] for i in range(len(t) - 1))


def _cosine(a: Counter, b: Counter) -> float:
    common = set(a) & set(b)
    num = sum(a[k] * b[k] for k in common)
    den = (sum(v * v for v in a.values()) ** 0.5) * (sum(v * v for v in b.values()) ** 0.5)
    return num / den if den else 0.0


def related(file: str, k: int = 5) -> list:
    """给定文档，返回最相关的 k 篇（余弦相似度 score∈[0,1]，越大越相关）。"""
    target = file if file.endswith('.md') else file + '.md'
    pages = {}
    for page in list_pages():
        if page.get('is_pdf'):
            continue
        pages[page['file']] = _load_page(os.path.join(config.kb_dir(), page['file']))
    if target not in pages:
        raise FileNotFoundError(target)
    tp = pages[target]
    t_fm = tp['frontmatter']
    t_vec = _bigram_vec(tp['body'][:4000] + ' '.join(t_fm.get('knowledge_points', [])))
    t_kp = set(t_fm.get('knowledge_points', []))
    out = []
    for fn, p in pages.items():
        if fn == target:
            continue
        p_fm = p['frontmatter']
        vec = _bigram_vec(p['body'][:4000] + ' '.join(p_fm.get('knowledge_points', [])))
        cos = _cosine(t_vec, vec)
        kp_overlap = sorted(t_kp & set(p_fm.get('knowledge_points', [])))
        score = round(0.85 * cos + 0.15 * min(len(kp_overlap) / 3, 1), 3)
        out.append({'file': fn, 'score': score, 'cosine': round(cos, 3),
                    'chapter': p_fm.get('chapter', ''), 'kp_overlap': kp_overlap})
    out.sort(key=lambda x: -x['score'])
    return out[:k]
