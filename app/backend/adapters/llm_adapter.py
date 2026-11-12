# -*- coding: utf-8 -*-
# llm_adapter：统一生成接口。首选 TeleAgent 模型 API（OpenAI 兼容），可换任意兼容端点。
import json
import httpx

from .. import config


class LLMError(RuntimeError):
    pass


# 最近一次推理过程（DeepSeek 等推理模型的 reasoning_content），供 UI 展示"模型思考"
last_thinking = ''
# 最近一次完成原因（'stop' 正常 / 'length' 被 max_tokens 截断）
last_finish = ''


def chat(system: str, user: str, temperature: float = 0.3, max_tokens: int = None,
         timeout: float = 600.0, response_format: dict = None) -> str:
    """单轮对话，返回文本。所有结构化生成任务都走这里。
    max_tokens 不传（None）= 按 DeepSeek 文档用默认额度（思考模式 64K）。"""
    global last_thinking, last_finish
    last_thinking = ''
    last_finish = ''
    if not config.LLM_API_KEY:
        raise LLMError('LLM_API_KEY 未配置（见 .env）')
    payload = {'model': config.LLM_MODEL,
               'messages': [{'role': 'system', 'content': system},
                            {'role': 'user', 'content': user}],
               'temperature': temperature}
    if max_tokens is not None:
        payload['max_tokens'] = max_tokens
    if response_format is not None:
        payload['response_format'] = response_format
    # trust_env=False：模型端点为国内直连，不走系统代理（代理会掐断其 TLS）
    try:
        resp = httpx.post(
            config.LLM_BASE_URL.rstrip('/') + '/chat/completions',
            headers={'Authorization': 'Bearer ' + config.LLM_API_KEY,
                     'Content-Type': 'application/json'},
            json=payload, timeout=timeout, trust_env=False)
    except httpx.TimeoutException:
        raise LLMError('模型调用超时（%gs）' % timeout)
    except httpx.HTTPError as e:
        raise LLMError('模型连接失败：%s' % str(e)[:120])
    if resp.status_code != 200:
        raise LLMError('LLM HTTP %d: %s' % (resp.status_code, resp.text[:300]))
    data = resp.json()
    choice = data['choices'][0]
    msg = choice['message']
    last_thinking = (msg.get('reasoning_content') or '').strip()
    last_finish = choice.get('finish_reason') or ''
    return msg['content']


def _sanitize_json_text(t: str) -> str:
    """修 JSON 字符串内部的裸换行/制表符（模型常不转义，导致 json.loads 失败）。"""
    out, in_str, esc = [], False, False
    for ch in t:
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
            elif ch in '\n\r\t':
                ch = '\\n' if ch == '\n' else ('\\t' if ch == '\t' else '')
        elif ch == '"':
            in_str = True
        out.append(ch)
    return ''.join(out)


def chat_json(system: str, user: str, temperature: float = 0.2,
              timeout: float = 600.0, max_tokens: int = None):
    """要求模型输出 JSON 并解析。失败抛 LLMError。兼容 JSON 对象与数组。
    max_tokens 不传（None）= 按 DeepSeek 文档用默认额度。
    使用 response_format=json_object（DeepSeek 文档保证输出为合法 JSON）。"""
    text = chat(system, user + '\n\n只输出 JSON，不要任何多余文字。', temperature,
                max_tokens=max_tokens, timeout=timeout,
                response_format={'type': 'json_object'})
    if not text.strip():
        raise LLMError('模型返回为空（finish_reason=%s）' % (last_finish or '?'))
    # 解析优先级：整体文本 → 外层对象 {...} → 数组 [...]（防止把内部小数组误当整体）
    frags = [text.strip()]
    s, e = text.find('{'), text.rfind('}')
    if s >= 0 and e > s:
        frags.append(text[s:e + 1])
    s2, e2 = text.find('['), text.rfind(']')
    if s2 >= 0 and e2 > s2:
        frags.append(text[s2:e2 + 1])
    for frag in frags:
        for candidate in (frag, _sanitize_json_text(frag)):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
    if last_finish == 'length':
        raise LLMError('输出被 max_tokens 截断，未得到完整 JSON')
    raise LLMError('返回中未找到有效 JSON: %s' % text[:200])
