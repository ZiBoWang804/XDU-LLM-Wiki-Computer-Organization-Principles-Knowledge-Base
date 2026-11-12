# -*- coding: utf-8 -*-
# Skill 框架：把智能体技能的【提示词 + 工具 + 规则】封装为可调用单元
# 流程：助教收到指令 → 执行 skill → 检查产出 → 入库知识库「智能体记录/」形成文档记录
import datetime
import io
import json
import os
import re

from . import config, db as dbm, services, teacher_tools
from .adapters import llm_adapter, wiki_adapter

def RECORD_DIR():
    return config.records_dir()


# ================= 记录入库 =================
def write_record(kind: str, title: str, body: str, kps: list = None) -> str:
    """检查通过后写入知识库，返回相对路径（供前端跳转阅读）。只读模式返回空。"""
    if config.is_readonly():
        return ''   # 只读模式：不落库
    os.makedirs(RECORD_DIR(), exist_ok=True)
    ts = datetime.datetime.now()
    fn = '%s-%s.md' % (kind, ts.strftime('%Y%m%d-%H%M%S'))
    fm = ('---\ntype: 智能体记录\nchapter: 智能体记录\nrecord_kind: %s\n'
          'created_at: %s\nknowledge_points: [%s]\n---\n\n'
          % (kind, ts.strftime('%Y-%m-%d %H:%M'), ', '.join(kps or [])))
    io.open(os.path.join(RECORD_DIR(), fn), 'w', encoding='utf-8').write(
        fm + '# %s\n\n%s\n' % (title, body))
    return '智能体记录/' + fn


# ================= Skill 基类 =================
class Skill:
    name = ''
    label = ''
    role = 'both'          # teacher | student | both
    desc = ''
    system_prompt = ''     # 提示词（LLM 增强时使用）
    rules = []             # 规则（检查项 + 展示给用户）
    tools = []             # 依赖工具

    def check(self, result: dict) -> tuple:
        """检查产出。返回 (通过?, 问题描述)。"""
        if not result:
            return False, '产出为空'
        return True, ''

    def run(self, params: dict, user: dict) -> dict:
        raise NotImplementedError

    def _finish(self, output: str, record_title: str, record_body: str,
                kps: list = None, extra: dict = None) -> dict:
        ok, problem = self.check({'output': output, 'record': record_body})
        if not ok:
            return {'ok': False, 'output': '❌ 检查未通过：%s（未入库）' % problem, 'record_file': ''}
        rf = write_record(self.name, record_title, record_body, kps)
        if rf:
            out = output + '\n\n✅ 已通过检查并入库：`%s`' % rf
        else:
            out = output + '\n\n✅ 已通过检查（只读模式，未落库）'
        r = {'ok': True, 'output': out, 'record_file': rf}
        if extra:
            r.update(extra)
        return r


