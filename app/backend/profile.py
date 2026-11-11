# -*- coding: utf-8 -*-
# 学生/教师档案：能力雷达 + 学习路径 + 学习画像（agent 可见——问答/技能自动携带）
import io
import json
import time

from . import config, db as dbm


def student_profile(student_id: int, name: str = '') -> dict:
    """学生档案：各知识点掌握度（能力雷达）+ 薄弱排序 + 学习路径 + 统计。"""
    weakness = dbm.weakness_ranking(student_id)
    # 能力雷达：图谱全部知识点 × 正确率
    try:
        graph = json.load(io.open(config.graph_path(), encoding='utf-8'))
        all_kps = [n['name'] for n in graph['nodes'] if n['type'] == 'knowledge_point']
        weights = {n['name']: n.get('weight', 5) for n in graph['nodes'] if n['type'] == 'knowledge_point'}
    except Exception:
        all_kps, weights = [], {}
    acc_map = {w['kp']: w['accuracy'] for w in weakness}
    radar = [{'kp': kp, 'mastery': round(acc_map.get(kp, 0) * 100),
              'weight': weights.get(kp, 5), 'trained': kp in acc_map}
             for kp in all_kps]
    # 学习路径：按 (1-掌握度)×权重 降序，取前 8 生成路径节点
    scored = sorted(
        ({'kp': kp, 'mastery': acc_map.get(kp, 0), 'weight': weights.get(kp, 5)} for kp in all_kps),
        key=lambda x: (1 - x['mastery']) * x['weight'], reverse=True)
    path = []
    for i, s in enumerate(scored[:8]):
        stage = '补弱' if s['mastery'] < 0.6 else ('巩固' if s['mastery'] < 0.85 else '保持')
        path.append({'step': i + 1, 'kp': s['kp'], 'stage': stage,
                     'mastery': round(s['mastery'] * 100), 'weight': s['weight']})
    trained = [w for w in weakness]
    overall = round(sum(w['accuracy'] * w['total'] for w in trained) / max(sum(w['total'] for w in trained), 1) * 100) if trained else 0
    return {
        'student_id': student_id, 'name': name,
        'overall_mastery': overall,
        'radar': radar,
        'weak_points': [{'kp': w['kp'], 'accuracy': round(w['accuracy'] * 100),
                         'error_causes': w['error_causes']} for w in weakness[:5]],
        'learning_path': path,
        'stats': {'trained_kps': len(trained), 'total_kps': len(all_kps)},
    }


def student_profile_text(student_id: int, name: str = '') -> str:
    """档案的紧凑文本版（注入 agent 系统提示词）。"""
    p = student_profile(student_id, name)
    if not p['stats']['trained_kps']:
        return '（新学生，暂无学习数据）'
    weak = '、'.join('%s(%d%%)' % (w['kp'], w['accuracy']) for w in p['weak_points'][:3])
    path = ' → '.join('%s[%s]' % (s['kp'], s['stage']) for s in p['learning_path'][:5])
    return ('学生%s：综合掌握 %d%%，已练 %d/%d 个知识点。'
            '薄弱：%s。建议学习路径：%s。'
            % (p['name'] or ('#' + str(student_id)), p['overall_mastery'],
               p['stats']['trained_kps'], p['stats']['total_kps'], weak or '无明显薄弱', path))


def teacher_profile(teacher_name: str = '') -> dict:
    """教师档案：所教班级学情总览 + 讲评建议（agent 可见）。"""
    heat = dbm.class_heatmap('编译2023')
    kps = sorted(heat['kp_accuracy'], key=lambda x: x['accuracy'])
    total_students = len(dbm.list_students('编译2023'))
    suggest = []
    for k in kps[:3]:
        if k['accuracy'] < 0.7:
            suggest.append('建议课堂讲评「%s」（全班正确率 %d%%）' % (k['kp'], k['accuracy'] * 100))
    return {
        'teacher': teacher_name, 'class_name': '编译2023',
        'total_students': total_students,
        'class_overall': round(sum(k['accuracy'] * k['total'] for k in kps) /
                               max(sum(k['total'] for k in kps), 1) * 100) if kps else 0,
        'weak_points': [{'kp': k['kp'], 'accuracy': round(k['accuracy'] * 100)} for k in kps[:5]],
        'suggestions': suggest,
    }


def teacher_profile_text(teacher_name: str = '') -> str:
    p = teacher_profile(teacher_name)
    if not p['total_students']:
        return '（班级暂无学生数据）'
    weak = '、'.join('%s(%d%%)' % (w['kp'], w['accuracy']) for w in p['weak_points'][:3])
    return ('教师%s：班级 %d 人，整体掌握 %d%%。'
            '班级薄弱：%s。讲评建议：%s。'
            % (teacher_name, p['total_students'], p['class_overall'], weak or '无', '；'.join(p['suggestions']) or '保持'))
