# -*- coding: utf-8 -*-
# 业务服务：复习计划 / 变式训练 / 自测题生成——全部由接入的 LLM 结合学情与能力轨迹生成
# 原则：不做规则/模板降级兜底；生成失败直接抛 LLMError 交由上层显式报错
import datetime
import difflib
import io
import json

from . import config, db as dbm, profile as profile_mod
from .adapters import llm_adapter
from .adapters.llm_adapter import LLMError

# 错因固定四分类（对应验收标准）
ERROR_CAUSES = ['概念不清', '计算失误', '审题偏差', '知识迁移不足']


# ---------- 学情上下文（个人情况 + 能力轨迹，注入所有生成提示词） ----------
def student_context(student_id: int) -> str:
    if not student_id:
        return '（未指定学生，按课程通用难度命题）'
    parts = [profile_mod.student_profile_text(student_id)]
    wk = dbm.weakness_ranking(student_id)
    causes = []
    for w in wk[:5]:
        if w.get('error_causes'):
            causes.append('%s（%s）' % (w['kp'], '、'.join(
                '%s×%d' % (k, v) for k, v in w['error_causes'].items())))
    if causes:
        parts.append('错因分布：' + '；'.join(causes))
    mistakes = dbm.recent_mistakes(student_id, 5)
    if mistakes:
        parts.append('最近错题轨迹：' + '；'.join(
            '%s[错因：%s]' % (m['question_text'][:45], m['error_cause'] or '未归类')
            for m in mistakes))
    return '\n'.join(parts)


def _load_bank() -> list:
    try:
        with open(config.questions_path(), encoding='utf-8') as f:
            return json.load(f).get('questions', [])
    except Exception:
        return []


def _bank_digest(kp: str = '') -> str:
    """题库摘要（严禁重复清单）。"""
    bank = _load_bank()
    hit = [q for q in bank if kp and (kp in q.get('kp', '') or q.get('kp', '') in kp)]
    pool = hit or bank
    if not pool:
        return '（题库为空）'
    return '\n'.join('- [%s] %s' % (q.get('kp', ''), str(q.get('q', ''))[:55]) for q in pool[-30:])


def _norm_questions(items: list, count: int) -> list:
    """规范化 LLM 输出的题目（选择 4 选项/答案下标；填空 1 标准答案）。"""
    out = []
    for q in items[:count * 2]:
        try:
            q = dict(q)
            qt = str(q.get('type', ''))
            if '选' in qt:
                q['type'] = '选择'
            elif '填' in qt:
                q['type'] = '填空'
            else:
                continue
            ans = q.get('answer', -1)
            if isinstance(ans, str):
                ans = ans.strip().rstrip('.').upper()
                if len(ans) == 1 and 'A' <= ans <= 'Z':
                    ans = ord(ans) - 65
                elif ans.isdigit():
                    ans = int(ans)
                else:
                    ans = -1
            q['answer'] = int(ans)
            q['kp'] = str(q.get('kp', '') or '综合')
            q['qtype'] = str(q.get('qtype', '') or q['type'])
            q['q'] = str(q.get('q', '')).strip()
            q['analysis'] = str(q.get('analysis', '') or '')
            q['source'] = 'agent 思考出题'
            if q['type'] == '选择':
                opts = [str(o) for o in q.get('options', []) if str(o).strip()]
                if len(opts) < 2 or not (0 <= q['answer'] < len(opts)) or not q['q']:
                    continue
                while len(opts) < 4:
                    opts.append('以上都不对')
                q['options'] = opts
            else:
                if not q.get('options') or not q['q']:
                    continue
                q['options'] = [str(q['options'][0])]
                q['answer'] = 0
            out.append(q)
        except (ValueError, TypeError, KeyError):
            continue
        if len(out) >= count:
            break
    return out


def _is_dup(text: str, pool: list, threshold: float = 0.78) -> bool:
    for old in pool:
        try:
            if difflib.SequenceMatcher(None, text, str(old)).ratio() > threshold:
                return True
        except Exception:
            continue
    return False


# ---------- 自测题生成（LLM + 学情 + 题库去重） ----------
QUIZ_SYSTEM = (
    '你是编译原理自测命题专家。结合【学情档案】为学生命制全新自测题：\n'
    '1. 优先覆盖薄弱知识点，难度贴合学生当前水平（掌握度高则加大综合/迁移题占比）；\n'
    '2. 严禁与【已有题库】重复——换情境、换参数、换设问角度，不照抄任何原题；\n'
    '3. 答案唯一正确，干扰项合理对应典型错误（可对准该生错因分布设计陷阱）；\n'
    '4. 只输出 JSON：{"questions":[{"type":"选择|填空","kp":"知识点","qtype":"题型",'
    '"q":"题干","options":["..."],"answer":0,"analysis":"完整解析：步骤+易错点，不超过 120 字"}]}\n'
    '格式：选择题恰好 4 个选项、answer 为正确项下标（0-3）；填空题 options 只含 1 个标准答案、answer 为 0。')