# ================= 1. 出题（教师） =================
class QuestionSkill(Skill):
    name = 'question'
    label = '✏️ 出题'
    role = 'teacher'
    desc = 'agent 自主查知识库+结合学情，思考后出全新题（答案解析默认隐藏）'
    system_prompt = (
        '你是编译原理命题专家 agent，自主完成出题全流程。规则只有输出格式规范，命题思路自由发散：\n'
        '1. 通读给定的【知识库资料】与【学情数据】，自主判断该考哪个概念、什么难度；\n'
        '2. 推理常见考法、易错陷阱，换情境/参数设计全新题——不要照抄资料中的原题；\n'
        '3. 自检：答案唯一正确、干扰项合理、无歧义；\n'
        '4. 输出格式（只输出 JSON）：\n'
        '{"questions":[{"type":"选择","kp":"知识点","qtype":"题型","q":"题干",'
        '"options":["选项文本(不带A/B前缀)","...","...","..."],"answer":1,"source":"命题依据",'
        '"analysis":"完整解析：解题步骤+易错点"},\n'
        '{"type":"填空","kp":"知识点","qtype":"题型","q":"题干______。",'
        '"options":["标准答案"],"answer":0,"source":"命题依据","analysis":"解析"}]}\n'
        '说明：选择题 4 个选项、answer 为正确项下标(0-3)；填空题 options 只含 1 个标准答案、answer 为 0。')
    rules = ['自主查库定考法（不指定知识点也能出）', '结合学情薄弱点命题',
             '题目全新原创、答案唯一', '解析完整（步骤+易错点）', '检查通过才入题库']
    tools = ['kb.search', 'profile.weakness', 'llm.think_generate', 'questions.save', 'kb.record']

    def run(self, params, user):
        req = params.get('req', '')
        kp = params.get('kp', '').strip()
        count = int(params.get('count', 1))

        # ===== Agent 第一步：自主检索知识库（发散——用要求原文+关键词搜） =====
        kb_ctx = ''
        try:
            queries = [req] if req else []
            if kp:
                queries.append(kp)
            queries.append(re.sub(r'[出一两三四五六七八九十道个题请帮我关于的]', ' ', req or kp).strip() or kp)
            seen = set()
            for qstr in queries:
                if not qstr or len(qstr) < 2:
                    continue
                for h in wiki_adapter.search(qstr, limit=3):
                    if h['file'] in seen:
                        continue
                    seen.add(h['file'])
                    try:
                        page = wiki_adapter.get_page(h['file'])
                        kb_ctx += '\n【知识库·%s（%s）】\n%s' % (
                            h['file'], h.get('chapter', ''), page['body'][:1000])
                    except Exception:
                        continue
                if len(seen) >= 4:
                    break
        except Exception:
            pass

        # ===== Agent 第二步：拉取学情（该出什么难度/方向） =====
        stu_ctx = ''
        try:
            if params.get('student_id'):
                from . import profile as _profile
                stu_ctx = _profile.student_profile_text(int(params['student_id']))
            else:
                heat = dbm.class_heatmap('编译2023')
                weak = sorted(heat.get('kp_accuracy', []), key=lambda x: x['accuracy'])[:5]
                stu_ctx = '班级薄弱：%s' % '、'.join(
                    '%s(%d%%)' % (w['kp'], w['accuracy'] * 100) for w in weak) if weak else '（暂无学情数据）'
        except Exception:
            stu_ctx = '（暂无学情数据）'

        # ===== Agent 第三步：思考生成（题干+答案+解析；格式不合直接报错） =====
        try:
            user_msg = ('【出题要求】%s\n【知识库资料】%s\n【学情数据】%s\n'
                        '请自主决定出什么题，出 %d 道。'
                        % (req or ('围绕知识点：' + kp) or '自由命题',
                           (kb_ctx or '（未检索到资料，按学科常识命题）')[:3500],
                           stu_ctx, count))
            raw = llm_adapter.chat_json(self.system_prompt, user_msg,
                                        timeout=services.TIMEOUT)
            items = raw if isinstance(raw, list) else (
                raw.get('questions') or [raw] if isinstance(raw, dict) else [])
            if not items:
                raise RuntimeError('LLM 未返回题目列表')
            new_qs = [services._coerce_question(q, i + 1) for i, q in enumerate(items[:count])]
        except Exception as e:
            return {'ok': False, 'output': '❌ 出题失败：%s' % str(e)[:150], 'record_file': ''}
        source = 'agent 思考出题'
        saved = []
        for q in new_qs:
            q.setdefault('source', source)
            q.setdefault('analysis', '')
            qid = teacher_tools.add_question(dict(q))
            saved.append((qid, q))

        # ===== 输出：题面可见 + 答案解析折叠 =====
        front, hidden = [], []
        for qid, q in saved:
            opts = ''.join('<br>　%s. %s' % ('ABCD'[i], o) for i, o in enumerate(q['options'])) if q['type'] == '选择' else '　（填空）'
            front.append('**[%s]【%s】%s**\n%s%s' % (qid, q['type'], q['q'], opts,
                       '\n<sub>来源：%s</sub>' % q.get('source', '')))
            hidden.append('**[%s] 答案：%s**\n%s' % (
                qid, q['options'][q['answer']] if q['options'] else '',
                q.get('analysis') or '（解析待补充）'))
        think = ''
        if llm_adapter.last_thinking:
            think = '\n\n🧠 **模型思考**：' + llm_adapter.last_thinking[:350] + '…'
        output = ('📝 已出 %d 道全新题（%s）：%s\n\n%s\n\n'
                  '<details><summary>🔑 答案与解析（点击展开）</summary>\n\n%s\n\n</details>'
                  % (len(saved), source, think,
                     '\n\n'.join(front), '\n\n'.join(hidden)))
        record_body = ('方式：%s\n要求：%s\n\n## 题面\n%s\n\n## 答案与解析\n%s%s'
                       % (source, req or kp, '\n\n'.join(front), '\n\n'.join(hidden), think))
        return self._finish(output, '出题记录 · %s' % (kp or req[:12] or '综合'),
                            record_body, [kp] if kp else [], {'count': len(saved)})


