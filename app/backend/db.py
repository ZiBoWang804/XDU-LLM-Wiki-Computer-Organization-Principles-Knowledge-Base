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
