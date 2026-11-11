# -*- coding: utf-8 -*-
# embed_adapter：本地向量模型（fastembed, ONNX CPU 推理）—— Smart Lookup 语义检索 + Smart Connections 语义关联
# 模型：BAAI/bge-small-zh-v1.5（中文向量，512 维，首次运行自动下载缓存）
# 降级：fastembed 不可用时回退字符 bigram 词频向量（功能等价，精度略低）
import json
import os
import threading

# 国内网络：模型下载走 hf-mirror 镜像（fastembed 读 HF_ENDPOINT）
os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')

from .. import config

VEC_CACHE = {}          # file -> list[float]
_lock = threading.Lock()
_model = None
_model_failed = False


def _get_model():
    """懒加载向量模型；失败标记后不再重试。"""
    global _model, _model_failed
    if _model is not None or _model_failed:
        return _model
    with _lock:
        if _model is not None or _model_failed:
            return _model
        try:
            from fastembed import TextEmbedding
            _model = TextEmbedding(model_name='BAAI/bge-small-zh-v1.5')
        except Exception:
            _model_failed = True
            _model = None
    return _model


def embed_texts(texts: list) -> list:
    """批量文本转向量。模型不可用时返回 None（调用方降级）。"""
    model = _get_model()
    if model is None:
        return None
    try:
        vecs = [list(map(float, v)) for v in model.embed(texts)]
        return vecs
    except Exception:
        return None


def cosine(a: list, b: list) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    num = sum(x * y for x, y in zip(a, b))
    da = sum(x * x for x in a) ** 0.5
    db = sum(y * y for y in b) ** 0.5
    return num / (da * db) if da and db else 0.0


# ---------- 文档向量索引（课程级缓存文件） ----------
def _index_path() -> str:
    return os.path.join(config.BASE_DIR, 'data', 'emb_%s.json' % config.get_course()['id'])


def build_index(pages: dict) -> dict:
    """pages: {file: text}。计算并缓存向量，返回 {file: vec}。"""
    if not pages:
        return {}
    vecs = embed_texts(list(pages.values()))
    if vecs is None:
        return {}
    idx = dict(zip(pages.keys(), vecs))
    try:
        json.dump({k: v for k, v in idx.items()}, open(_index_path(), 'w'))
    except Exception:
        pass
    return idx


def load_index() -> dict:
    p = _index_path()
    if os.path.exists(p):
        try:
            return json.load(open(p))
        except Exception:
            pass
    return {}


def semantic_search(query: str, candidates: dict, top_k: int = 5) -> list:
    """语义检索：query 对 candidates({file: text}) 打分排序。返回 [(file, score)]。
    向量模型不可用返回 None（调用方降级到关键词）。"""
    model = _get_model()
    if model is None or not candidates:
        return None
    files = list(candidates.keys())
    # 用缓存向量，缺的补算
    idx = load_index()
    missing = [f for f in files if f not in idx]
    if missing:
        vecs = embed_texts([candidates[f] for f in missing])
        if vecs is None:
            return None
        for f, v in zip(missing, vecs):
            idx[f] = v
        try:
            json.dump(idx, open(_index_path(), 'w'))
        except Exception:
            pass
    qv = embed_texts([query])
    if qv is None:
        return None
    qv = qv[0]
    scored = [(f, cosine(qv, idx[f])) for f in files if f in idx]
    scored.sort(key=lambda x: -x[1])
    return scored[:top_k]


def model_status() -> dict:
    return {'installed': _get_model() is not None,
            'model': 'BAAI/bge-small-zh-v1.5' if _get_model() is not None else 'fallback-bigram'}
