# -*- coding: utf-8 -*-
# llm_adapter：统一生成接口。首选 TeleAgent 模型 API（OpenAI 兼容），可换任意兼容端点。
import json
import httpx

from .. import config


class LLMError(RuntimeError):
    pass


# 最近一次推理过程（DeepSeek 等推理模型的 reasoning_content），供 UI 展示"模型思考"
last_thinking = ''


def chat(system: str, user: str, temperature: float = 0.3, max_tokens: int = 2048,
         timeout: float = 60.0) -> str:
    """单轮对话，返回文本。所有结构化生成任务都走这里。"""
    global last_thinking
    last_thinking = ''
    if not config.LLM_API_KEY:
        raise LLMError('LLM_API_KEY 未配置（见 .env）')
    resp = httpx.post(
        config.LLM_BASE_URL.rstrip('/') + '/chat/completions',
        headers={'Authorization': 'Bearer ' + config.LLM_API_KEY,
                 'Content-Type': 'application/json'},
        json={'model': config.LLM_MODEL,
              'messages': [{'role': 'system', 'content': system},
                           {'role': 'user', 'content': user}],
              'temperature': temperature, 'max_tokens': max_tokens},
        timeout=timeout)
    if resp.status_code != 200:
        raise LLMError('LLM HTTP %d: %s' % (resp.status_code, resp.text[:300]))
    data = resp.json()
    msg = data['choices'][0]['message']
    last_thinking = (msg.get('reasoning_content') or '').strip()
    return msg['content']


def chat_json(system: str, user: str, temperature: float = 0.2,
              timeout: float = 60.0, max_tokens: int = 2048):
    """要求模型输出 JSON 并解析。失败抛 LLMError。兼容 JSON 对象与数组。"""
    text = chat(system, user + '\n\n只输出 JSON，不要任何多余文字。', temperature,
                max_tokens=max_tokens, timeout=timeout)
    for oc, cc in (('[', ']'), ('{', '}')):
        s, e = text.find(oc), text.rfind(cc)
        if s >= 0 and e > s:
            try:
                return json.loads(text[s:e + 1])
            except json.JSONDecodeError:
                continue
    raise LLMError('返回中未找到有效 JSON: %s' % text[:200])
