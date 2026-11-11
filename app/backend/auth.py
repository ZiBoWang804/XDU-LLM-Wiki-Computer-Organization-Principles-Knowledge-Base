# -*- coding: utf-8 -*-
# 登录鉴权：账号 + 会话 token + 角色（teacher/student）
import hashlib
import os
import secrets
import time

from . import db as dbm

USERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL,              -- teacher | student
  display_name TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS sessions(
  token TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL,
  created_at INTEGER
);
"""

# 演示账号（首次启动自动创建）
SEED_USERS = [
    ('teacher', 'teacher123', 'teacher', '王老师'),
    ('student', 'student123', 'student', '张三'),
]


def _hash(pw: str) -> str:
    return hashlib.sha256(('salt_ta_' + pw).encode()).hexdigest()


def init_auth():
    with dbm.get_conn() as conn:
        conn.executescript(USERS_SCHEMA)
        for u, p, r, d in SEED_USERS:
            conn.execute('INSERT OR IGNORE INTO users(username, password_hash, role, display_name)'
                         ' VALUES(?,?,?,?)', (u, _hash(p), r, d))


def login(username: str, password: str) -> dict:
    with dbm.get_conn() as conn:
        row = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    if not row or row['password_hash'] != _hash(password):
        raise PermissionError('用户名或密码错误')
    token = secrets.token_hex(24)
    with dbm.get_conn() as conn:
        conn.execute('INSERT INTO sessions(token, user_id, created_at) VALUES(?,?,?)',
                     (token, row['id'], int(time.time())))
    return {'token': token, 'role': row['role'], 'display_name': row['display_name'] or username}


def register(username: str, password: str, display_name: str = '', role: str = 'student') -> dict:
    with dbm.get_conn() as conn:
        try:
            conn.execute('INSERT INTO users(username, password_hash, role, display_name) VALUES(?,?,?,?)',
                         (username, _hash(password), role, display_name or username))
        except Exception:
            raise ValueError('用户名已存在')
    return login(username, password)


def logout(token: str):
    with dbm.get_conn() as conn:
        conn.execute('DELETE FROM sessions WHERE token=?', (token,))


def verify(token: str) -> dict | None:
    """返回 {user_id, username, role, display_name} 或 None。"""
    if not token:
        return None
    with dbm.get_conn() as conn:
        row = conn.execute('SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id'
                           ' WHERE s.token=?', (token,)).fetchone()
    if not row:
        return None
    return {'user_id': row['id'], 'username': row['username'], 'role': row['role'],
            'display_name': row['display_name'] or row['username']}
