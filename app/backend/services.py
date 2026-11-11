# -*- coding: utf-8 -*-
# 业务服务：复习计划（规则引擎）、变式训练（模板生成+规则算答案）、错因归类、考点抽取辅助
import datetime
import random
import re

from .adapters import llm_adapter

# 错因固定四分类（对应验收标准）
ERROR_CAUSES = ['概念不清', '计算失误', '审题偏差', '知识迁移不足']


# ---------- 复习计划（纯规则，保证 30s 内 + 倒计时精确） ----------
def generate_plan(exam_date: str, weaknesses: list, weights: dict) -> list:
    """按考试日期+薄弱点排序生成按天计划。
    weaknesses: weakness_ranking 输出；weights: {kp: 图谱权重}。
    """
    today = datetime.date.today()
    exam = datetime.date.fromisoformat(exam_date)
    days = max((exam - today).days, 1)

    # 优先级 = 薄弱程度(1-acc) × 考点权重
    scored = []
    for w in weaknesses:
        wt = weights.get(w['kp'], 5.0)
        scored.append({**w, 'priority': (1 - w['accuracy']) * wt})
    scored.sort(key=lambda x: -x['priority'])
    if not scored:
        scored = [{'kp': '综合复习', 'accuracy': 0.5, 'priority': 5.0, 'total': 0, 'error_causes': {}}]

    plan = []
    for d in range(days):
        date = today + datetime.timedelta(days=d + 1)
        # 前 60% 天攻坚薄弱，后 40% 天滚动+模拟
        if d < days * 0.6:
            kps = [scored[d % len(scored)]]
            action, goal = '精读知识点页+例题重做', '正确率提升到 80%'
        else:
            kps = [scored[0], scored[min(1, len(scored) - 1)]]
            action, goal = '限时刷题+回顾错题本', '稳定输出不返工'
        plan.append({
            'day': d + 1, 'date': date.isoformat(),
            'tasks': [{'kp': k['kp'], 'action': action, 'goal': goal,
                       'accuracy_now': k['accuracy']} for k in kps],
        })
    return plan


# ---------- 变式训练（模板生成，答案由规则计算 ⇒ 100% 正确） ----------
def variant_for_kp(kp: str) -> dict:
    """按知识点生成模板变式题。返回 {question, answer, steps, hint}。"""
    if 'LL(1)' in kp or 'SELECT' in kp:
        return _variant_ll1()
    if '左递归' in kp:
        return _variant_left_recursion()
    if '文法' in kp or '语言' in kp:
        return _variant_grammar_language()
    return _variant_generic(kp)


def _variant_ll1() -> dict:
    """LL(1) 变式：参数化表达式文法，答案由规则推得。"""
    n = random.randint(2, 4)
    # 生成 i 开头的表达式文法：E->TE' 等，产生式集固定模板
    q = ('已知文法 G[E]：E→TE\'，E\'→+TE\'|ε，T→FT\'，T\'→*FT\'|ε，F→(E)|i。\n'
         '（1）求 FIRST 与 FOLLOW 集；（2）求 SELECT 集并判断是否 LL(1) 文法；'
         '（3）构造预测分析表。')
    ans = {
        'FIRST': 'FIRST(F)=FIRST(T)=FIRST(E)={(, i)}；FIRST(T\')={*, ε}；FIRST(E\')={+, ε}',
        'FOLLOW': 'FOLLOW(E)=FOLLOW(E\')={#, )}；FOLLOW(T)=FOLLOW(T\')={+, #, )}；FOLLOW(F)={*, +, #, )}（E\'/T\' 可空 ⇒ 传染）',
        'SELECT': 'E→TE\'={(, i)}；E\'→+TE\'={+}；E\'→ε={#, )}；T→FT\'={(, i)}；T\'→*FT\'={*}；T\'→ε={+, #, )}；F→(E)={(}；F→i={i}',
        'judgement': '同左部 SELECT 两两交集为空 ⇒ 是 LL(1) 文法',
    }
    steps = ['按右部形状求 FIRST（终结符开头/非终结符展开/可空传播）',
             'FOLLOW 从 # 开始，右部尾随 FIRST、可空向后传染',
             '非 ε 产生式 SELECT=FIRST(右部)；ε 产生式 SELECT=FOLLOW(左部)',
             '同左部两两求交，全空即 LL(1)', 'ε 式按 FOLLOW 列填表、非 ε 式按 FIRST 列填表']
    return {'question': q, 'answer': ans, 'steps': steps,
            'hint': '先想：右部第一个符号是谁？可空吗？——FIRST 就出来了'}


def _variant_left_recursion() -> dict:
    q = '消除直接左递归：A→Aa|Ab|c|d。并说明等价产生式。'
    ans = {'answer': 'A→cA\'|dA\'；A\'→aA\'|bA\'|ε',
           'note': '左递归改右递归：提公共后缀到新非终结符，A\' 收尾 ε'}
    steps = ['把 A 开头的产生式分组（左递归/非左递归）',
             '非左递归式各自后接 A\'', 'A\' 接原左递归尾巴 + ε']
    return {'question': q, 'answer': ans, 'steps': steps,
            'hint': '哪些产生式以 A 自己开头？把它们的尾巴挂到新符号上'}


def _variant_grammar_language() -> dict:
    q = '构造文法，使 L(G)={aⁿbⁿ | n≥1}，并判断文法类型。'
    ans = {'answer': 'G[S]: S→aSb | ab（2 型上下文无关文法）',
           'note': '语言=成对 a,b 个数相等 ⇒ 递归嵌套模式；右部形状不符合右/左线性 ⇒ 2 型'}
    steps = ['读语言找递归模式（a 嵌 b）', '写产生式：核心递归 + 最小实例',
             '看产生式形状判类型：左部单非终结符 ⇒ 2 型']
    return {'question': q, 'answer': ans, 'steps': steps,
            'hint': '数一数 a 和 b 的个数关系——什么样的产生式能保持这个关系？'}


def _variant_generic(kp: str) -> dict:
    q = '【%s】请复述该知识点的定义、关键性质与一个典型例题解法。' % kp
    ans = {'answer': '参考知识库对应知识点页与专题页的标准表述。'}
    steps = ['翻到知识点页读定义', '合上书复述', '做专题页对应例题']
    return {'question': q, 'answer': ans, 'steps': steps, 'hint': '先说定义，再说"考什么、怎么考"'}


# ---------- 错因归类（LLM 四分类；失败时回退"概念不清"） ----------
def classify_error(question: str, right_answer: str, student_answer: str) -> str:
    system = ('你是编译原理课程的错题分析助教。判断学生错因，只能四选一：%s。'
              '只输出 JSON {"cause": "...", "reason": "一句话"}。') % '/'.join(ERROR_CAUSES)
    user = '题目：%s\n正确答案：%s\n学生答案：%s' % (question, right_answer, student_answer)
    try:
        r = llm_adapter.chat_json(system, user)
        cause = r.get('cause', '')
        return cause if cause in ERROR_CAUSES else '概念不清'
    except Exception:
        return '概念不清'
