# -*- coding: utf-8 -*-
# 教师端服务：勘误/知识库更新/出题作业/浏览热力图/知识库状态
import io
import json
import os
import re
import time

import yaml

from . import config, db as dbm

TEACHER_SCHEMA = """
CREATE TABLE IF NOT EXISTS errata(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file TEXT NOT NULL,
  teacher TEXT DEFAULT '',
  kind TEXT DEFAULT '勘误',       -- 勘误/修改
  before TEXT DEFAULT '',
  after TEXT DEFAULT '',
  note TEXT DEFAULT '',
  status TEXT DEFAULT '待确认',   -- 待确认/已应用/已驳回
  created_at INTEGER
);
CREATE TABLE IF NOT EXISTS homework(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  detail TEXT DEFAULT '',
  kp TEXT DEFAULT '',
  question_ids TEXT DEFAULT '',
  due_date TEXT DEFAULT '',
  teacher TEXT DEFAULT '',
  created_at INTEGER
);
CREATE TABLE IF NOT EXISTS page_views(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file TEXT NOT NULL,
  user_name TEXT DEFAULT '',
  viewed_at INTEGER
);
"""


def init_teacher_db():
    with dbm.get_conn() as conn:
        conn.executescript(TEACHER_SCHEMA)


# ---------- 勘误 / 修改 ----------
def add_errata(file: str, kind: str, before: str, after: str, note: str, teacher: str) -> int:
    with dbm.get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO errata(file, teacher, kind, before, after, note, created_at)'
            ' VALUES(?,?,?,?,?,?,?)', (file, teacher, kind, before, after, note, int(time.time())))
        return cur.lastrowid


def list_errata(status: str = '') -> list:
    sql = 'SELECT * FROM errata'
    args = ()
    if status:
        sql += ' WHERE status=?'
        args = (status,)
    sql += ' ORDER BY id DESC'
    with dbm.get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, args)]


def apply_errata(errata_id: int) -> str:
    """把勘误直接写回知识库 md 文件（替换 before→after），状态置已应用。"""
    with dbm.get_conn() as conn:
        row = conn.execute('SELECT * FROM errata WHERE id=?', (errata_id,)).fetchone()
    if not row:
        raise FileNotFoundError('勘误单不存在')
    path = os.path.join(config.kb_dir(), row['file'])
    if not os.path.exists(path):
        raise FileNotFoundError(row['file'])
    text = io.open(path, encoding='utf-8').read()
    if row['before'] and row['before'] in text:
        text = text.replace(row['before'], row['after'], 1)
        io.open(path, 'w', encoding='utf-8').write(text)
    with dbm.get_conn() as conn:
        conn.execute('UPDATE errata SET status="已应用" WHERE id=?', (errata_id,))
    return 'ok'


# ---------- 知识库更新 ----------
def kb_files() -> list:
    out = []
    for fn in sorted(os.listdir(config.kb_dir())):
        if not fn.endswith('.md'):
            continue
        p = os.path.join(config.kb_dir(), fn)
        text = io.open(p, encoding='utf-8').read()
        fm = {}
        if text.startswith('---'):
            try:
                fm = yaml.safe_load(text.split('---', 2)[1]) or {}
            except Exception:
                fm = {}
        words = len(re.sub(r'\s', '', text))
        out.append({'file': fn, 'type': fm.get('type', ''), 'chapter': fm.get('chapter', ''),
                    'has_frontmatter': bool(fm), 'chars': words,
                    'kps': len(fm.get('knowledge_points', [])),
                    'eps': len(fm.get('exam_points', [])),
                    'mtime': int(os.path.getmtime(p))})
    return out


def save_page(file: str, body: str) -> str:
    """教师直接编辑知识库页面（保持 frontmatter 不动，只替换正文）。"""
    path = os.path.join(config.kb_dir(), file)
    if not os.path.exists(path):
        raise FileNotFoundError(file)
    text = io.open(path, encoding='utf-8').read()
    if text.startswith('---'):
        parts = text.split('---', 2)
        front = '---' + parts[1] + '---\n\n'
    else:
        front = ''
    io.open(path, 'w', encoding='utf-8').write(front + body)
    return 'ok'