# ================= 2. 勘误（教师） =================
class ErrataSkill(Skill):
    name = 'errata'
    label = '📝 勘误'
    role = 'teacher'
    desc = '提交勘误并可直接修正知识库，生成勘误记录'
    system_prompt = (
        '你是编译原理知识库审校。给定文档与勘误内容，输出 JSON：'
        '{"file":"文档名","before":"原文","after":"改为","note":"勘误依据"}。'
        'before 必须逐字来自原文，after 必须科学正确。')
    rules = ['before 必须在原文中存在', '改动最小化', '记录勘误依据', '生成勘误记录文档']
    tools = ['kb.read', 'kb.replace', 'errata.save', 'kb.record']

    def run(self, params, user):
        file = params.get('file', '')
        before = params.get('before', '')
        after = params.get('after', '')
        note = params.get('note', '')
        if not file or not before or not after:
            return {'ok': False, 'output': '❌ 需要 file / before / after 三个参数（未入库）', 'record_file': ''}
        try:
            page = wiki_adapter.get_page(file)
        except Exception:
            return {'ok': False, 'output': '❌ 文档不存在：%s' % file, 'record_file': ''}
        if before not in page['body']:
            return {'ok': False,
                    'output': '❌ 检查未通过：before 不在原文中，为防误改未执行（未入库）\n原文片段：…%s…'
                              % page['body'][:120], 'record_file': ''}
        eid = teacher_tools.add_errata(file, '勘误', before, after, note, user.get('display_name', ''))
        teacher_tools.apply_errata(eid)
        output = '📝 勘误已应用到 `%s`：\n- 原文：%s\n- 改为：%s\n- 依据：%s' % (file, before, after, note or '未填')
        return self._finish(output, '勘误记录 · %s' % file,
                            '文档：%s\n\n| 原文 | 改为 | 依据 |\n|---|---|---|\n| %s | %s | %s |\n'
                            % (file, before, after, note), [], {'errata_id': eid})


# ================= 3. 布置作业（教师） =================
class HomeworkSkill(Skill):
    name = 'homework'
    label = '📋 布置作业'
    role = 'teacher'
    desc = '布置作业到知识库系统，学生端可见，生成布置记录'
    system_prompt = (
        '你是编译原理任课教师。按要求拟作业说明，输出 JSON：'
        '{"title":"标题","detail":"作业说明与题目","kp":"知识点","due_date":"YYYY-MM-DD"}。作业难度适中、指向明确。')
    rules = ['标题与说明完整', '知识点来自课程', '截止日期明确', '发布后学生端可见', '生成布置记录文档']
    tools = ['llm.generate', 'homework.save', 'kb.record']

    def run(self, params, user):
        title = params.get('title', '').strip()
        detail = params.get('detail', '').strip()
        kp = params.get('kp', '').strip()
        due = params.get('due_date', '').strip()
        if not title:
            # LLM 代拟
            try:
                r = llm_adapter.chat_json(self.system_prompt,
                                          '围绕知识点「%s」布置一次作业，截止 %s。%s'
                                          % (kp or '综合', due or '下周',
                                             ('额外要求：' + params.get('req', '')) if params.get('req') else ''))
                title, detail = r.get('title', ''), r.get('detail', '')
                kp = kp or r.get('kp', '')
                due = due or r.get('due_date', '')
            except Exception as e:
                return {'ok': False, 'output': '❌ 作业代拟失败：%s（未入库）' % str(e)[:150],
                        'record_file': ''}
        if not title:
            return {'ok': False, 'output': '❌ LLM 未返回有效作业标题（未入库）', 'record_file': ''}
        hid = teacher_tools.add_homework(title, detail, kp, '', due, user.get('display_name', ''))
        output = '📋 作业已发布：**%s**\n- 知识点：%s\n- 截止：%s\n- 说明：%s' % (
            title, kp or '综合', due or '未定', detail[:120] or '（无）')
        return self._finish(output, '作业布置 · %s' % title,
                            '标题：%s\n知识点：%s\n截止：%s\n\n## 说明\n%s\n' % (title, kp, due, detail),
                            [kp] if kp else [], {'homework_id': hid})


