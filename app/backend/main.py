# -*- coding: utf-8 -*-
# FastAPI 主应用：双端（学生/教师）API + 登录鉴权 + 静态页托管
import json
import os
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import auth, config, db, profile, services, skills, teacher_tools
from .adapters import database_adapter, dataset_adapter, llm_adapter, wiki_adapter

app = FastAPI(title='编译原理考点地图智能体')

db.init_db()
auth.init_auth()
teacher_tools.init_teacher_db()


# ================= 鉴权 =================
class LoginReq(BaseModel):
    username: str
    password: str


class RegisterReq(BaseModel):
    username: str
    password: str
    display_name: str = ''


@app.post('/api/auth/login')
def api_login(req: LoginReq):
    try:
        return auth.login(req.username, req.password)
    except PermissionError as e:
        raise HTTPException(401, str(e))


@app.post('/api/auth/register')
def api_register(req: RegisterReq):
    try:
        return auth.register(req.username, req.password, req.display_name)
    except ValueError as e:
        raise HTTPException(409, str(e))


@app.post('/api/auth/logout')
def api_logout(request: Request):
    auth.logout(request.headers.get('X-Token', ''))
    return {'ok': True}


@app.get('/api/auth/me')
def api_me(request: Request):
    user = auth.verify(request.headers.get('X-Token', ''))
    if not user:
        raise HTTPException(401, '未登录')
    return user


def _user(request: Request, role: str = '') -> dict:
    user = auth.verify(request.headers.get('X-Token', ''))
    if not user:
        raise HTTPException(401, '未登录')
    if role and user['role'] != role:
        raise HTTPException(403, '需要 %s 权限' % role)
    return user


@app.middleware('http')
async def auth_middleware(request: Request, call_next):
    """除 /api/auth/* 与静态页外，所有 /api/* 需携带 X-Token 登录；X-Course-Id 切换课程。"""
    path = request.url.path
    cid = request.headers.get('X-Course-Id', '')
    if cid:
        config.set_course(cid)
    if path.startswith('/api/') and not path.startswith('/api/auth/'):
        if not auth.verify(request.headers.get('X-Token', '')):
            return JSONResponse({'detail': '未登录'}, status_code=401)
    return await call_next(request)


# ================= 课程管理（多知识库可复用） =================
class CourseReq(BaseModel):
    name: str
    description: str = ''
    kb_dir: str = ''


@app.get('/api/courses')
def api_courses():
    return config.list_courses()


@app.post('/api/courses')
def api_create_course(req: CourseReq, request: Request):
    _user(request, 'teacher')
    c = config.create_course(req.name, req.description, req.kb_dir)
    return c


class CourseSwitchReq(BaseModel):
    course_id: str


@app.post('/api/courses/switch')
def api_switch_course(req: CourseSwitchReq):
    config.set_course(req.course_id)
    c = config.get_course()
    return {'ok': True, 'course': {'id': c['id'], 'name': c['name']}}


# ================= 考点图谱 =================
@app.get('/api/graph')
def get_graph():
    with open(config.graph_path(), encoding='utf-8') as f:
        return json.load(f)


# ================= LLM Wiki 层（权威知识） =================
@app.get('/api/wiki/pages')
def wiki_pages():
    return wiki_adapter.list_pages()


@app.get('/api/wiki/page')
def wiki_page(name: str):
    try:
        return wiki_adapter.get_page(name)
    except FileNotFoundError:
        raise HTTPException(404, '页面不存在: ' + name)


@app.get('/api/wiki/file')
def wiki_file(name: str):
    """PDF/附件预览：返回原始文件流（浏览器可直接渲染 PDF）。"""
    import mimetypes
    safe = name.replace('..', '')
    path = os.path.join(config.kb_dir(), safe)
    if not os.path.exists(path) or not os.path.isfile(path):
        raise HTTPException(404, '文件不存在')
    mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    return FileResponse(path, media_type=mime)


@app.get('/api/wiki/search')
def wiki_search(q: str):
    return wiki_adapter.search(q)


@app.get('/api/wiki/related')
def wiki_related(name: str, k: int = 5):
    """Smart Connections：返回相关文档（本地向量相似度）。"""
    try:
        return wiki_adapter.related(name, k)
    except FileNotFoundError:
        raise HTTPException(404, '页面不存在: ' + name)


class LocateReq(BaseModel):
    name: str
    q: str


