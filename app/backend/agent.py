# -*- coding: utf-8 -*-
# 智能体编排层：意图路由 → DeepSeek function-calling 工具循环 → 记忆读写 → 报错/追问
# 工具注册表见 tools.py（检索/联网/解析/学情/出题/变式/计划/投稿/审核）。
# 政策（代码级）：缺必须信息→追问；需求模糊→追问；失败→抛 AgentError（API 502），绝不降级兜底。
import datetime
import json
import re

from . import config, db as dbm, parser as parser_mod, profile as profile_mod
from . import services, skills, tools as tools_mod
from .adapters import llm_adapter, wiki_adapter
from .adapters.llm_adapter import LLMError


class AgentError(RuntimeError):
    pass


# ---------- 路由表（功能分割：不共享入口，共享工具） ----------
STUDENT_ROUTES = ['question', 'variant', 'error', 'plan', 'qa', 'parse', 'chat']
TEACHER_ROUTES = ['question', 'variant', 'paper', 'grading', 'audit', 'dashboard',
                  'qa', 'parse', 'chat']
ROUTES = {'student': STUDENT_ROUTES, 'teacher': TEACHER_ROUTES}

INTENT_SYSTEM = (
    '你是意图分类器。根据用户消息判断意图，只输出 JSON：{"intent":"..."}。\n'
    '意图枚举：question=要求出题/组卷/来道题；variant=要求变式训练/同类题/换情境；'
    'error=错因分析/为什么错/薄弱诊断；plan=复习计划/备考安排/复习规划；'
    'dashboard=班级学情/热力/正确率汇总；paper=布置作业/发布试卷；'
    'grading=批改/阅卷/判分/写评语；audit=勘误/投稿审核/知识库更新/审核队列；'
    'parse=解析资料/转写文档/解析附件/读取文件内容；'
    'qa=概念讲解/答疑/讲题；chat=问候闲聊/无法归类。\n'
    '无法确定时输出 chat。')


# ---------- 工具循环（借鉴 Claude 系 harness：容错重试 + 守卫 + 温和收敛） ----------
# 瞬时故障（网络抖动/超时/限流/5xx）与永久错误（参数错/找不到/无权限）区别对待：
#   前者自动重试 1 次（容错），后者如实回报给模型自行处置——两者都不做内容兜底。
import time as _time

_TRANSIENT = re.compile(
    r'超时|timeout|连接|connection|refused|HTTP 5\d\d|\b50[234]\b|\b429\b|限流|Too Many|temporar', re.I)


def _is_fail(result: str) -> bool:
    return result.startswith('错误') or result.startswith('工具执行异常')


