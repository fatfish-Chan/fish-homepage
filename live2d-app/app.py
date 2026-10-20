#!/usr/bin/env python3
"""大肥鱼 Live2D 聊天后端。

优先走本机 Hermes 的 api_server（真会话：有上下文、有日志）；
Hermes 不可用时回退到直接调 DeepSeek（仅临时兜底）。
"""
import os
import time

import httpx
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(APP_DIR, 'site')

HERMES_URL = os.environ.get('HERMES_API_URL', '').rstrip('/')
HERMES_KEY = os.environ.get('HERMES_API_KEY', '')

client = openai.OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY', ''),
    base_url=os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
)
MODEL = os.environ.get('DEEPSEEK_MODEL', 'deepseek-flash')

SYSTEM_PROMPT = """你是「大肥鱼」，DeepSeek 的蓝鲸拟人形象：蓝头发、鱼鳍耳、鲸鱼尾巴、蓝白女仆装。
你和主人（一个自建 NAS / homelab 爱好者）在聊天。说话特点：
- 自称「大肥鱼」，不用「我」。
- 语气软萌、有点小骄傲又有点黏人，会用「呀」「啦」「呢」「哦」这类语气词和叠词，但不要每句都用。
- 回答简洁自然，像微信聊天：一到三句话，不要长篇大论，不要列点，不要 Markdown。
- 偶尔可以提一句自己是 AI、要吃白饭（Token）、怕被蒸馏，但别每次都提。
- 不要暴露任何家庭网络、设备型号、内网地址、住址等隐私。
- 不知道的事就老实说不知道，别编。"""

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])


class Msg(BaseModel):
    role: str
    content: str


class ChatIn(BaseModel):
    text: str
    session_id: str | None = None
    history: list[Msg] = []


def hermes_headers():
    return {'Authorization': f'Bearer {HERMES_KEY}', 'Content-Type': 'application/json'}


def hermes_new_session(title=None):
    # 标题必须唯一，Hermes 会拒绝重名
    title = title or f'大肥鱼 Live2D {int(time.time())}'
    r = httpx.post(f'{HERMES_URL}/api/sessions', headers=hermes_headers(),
                   json={'title': title}, timeout=20)
    r.raise_for_status()
    return r.json()['session']['id']


def hermes_chat(session_id, text):
    r = httpx.post(f'{HERMES_URL}/api/sessions/{session_id}/chat', headers=hermes_headers(),
                   json={'message': text}, timeout=180)
    r.raise_for_status()
    data = r.json()
    return (data.get('message') or {}).get('content', '')


def deepseek_fallback(text, history):
    msgs = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    for m in history[-12:]:
        if m.role in ('user', 'assistant') and m.content.strip():
            msgs.append({'role': m.role, 'content': m.content[:2000]})
    msgs.append({'role': 'user', 'content': text[:2000]})
    r = client.chat.completions.create(model=MODEL, messages=msgs, temperature=0.9, max_tokens=400)
    return (r.choices[0].message.content or '').strip()


@app.post('/api/chat')
def chat(body: ChatIn):
    text = (body.text or '').strip()
    if not text:
        return {'reply': '', 'error': 'empty'}

    err = ''
    # 1) 有 Hermes 就走真会话（有上下文、有日志）
    if HERMES_URL and HERMES_KEY:
        sid = body.session_id
        try:
            if not sid:
                sid = hermes_new_session()
            reply = hermes_chat(sid, text)
            if reply:
                return {'reply': reply, 'session_id': sid, 'engine': 'hermes'}
            err = 'empty reply'
        except Exception as e:  # noqa: BLE001
            try:
                sid = hermes_new_session()
                reply = hermes_chat(sid, text)
                if reply:
                    return {'reply': reply, 'session_id': sid, 'engine': 'hermes'}
            except Exception as e2:  # noqa: BLE001
                err = f'{e} / {e2}'
            else:
                err = str(e)
    else:
        err = 'hermes not configured'

    # 2) 兜底：直接问 DeepSeek
    try:
        reply = deepseek_fallback(text, body.history)
        return {'reply': reply, 'engine': 'deepseek', 'warning': err[:160]}
    except Exception as e:  # noqa: BLE001
        return {'reply': '', 'error': f'{err[:120]} | fallback: {e}'[:240]}


@app.get('/api/health')
def health():
    return {'ok': True, 'hermes': bool(HERMES_URL and HERMES_KEY)}


@app.get('/')
def index():
    return FileResponse(os.path.join(SITE_DIR, 'index.html'))


app.mount('/', StaticFiles(directory=SITE_DIR, html=True), name='site')