@app.post('/api/wiki/locate')
def wiki_locate(req: LocateReq):
    """Smart Lookup：返回正文中每个命中位置的上下文，供前端滚动定位+高亮。"""
    try:
        page = wiki_adapter.get_page(req.name)
    except FileNotFoundError:
        raise HTTPException(404, '页面不存在')
    body = page['body']
    hits, start = [], 0
    q = req.q
    while True:
        i = body.find(q, start)
        if i < 0:
            break
        hits.append({'pos': i, 'excerpt': body[max(0, i - 40):i + len(q) + 40].replace('\n', ' ')})
        start = i + len(q)
        if len(hits) >= 20:
            break
    return {'file': req.name, 'query': q, 'hits': hits}


# ================= RAG 层（TeleAgent 知识库） =================
class RagQuery(BaseModel):
    query: str
    top_k: int = 3


@app.post('/api/rag/retrieve')
def rag_retrieve(req: RagQuery):
    ds = os.environ.get('TELEAI_DATASET_ID', '')
    if not ds:
        return {'hits': [], 'note': 'TELEAI_DATASET_ID 未配置，RAG 层未启用'}
    try:
        return {'hits': dataset_adapter.retrieve(req.query, [ds], req.top_k)}
    except Exception as exc:
        return {'hits': [], 'error': str(exc)}


# ================= 智能问答（Wiki 优先 + RAG 兜底 + 引用出处） =================
class AskReq(BaseModel):
    question: str
    student_id: int = 0
    context_file: str = ''
    hint_first: bool = True
    temperature: float = 0.3


@app.post('/api/ask')
def ask(req: AskReq):
    # 第一层 wiki 检索（带当前关联文档优先）
    hits = wiki_adapter.search(req.question, limit=3)
    ctx_files = []
    if req.context_file:
        try:
            ctx_files.append(wiki_adapter.get_page(req.context_file))
        except FileNotFoundError:
            pass
    wiki_ctx = '\n\n'.join(
        '【%s（%s）】\n%s' % (h['file'], h['chapter'], h['excerpt']) for h in hits)
    for p in ctx_files:
        wiki_ctx = '【当前关联文档：%s】\n%s\n\n' % (p['file'], p['body'][:1500]) + wiki_ctx
    # 第二层 RAG（若配置）
    rag_ctx = ''
    ds = os.environ.get('TELEAI_DATASET_ID', '')
    if ds:
        try:
            for hit in dataset_adapter.retrieve(req.question, [ds], 2):
                rag_ctx += '\n【RAG:%s】\n%s' % (hit['document_name'], hit['content'][:500])
        except Exception:
            pass
    system = ('你是编译原理课程助教（TeleAgent 智能体）。回答必须严格依据给定资料，注明资料来源（文件名/文档名），'
              '严禁编造教材页码或题号。资料不足时明确说"资料中未覆盖"。' +
              ('讲解题目先给思路提示、学生尝试后再给完整解答，避免直接抄答案。' if req.hint_first
               else '可直接给出完整解答。'))
    # 学生档案注入：agent 记得住这个学生（薄弱点/学习路径/能力画像）
    stu_ctx = ''
    if req.student_id:
        try:
            stu_ctx = '\n\n【学生档案】' + profile.student_profile_text(req.student_id)
        except Exception:
            pass
    user = '资料：\n%s%s\n\n%s\n\n学生问题：%s' % (wiki_ctx, rag_ctx, stu_ctx, req.question)
    try:
        answer = llm_adapter.chat(system, user, temperature=req.temperature)
    except Exception as exc:
        raise HTTPException(502, '问答生成失败：%s' % str(exc)[:150])
    return {'answer': answer, 'sources': hits}


# ================= 学生端：自测/诊断/计划/变式 =================
def QUESTIONS_PATH():
    return config.questions_path()


_questions_path_old = ''


@app.get('/api/quiz/questions')
def quiz_questions(kp: str = '', limit: int = 10, student_id: int = 0):
    """自测题（LLM 结合学情/能力轨迹全新生成，与题库去重后入库）。不含答案泄露字段。"""
    try:
        qs = services.llm_quiz(kp, limit, student_id)
    except llm_adapter.LLMError as e:
        raise HTTPException(502, '自测题生成失败：%s' % e)
    out = []
    for q in qs:
        qid = teacher_tools.add_question(dict(q))
        out.append({'id': qid, 'type': q['type'], 'kp': q['kp'], 'qtype': q['qtype'],
                    'q': q['q'], 'options': q['options']})
    return out


@app.get('/api/quiz/answer')
def quiz_answer(question_id: str):
    """判题用：返回标准答案与出处（提交时才调用）。"""
    with open(QUESTIONS_PATH(), encoding='utf-8') as f:
        qs = json.load(f)['questions']
    for q in qs:
        if q['id'] == question_id:
            return {'answer': q['answer'], 'source': q['source']}
    raise HTTPException(404, '题目不存在')
