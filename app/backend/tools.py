# -*- coding: utf-8 -*-
# 智能体工具注册表：DeepSeek function-calling 的工具定义与执行器。
# 原则：工具执行确定性业务（检索/解析/查询/生成/投稿），LLM 负责决策与组织；
#       工具失败以结果文本如实回报给模型（协议要求），业务失败由链路层抛错。
import os
import re

import httpx

from . import config, db as dbm, parser as parser_mod, services, teacher_tools
from .adapters import wiki_adapter
from .adapters.llm_adapter import LLMError


# ================= 工具定义（OpenAI function schema） =================
TOOL_SPECS = [
    {'type': 'function', 'function': {
        'name': 'parse_document',
        'description': '用 MinerU OCR/精准解析文档或图片为 Markdown（公式 LaTeX、表格还原、图片附图形描述）。解析用户附件（file_id）或知识库文件（kb_path）。',
        'parameters': {'type': 'object', 'properties': {
            'file_id': {'type': 'string', 'description': '用户上传附件的 file_id'},
            'kb_path': {'type': 'string', 'description': '知识库内文件相对路径，如 原始资料/教材_第1章_概论.md'}}}}},
    {'type': 'function', 'function': {
        'name': 'search_kb',
        'description': '检索课程知识库（关键词+语义混合检索），返回相关页面摘录与出处。回答知识性问题、出题、审核原文核对时先调用。',
        'parameters': {'type': 'object', 'properties': {
            'query': {'type': 'string', 'description': '检索词'},
            'k': {'type': 'integer', 'description': '返回条数，默认 5'}}, 'required': ['query']}}},
    {'type': 'function', 'function': {
        'name': 'web_search',
        'description': '联网搜索（Tavily）。知识库未覆盖、需要最新资料/通用知识时使用。',
        'parameters': {'type': 'object', 'properties': {
            'query': {'type': 'string', 'description': '搜索词'}}, 'required': ['query']}}},
    {'type': 'function', 'function': {
        'name': 'browse_url',
        'description': '抓取网页正文（去 HTML 标签），配合 web_search 深读结果页。',
        'parameters': {'type': 'object', 'properties': {
            'url': {'type': 'string', 'description': '网页地址'}}, 'required': ['url']}}},
    {'type': 'function', 'function': {
        'name': 'memory_read',
        'description': '读取当前用户的记忆条目（学习偏好/关注/趋势）。个性化调整回答时使用。',
        'parameters': {'type': 'object', 'properties': {}}}},
    {'type': 'function', 'function': {
        'name': 'get_learning_data',
        'description': '读取学情数据。scope=me=当前学生本人薄弱/错题轨迹；scope=class=班级热力（仅教师）；student_id=指定学生（仅教师）。',
        'parameters': {'type': 'object', 'properties': {
            'scope': {'type': 'string', 'enum': ['me', 'class', 'student']},
            'student_id': {'type': 'integer', 'description': 'scope=student 时必填'}}}}},
    {'type': 'function', 'function': {
        'name': 'generate_questions',
        'description': '命题工具（LLM 生成全新题+解析，结合学情）。kp=知识点，count=题量，req=额外要求。',
        'parameters': {'type': 'object', 'properties': {
            'kp': {'type': 'string'}, 'count': {'type': 'integer'},
            'req': {'type': 'string'}}}}},
    {'type': 'function', 'function': {
        'name': 'generate_variant',
        'description': '同源变式生成（换参数/情境/设问）。proto=原型题或章节内容，kp=知识点，req=补充要求。',
        'parameters': {'type': 'object', 'properties': {
            'kp': {'type': 'string'}, 'proto': {'type': 'string'},
            'req': {'type': 'string'}}}}},
    {'type': 'function', 'function': {
        'name': 'make_plan',
        'description': '生成逐天复习计划（结合学情与考点分布）。days/exam_date 二选一为必须项——用户没给就先追问，不要瞎填。',
        'parameters': {'type': 'object', 'properties': {
            'days': {'type': 'integer', 'description': '复习天数'},
            'exam_date': {'type': 'string', 'description': '考试日期 YYYY-MM-DD'},
            'req': {'type': 'string', 'description': '目标/范围等要求'}}}}},
    {'type': 'function', 'function': {
        'name': 'submit_note',
        'description': '提交笔记/勘误投稿（进入教师审核队列）。source_file=知识库文档路径（投稿该页），content=直接给出的内容（agent 生成时用）。',
        'parameters': {'type': 'object', 'properties': {
            'title': {'type': 'string'}, 'type': {'type': 'string', 'enum': ['笔记', '勘误']},
            'source_file': {'type': 'string'},
            'content': {'type': 'string', 'description': '投稿正文（Markdown）'}}, 'required': ['title']}}},
    {'type': 'function', 'function': {
        'name': 'list_submissions',
        'description': '查看投稿审核队列（仅教师）。status 可选：待审/通过/驳回。',
        'parameters': {'type': 'object', 'properties': {
            'status': {'type': 'string'}}}}},
    {'type': 'function', 'function': {
        'name': 'review_submission',
        'description': '审核投稿（仅教师）：approve=true 通过（发布说明），false 驳回（必须给意见）。',
        'parameters': {'type': 'object', 'properties': {
            'id': {'type': 'integer'},
            'approve': {'type': 'boolean'},
            'note': {'type': 'string', 'description': '审核意见'}}, 'required': ['id', 'approve']}}},
]