# ================= 4. 自测（学生，UI 保留 + 对话组卷） =================
class QuizSkill(Skill):
    name = 'quiz'
    label = '✏️ 自测'
    role = 'student'
    desc = '结合学情与能力轨迹 LLM 思考命制全新小测卷（与题库去重，答案另附于记录）'
    system_prompt = services.QUIZ_SYSTEM
    rules = ['LLM 结合学情/能力轨迹命题', '全新题、与题库查重通过', '答案写入记录不发给学生', '生成自测记录文档']
    tools = ['db.weakness', 'profile.trajectory', 'llm.think_generate', 'questions.save', 'kb.record']

    def run(self, params, user):
        kp = params.get('kp', '').strip()
        count = int(params.get('count', 3))
        sid = int(params.get('student_id', 0) or 0)
        try:
            picked = services.llm_quiz(kp, count, sid)
        except Exception as e:
            return {'ok': False, 'output': '❌ 自测题生成失败：%s（未入库，不降级组卷）' % str(e)[:150],
                    'record_file': ''}
        saved = []
        for q in picked:
            qid = teacher_tools.add_question(dict(q))
            saved.append((qid, q))
        paper = '\n'.join('%d.【%s·%s】%s\n   %s' % (i + 1, q['kp'], q['qtype'], q['q'],
                          '　'.join('%s. %s' % ('ABCD'[j], o) for j, o in enumerate(q['options']))
                          if q['type'] == '选择' else '　（填空）')
                          for i, (qid, q) in enumerate(saved))
        ans = '\n'.join('%d.[%s] 答案：%s\n　解析：%s' % (i + 1, qid, q['options'][q['answer']],
                        q.get('analysis') or '（解析待补充）') for i, (qid, q) in enumerate(saved))
        think = ''
        from .adapters import llm_adapter as _llm
        if _llm.last_thinking:
            think = '\n\n🧠 **模型思考**：' + _llm.last_thinking[:350] + '…'
        output = ('📖 小测卷（%d 道全新题%s）：\n%s%s\n\n做完可在「自测刷题」UI 交卷自动判分，答案在记录中。'
                  % (len(saved), '，知识点：' + kp if kp else '，按学情薄弱点配比', paper, think))
        return self._finish(output, '自测组卷 · %s' % (kp or '按学情'),
                            '## 试卷\n%s\n\n## 标准答案与解析（不发给学生）\n%s\n%s'
                            % (paper, ans, think),
                            [kp] if kp else [], {'paper': paper, 'answers': ans})


# ================= 5. 薄弱训练（学生） =================
class DiagnosisSkill(Skill):
    name = 'diagnosis'
    label = '🎯 薄弱训练'
    role = 'student'
    desc = '诊断薄弱点并给出训练方案，生成诊断记录'
    system_prompt = (
        '你是编译原理学习教练。根据学生答题数据，输出 JSON：'
        '{"summary":"一句话诊断","training":["训练建议1","训练建议2"]}。语气鼓励、建议具体可执行。')
    rules = ['诊断必须基于真实答题数据', '训练建议对应薄弱知识点', '生成诊断记录文档']
    tools = ['db.weakness', 'llm.generate', 'kb.record']

    def run(self, params, user):
        sid = int(params.get('student_id', 0) or 0)
        weakness = dbm.weakness_ranking(sid) if sid else []
        if not weakness:
            return {'ok': False, 'output': '❌ 还没有答题记录——先在「自测刷题」做一轮再诊断（未入库）', 'record_file': ''}
        top = weakness[:3]
        lines = ['- %s：正确率 %.0f%%（%d 题）' % (w['kp'], w['accuracy'] * 100, w['total']) for w in top]
        summary = '薄弱点集中在 ' + '、'.join(w['kp'] for w in top)
        try:
            r = llm_adapter.chat_json(self.system_prompt,
                                      '学生数据：%s。%s' % ('；'.join(lines),
                                       params.get('req') or '请诊断并给 2-3 条训练建议。'))
            if isinstance(r, list):
                r = r[0] if r and isinstance(r[0], dict) else {'training': [str(x) for x in r]}
            summary = r.get('summary', summary)
            training = [str(t).strip() for t in r.get('training', []) if str(t).strip()]
        except Exception as e:
            return {'ok': False, 'output': '❌ 诊断生成失败：%s（未入库，不降级套话）' % str(e)[:150],
                    'record_file': ''}
        if not training:
            return {'ok': False, 'output': '❌ 诊断生成失败：训练方案为空（未入库）', 'record_file': ''}
        output = ('🎯 诊断：%s\n\n薄弱排序：\n%s\n\n训练方案：\n%s'
                  % (summary, '\n'.join(lines), '\n'.join('- ' + t for t in training)))
        return self._finish(output, '薄弱诊断记录',
                            '## 诊断\n%s\n\n## 薄弱排序\n%s\n\n## 训练方案\n%s\n'
                            % (summary, '\n'.join(lines), '\n'.join('- ' + t for t in training)),
                            [w['kp'] for w in top])