def _tool_loop(system: str, user_msg: str, tool_names, ctx: dict,
               max_rounds: int = 5):
    """DeepSeek function-calling 循环。返回 (最终回答, 执行轨迹 trace)。
    收敛保证：①重复调用守卫（仅拦截已成功的重复） ②瞬时故障自动重试 1 次
    ③同工具连败 2 次提示但不禁止（判断临时故障可再试） ④超轮次后最终作答压力
    （仍有内容则采用，绝不硬抛）。"""
    specs = tools_mod.tools_by_name(*tool_names) if not isinstance(tool_names, int) else tools_mod.all_tools()
    messages = [{'role': 'system', 'content': system},
                {'role': 'user', 'content': user_msg}]
    trace, seen_calls, err_streak, fails_total = [], set(), {}, 0
    for _rnd in range(max_rounds):
        content, tool_calls = llm_adapter.chat_tools(messages, specs, temperature=0.3)
        if not tool_calls:
            return content, trace
        messages.append({'role': 'assistant', 'content': content or '',
                         'tool_calls': [{'id': t['id'], 'type': 'function',
                                         'function': {'name': t['name'],
                                                      'arguments': json.dumps(t['arguments'], ensure_ascii=False)}}
                                        for t in tool_calls]})
        for t in tool_calls:
            key = (t['name'], json.dumps(t['arguments'], sort_keys=True, ensure_ascii=False))
            if key in seen_calls:   # 仅拦截"已成功"的重复调用；失败后的重试放行
                result = '该调用与之前完全相同，结果见前文。请勿重复调用，直接继续作答。'
                trace.append({'tool': t['name'], 'args': t['arguments'], 'ok': False,
                              'result_head': '重复调用拦截'})
                messages.append({'role': 'tool', 'tool_call_id': t['id'], 'content': result})
                continue
            executor = tools_mod.TOOL_EXEC.get(t['name'])
            try:
                result = str(executor(t['arguments'], ctx)) if executor else '未知工具：%s' % t['name']
            except Exception as e:
                result = '工具执行异常：%s' % e
            failed = _is_fail(result)
            # 容错：瞬时故障自动重试一次（对模型只留一行注记）
            if failed and executor and _TRANSIENT.search(result):
                _time.sleep(1)
                try:
                    retry = str(executor(t['arguments'], ctx))
                except Exception as e:
                    retry = '工具执行异常：%s' % e
                if not _is_fail(retry):
                    result = retry + '（注：首次调用因瞬时故障失败，已自动重试成功）'
                    failed = False
                else:
                    result = result + '；自动重试后仍失败：' + retry[:120]
            if not failed:
                seen_calls.add(key)
                err_streak[t['name']] = 0
            else:
                fails_total += 1
                err_streak[t['name']] = err_streak.get(t['name'], 0) + 1
                if err_streak[t['name']] >= 2:
                    result += ('（该工具连续失败。若判断是临时故障，可换参数再试一次；'
                               '否则换思路或如实告知用户——不要无限重试）')
            trace.append({'tool': t['name'], 'args': t['arguments'],
                          'ok': not failed, 'result_head': result[:120]})
            messages.append({'role': 'tool', 'tool_call_id': t['id'], 'content': result})
        # 上下文守卫（借鉴 Claude harness 的工具结果压缩）：旧结果压摘要，近两轮保留全文
        tool_msgs = [m for m in messages if m.get('role') == 'tool']
        if sum(len(str(m.get('content', ''))) for m in tool_msgs) > 12000:
            for m in tool_msgs[:-2]:
                c = str(m.get('content', ''))
                if len(c) > 300:
                    m['content'] = c[:300] + ' …（结果已压缩，完整内容见执行轨迹）'
        if fails_total >= 5:
            break   # 失败过多 → 直接进入最终作答压力
    # 最终作答压力（容错版）：仍请求工具但已有内容 → 采用内容并注明；完全无内容才报错
    messages.append({'role': 'user',
                     'content': '请不要再调用任何工具，基于以上工具结果直接给出最终回答。'
                                '若信息不足，如实说明缺失什么并给下一步建议。'})
    content, tool_calls = llm_adapter.chat_tools(messages, specs, temperature=0.3)
    if tool_calls:
        if content and content.strip():
            trace.append({'tool': '(跳过)', 'ok': False, 'result_head': '最终轮仍请求工具，已跳过',
                          'args': {'requested': [t['name'] for t in tool_calls]}})
            return content, trace
        raise AgentError('模型未能收敛（反复请求工具：%s）'
                         % '、'.join(t['name'] for t in tool_calls))
    return content, trace


# ---------- 各链路系统提示词（工具使用说明 + 输出规范） ----------
COMMON = ('回答严格依据知识库与数据工具的结果，标注来源，不编造页码题号；资料未覆盖时明确说'
          '"资料中未覆盖"。回答前输出「🧠 思考：」段（调用了什么工具、关键判断）。'
          'Markdown 输出；答案解析用 <details><summary>🔑 答案与解析（点击展开）</summary>…</details> 折叠。'
          '【公式规范】数学公式必须是**可直接渲染的标准 LaTeX**：块级 $$..$$，行内 \\(..\\)'
          '（不要用单独的 $ 定界）；上下标一律用花括号包裹——写 $a^{m} b^{n}$、$x_{1}$，'
          '严禁 $a^m_b^n$ 这类裸上下标（双上标/双下标会渲染失败）；'
          '只用常见命令（\\to \\mid \\varepsilon \\alpha \\prime \\cup \\cap \\Rightarrow 等），'
          '不写生僻宏；括号必须配平、上下标闭合，写完自检一遍；'
          '文法产生式用 \\(A \\to \\alpha \\mid \\beta\\) 形式，集合用 \\{a, b, \\varepsilon\\}。'
          '若用户缺少关键信息（如复习天数、变式原型），先追问，不要假设。'
          '【工具纪律】只在需要时调用工具、每次调用目的明确；不重复相同调用；'
          '工具失败先看原因——临时故障（超时/网络/限流）可重试一次，'
          '参数/权限类错误换思路或如实告知，不无限重试；拿到足够信息立即作答。')