# ---------- 出题 / 作业 ----------
def QUESTIONS_PATH():
    return config.questions_path()


_questions_path_old = ''


def add_question(q: dict) -> str:
    if config.is_readonly():
        return 'readonly-' + q.get('id', 'preview')
    data = json.load(io.open(QUESTIONS_PATH(), encoding='utf-8'))
    ids = [x['id'] for x in data['questions']]
    n = 1
    while ('q%02d' % n) in ids:
        n += 1
    q['id'] = 'q%02d' % n
    data['questions'].append(q)
    io.open(QUESTIONS_PATH(), 'w', encoding='utf-8').write(
        json.dumps(data, ensure_ascii=False, indent=1))
    return q['id']


def list_questions() -> list:
    return json.load(io.open(QUESTIONS_PATH(), encoding='utf-8'))['questions']


def add_homework(title: str, detail: str, kp: str, question_ids: str,
                 due_date: str, teacher: str) -> int:
    with dbm.get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO homework(title, detail, kp, question_ids, due_date, teacher, created_at)'
            ' VALUES(?,?,?,?,?,?,?)',
            (title, detail, kp, question_ids, due_date, teacher, int(time.time())))
        return cur.lastrowid


def list_homework() -> list:
    with dbm.get_conn() as conn:
        return [dict(r) for r in conn.execute('SELECT * FROM homework ORDER BY id DESC')]


# ---------- 浏览热力图 ----------
def record_view(file: str, user_name: str):
    with dbm.get_conn() as conn:
        conn.execute('INSERT INTO page_views(file, user_name, viewed_at) VALUES(?,?,?)',
                     (file, user_name, int(time.time())))


def view_heatmap() -> dict:
    with dbm.get_conn() as conn:
        by_file = conn.execute(
            'SELECT file, COUNT(*) AS n FROM page_views GROUP BY file ORDER BY n DESC').fetchall()
        by_user = conn.execute(
            'SELECT user_name, COUNT(*) AS n FROM page_views GROUP BY user_name ORDER BY n DESC'
        ).fetchall()
        recent = conn.execute(
            'SELECT * FROM page_views ORDER BY id DESC LIMIT 20').fetchall()
    return {'by_file': [dict(r) for r in by_file],
            'by_user': [dict(r) for r in by_user],
            'recent': [dict(r) for r in recent]}


# ---------- 知识库状态（Smart Environment 式面板） ----------
def kb_status() -> dict:
    files = kb_files()
    total_chars = sum(f['chars'] for f in files)
    with_fm = sum(1 for f in files if f['has_frontmatter'])
    types = {}
    for f in files:
        types[f['type'] or '未分类'] = types.get(f['type'] or '未分类', 0) + 1
    graph = json.load(io.open(config.graph_path(), encoding='utf-8'))
    eps = [n for n in graph['nodes'] if n['type'] == 'exam_point']
    levels = {}
    for e in eps:
        levels[e['level']] = levels.get(e['level'], 0) + 1
    try:
        n_q = len(list_questions())
    except Exception:
        n_q = 0
    with dbm.get_conn() as conn:
        n_err = conn.execute('SELECT COUNT(*) c FROM errata').fetchone()['c']
        n_hw = conn.execute('SELECT COUNT(*) c FROM homework').fetchone()['c']
        n_views = conn.execute('SELECT COUNT(*) c FROM page_views').fetchone()['c']
    return {
        'sources': {'total': len(files), 'with_frontmatter': with_fm,
                    'coverage': round(with_fm / max(len(files), 1), 3),
                    'total_chars': total_chars},
        'types': types,
        'graph': {'nodes': len(graph['nodes']), 'links': len(graph['links']),
                  'exam_points': len(eps), 'levels': levels,
                  'total_weight': graph.get('stats', {}).get('total_weight', 0)},
        'banks': {'questions': n_q, 'errata': n_err, 'homework': n_hw, 'page_views': n_views},
    }
