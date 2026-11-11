# -*- coding: utf-8 -*-
# 全局配置：环境变量 + 多课程注册表（知识库可插拔——换课程=注册新课程，无需改代码）
import contextvars
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # app/
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), '.env')


def _load_env():
    if not os.path.exists(ENV_PATH):
        return
    with open(ENV_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())


_load_env()

# TeleAgent 平台
TELEAI_BASE = os.environ.get('TELEAI_BASE', 'https://agent.teleai.com.cn')
TELEAI_DATASET_KEY = os.environ.get('TELEAI_DATASET_KEY', '')
TELEAI_DATABASE_KEY = os.environ.get('TELEAI_DATABASE_KEY', '')

# 模型 API（OpenAI 兼容）
LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api-maas.teleai.com.cn/v1')
LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_MODEL = os.environ.get('LLM_MODEL', 'TeleChat3-438B-A24B')

DB_PATH = os.path.join(BASE_DIR, 'data', 'app.db')

# 知识库写权限（Claudian 式"YOLO 开关"）：readonly=True 时技能只预览不落库
import contextvars
READONLY = contextvars.ContextVar('readonly', default=False)


def is_readonly() -> bool:
    return READONLY.get()

# ================= 多课程注册表（可复用核心） =================
COURSES_PATH = os.path.join(BASE_DIR, 'data', 'courses.json')
DEFAULT_COURSE = 'compiler'


def _seed_courses():
    return [{
        'id': 'compiler',
        'name': '编译原理',
        'description': '《编译原理》第3版 王生原等 · 清华大学出版社',
        'kb_dir': os.path.join(os.path.dirname(BASE_DIR), '编译原理知识库'),
    }]


def _load_courses():
    if os.path.exists(COURSES_PATH):
        try:
            return json.load(open(COURSES_PATH, encoding='utf-8'))
        except Exception:
            pass
    cs = _seed_courses()
    save_courses(cs)
    return cs


def save_courses(courses):
    os.makedirs(os.path.dirname(COURSES_PATH), exist_ok=True)
    json.dump(courses, open(COURSES_PATH, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


COURSES = _load_courses()
# 课程上下文：优先请求头 X-Course-Id（中间件设置），子进程用 COURSE_ID 环境变量
_course_var = contextvars.ContextVar('course_id',
                                     default=os.environ.get('COURSE_ID', DEFAULT_COURSE))


def list_courses():
    return [{k: c[k] for k in ('id', 'name', 'description') if k in c} for c in COURSES]


def get_course(cid: str = None) -> dict:
    cid = cid or _course_var.get()
    for c in COURSES:
        if c['id'] == cid:
            return c
    return COURSES[0]


def set_course(cid: str):
    if any(c['id'] == cid for c in COURSES):
        _course_var.set(cid)


def create_course(name: str, description: str = '', kb_dir: str = '') -> dict:
    cid = 'c' + str(abs(hash(name)) % 100000)
    if not kb_dir:
        kb_dir = os.path.join(os.path.dirname(BASE_DIR), 'courses', cid)
    os.makedirs(kb_dir, exist_ok=True)
    c = {'id': cid, 'name': name, 'description': description, 'kb_dir': kb_dir}
    COURSES.append(c)
    save_courses(COURSES)
    return c


# ---- 按当前课程解析路径（上下文变量，请求级隔离） ----
def kb_dir() -> str:
    return get_course()['kb_dir']


def graph_path() -> str:
    return os.path.join(BASE_DIR, 'data', 'graph_%s.json' % get_course()['id'])


def questions_path() -> str:
    return os.path.join(BASE_DIR, 'data', 'questions_%s.json' % get_course()['id'])


def records_dir() -> str:
    return os.path.join(kb_dir(), '智能体记录')