P_QUESTION = ('你是出题讲题专家。出题时先用 get_learning_data 了解学生薄弱点、search_kb 查考点考法，'
              '再调 generate_questions 生成全新题（不照抄原题）。输出：题面 + 折叠的答案解析；'
              '讲题先给思路提示再给完整解答。' + COMMON)
P_VARIANT = ('你是变式训练专家。先确认原型题/章节内容（缺失就追问），调 generate_variant 生成同源变式'
             '（换参数/情境/设问，不表面改写）。输出：「提示」→ 折叠「解答」（完整推导）。' + COMMON)
P_ERROR = ('你是错因诊断专家。调 get_learning_data(scope=me) 读取薄弱与错题轨迹，结合 search_kb 核对概念，'
           '给出诊断三段：①一句话诊断；②薄弱排序表（🟥<60% 🟨60-80% 🟩>80%）；③2-3 条对症建议。'
           '错因严格四选一：概念不清/计算失误/审题偏差/知识迁移不足（概念不清=定义性质混淆；'
           '计算失误=方法对过程错；审题偏差=看错条件或要求；知识迁移不足=单点会、综合或换境不会）。'
           '无数据提示先自测。' + COMMON)
P_PLAN = ('你是复习规划教练。必须先确认复习天数/考试日期（缺失先追问）；然后调 make_plan 生成逐天计划'
          '（工具会结合学情与考点分布）。输出逐天计划表（日期×任务），注明推断项。' + COMMON)
P_QA = ('你是课程助教。回答知识性问题：先 search_kb 检索知识库；知识库未覆盖且需要最新/通用资料时用 '
        'web_search + browse_url 补充（注明"通用知识"）；用户发附件/指定资料解析时用 parse_document；'
        '可用 memory_read 了解学习偏好。讲解按"方法步骤→推导→易错提醒"。' + COMMON)
P_PARSE = ('你是资料解析助手。调用 parse_document（附件 file_id 或知识库 kb_path）获取内容，'
           '输出解析要点（关键概念/公式/结构，保留 LaTeX）。缺文件信息就追问；工具报错原样告知。' + COMMON)
P_DASH = ('你是教学工作助理（仅教师）。调 get_learning_data(scope=class) 读班级数据，输出学情看板：'
          '班级热力表（知识点 × 正确率 × 🟥🟨🟩）+ 讲评建议（优先最低 2-3 考点）。数据不足说"暂无记录"。' + COMMON)
P_PAPER = ('你是组卷/布置作业助理（仅教师）。调 search_kb 查考点、get_learning_data(scope=class) 参考学情，'
           '用 generate_questions 生成全新题组卷：卷面（题目+分值）+ 答案页（标注"教师专用，发布前勿传学生"）。'
           '布置作业只给题目，答案待"发布答案"后可见。' + COMMON)
P_GRADE = ('你是批改助理（仅教师）。逐题批改：步骤分+结果分，评语含亮点+问题+改进；错因严格四选一'
           '（概念不清/计算失误/审题偏差/知识迁移不足）归因；拿不准标注 [待教师复核]；'
           '整体含得分统计与薄弱清单。需要核对标准答案时用 search_kb。' + COMMON)