class AnswerReq(BaseModel):
    student_id: int
    question_id: str
    kp: str
    qtype: str = ''
    correct: bool
    question_text: str = ''
    student_answer: str = ''
    right_answer: str = ''


@app.post('/api/quiz/submit')
def quiz_submit(req: AnswerReq):
    cause, cause_msg = '', ''
    if not req.correct and req.question_text:
        try:
            cause = services.classify_error(req.question_text, req.right_answer, req.student_answer)
        except Exception as e:
            cause_msg = '错因归类失败：%s' % str(e)[:80]
        db.add_wrong_question(req.student_id, req.question_id, req.kp, req.question_text,
                              req.student_answer, req.right_answer, cause)
    db.record_answer(req.student_id, req.question_id, req.kp, req.qtype, req.correct, cause)
    return {'ok': True, 'error_cause': cause or cause_msg}


@app.get('/api/quiz/weakness')
def quiz_weakness(student_id: int):
    return db.weakness_ranking(student_id)


class PlanReq(BaseModel):
    student_id: int
    exam_date: str  # YYYY-MM-DD
    req: str = ''   # 额外要求


@app.post('/api/plan/generate')
def plan_generate(req: PlanReq):
    t0 = time.time()
    try:
        plan = services.llm_plan(req.exam_date, req.student_id, req.req)
    except llm_adapter.LLMError as e:
        raise HTTPException(502, '复习计划生成失败：%s' % e)
    db.save_plan(req.student_id, req.exam_date, plan)
    return {'plan': plan, 'days': len(plan), 'elapsed_s': round(time.time() - t0, 2)}


class VariantReq(BaseModel):
    student_id: int
    kp: str
    proto: str = ''
    req: str = ''


@app.post('/api/variant/generate')
def variant_generate(req: VariantReq):
    try:
        v = services.llm_variant(req.kp, req.proto, req.req, req.student_id)
    except llm_adapter.LLMError as e:
        raise HTTPException(502, '变式题生成失败：%s' % e)
    if req.student_id:
        db.save_variant(req.student_id, req.kp, v)
    return v


@app.get('/api/variants')
def variant_list(student_id: int = 0):
    """变式题记录（变式页纯展示数据源）。"""
    return db.list_variants(student_id, limit=40)


# ================= 模型配置状态 =================
@app.get('/api/config/status')
def config_status():
    return {'llm_configured': bool(config.LLM_API_KEY),
            'llm_model': config.LLM_MODEL, 'llm_base_url': config.LLM_BASE_URL,
            'dataset_key': bool(config.TELEAI_DATASET_KEY),
            'database_key': bool(config.TELEAI_DATABASE_KEY)}


# ================= Skill 技能调度（助教调用） =================
@app.get('/api/skills')
def api_skills(request: Request):
    user = _user(request)
    return skills.list_skills(user['role'])


class SkillReq(BaseModel):
    skill: str
    params: dict = {}
    effort: str = 'high'        # 思考等级：low / medium / high（Claudian 式）
    kb_write: bool = True       # 知识库写权限（YOLO 开关）：False=只预览不落库


@app.post('/api/skills/run')
def api_skill_run(req: SkillReq, request: Request):
    user = _user(request)
    config.READONLY.set(not req.kb_write)
    # 思考等级 → 生成参数：低=快而省，高=慢而深
    req.params.setdefault('effort', req.effort)
    try:
        result = skills.run_skill(req.skill, req.params, user)
    except KeyError as e:
        raise HTTPException(404, str(e))
    except PermissionError as e:
        raise HTTPException(403, str(e))
    finally:
        config.READONLY.set(False)
    if not req.kb_write:
        result['readonly'] = True
        result['output'] = result.get('output', '') + '\n\n⚠️ 只读模式：以上内容未写入知识库'
    return result


# ================= 档案（学生能力雷达/学习路径 · 教师学情画像） =================
@app.get('/api/profile/student')
def profile_student(student_id: int, name: str = ''):
    return profile.student_profile(student_id, name)


@app.get('/api/profile/teacher')
def profile_teacher(request: Request):
    user = _user(request)
    return profile.teacher_profile(user.get('display_name', ''))


# ================= 教师端：勘误 / 知识库管理 =================
class ErrataReq(BaseModel):
    file: str
    kind: str = '勘误'
    before: str = ''
    after: str = ''
    note: str = ''