# ================= 6. 复习计划（学生） =================
class PlanSkill(Skill):
    name = 'plan'
    label = '📅 复习计划'
    role = 'student'
    desc = 'LLM 结合学情、错因分布与能力轨迹生成逐天复习计划（倒计时精确）'
    system_prompt = services.PLAN_SYSTEM
    rules = ['LLM 结合学情/错因/能力轨迹生成', '天数与考试倒计时精确一致', '任务逐天递进、针对错因给动作', '生成计划记录文档']
    tools = ['db.weakness', 'profile.trajectory', 'llm.think_generate', 'kb.record']

    def run(self, params, user):
        sid = int(params.get('student_id', 0) or 0)
        exam_date = params.get('exam_date', '').strip()
        if not exam_date:
            exam_date = (datetime.date.today() + datetime.timedelta(days=21)).isoformat()
        try:
            plan = services.llm_plan(exam_date, sid, params.get('req', ''))
        except Exception as e:
            return {'ok': False, 'output': '❌ 复习计划生成失败：%s（未入库，不降级规则排程）' % str(e)[:150],
                    'record_file': ''}
        if sid:
            dbm.save_plan(sid, exam_date, plan)
        day_lines = '\n'.join('- **Day %d（%s）**：%s' % (
            d['day'], d['date'], '；'.join('%s %s（目标：%s）' % (t['kp'], t['action'], t['goal']) for t in d['tasks']))
            for d in plan[:7])
        think = ''
        from .adapters import llm_adapter as _llm
        if _llm.last_thinking:
            think = '\n\n🧠 **模型思考**：' + _llm.last_thinking[:350] + '…'
        output = '📅 距考试 %d 天，复习计划已生成（结合学情与能力轨迹，倒计时精确）：\n%s%s%s' % (
            len(plan), day_lines, '\n- ……（完整计划见记录）' if len(plan) > 7 else '', think)
        body = '考试日期：%s\n生成时间：%s\n\n%s' % (
            exam_date, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            '\n'.join('- Day %d（%s）：%s' % (d['day'], d['date'],
                                             '；'.join('%s %s｜%s' % (t['kp'], t['action'], t['goal']) for t in d['tasks']))
                      for d in plan))
        return self._finish(output, '复习计划 · 考试 %s' % exam_date, body + think,
                            [], {'days': len(plan)})


# ================= 7. 变式训练（学生） =================
class VariantSkill(Skill):
    name = 'variant'
    label = '🔁 变式训练'
    role = 'student'
    desc = 'LLM 对原型题/章节内容生成同源变式题（查重通过后入库）'
    system_prompt = services.VARIANT_SYSTEM
    rules = ['与原型/章节同源同难度、换情境设问', '与已出题目查重不重复', '答案完整正确可验证', '检查后入库记录']
    tools = ['llm.think_generate', 'variant.dedup', 'profile.trajectory', 'kb.record']

    def run(self, params, user):
        kp = params.get('kp', '').strip() or 'LL(1)文法'
        req = params.get('req', '')
        proto = params.get('proto', '') or req
        sid = int(params.get('student_id', 0) or 0)
        try:
            v = services.llm_variant(kp, proto, req, sid)
        except Exception as e:
            return {'ok': False, 'output': '❌ 变式题生成失败：%s（未入库，不降级模板）' % str(e)[:150],
                    'record_file': ''}
        ans = v['answer']
        ans_s = '\n'.join('- %s：%s' % (k, x) for k, x in ans.items()) if isinstance(ans, dict) else str(ans)
        if not ans_s.strip():
            return {'ok': False, 'output': '❌ 检查未通过：答案为空（未入库）', 'record_file': ''}
        if user.get('role') == 'student':
            dbm.save_variant(sid, kp, v)
        think = ''
        from .adapters import llm_adapter as _llm
        if _llm.last_thinking:
            think = '\n\n🧠 **模型思考**：' + _llm.last_thinking[:350] + '…'
        output = ('🔁 变式题【%s】（LLM 同源生成）：\n%s%s\n\n💡 提示：%s\n\n（完整解答见知识库记录）'
                  % (kp, v['question'], think, v['hint']))
        body = ('## 变式题（LLM 同源生成）\n%s\n\n## 提示\n%s\n\n## 标准解答\n%s\n\n## 解题步骤\n%s\n'
                % (v['question'], v['hint'], ans_s, '\n'.join('- ' + s for s in v['steps'])))
        return self._finish(output, '变式训练 · %s' % kp, body + think, [kp])