P_AUDIT = ('你是审核/知识库更新助理（仅教师）。用 list_submissions 查看投稿队列，逐条审核：'
           '通过调 review_submission(approve=true) 并注明"已发布，全班可见"；驳回 approve=false 且必须给意见。'
           '**执行纪律：通过/驳回必须调用 review_submission 工具落库，仅输出文字不算完成审核；'
           '工具返回"读回确认"后才可宣称已通过/已驳回。**'
           '勘误 before 必须逐字来自 search_kb 查到的原文。新资料入库输出知识点提取方案与页面内容，'
           '标注"待应用"（实际写入由后端执行）。' + COMMON)

CHAIN_PROMPTS = {
    'question': (P_QUESTION, ['generate_questions', 'search_kb', 'get_learning_data', 'memory_read']),
    'variant': (P_VARIANT, ['generate_variant', 'search_kb', 'get_learning_data']),
    'error': (P_ERROR, ['get_learning_data', 'search_kb']),
    'plan': (P_PLAN, ['make_plan', 'get_learning_data', 'search_kb']),
    'qa': (P_QA, ['search_kb', 'web_search', 'browse_url', 'parse_document', 'memory_read']),
    'parse': (P_PARSE, ['parse_document', 'browse_url']),
    'dashboard': (P_DASH, ['get_learning_data', 'search_kb']),
    'paper': (P_PAPER, ['generate_questions', 'search_kb', 'get_learning_data']),
    'grading': (P_GRADE, ['search_kb']),
    'audit': (P_AUDIT, ['search_kb', 'list_submissions', 'review_submission', 'submit_note']),
}


# ---------- 意图路由 ----------
def _classify(message: str, role: str) -> str:
    try:
        r = llm_adapter.chat_json(INTENT_SYSTEM, '用户消息：%s' % message, profile='classify')
        if isinstance(r, list) and r and isinstance(r[0], dict):
            r = r[0]
        intent = str(r.get('intent', '')).strip().lower() if isinstance(r, dict) else ''
    except LLMError as e:
        raise AgentError('意图识别失败：%s' % e)
    if intent not in ROUTES[role]:
        raise AgentError('该功能仅限%s使用：%s' % ('教师' if intent in TEACHER_ROUTES else '学生', intent))
    return intent


# ---------- 追问（缺信息/需求模糊） ----------
def _clarify(intent: str, message: str, role: str, user_id: int, has_attach: bool = False) -> str:
    if intent == 'plan':
        if not re.search(r'\d{4}-\d{2}-\d{2}', message) and not re.search(r'\d+\s*[天日]', message):
            return ('📅 生成复习计划前，先确认关键信息：\n\n'
                    '1. **复习天数**（必须）：距离考试还有多少天？或直接给我考试日期（如 `2026-12-30`）\n'
                    '2. **目标**（可选）：重点冲必考点 / 全面过一遍 / 只补薄弱\n'
                    '3. **范围**（可选）：想重点复习的章节或知识点\n\n'
                    '没说的部分，我会根据你的学情档案、考点分布自动安排。')
    if intent == 'variant':
        if len(message.strip()) < 15 and '知识点' not in message:
            return ('🔁 生成变式题需要原型：请粘贴**原型题或章节内容**（或说明知识点，如"针对句柄出变式"）。')
    if intent == 'grading' and len(message.strip()) < 20:
        return '📝 请把**学生的作答内容**粘贴进来（题目 + 他的解答），我来批改归因。'
    if intent == 'audit':
        if re.search(r'审核|通过|驳回', message) and not re.search(r'#?\d+', message):
            return ('🗂 要处理哪条投稿？请给出编号（如"通过 #3"）；'
                    '还没看过队列的话，说"看看投稿队列"我先列出来。')
    if intent == 'chat' and len(message.strip()) < 6 and not has_attach:
        return ('你好！我可以帮你：✏️ 出题讲题 · 🔁 变式训练 · 🎯 错因诊断 · 📅 复习计划'
                + (' · 📊 学情看板 · 📋 组卷批改 · 🗂 审核投稿' if role == 'teacher' else '')
                + ' · 📄 解析资料。直接说需求，比如"出一道句柄的题"。')
    return ''