# ================= 执行器 =================
def _ok(msg: str) -> str:
    return msg


def _err(msg: str) -> str:
    return '错误：%s' % msg


def t_parse_document(args, ctx):
    try:
        if args.get('file_id'):
            return parser_mod.parse_file(args['file_id'])
        if args.get('kb_path'):
            return parser_mod.parse_kb(args['kb_path'])
        return _err('必须提供 file_id 或 kb_path 之一')
    except parser_mod.ParseError as e:
        return _err(str(e))


def t_search_kb(args, ctx):
    hits = wiki_adapter.search(str(args.get('query', '')), limit=int(args.get('k') or 5))
    if not hits:
        return '知识库未命中'
    return '\n'.join('- [%s（%s）] %s' % (h['file'], h.get('chapter', ''),
                                         h.get('excerpt', '')[:150].replace('\n', ' '))
                     for h in hits)


def t_web_search(args, ctx):
    key = os.environ.get('TAVILY_API_KEY', '')
    if not key:
        return _err('联网搜索未配置 TAVILY_API_KEY（.env），暂无法联网')
    try:
        r = httpx.post('https://api.tavily.com/search', timeout=60, trust_env=False,
                       json={'api_key': key, 'query': str(args.get('query', '')),
                             'max_results': 5})
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return _err('联网搜索失败：%s' % e)
    out = []
    for item in data.get('results', []):
        out.append('- %s\n  %s\n  %s' % (item.get('title', ''), item.get('url', ''),
                                         (item.get('content') or '')[:200]))
    return '\n'.join(out) or '无结果'