@app.post('/api/teacher/errata')
def t_add_errata(req: ErrataReq, request: Request):
    user = _user(request, 'teacher')
    eid = teacher_tools.add_errata(req.file, req.kind, req.before, req.after, req.note,
                                   user['display_name'])
    return {'id': eid}


@app.get('/api/teacher/errata')
def t_list_errata(request: Request, status: str = ''):
    _user(request, 'teacher')
    return teacher_tools.list_errata(status)


@app.post('/api/teacher/errata/apply')
def t_apply_errata(request: Request, id: int = 0):
    _user(request, 'teacher')
    try:
        return {'ok': teacher_tools.apply_errata(id) == 'ok'}
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


class SavePageReq(BaseModel):
    name: str
    body: str


@app.post('/api/teacher/page/save')
def t_save_page(req: SavePageReq, request: Request):
    user = _user(request, 'teacher')
    try:
        teacher_tools.save_page(req.name, req.body)
    except FileNotFoundError:
        raise HTTPException(404, '页面不存在')
    teacher_tools.add_errata(req.name, '修改', '', '', '教师编辑保存', user['display_name'])
    return {'ok': True}


@app.get('/api/teacher/kb/files')
def t_kb_files(request: Request):
    _user(request, 'teacher')
    return teacher_tools.kb_files()


@app.post('/api/teacher/kb/rebuild')
def t_kb_rebuild(request: Request):
    """重建考点图谱（知识库更新后刷新）。"""
    _user(request, 'teacher')
    import subprocess, sys
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(config.BASE_DIR), 'tmp', 'build_graph.py')],
                       capture_output=True, text=True)
    return {'ok': r.returncode == 0, 'output': (r.stdout or '')[-400:]}


# ================= 教师端：出题 / 作业 =================
class QuestionReq(BaseModel):
    type: str
    kp: str
    qtype: str
    q: str
    options: list
    answer: int
    source: str = '教师出题'


@app.post('/api/teacher/question')
def t_add_question(req: QuestionReq, request: Request):
    _user(request, 'teacher')
    qid = teacher_tools.add_question(req.dict())
    return {'id': qid}


@app.get('/api/teacher/questions')
def t_list_questions(request: Request):
    _user(request, 'teacher')
    return teacher_tools.list_questions()


class HomeworkReq(BaseModel):
    title: str
    detail: str = ''
    kp: str = ''
    question_ids: str = ''
    due_date: str = ''


@app.post('/api/teacher/homework')
def t_add_homework(req: HomeworkReq, request: Request):
    user = _user(request, 'teacher')
    hid = teacher_tools.add_homework(req.title, req.detail, req.kp, req.question_ids,
                                     req.due_date, user['display_name'])
    return {'id': hid}


@app.get('/api/teacher/homework')
def t_list_homework(request: Request):
    _user(request)  # 学生也可查看作业
    return teacher_tools.list_homework()


# ================= 教师端：浏览热力图 / 知识库状态 =================
class ViewReq(BaseModel):
    file: str
    user_name: str = ''


@app.post('/api/view/record')
def view_record(req: ViewReq):
    teacher_tools.record_view(req.file, req.user_name)
    return {'ok': True}


@app.get('/api/teacher/view-heatmap')
def t_view_heatmap(request: Request):
    _user(request, 'teacher')
    return teacher_tools.view_heatmap()


@app.get('/api/teacher/kb-status')
def t_kb_status(request: Request):
    _user(request, 'teacher')
    return teacher_tools.kb_status()


# ================= Inline Edit（选中改写 + diff 预览） =================
class RewriteReq(BaseModel):
    text: str
    instruction: str = '润色'
    context_file: str = ''


@app.post('/api/rewrite')
def api_rewrite(req: RewriteReq, request: Request):
    """选中文字 + 改写指令 → 新文本（diff 由前端对比展示）。"""
    user = _user(request)
    system = ('你是编译原理知识库的文本改写助手。按用户指令改写给定文字，只输出改写结果本身，'
              '保持术语准确、markdown 格式、数学符号（$..$）不变。严禁引入事实错误或编造页码。')
    instruction = req.instruction.strip() or '润色'
    try:
        new_text = llm_adapter.chat(system, '【原文】\n%s\n\n【改写指令】%s' % (req.text, instruction),
                                    temperature=0.3)
    except Exception as e:
        raise HTTPException(502, '改写失败：%s' % str(e)[:150])
    return {'before': req.text, 'after': new_text, 'instruction': instruction}


class ApplyRewriteReq(BaseModel):
    file: str
    before: str
    after: str
    note: str = 'Inline Edit 改写'