# ================= 知识库构建工作流（教师，可复用到任意课程） =================
class KbImportSkill(Skill):
    name = 'import'
    label = '📥 导入资料'
    role = 'teacher'
    desc = '导入课程资料（课件/大纲/真题文本），自动清洗切片入知识库资料层'
    system_prompt = ''
    rules = ['文本自动清洗（去噪/去空行）', '按标题层级切片', '落入资料层不覆盖已有页面', '生成导入记录']
    tools = ['kb.write_raw', 'kb.record']

    def run(self, params, user):
        import re as _re
        content = params.get('content', '') or params.get('req', '')
        name = params.get('name', '').strip() or '导入资料-' + datetime.datetime.now().strftime('%m%d%H%M')
        if not content.strip():
            return {'ok': False, 'output': '❌ 缺少资料内容（把课件/大纲/真题文本贴给我即可）', 'record_file': ''}
        # 清洗：去多余空白/页眉页脚噪声
        cleaned = _re.sub(r'\n{3,}', '\n\n', '\n'.join(l.rstrip() for l in content.splitlines() if l.strip()))
        # 切片：按一级/二级标题
        slices = _re.split(r'(?m)^(#{1,2}\s)', cleaned)
        n_slices = max(len(_re.findall(r'(?m)^#{1,2}\s', cleaned)), 1)
        raw_dir = os.path.join(config.kb_dir(), '原始资料')
        os.makedirs(raw_dir, exist_ok=True)
        fn = name.replace('/', '_') + '.md'
        io.open(os.path.join(raw_dir, fn), 'w', encoding='utf-8').write(cleaned)
        output = ('📥 已导入「%s」→ 原始资料/%s\n- 字数：%d\n- 切片：%d 段（按标题层级）\n'
                  '下一步：/extract 从中提取知识点与考点' % (name, fn, len(cleaned), n_slices))
        return self._finish(output, '资料导入 · %s' % name,
                            '来源：%s\n字数：%d\n切片：%d 段\n' % (fn, len(cleaned), n_slices))


class KbExtractSkill(Skill):
    name = 'extract'
    label = '🧬 提取知识点'
    role = 'teacher'
    desc = 'LLM 从资料提取知识点/考点/权重，生成知识库页面（任意课程通用）'
    system_prompt = (
        '你是课程知识库构建专家。从给定课程资料提取知识结构，只输出 JSON：'
        '{"pages":[{"filename":"页名（中文短横线风格）","chapter":"第N章 名称",'
        '"knowledge_points":["知识点1",...],'
        '"exam_points":[{"kp":"所属知识点","name":"考点描述","level":"必考|常考|了解",'
        '"weight":1-10,"qtype":"对应题型"}],'
        '"content":"markdown 正文（保留资料原有表述，禁止编造）"}]}。'
        'weight 按考试出现频次与分值估计；页数按资料章节自适应。')
    rules = ['知识点/考点全部来自资料原文', '分级三档（必考/常考/了解）', '权重自洽（同章内相对合理）',
             'content 不得编造', '检查后写入知识库']
    tools = ['llm.generate', 'kb.write_page', 'graph.rebuild', 'kb.record']

    def run(self, params, user):
        source = params.get('source', '').strip()   # 原始资料文件名；空=最近导入的
        req = params.get('req', '')
        raw_dir = os.path.join(config.kb_dir(), '原始资料')
        # 取资料：指定文件 > 直接贴在 req 里的内容 > 最近导入
        text = ''
        src_name = source
        if source:
            p = os.path.join(raw_dir, source if source.endswith('.md') else source + '.md')
            if os.path.exists(p):
                text = io.open(p, encoding='utf-8').read()
        if not text and req and len(req) > 100:
            text, src_name = req, '（直接输入的资料）'
        if not text:
            cands = sorted([f for f in os.listdir(raw_dir) if f.endswith('.md')],
                           key=lambda f: os.path.getmtime(os.path.join(raw_dir, f)),
                           reverse=True) if os.path.isdir(raw_dir) else []
            if cands:
                src_name = cands[0]
                text = io.open(os.path.join(raw_dir, cands[0]), encoding='utf-8').read()
        if not text:
            return {'ok': False, 'output': '❌ 没有可提取的资料。先 /import 导入，或把资料内容直接发我。', 'record_file': ''}
        pages_out = []
        try:
            r = llm_adapter.chat_json(self.system_prompt,
                                      '课程资料（%s，%d 字）：\n%s%s'
                                      % (src_name, len(text), text[:6000],
                                         ('\n\n额外要求：' + req) if req else ''))
            pages_out = r.get('pages', [])
        except Exception as e:
            return {'ok': False, 'output': '❌ LLM 提取失败：%s（未入库）' % e, 'record_file': ''}
        written = []
        for pg in pages_out:
            fn = (pg.get('filename') or '新知识点页').strip() + '.md'
            fn = fn.replace('/', '_')
            fm = ('---\ntype: 知识点页\nchapter: %s\nknowledge_points: [%s]\nexam_points:\n%s\n---\n\n'
                  % (pg.get('chapter', ''), ', '.join(pg.get('knowledge_points', [])),
                     '\n'.join('- kp: %s\n  name: %s\n  level: %s\n  weight: %s\n  qtype: %s'
                               % (e.get('kp', ''), e.get('name', ''), e.get('level', '常考'),
                                  e.get('weight', 5), e.get('qtype', ''))
                               for e in pg.get('exam_points', []))))
            io.open(os.path.join(config.kb_dir(), fn), 'w', encoding='utf-8').write(
                fm + '# %s\n\n%s\n' % (pg.get('filename', ''), pg.get('content', '')))
            written.append(fn)
        if not written:
            return {'ok': False, 'output': '❌ 未提取到任何页面（未入库）', 'record_file': ''}
        # 重建图谱（失败如实报告，不谎报）
        rebuilt = False
        try:
            import subprocess, sys as _sys
            r2 = subprocess.run([_sys.executable,
                                 os.path.join(os.path.dirname(config.BASE_DIR), 'tmp', 'build_graph.py')],
                                capture_output=True, timeout=30)
            rebuilt = r2.returncode == 0
        except Exception:
            rebuilt = False
        output = ('🧬 已从「%s」提取 %d 个知识点页并入库（%s）：\n%s\n'
                  '下一步：/check 体检知识库' % (src_name, len(written),
                                              '图谱已重建' if rebuilt else '⚠️ 图谱重建失败，请手动 /graph',
                                              '\n'.join('- ' + f for f in written)))
        body = '来源：%s\n\n## 生成页面\n%s\n\n## 要求\n%s\n' % (
            src_name, '\n'.join('- %s' % f for f in written), req or '（无）')
        return self._finish(output, '知识点提取 · %s' % src_name, body)