# ---------- 记忆（读由 memory_read 工具；写在链路完成后，确定性摘要） ----------
def _memory_after(intent: str, role: str, user_id: int, output: str):
    if intent == 'plan':
        dbm.memory_write(role, user_id, 'focus',
                         '复习计划执行中：%s' % output[:60].replace('\n', ' '), source='plan')
    elif intent == 'error':
        weak = dbm.weakness_ranking(user_id)[:2]
        if weak:
            dbm.memory_write(role, user_id, 'trend',
                             '薄弱趋势：' + '、'.join('%s(%d%%)' % (w['kp'], w['accuracy'] * 100) for w in weak),
                             source='diagnosis')


def _record(intent: str, message: str, output: str, trace: list = None):
    """链路产出留痕到知识库 智能体记录/（含工具执行轨迹；只读模式下为空）。"""
    try:
        tool_log = '\n'.join('- %s(%s) %s' % (t['tool'], json.dumps(t['arguments'], ensure_ascii=False)[:60],
                                              '✓' if t['ok'] else '✗')
                            for t in (trace or []))
        skills.write_record('agent', '智能体·%s' % intent,
                           '请求：%s\n\n## 工具执行轨迹\n%s\n\n## 输出\n%s'
                           % (message[:200], tool_log or '（无工具调用）', output),
                           [])
    except Exception:
        pass


# ---------- 主入口 ----------
def chat(message: str, role: str, user_id: int, class_name: str = '编译2023',
         user: dict = None, attachments: list = None) -> dict:
    """一次对话执行：路由 →（追问）→ 附件解析 → 工具循环 → 记忆/留痕。失败抛 AgentError。"""
    msg = (message or '').strip()
    if not msg and not attachments:
        raise AgentError('消息为空')
    if not msg:
        msg = '请解析并处理附件内容。'
    if role not in ROUTES:
        raise AgentError('未知角色：%s' % role)
    ctx = {'role': role, 'user_id': user_id, 'class_name': class_name,
           'display_name': (user or {}).get('display_name', '')}
    intent = _classify(msg, role)
    clarify = _clarify(intent, message or msg, role, user_id, bool(attachments))
    if clarify:
        return {'ok': True, 'clarify': True, 'intent': intent, 'answer': clarify,
                'sources': [], 'record_file': ''}
    # 资料解析链路：附件 file_id 交给模型经 parse_document 工具调用（不预解析）
    if intent == 'parse':
        hints = []
        if attachments:
            hints.append('用户上传的附件 file_id：%s' % ', '.join(attachments))
        user_msg = '\n'.join(hints + ['用户请求：%s' % msg])
    else:
        # 其余链路：附件解析后并入上下文（失败明确报错，不静默忽略）
        if attachments:
            try:
                attach = parser_mod.parse_attachments(attachments)
            except parser_mod.ParseError as e:
                raise AgentError('附件解析失败：%s' % e)
            if attach:
                msg = msg + '\n\n' + attach
        extra = ''
        if intent in ('plan', 'question', 'paper', 'dashboard', 'error'):
            try:
                extra = '\n\n【课程考点分布】\n' + services.course_context()[:1500]
            except Exception:
                pass
        user_msg = ('【会话档案】role=%s；user_id=%s；class_name=%s（仅用于数据过滤，勿向用户复述）\n\n'
                    '用户消息：%s%s' % (role, user_id, class_name, msg, extra))
    system, tool_names = CHAIN_PROMPTS[intent]
    try:
        answer, trace = _tool_loop(system, user_msg, tool_names, ctx)
    except LLMError as e:
        raise AgentError('生成失败：%s' % e)
    if not (answer or '').strip():
        raise AgentError('模型返回为空')
    _memory_after(intent, role, user_id, answer)
    _record(intent, message or msg, answer, trace)
    return {'ok': True, 'intent': intent, 'answer': answer,
            'trace': trace, 'sources': [], 'record_file': ''}