def llm_quiz(kp: str, count: int, student_id: int = 0) -> list:
    """LLM 生成全新自测题（分批生成 + 跨批去重，未入库）。失败抛 LLMError。"""
    digest = _bank_digest(kp)
    stu = student_context(student_id)
    seen = [str(q.get('q', '')) for q in _load_bank()]
    collected = []
    batches = 0
    last_err = None
    while len(collected) < count and batches < 3:
        batches += 1
        batch_n = min(count - len(collected), 5)
        extra = ''
        if collected:
            extra += '\n【本批之前已生成（必须再不同）】\n' + '\n'.join(
                '- ' + q['q'][:55] for q in collected)
        if batches > 1:
            extra += '\n【此前批次输出被判重或不合格式，请彻底换情境与角度】'
        user_msg = ('【出题范围】%s\n【本批题量】%d 道（选择/填空搭配）\n'
                    '【学情档案】\n%s\n【已有题库（严禁重复）】\n%s%s'
                    % (kp or '全书综合', batch_n, stu, digest, extra))
        try:
            raw = llm_adapter.chat_json(QUIZ_SYSTEM, user_msg, temperature=0.5,
                                        max_tokens=8000, timeout=150)
        except LLMError as e:
            last_err = e
            continue
        items = raw.get('questions') if isinstance(raw, dict) else raw
        for q in _norm_questions(items if isinstance(items, list) else [], batch_n):
            if _is_dup(q['q'], seen):
                continue
            seen.append(q['q'])
            collected.append(q)
    if not collected:
        raise LLMError('自测题生成失败：%s' % (last_err or '输出不合格式或与题库重复'))
    return collected[:count]


# ---------- 复习计划生成（LLM + 学情 + 能力轨迹） ----------
PLAN_SYSTEM = (
    '你是编译原理课程的复习规划教练。根据【学情档案】【考点权重】为学生制定逐天复习计划。\n'
    '要求：\n'
    '1. 天数必须与给定【日期列表】完全一致，一天不多一天不少，不得改动日期；\n'
    '2. 按"薄弱程度×考点权重"定优先级：前期（约前 60%% 天数）攻坚薄弱点，后期滚动回顾+限时自测，考前最后一天只做错题回顾与心态调整；\n'
    '3. 任务具体到动作：读什么类型的页（概念辨析/例题/公式）、做什么题（错题重做/变式/限时套卷）、练什么能力；'
    '每天恰好 2 个任务，action 与 goal 各不超过 25 字，不得雷同照抄，要随进度递进；\n'
    '4. 结合错因分布给针对性动作：概念不清→对比辨析精读；计算失误→限时手算核对；审题偏差→圈画关键词训练；知识迁移不足→跨章节对比题；\n'
    '5. 只输出 JSON：{"plan":[{"day":1,"tasks":[{"kp":"知识点","action":"具体动作",'
    '"goal":"可检验目标","accuracy_now":0.5}]}]}，day 从 1 连续编号。')


def llm_plan(exam_date: str, student_id: int = 0, req: str = '') -> list:
    """LLM 生成逐天复习计划，日期由本函数精确回填。分段生成防截断。失败抛 LLMError。"""
    today = datetime.date.today()
    try:
        exam = datetime.date.fromisoformat(exam_date)
    except ValueError:
        raise LLMError('考试日期格式应为 YYYY-MM-DD')
    days = max((exam - today).days, 1)
    dates = [(today + datetime.timedelta(days=i + 1)).isoformat() for i in range(days)]
    try:
        graph = json.load(io.open(config.graph_path(), encoding='utf-8'))
        weights = {n['name']: n.get('weight', 5) for n in graph['nodes']
                   if n['type'] == 'knowledge_point'}
    except Exception:
        weights = {}
    wt_line = '、'.join('%s(权重%s)' % (k, w) for k, w in
                       sorted(weights.items(), key=lambda x: -x[1])[:12]) or '（暂无图谱）'
    stu = student_context(student_id)
    plan = []
    chunk = 10
    for start in range(0, days, chunk):
        seg = dates[start:start + chunk]
        prev = ''
        if plan:
            prev = '\n【前序计划（保持递进连贯，不要重复前序任务）】\n' + '\n'.join(
                '- %s：%s' % (d['date'], '；'.join(t['kp'] + '-' + t['action'] for t in d['tasks']))
                for d in plan[-6:])
        user_msg = ('考试日期：%s（距今 %d 天，整份计划分 %d 段，这是第 %d 段）\n'
                    '【本段日期列表】%s\n【学情档案】\n%s\n【考点权重】%s%s\n'
                    '【额外要求】%s\n请为本段输出恰好 %d 天的计划。'
                    % (exam_date, days, (days + chunk - 1) // chunk, start // chunk + 1,
                       ','.join(seg), stu, wt_line, prev, req or '无', len(seg)))
        raw = llm_adapter.chat_json(PLAN_SYSTEM, user_msg, temperature=0.4,
                                    max_tokens=8000, timeout=240)
        items = raw.get('plan') if isinstance(raw, dict) else raw
        if not isinstance(items, list):
            raise LLMError('复习计划输出格式错误')
        if len(items) != len(seg):
            raise LLMError('复习计划天数不符（本段要求 %d 天，得到 %d 天）' % (len(seg), len(items)))
        for i, it in enumerate(items):
            tasks = []
            for t in (it.get('tasks') or []):
                if not str(t.get('kp', '')).strip() or not str(t.get('action', '')).strip():
                    continue
                try:
                    acc = float(t.get('accuracy_now', 0.5))
                except (ValueError, TypeError):
                    acc = 0.5
                tasks.append({'kp': str(t['kp']).strip(), 'action': str(t['action']).strip(),
                              'goal': str(t.get('goal', '')).strip(), 'accuracy_now': acc})
            if not tasks:
                raise LLMError('第 %d 天任务为空' % (start + i + 1))
            plan.append({'day': start + i + 1, 'date': seg[i], 'tasks': tasks})
    return plan