class KbGraphSkill(Skill):
    name = 'graph'
    label = '🗺 生成图谱'
    role = 'teacher'
    desc = '从知识库 frontmatter 重建"章节→知识点→考点"三级图谱'
    system_prompt = ''
    rules = ['权重归一化到 100', '三级结构完整', '生成图谱记录']
    tools = ['graph.rebuild', 'kb.record']

    def run(self, params, user):
        import subprocess, sys as _sys
        r = subprocess.run([_sys.executable,
                            os.path.join(os.path.dirname(config.BASE_DIR), 'tmp', 'build_graph.py')],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return {'ok': False, 'output': '❌ 图谱重建失败：%s' % (r.stderr or '')[-200:], 'record_file': ''}
        graph = json.load(io.open(config.graph_path(), encoding='utf-8'))
        stats = graph.get('stats', {})
        output = ('🗺 考点图谱已重建：%d 章节 / %d 知识点 / %d 考点，总权重 %s'
                  % (stats.get('chapters', 0),
                     len([n for n in graph['nodes'] if n['type'] == 'knowledge_point']),
                     len([n for n in graph['nodes'] if n['type'] == 'exam_point']),
                     stats.get('total_weight', 0)))
        return self._finish(output, '图谱重建', output)


class KbCheckSkill(Skill):
    name = 'check'
    label = '✅ 知识库体检'
    role = 'teacher'
    desc = '知识库体检：元数据覆盖率/权重分布/结构完整性报告'
    system_prompt = ''
    rules = ['覆盖率逐项核对', '问题明确指出', '生成体检报告']
    tools = ['kb.status', 'kb.record']

    def run(self, params, user):
        s = teacher_tools.kb_status()
        cov = s['sources']['coverage'] * 100
        issues = []
        if cov < 100:
            issues.append('%d 篇缺 frontmatter' % (s['sources']['total'] - s['sources']['with_frontmatter']))
        if s['graph']['exam_points'] == 0:
            issues.append('图谱无考点')
        lv = s['graph']['levels']
        if not lv.get('必考'):
            issues.append('无"必考"级考点')
        output = ('✅ 知识库体检：\n'
                  '- 索引 %d 篇，元数据覆盖 %.0f%%\n'
                  '- 考点 %d 个（必考 %d / 常考 %d / 了解 %d），总权重 %s\n'
                  '- 题库 %d 题 · 浏览 %d 次\n'
                  '- 问题：%s' % (s['sources']['total'], cov, s['graph']['exam_points'],
                                lv.get('必考', 0), lv.get('常考', 0), lv.get('了解', 0),
                                s['graph']['total_weight'], s['banks']['questions'],
                                s['banks']['page_views'], '；'.join(issues) or '无'))
        return self._finish(output, '知识库体检报告', output)


# ================= 注册表 + 调度 =================
SKILLS = {s.name: s for s in [QuestionSkill(), ErrataSkill(), HomeworkSkill(),
                              QuizSkill(), DiagnosisSkill(), PlanSkill(), VariantSkill(),
                              KbImportSkill(), KbExtractSkill(), KbGraphSkill(), KbCheckSkill()]}


def _parse_req(params: dict) -> dict:
    """从自由要求文本里抽参数（数量/日期/知识点），合并进 params。"""
    import re
    req = params.get('req', '')
    if not req:
        return params
    m = re.search(r'(\d+)\s*[道题个]', req) or re.search(r'count[=:\s]*(\d+)', req)
    if m and 'count' not in params:
        params['count'] = int(m.group(1))
    elif 'count' not in params:
        # 中文数字：出一道/两道/三道…
        cn = {'一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
        m2 = re.search(r'([一两二三四五六七八九十])\s*[道题个]', req)
        if m2:
            params['count'] = cn.get(m2.group(1), 3)
    m = re.search(r'(\d{4}-\d{2}-\d{2})', req)
    if m and 'exam_date' not in params:
        params['exam_date'] = m.group(1)
    if not params.get('kp'):
        # 先与图谱知识点比对（取 req 里出现的最长者），再用 wiki 搜索定位，最后正则截取
        try:
            import json as _j
            graph = _j.load(io.open(config.graph_path(), encoding='utf-8'))
            kps = [n['name'] for n in graph['nodes'] if n['type'] == 'knowledge_point']
            hit = max([k for k in kps if k in req], key=len, default='')
            if hit:
                params['kp'] = hit
        except Exception:
            pass
        if not params.get('kp'):
            # 清洗命令虚词后用 wiki 搜索定位知识点（只认正规页，排除智能体记录防污染）
            try:
                from .adapters import wiki_adapter as _w
                cleaned = req
                for stop in ['帮我', '请', '给我', '出一道', '出几道', '出', '写', '生成', '来一道',
                             '一道', '几道', '一个', '关于', '针对', '围绕', '变式题', '变式', '题目',
                             '的', '题', '一下', '知识点', '复习计划', '计划', '作业']:
                    cleaned = cleaned.replace(stop, ' ')
                cleaned = ' '.join(cleaned.split())
                for q in [cleaned, req]:
                    if not q:
                        continue
                    hits = _w.search(q, limit=5)
                    hit = next((h for h in hits
                                if not h['file'].startswith('智能体记录/')
                                and h.get('type') in ('知识点页', '专题页', '题解页', '题库页', '试卷页')), None)
                    if hit:
                        p = _w.get_page(hit['file'])
                        kps = p['frontmatter'].get('knowledge_points', [])
                        if kps:
                            params['kp'] = kps[0]
                            break
            except Exception:
                pass
        if not params.get('kp'):
            m = re.search(r'(?:关于|针对|围绕|知识点)[:：]?\s*([^\s，。,、]{2,14})', req)
            if m:
                params['kp'] = m.group(1)
    return params


def list_skills(role: str) -> list:
    return [{'name': s.name, 'label': s.label, 'desc': s.desc,
             'rules': s.rules, 'tools': s.tools,
             'usage': {'question': '出 3 道 LL(1) 的题', 'errata': '把 <原文> 改为 <新文>',
                       'homework': '围绕 LL(1) 布置作业，截止 2026-12-01',
                       'quiz': '来 3 道左递归的题', 'diagnosis': '诊断我的薄弱点',
                       'plan': '生成复习计划，考试 2026-12-10',
                       'variant': '（粘贴原型题或章节内容）为这道题出一道同源变式',
                       'import': '（粘贴课件/大纲/真题文本）导入这份资料',
                       'extract': '从最近导入的资料提取知识点与考点',
                       'graph': '重建考点图谱', 'check': '知识库体检'}.get(s.name, '')}
            for s in SKILLS.values() if s.role in (role, 'both')]


def run_skill(name: str, params: dict, user: dict) -> dict:
    skill = SKILLS.get(name)
    if not skill:
        raise KeyError('未知技能: ' + name)
    if skill.role != 'both' and skill.role != user.get('role'):
        raise PermissionError('该技能仅限 %s 调用' % skill.role)
    params = _parse_req(dict(params or {}))
    result = skill.run(params, user)
    result['skill'] = name
    result['label'] = skill.label
    result['rules'] = skill.rules
    result['req'] = params.get('req', '')
    return result
