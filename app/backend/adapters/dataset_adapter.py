# -*- coding: utf-8 -*-
# dataset_adapter：TeleAgent 知识库API（RAG 原文层）——上传/绑定/召回检索
# 接口规格见 D:\wzb\编译原理\teleai_api_reference.md
import os

import httpx

from .. import config


class DatasetError(RuntimeError):
    pass


def _headers():
    if not config.TELEAI_DATASET_KEY:
        raise DatasetError('TELEAI_DATASET_KEY 未配置（见 .env）')
    return {'Authorization': 'Bearer ' + config.TELEAI_DATASET_KEY}


def _req(method: str, path: str, **kw) -> dict:
    url = config.TELEAI_BASE.rstrip('/') + path
    resp = httpx.request(method, url, headers={**_headers(), **kw.pop('headers', {})},
                         timeout=60.0, **kw)
    try:
        body = resp.json()
    except Exception:
        raise DatasetError('HTTP %d 非 JSON: %s' % (resp.status_code, resp.text[:200]))
    if resp.status_code != 200:
        raise DatasetError('HTTP %d: %s' % (resp.status_code, body))
    return body


# ---------- 知识库 ----------
def create_dataset(name: str, ocr_enable: str = '1') -> dict:
    """创建知识库。ocr_enable: '0'快速解析 / '1'精准解析(图片型PDF)。返回含 dataset id。"""
    return _req('POST', '/v1/api_key/datasets/init',
                json={'name': name, 'ocr_enable': ocr_enable,
                      'enhanced_enable': '0'})


# ---------- 文件 ----------
def upload_file(file_path: str) -> str:
    """上传单文件(≤20MB)，返回 file_id。"""
    with open(file_path, 'rb') as f:
        body = _req('POST', '/v1/api_key/files/upload',
                    files={'file': (os.path.basename(file_path), f)})
    data = body.get('data', body)
    return data.get('id') or data.get('file_id')


def bind_documents(dataset_id: str, file_ids: list, doc_language: str = 'chinese') -> dict:
    """把已上传文件绑定进知识库（自动分段+语义检索配置）。异步处理。"""
    payload = {
        'data_source': {'type': 'upload_file',
                        'info_list': {'data_source_type': 'upload_file',
                                      'file_info_list': {'file_ids': file_ids}}},
        'process_rule': {'rules': {}, 'mode': 'automatic'},
        'doc_form': 'text_model',
        'doc_language': doc_language,
        'retrieval_model': {
            'search_method': 'semantic_search',
            'reranking_enable': False,
            'reranking_mode': 'weighted_score',
            'reranking_model': {'reranking_provider_name': '', 'reranking_model_name': ''},
            'weights': {'keyword_setting': {'keyword_weight': 0.3},
                        'vector_setting': {'vector_weight': 0.7,
                                           'embedding_model_name': '',
                                           'embedding_provider_name': ''}},
            'top_k': 3, 'score_threshold_enabled': True, 'score_threshold': 0.5},
    }
    return _req('POST', '/v1/api_key/datasets/%s/documents' % dataset_id, json=payload)


def list_documents(dataset_id: str, page: int = 1, limit: int = 20) -> dict:
    """文档列表（含 display_status：queuing/indexing/done/failed）。"""
    return _req('GET', '/v1/api_key/datasets/%s/documents' % dataset_id,
                params={'page': page, 'limit': limit})


def wait_indexed(dataset_id: str, max_wait: float = 120.0) -> bool:
    """轮询直到全部文档索引完成。超时返回 False。"""
    import time
    deadline = time.time() + max_wait
    while time.time() < deadline:
        docs = list_documents(dataset_id, limit=100).get('data', {}).get('docs', [])
        if docs and all(d.get('display_status') == 'done' for d in docs):
            return True
        time.sleep(3)
    return False


# ---------- 召回检索 ----------
def retrieve(query: str, dataset_ids: list, top_k: int = 3) -> list:
    """RAG 召回。返回 [{title, content, score, document_name, dataset_id, segment_id}]。"""
    payload = {
        'inputs': query,
        'retry_config': {'max_retries': 2, 'retry_interval': 10, 'retry_enabled': True},
        'dataset_ids': dataset_ids,
        'retrieval_mode': 'multiple',
        'multiple_retrieval_config': {
            'top_k': top_k, 'score_threshold': 0.1,
            'reranking_enable': False, 'reranking_mode': 'weighted_score',
            'reranking_model': {'provider': '', 'model': ''},
            'weights': {'vector_setting': {'vector_weight': 0.7},
                        'keyword_setting': {'keyword_weight': 0.3}}},
    }
    body = _req('POST', '/v1/api_key/datasets/draft', json=payload)
    out = []
    for item in body.get('data', []):
        for m in item.get('metadata', [{}]):
            out.append({'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'score': m.get('score', 0),
                        'document_name': m.get('document_name', ''),
                        'dataset_id': m.get('dataset_id', ''),
                        'segment_id': m.get('segment_id', '')})
    return out