# ---------- 变式题生成（LLM 同源变式 + 查重） ----------
VARIANT_SYSTEM = (
    '你是编译原理命题专家。根据【原型题/章节内容】命制一道同源变式题。\n'
    '要求：\n'
    '1. 与原型同知识点、同难度层级，但必须换参数/换情境/换设问角度，形成新题；\n'
    '2. 严禁与【已出过的题】重复或仅做表面改写；\n'
    '3. 答案完整正确且可验证：给出充分的推导/求解过程（简洁，不超过 400 字），不编造教材页码与题号；\n'
    '4. 结合【学情档案】避开该生已熟练方向，主攻其薄弱环节对应的设问；\n'
    '5. 只输出 JSON：{"question":"题干","answer":"完整标准答案（含推导）",'
    '"steps":["步骤1","步骤2"],"hint":"思路提示，不剧透答案"}')


def llm_variant(kp: str, proto: str = '', req: str = '', student_id: int = 0) -> dict:
    """LLM 生成同源变式题（查重通过）。失败抛 LLMError。"""
    history = [str(v.get('variant', {}).get('question', '')) for v in
               dbm.list_variants(student_id, limit=20)]
    history += [str(q.get('q', '')) for q in _load_bank() if kp and kp in q.get('kp', '')]
    history = [h for h in history if h.strip()]
    stu = student_context(student_id)
    seen = list(history)
    for attempt in range(2):
        user_msg = ('【知识点】%s\n【原型题/章节内容】\n%s\n【补充要求】%s\n'
                    '【学情档案】\n%s\n【已出过的题（严禁重复）】\n%s%s'
                    % (kp or '综合', (proto or '（无原型，按知识点自主命题）')[:2500],
                       req or '无', stu,
                       '\n'.join('- ' + h[:55] for h in history) or '（无）',
                       '\n【上一版被判重，请彻底换情境与设问角度】' if attempt else ''))
        raw = llm_adapter.chat_json(VARIANT_SYSTEM, user_msg, temperature=0.5,
                                    max_tokens=5000, timeout=120)
        if isinstance(raw, list) and raw and isinstance(raw[0], dict):
            raw = raw[0]
        if not isinstance(raw, dict) or not str(raw.get('question', '')).strip():
            raise LLMError('变式题输出格式错误')
        qtext = str(raw['question']).strip()
        if _is_dup(qtext, seen, threshold=0.78):
            continue
        answer = raw.get('answer', '')
        if isinstance(answer, dict):
            ans_s = '；'.join('%s：%s' % kv for kv in answer.items())
        else:
            ans_s = str(answer).strip()
        if not ans_s:
            raise LLMError('变式题答案为空')
        return {'question': qtext, 'answer': answer,
                'steps': [str(s) for s in raw.get('steps', []) if str(s).strip()],
                'hint': str(raw.get('hint', '') or '先分析原型考查的核心概念')}
    raise LLMError('变式题生成失败：与已出题目重复，未能换出新角度')


# ---------- 错因归类（LLM 四分类） ----------
def classify_error(question: str, right_answer: str, student_answer: str) -> str:
    system = ('你是编译原理课程的错题分析助教。判断学生错因，只能四选一：%s。'
              '只输出 JSON {"cause": "...", "reason": "一句话"}。') % '/'.join(ERROR_CAUSES)
    user = '题目：%s\n正确答案：%s\n学生答案：%s' % (question, right_answer, student_answer)
    r = llm_adapter.chat_json(system, user)
    if isinstance(r, list) and r and isinstance(r[0], dict):
        r = r[0]
    cause = str(r.get('cause', '')) if isinstance(r, dict) else ''
    if cause not in ERROR_CAUSES:
        raise LLMError('错因归类结果不在四分类内：%s' % cause[:50])
    return cause