@app.post('/api/rewrite/apply')
def api_rewrite_apply(req: ApplyRewriteReq, request: Request):
    """应用改写到知识库（写权限开启时直接替换，关闭时落为勘误单）。"""
    user = _user(request)
    try:
        page = wiki_adapter.get_page(req.file)
    except FileNotFoundError:
        raise HTTPException(404, '页面不存在')
    if req.before not in page['body']:
        raise HTTPException(400, '原文已变化，请重新选中')
    if not config.is_readonly():
        body = page['body'].replace(req.before, req.after, 1)
        teacher_tools.save_page(req.file, body)
        teacher_tools.add_errata(req.file, '修改', req.before, req.after, req.note,
                                 user.get('display_name', ''))
        return {'applied': True, 'readonly': False}
    # 只读模式：落勘误单（不直接改原文）
    teacher_tools.add_errata(req.file, '勘误', req.before, req.after, req.note,
                             user.get('display_name', ''))
    return {'applied': False, 'readonly': True, 'note': '已记录为勘误单，写库开关打开后可应用'}


# ================= Cross-Session（多智能体协作） =================
class CollabReq(BaseModel):
    task: str
    teacher_name: str = '教师智能体'
    student_name: str = '学生智能体'
    rounds: int = 2


@app.post('/api/collab')
def api_collab(req: CollabReq, request: Request):
    """双智能体协作：教师智能体布置/审阅 + 学生智能体作答，多轮对话完成任务。"""
    user = _user(request)
    dialogue = []
    task = req.task
    for i in range(min(req.rounds, 3)):
        # 学生智能体作答
        try:
            stu = llm_adapter.chat(
                '你是学生智能体「%s」，正在和教师智能体「%s」协作完成编译原理学习任务。'
                '请认真作答或执行分给你的部分，输出你的成果。若前一轮教师给了修改意见，先回应再修订。' % (req.student_name, req.teacher_name),
                '任务：%s\n%s' % (task, '\n'.join('【%s】%s' % (d['agent'], d['text'][-300:]) for d in dialogue[-2:]) or '（开始作答）'),
                temperature=0.4)
        except Exception as e:
            raise HTTPException(502, '学生智能体第 %d 轮失败：%s' % (i + 1, str(e)[:120]))
        dialogue.append({'agent': req.student_name, 'role': 'student', 'text': stu})
        # 教师智能体审阅
        try:
            tea = llm_adapter.chat(
                '你是教师智能体「%s」，正在审阅学生智能体「%s」的成果并给修改意见。'
                '任务完成度够了就说"通过"并总结成果；不够就给出具体修改意见。要求：结论明确、意见具体。' % (req.teacher_name, req.student_name),
                '任务：%s\n【学生成果】\n%s' % (task, stu), temperature=0.3)
        except Exception as e:
            raise HTTPException(502, '教师智能体第 %d 轮失败：%s' % (i + 1, str(e)[:120]))
        dialogue.append({'agent': req.teacher_name, 'role': 'teacher', 'text': tea})
        if '通过' in tea[:20] or '完成' in tea[:20]:
            break
    final = dialogue[-1]['text'] if dialogue else ''
    return {'dialogue': dialogue, 'final': final, 'rounds': len(dialogue) // 2}


# ================= 教师端 =================
@app.get('/api/teacher/heatmap')
def teacher_heatmap(class_name: str = '编译2023'):
    return db.class_heatmap(class_name)


@app.get('/api/teacher/students')
def teacher_students(class_name: str = '编译2023'):
    return db.list_students(class_name)


@app.post('/api/admin/sync')
def admin_sync():
    """SQLite 导出 CSV 快照并同步到平台数据库（需配置 TELEAI_TEACHER_DB_ID / STUDENT_DB_ID）。"""
    results = {}
    for table, envk in [('quiz_records', 'TELEAI_TEACHER_DB_ID'), ('students', 'TELEAI_STUDENT_DB_ID')]:
        dbid = os.environ.get(envk, '')
        if not dbid:
            results[table] = {'skipped': 'env ' + envk + ' 未配置'}
            continue
        csv_path = os.path.join(config.BASE_DIR, 'data', table + '.csv')
        db.export_csv(table, csv_path)
        try:
            results[table] = database_adapter.sync_snapshot(dbid, csv_path)
        except Exception as exc:
            results[table] = {'error': str(exc)}
    return results


# ================= 静态页 =================
STATIC = os.path.join(config.BASE_DIR, 'static')
app.mount('/static', StaticFiles(directory=STATIC), name='static')


@app.get('/')
def index():
    return FileResponse(os.path.join(STATIC, 'index.html'))