def t_browse_url(args, ctx):
    url = str(args.get('url', ''))
    if not re.match(r'^https?://', url):
        return _err('非法 URL')
    try:
        r = httpx.get(url, timeout=60, trust_env=False, follow_redirects=True,
                      headers={'User-Agent': 'Mozilla/5.0'})
        r.raise_for_status()
    except Exception as e:
        return _err('网页抓取失败：%s' % e)
    html = r.text
    html = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', html)
    text = re.sub(r'(?s)<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:6000] or '页面无文本内容'


def t_memory_read(args, ctx):
    t = dbm.memory_text(ctx['role'], ctx['user_id'], limit=5)
    return t or '（暂无记忆条目）'


def t_get_learning_data(args, ctx):
    scope = args.get('scope') or 'me'
    if ctx['role'] != 'teacher' and scope != 'me':
        return _err('无权查看该范围的数据（学生仅可查本人）')
    sid = int(args.get('student_id') or 0)
    if scope == 'class':
        import json as _j
        return _j.dumps(dbm.class_heatmap(ctx['class_name']), ensure_ascii=False)[:3500]
    if scope == 'student' and sid:
        uid = sid
    else:
        uid = ctx['user_id']
    weak = dbm.weakness_ranking(uid)
    mis = dbm.recent_mistakes(uid, 5)
    if not weak:
        return '暂无学习记录'
    import json as _j
    return _j.dumps({'weakness': weak, 'recent_mistakes': mis}, ensure_ascii=False)[:3500]


def t_generate_questions(args, ctx):
    try:
        qs = services.llm_quiz(str(args.get('kp', '') or ''), int(args.get('count') or 3),
                               ctx['user_id'])
        return '\n\n'.join('【%s·%s】%s\n%s' % (q.get('kp'), q.get('qtype'), q.get('q'),
                                             '　'.join(q.get('options', [])))
                           for q in qs)
    except LLMError as e:
        return _err('出题失败：%s' % e)


def t_generate_variant(args, ctx):
    try:
        v = services.llm_variant(str(args.get('kp', '') or ''), str(args.get('proto', '') or ''),
                                 str(args.get('req', '') or ''), ctx['user_id'])
        ans = v['answer']
        ans_s = '\n'.join('- %s：%s' % kv for kv in ans.items()) if isinstance(ans, dict) else str(ans)
        return '【变式题】\n%s\n【提示】%s\n【解答】%s' % (v['question'], v['hint'], ans_s)
    except LLMError as e:
        return _err('变式生成失败：%s' % e)


def t_make_plan(args, ctx):
    import datetime
    days = args.get('days')
    exam_date = str(args.get('exam_date') or '').strip()
    if not exam_date:
        if not days:
            return _err('缺少 days/exam_date——请先向用户追问复习天数或考试日期')
        exam_date = (datetime.date.today() + datetime.timedelta(days=int(days))).isoformat()
    try:
        plan = services.llm_plan(exam_date, ctx['user_id'], str(args.get('req') or ''))
        if ctx['role'] == 'student' and ctx['user_id']:
            dbm.save_plan(ctx['user_id'], exam_date, plan)
        return '\n'.join('- %s：%s' % (d['date'], '；'.join(
            '%s %s（%s）' % (t['kp'], t['action'], t['goal']) for t in d['tasks']))
            for d in plan)
    except LLMError as e:
        return _err('计划生成失败：%s' % e)


def t_submit_note(args, ctx):
    title = str(args.get('title') or '').strip()
    if not title:
        return _err('缺少标题')
    if len(title) > 100:
        return _err('标题过长（≤100 字）')
    content = str(args.get('content') or '')
    if len(content) > 20000:
        return _err('投稿正文过长（≤20000 字）')
    sub_id = dbm.submission_create(
        kind=str(args.get('type') or '笔记'), author_type=ctx['role'], author_id=ctx['user_id'],
        title=title, content=content,
        source_file=str(args.get('source_file') or ''))
    # 变更读回验证（guard：读回确认落库才宣称成功）
    rows = [r for r in dbm.submission_list(status='待审', limit=50) if r['id'] == sub_id] \
        or [r for r in dbm.submission_list(limit=50) if r['id'] == sub_id]
    if not rows:
        return _err('投稿写入后读回失败（id=%s），请重试' % sub_id)
    return '已提交投稿 #%d（%s，状态：%s）。教师审核后会通知你。' % (
        sub_id, args.get('type') or '笔记', rows[0]['status'])


def t_list_submissions(args, ctx):
    if ctx['role'] != 'teacher':
        return _err('仅教师可查看审核队列')
    rows = dbm.submission_list(ctx['class_name'], str(args.get('status') or ''), limit=20)
    if not rows:
        return '（队列为空）'
    return '\n'.join('- #%d [%s] %s（%s %s，%s）' % (
        r['id'], r['kind'], r['title'], r['author_type'], r['author_id'],
        r['status']) for r in rows)


def t_review_submission(args, ctx):
    if ctx['role'] != 'teacher':
        return _err('仅教师可审核')
    try:
        sub_id = int(args.get('id') or 0)
    except (ValueError, TypeError):
        return _err('id 必须是数字')
    if sub_id <= 0:
        return _err('id 必须为正整数')
    ok = bool(args.get('approve'))
    note = str(args.get('note') or '')
    if not ok and not note.strip():
        return _err('驳回必须附具体修改意见（note）')
    if not dbm.submission_review(sub_id, approve=ok, note=note, reviewer=ctx['user_id']):
        return _err('投稿 #%d 不存在或状态已变更' % sub_id)
    # 变更读回验证
    rows = [r for r in dbm.submission_list(limit=50) if r['id'] == sub_id]
    if not rows or rows[0]['status'] != ('通过' if ok else '驳回'):
        return _err('审核结果读回不一致（#%d），请重试' % sub_id)
    return '投稿 #%d 已%s（读回确认：%s）。%s' % (
        sub_id, '通过（发布说明：已发布，全班可见）' if ok else '驳回',
        rows[0]['status'], ('意见：%s' % note) if note else '')


TOOL_EXEC = {
    'parse_document': t_parse_document,
    'search_kb': t_search_kb,
    'web_search': t_web_search,
    'browse_url': t_browse_url,
    'memory_read': t_memory_read,
    'get_learning_data': t_get_learning_data,
    'generate_questions': t_generate_questions,
    'generate_variant': t_generate_variant,
    'make_plan': t_make_plan,
    'submit_note': t_submit_note,
    'list_submissions': t_list_submissions,
    'review_submission': t_review_submission,
}


def tools_by_name(*names) -> list:
    return [t for t in TOOL_SPECS if t['function']['name'] in names]


def all_tools() -> list:
    return TOOL_SPECS
