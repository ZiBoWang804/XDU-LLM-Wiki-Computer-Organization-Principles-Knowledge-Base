# -*- coding: utf-8 -*-
# SQLite 账本：答题记录/错题/计划/班级数据。平台数据库只是它的 CSV 镜像。
import json
import os
import sqlite3
import time

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS students(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  class_name TEXT DEFAULT '编译2023',
  created_at INTEGER
);
CREATE TABLE IF NOT EXISTS quiz_records(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  question_id TEXT NOT NULL,          -- 题目标识（如 题库:选择题#3）
  kp TEXT NOT NULL,                   -- 所属知识点
  qtype TEXT DEFAULT '',              -- 题型/考点类型
  correct INTEGER NOT NULL,           -- 1对 0错
  error_cause TEXT DEFAULT '',        -- 概念不清/计算失误/审题偏差/知识迁移不足
  answered_at INTEGER
);
CREATE TABLE IF NOT EXISTS wrong_questions(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  question_id TEXT NOT NULL,
  kp TEXT NOT NULL,
  question_text TEXT DEFAULT '',
  student_answer TEXT DEFAULT '',
  right_answer TEXT DEFAULT '',
  error_cause TEXT DEFAULT '',
  created_at INTEGER
);
CREATE TABLE IF NOT EXISTS review_plans(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  exam_date TEXT NOT NULL,
  plan_json TEXT NOT NULL,            -- [{day, date, tasks:[{kp, action, goal}]}]
  created_at INTEGER
);
CREATE TABLE IF NOT EXISTS variant_records(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  kp TEXT NOT NULL,
  variant_json TEXT NOT NULL,         -- {question, answer, steps, hint}
  created_at INTEGER
);
CREATE TABLE IF NOT EXISTS class_stats(      -- 教师端聚合缓存
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  class_name TEXT NOT NULL,
  stat_json TEXT NOT NULL,
  updated_at INTEGER
);
CREATE TABLE IF NOT EXISTS memories(        -- 学习/教学记忆（owner 双命名空间硬隔离）
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_type TEXT NOT NULL,                 -- student | teacher
  owner_id INTEGER NOT NULL,                -- 学号/工号
  kind TEXT NOT NULL,                       -- preference | focus | trend | habit
  content TEXT NOT NULL,
  source TEXT DEFAULT '',                   -- 来源链路（plan/diagnosis/chat…）
  created_at INTEGER,
  updated_at INTEGER
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_mem_owner ON memories(owner_type, owner_id, kind);
CREATE TABLE IF NOT EXISTS selftests(        -- 自测整卷（历史可回看）
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  title TEXT DEFAULT '',
  content_md TEXT NOT NULL,
  meta_json TEXT DEFAULT '[]',
  created_at INTEGER
);
CREATE TABLE IF NOT EXISTS selftest_marks(   -- 逐题自评：正确 | 错误 | 不确定
  selftest_id INTEGER NOT NULL,
  q_idx INTEGER NOT NULL,
  verdict TEXT NOT NULL,
  kp TEXT DEFAULT '',
  created_at INTEGER,
  UNIQUE(selftest_id, q_idx)
);
CREATE TABLE IF NOT EXISTS submissions(      -- 投稿审核队列（学生笔记/勘误 → 教师审）
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT DEFAULT '笔记',                  -- 笔记 | 勘误
  author_type TEXT NOT NULL,                 -- student | teacher
  author_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  content TEXT DEFAULT '',
  source_file TEXT DEFAULT '',               -- 投稿的来源页（可空）
  status TEXT DEFAULT '待审',                -- 待审 | 通过 | 驳回
  review_note TEXT DEFAULT '',
  reviewer INTEGER DEFAULT 0,
  created_at INTEGER,
  reviewed_at INTEGER
);
"""


def get_conn():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


# ---------- 学生 ----------
def add_student(name: str, class_name: str = '编译2023') -> int:
    with get_conn() as conn:
        cur = conn.execute('INSERT INTO students(name, class_name, created_at) VALUES(?,?,?)',
                           (name, class_name, int(time.time())))
        return cur.lastrowid


def list_students(class_name: str = '') -> list:
    sql = 'SELECT * FROM students'
    args = ()
    if class_name:
        sql += ' WHERE class_name=?'
        args = (class_name,)
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, args)]


# ---------- 答题 ----------
def record_answer(student_id: int, question_id: str, kp: str, qtype: str,
                  correct: bool, error_cause: str = '') -> int:
    with get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO quiz_records(student_id, question_id, kp, qtype, correct, error_cause, answered_at)'
            ' VALUES(?,?,?,?,?,?,?)',
            (student_id, question_id, kp, qtype, int(correct), error_cause, int(time.time())))
        return cur.lastrowid


def add_wrong_question(student_id: int, question_id: str, kp: str, question_text: str,
                       student_answer: str, right_answer: str, error_cause: str = '') -> int:
    with get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO wrong_questions(student_id, question_id, kp, question_text,'
            ' student_answer, right_answer, error_cause, created_at) VALUES(?,?,?,?,?,?,?,?)',
            (student_id, question_id, kp, question_text, student_answer, right_answer,
             error_cause, int(time.time())))
        return cur.lastrowid


def recent_mistakes(student_id: int, limit: int = 5) -> list:
    """最近错题（能力轨迹：错题趋势注入生成提示词）。"""
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT kp, question_text, student_answer, right_answer, error_cause, created_at'
            ' FROM wrong_questions WHERE student_id=? ORDER BY created_at DESC LIMIT ?',
            (student_id, limit)).fetchall()
    return [dict(r) for r in rows]


# ---------- 薄弱点诊断 ----------
def weakness_ranking(student_id: int) -> list:
    """按知识点统计正确率，输出薄弱排序 + 错因分布。"""
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT kp, SUM(correct) AS right_cnt, COUNT(*) AS total FROM quiz_records'
            ' WHERE student_id=? GROUP BY kp', (student_id,)).fetchall()
        causes = conn.execute(
            'SELECT kp, error_cause, COUNT(*) AS n FROM quiz_records'
            ' WHERE student_id=? AND correct=0 AND error_cause!="" GROUP BY kp, error_cause',
            (student_id,)).fetchall()
    cause_map = {}
    for c in causes:
        cause_map.setdefault(c['kp'], {})[c['error_cause']] = c['n']
    out = []
    for r in rows:
        acc = r['right_cnt'] / r['total'] if r['total'] else 1.0
        out.append({'kp': r['kp'], 'accuracy': round(acc, 3), 'total': r['total'],
                    'error_causes': cause_map.get(r['kp'], {})})
    out.sort(key=lambda x: (x['accuracy'], -x['total']))
    return out


# ---------- 计划/变式 ----------
def save_plan(student_id: int, exam_date: str, plan: list) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO review_plans(student_id, exam_date, plan_json, created_at) VALUES(?,?,?,?)',
            (student_id, exam_date, json.dumps(plan, ensure_ascii=False), int(time.time())))
        return cur.lastrowid


def save_variant(student_id: int, kp: str, variant: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO variant_records(student_id, kp, variant_json, created_at) VALUES(?,?,?,?)',
            (student_id, kp, json.dumps(variant, ensure_ascii=False), int(time.time())))
        return cur.lastrowid


def list_variants(student_id: int = 0, limit: int = 30) -> list:
    sql = 'SELECT * FROM variant_records'
    args = ()
    if student_id:
        sql += ' WHERE student_id=?'
        args = (student_id,)
    sql += ' ORDER BY id DESC LIMIT ?'
    with get_conn() as conn:
        rows = [dict(r) for r in conn.execute(sql, args + (limit,))]
    for r in rows:
        try:
            r['variant'] = json.loads(r['variant_json'])
        except Exception:
            r['variant'] = {}
    return rows


# ---------- 记忆库（owner_type+owner_id 双命名空间；每 kind 一槽位，新覆盖旧） ----------
def memory_read(owner_type: str, owner_id: int, limit: int = 5) -> list:
    """只返回属于该 owner 的记忆条目——横向隔离由 WHERE 保证。"""
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT kind, content, source, updated_at FROM memories'
            ' WHERE owner_type=? AND owner_id=? ORDER BY updated_at DESC LIMIT ?',
            (owner_type, owner_id, limit)).fetchall()
    return [dict(r) for r in rows]


def memory_write(owner_type: str, owner_id: int, kind: str, content: str,
                 source: str = '') -> int:
    """写入/覆盖一条记忆（同 owner 同 kind 覆盖）。"""
    now = int(time.time())
    with get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO memories(owner_type, owner_id, kind, content, source, created_at, updated_at)'
            ' VALUES(?,?,?,?,?,?,?)'
            ' ON CONFLICT(owner_type, owner_id, kind)'
            ' DO UPDATE SET content=excluded.content, source=excluded.source, updated_at=excluded.updated_at',
            (owner_type, owner_id, kind, content, source, now, now))
        return cur.lastrowid


def memory_text(owner_type: str, owner_id: int, limit: int = 5) -> str:
    """记忆的紧凑文本版（注入生成上下文）。"""
    items = memory_read(owner_type, owner_id, limit)
    if not items:
        return ''
    return '\n'.join('- [%s] %s' % (m['kind'], m['content']) for m in items)


# ---------- 自测卷（整卷历史 + 逐题自评） ----------
def selftest_save(student_id: int, title: str, content_md: str, meta: list) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO selftests(student_id, title, content_md, meta_json, created_at)'
            ' VALUES(?,?,?,?,?)',
            (student_id, title, content_md, json.dumps(meta, ensure_ascii=False), int(time.time())))
        return cur.lastrowid


def selftest_list(student_id: int, limit: int = 20) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT id, title, meta_json, created_at FROM selftests'
            ' WHERE student_id=? ORDER BY id DESC LIMIT ?', (student_id, limit)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        try:
            d['count'] = len(json.loads(d.pop('meta_json') or '[]'))
        except Exception:
            d['count'] = 0
        out.append(d)
    return out


def selftest_get(selftest_id: int) -> dict:
    with get_conn() as conn:
        row = conn.execute('SELECT * FROM selftests WHERE id=?', (selftest_id,)).fetchone()
    if not row:
        return {}
    d = dict(row)
    try:
        d['meta'] = json.loads(d.pop('meta_json') or '[]')
    except Exception:
        d['meta'] = []
    return d


def selftest_mark(selftest_id: int, q_idx: int, verdict: str, kp: str = '') -> int:
    now = int(time.time())
    with get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO selftest_marks(selftest_id, q_idx, verdict, kp, created_at) VALUES(?,?,?,?,?)'
            ' ON CONFLICT(selftest_id, q_idx)'
            ' DO UPDATE SET verdict=excluded.verdict, kp=excluded.kp, created_at=excluded.created_at',
            (selftest_id, q_idx, verdict, kp, now))
        return cur.lastrowid


# ---------- 投稿审核队列（学生笔记/勘误 → 教师审 → 发布/驳回） ----------
def submission_create(kind: str, author_type: str, author_id: int, title: str,
                      content: str = '', source_file: str = '') -> int:
    with get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO submissions(kind, author_type, author_id, title, content, source_file,'
            ' status, created_at) VALUES(?,?,?,?,?,?,"待审",?)',
            (kind, author_type, author_id, title, content, source_file, int(time.time())))
        return cur.lastrowid


def submission_list(class_name: str = '', status: str = '', limit: int = 20) -> list:
    """教师视图：按班级过滤（学生投稿经 students 关联），可按状态过滤。"""
    sql = ('SELECT sub.* FROM submissions sub'
           ' LEFT JOIN students s ON s.id = sub.author_id AND sub.author_type = "student"')
    conds, args = [], []
    if class_name:
        conds.append('(sub.author_type = "teacher" OR s.class_name = ?)')
        args.append(class_name)
    if status:
        conds.append('sub.status = ?')
        args.append(status)
    if conds:
        sql += ' WHERE ' + ' AND '.join(conds)
    sql += ' ORDER BY sub.id DESC LIMIT ?'
    args.append(limit)
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, tuple(args))]


def submission_review(sub_id: int, approve: bool, note: str = '', reviewer: int = 0) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            'UPDATE submissions SET status=?, review_note=?, reviewer=?, reviewed_at=? WHERE id=?',
            ('通过' if approve else '驳回', note, reviewer, int(time.time()), sub_id))
        return cur.rowcount > 0


# ---------- 班级聚合（教师端） ----------
def class_heatmap(class_name: str = '编译2023') -> dict:
    """班级薄弱点热力图数据：kp → 全班正确率/错因分布/高频错题。"""
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT q.kp, SUM(q.correct) AS right_cnt, COUNT(*) AS total'
            ' FROM quiz_records q JOIN students s ON s.id=q.student_id'
            ' WHERE s.class_name=? GROUP BY q.kp', (class_name,)).fetchall()
        causes = conn.execute(
            'SELECT q.kp, q.error_cause, COUNT(*) AS n'
            ' FROM quiz_records q JOIN students s ON s.id=q.student_id'
            ' WHERE s.class_name=? AND q.correct=0 AND q.error_cause!=""'
            ' GROUP BY q.kp, q.error_cause', (class_name,)).fetchall()
        hot = conn.execute(
            'SELECT question_id, kp, COUNT(*) AS wrong_n FROM wrong_questions w'
            ' JOIN students s ON s.id=w.student_id WHERE s.class_name=?'
            ' GROUP BY question_id ORDER BY wrong_n DESC LIMIT 10', (class_name,)).fetchall()
    cause_map = {}
    for c in causes:
        cause_map.setdefault(c['kp'], {})[c['error_cause']] = c['n']
    return {
        'kp_accuracy': [{'kp': r['kp'],
                         'accuracy': round(r['right_cnt'] / r['total'], 3) if r['total'] else 1.0,
                         'total': r['total']} for r in rows],
        'error_causes': cause_map,
        'hot_wrong': [dict(r) for r in hot],
    }


def export_csv(table: str, out_path: str):
    """导出表为 UTF-8 CSV（平台数据库镜像用）。"""
    import csv
    with get_conn() as conn:
        rows = conn.execute('SELECT * FROM %s' % table).fetchall()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        if rows:
            w = csv.writer(f)
            w.writerow(rows[0].keys())
            for r in rows:
                w.writerow(list(r))
    return out_path
