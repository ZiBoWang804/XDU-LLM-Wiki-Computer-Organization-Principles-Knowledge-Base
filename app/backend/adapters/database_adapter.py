# -*- coding: utf-8 -*-
# database_adapter：TeleAgent 数据库API——平台侧档案镜像（智能体可见）
# 注意：无行级 CRUD，数据经 CSV/Excel 文件导入；SQLite 是真实账本。
import os

import httpx

from .. import config


class DatabaseError(RuntimeError):
    pass


def _req(method: str, path: str, **kw) -> dict:
    if not config.TELEAI_DATABASE_KEY:
        raise DatabaseError('TELEAI_DATABASE_KEY 未配置（见 .env）')
    url = config.TELEAI_BASE.rstrip('/') + path
    resp = httpx.request(method, url,
                         headers={'Authorization': 'Bearer ' + config.TELEAI_DATABASE_KEY},
                         timeout=60.0, **kw)
    try:
        body = resp.json()
    except Exception:
        raise DatabaseError('HTTP %d 非 JSON: %s' % (resp.status_code, resp.text[:200]))
    if resp.status_code != 200:
        raise DatabaseError('HTTP %d: %s' % (resp.status_code, body))
    return body


# ---------- 数据库 ----------
def create_database(name: str, description: str = '') -> dict:
    return _req('POST', '/v1/api_key/databases/create',
                json={'name': name, 'description': description, 'type': '1'})


def list_databases(page: int = 1, size: int = 30, keyword: str = '') -> dict:
    return _req('POST', '/v1/api_key/databases/list',
                json={'page': page, 'size': size, 'keyword': keyword})


# ---------- 文件导入建表 ----------
def upload_data_file(db_id: str, file_path: str) -> str:
    """上传 CSV/XLSX（≤15MB，CSV 须 UTF-8），返回 file_id。"""
    with open(file_path, 'rb') as f:
        body = _req('POST', '/v1/api_key/databases/files/upload',
                    data={'db_id': db_id},
                    files={'file': (os.path.basename(file_path), f)})
    tables = body.get('data', {}).get('tables', [])
    if tables:
        return tables[0].get('file_id', '')
    raise DatabaseError('上传响应缺 file_id: %s' % body)


def create_table_from_file(db_id: str, file_id: str, read_write: bool = True) -> str:
    """用 file_id 建表，返回 table_id。"""
    body = _req('POST', '/v1/api_key/databases/table/create',
                json={'db_id': db_id, 'files': [{'file_id': file_id}],
                      'data_permission': 1 if read_write else 0})
    tables = body.get('data', {}).get('tables', [])
    if tables:
        return tables[0].get('table_id', '')
    raise DatabaseError('建表响应缺 table_id: %s' % body)


def create_custom_table(db_id: str, table_name: str, columns: list,
                        table_desc: str = '') -> str:
    """自定义建表。columns: [{name, description, type, is_necessary}]，返回 table_id。"""
    body = _req('POST', '/v1/api_key/databases/table/create_custom_table',
                json={'db_id': db_id, 'table_name': table_name, 'table_desc': table_desc,
                      'tab_desc': 0, 'data_permission': 1, 'columns': columns})
    return body.get('table_id') or body.get('data', {}).get('table_id', '')


def list_tables(db_id: str) -> dict:
    return _req('POST', '/v1/api_key/databases/table/list', json={'db_id': db_id})


def table_status(db_id: str, table_id: str) -> dict:
    """表处理状态。status_import==2 表示导入完成可用。"""
    return _req('POST', '/v1/api_key/databases/table/status',
                json={'db_id': db_id, 'table_id': table_id})


# ---------- 业务封装 ----------
def sync_snapshot(db_id: str, csv_path: str) -> dict:
    """把 SQLite 导出的 CSV 快照导入平台库（新建表）。返回 {file_id, table_id}。"""
    fid = upload_data_file(db_id, csv_path)
    tid = create_table_from_file(db_id, fid)
    return {'file_id': fid, 'table_id': tid}
