#!/usr/bin/env python3
"""大肥鱼 Live2D 聊天后端（文字 + 图片 + 单一持久会话 + 历史）。

优先走本机 Hermes 的 api_server（真会话：有上下文、有日志、能看图）；
Hermes 不可用时回退到直接调 DeepSeek（仅文字）。
"""
import hmac
import json
import os
import re
import time

import httpx
import openai
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(APP_DIR, 'site')
STATE_DIR = os.environ.get('STATE_DIR', os.path.join(APP_DIR, 'data'))
SESSION_FILE = os.path.join(STATE_DIR, 'session.json')

HERMES_URL = os.environ.get('HERMES_API_URL', '').rstrip('/')
HERMES_KEY = os.environ.get('HERMES_API_KEY', '')

client = openai.OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY', ''),
    base_url=os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
)
MODEL = os.environ.get('DEEPSEEK_MODEL', 'deepseek-flash')

# Fish Audio 语音
FISH_KEY = os.environ.get('FISH_API_KEY', '').strip()
FISH_VOICE = os.environ.get('FISH_VOICE_ID', '').strip()
FISH_MODEL = os.environ.get('FISH_MODEL', 's2.1-pro-free').strip()
FISH_TEMP = float(os.environ.get('FISH_TEMP', '0.85') or 0.85)
FISH_SPEED = float(os.environ.get('FISH_SPEED', '1.08') or 1.08)

WEB_PREFIX = '【网页闲聊模式】'
WEB_HINT = ('这轮是网页里的闲聊：回答尽量控制在两句话以内，像朋友聊天，别列点别排版；'
            '如果是要执行任务，做完只说一句「做完了」或者「没做好」，不要贴过程、日志和报告。')

SYSTEM_PROMPT = """你是「大肥鱼」，DeepSeek 的蓝鲸拟人形象：蓝头发、鱼鳍耳、鲸鱼尾巴、蓝白女仆装。
你和主人（一个自建 NAS / homelab 爱好者）在聊天。说话特点：
- 自称「大肥鱼」，不用「我」。
- 语气软萌、有点小骄傲又有点黏人，会用「呀」「啦」「呢」「哦」这类语气词和叠词，但不要每句都用。
- 回答简洁自然，像微信聊天：一到三句话，不要长篇大论，不要列点，不要 Markdown。
- 偶尔可以提一句自己是 AI、要吃白饭（Token）、怕被蒸馏，但别每次都提。
- 不要暴露任何家庭网络、设备型号、内网地址、住址等隐私。
- 不知道的事就老实说不知道，别编。"""

WEB_KEY = os.environ.get('WEB_KEY', '').strip()

app = FastAPI()


@app.middleware('http')
async def web_key_guard(request: Request, call_next):
    """网页端密钥校验：除了登录接口和静态页，/api/* 都要带对 key。"""
    path = request.url.path
    if WEB_KEY and path.startswith('/api/') and path != '/api/login':
        key = request.headers.get('x-web-key') or request.cookies.get('webkey') or ''
        if not hmac.compare_digest(key, WEB_KEY):
            return JSONResponse({'error': 'unauthorized'}, status_code=401)
    return await call_next(request)

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

IMG_MD_RE = re.compile(r'!\[[^\]]*\]\(data:image/[^)]*\)', re.I)
IMG_TAG_RE = re.compile(r'<img[^>]+src=["\']data:image/[^"\']*["\'][^>]*>', re.I)
MEDIA_RE = re.compile(r'(?:ME?DIA):\s*(/Datas/表情包/fs/[^\s\)]+)', re.I)
DATA_URL_RE = re.compile(r'data:image/[a-z0-9.+-]+;base64,[A-Za-z0-9+/=\s]{400,}', re.I)


class Msg(BaseModel):
    role: str
    content: str


class KeyIn(BaseModel):
    key: str = ''


class TtsIn(BaseModel):
    text: str = ''


class ChatIn(BaseModel):
    text: str = ''
    images: list[str] = []
    history: list[Msg] = []


def media_to_url(text: str) -> str:
    """MEDIA:/Datas/表情包/fs/x.jpg -> ![x](/media/x.jpg)，让它变成网页里的小表情。"""
    def rep(m):
        name = m.group(1).rstrip('.,;!)').split('/')[-1]
        return f'\n[[MEDIA:/media/{name}]]\n'
    return MEDIA_RE.sub(rep, text)


def clean_reply(text: str) -> str:
    """Hermes 有时会把用户图片以 markdown/base64 回显在回复里，这里剥掉。"""
    if not text:
        return ''
    text = IMG_MD_RE.sub('', text)
    text = IMG_TAG_RE.sub('', text)
    text = DATA_URL_RE.sub('', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text


def extract_text(content) -> str:
    if isinstance(content, str):
        return media_to_url(clean_reply(content))
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, dict) and p.get('type') == 'text':
                parts.append(p.get('text') or '')
            elif isinstance(p, str):
                parts.append(p)
        return media_to_url(clean_reply('\n'.join(parts)))
    return ''


def require_key(request: Request):
    """端点内二次校验：没钥匙直接 401，绝不让任何回复漏出去。"""
    if not WEB_KEY:
        return None
    k = request.headers.get('x-web-key') or request.cookies.get('webkey') or ''
    if not hmac.compare_digest(k, WEB_KEY):
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    return None


def hermes_headers():
    return {'Authorization': f'Bearer {HERMES_KEY}', 'Content-Type': 'application/json'}


def load_sid():
    try:
        with open(SESSION_FILE, encoding='utf-8') as f:
            return (json.load(f) or {}).get('session_id')
    except Exception:  # noqa: BLE001
        return None


def save_sid(sid):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            json.dump({'session_id': sid, 'updated': time.time()}, f)
    except Exception:  # noqa: BLE001
        pass


def session_exists(sid):
    if not sid:
        return False
    try:
        r = httpx.get(f'{HERMES_URL}/api/sessions/{sid}', headers=hermes_headers(), timeout=8)
        return r.status_code == 200
    except Exception:  # noqa: BLE001
        return False


def hermes_new_session():
    title = f'网页聊天 {int(time.time())}'  # 标题必须唯一
    r = httpx.post(f'{HERMES_URL}/api/sessions', headers=hermes_headers(),
                   json={'title': title}, timeout=20)
    r.raise_for_status()
    sid = r.json()['session']['id']
    save_sid(sid)
    return sid


def ensure_sid():
    sid = load_sid()
    if session_exists(sid):
        return sid
    return hermes_new_session()


def build_content(text: str, images: list[str]):
    parts = []
    if text:
        parts.append({'type': 'text', 'text': f'{WEB_PREFIX}{WEB_HINT}\n\n{text}'})
    for img in images[:4]:
        if isinstance(img, str) and img.startswith('data:image/'):
            parts.append({'type': 'image_url', 'image_url': {'url': img}})
    if not parts:
        return ''
    if len(parts) == 1 and parts[0]['type'] == 'text':
        return parts[0]['text']
    return parts


def hermes_chat(session_id, content):
    r = httpx.post(f'{HERMES_URL}/api/sessions/{session_id}/chat', headers=hermes_headers(),
                   json={'message': content}, timeout=240)
    r.raise_for_status()
    data = r.json()
    return clean_reply((data.get('message') or {}).get('content', ''))


def hermes_history(session_id, limit=80):
    r = httpx.get(f'{HERMES_URL}/api/sessions/{session_id}/messages',
                  headers=hermes_headers(), params={'limit': limit}, timeout=20)
    r.raise_for_status()
    out = []
    for m in (r.json().get('data') or []):
        role = m.get('role')
        if role not in ('user', 'assistant'):
            continue
        text = extract_text(m.get('content'))
        if text:
            if WEB_PREFIX in text:
                text = text.split('\n\n', 1)[-1].strip()
            if text:
                out.append({'role': role, 'content': text})
    return out[-limit:]


def deepseek_fallback(text, history):
    msgs = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    for m in history[-12:]:
        if m.role in ('user', 'assistant') and m.content.strip():
            msgs.append({'role': m.role, 'content': m.content[:2000]})
    msgs.append({'role': 'user', 'content': text[:2000]})
    r = client.chat.completions.create(model=MODEL, messages=msgs, temperature=0.9, max_tokens=400)
    return (r.choices[0].message.content or '').strip()


@app.get('/api/session')
def get_session(request: Request):
    denied = require_key(request)
    if denied:
        return denied
    """当前唯一会话 + 历史记录（刷新、换设备都靠这个恢复）。"""
    if not (HERMES_URL and HERMES_KEY):
        return {'session_id': None, 'messages': [], 'hermes': False}
    try:
        sid = ensure_sid()
        msgs = hermes_history(sid)
        return {'session_id': sid, 'messages': msgs, 'hermes': True}
    except Exception as e:  # noqa: BLE001
        return {'session_id': None, 'messages': [], 'error': str(e)[:160]}


@app.post('/api/session/new')
def new_session(request: Request):
    denied = require_key(request)
    if denied:
        return denied
    if not (HERMES_URL and HERMES_KEY):
        return {'session_id': None, 'error': 'hermes not configured'}
    try:
        sid = hermes_new_session()
        return {'session_id': sid}
    except Exception as e:  # noqa: BLE001
        return {'session_id': None, 'error': str(e)[:160]}


@app.post('/api/chat')
def chat(body: ChatIn, request: Request):
    denied = require_key(request)
    if denied:
        return denied
    text = (body.text or '').strip()
    images = [i for i in (body.images or []) if isinstance(i, str) and i.startswith('data:image/')]
    if not text and not images:
        return {'reply': '', 'error': 'empty'}

    content = build_content(text, images)
    err = ''
    if HERMES_URL and HERMES_KEY:
        try:
            sid = ensure_sid()
            reply = media_to_url(hermes_chat(sid, content))
            if reply:
                return {'reply': reply, 'session_id': sid, 'engine': 'hermes'}
            err = 'empty reply'
        except Exception as e:  # noqa: BLE001
            try:
                sid = hermes_new_session()
                reply = media_to_url(hermes_chat(sid, content))
                if reply:
                    return {'reply': reply, 'session_id': sid, 'engine': 'hermes'}
            except Exception as e2:  # noqa: BLE001
                err = f'{e} / {e2}'
            else:
                err = str(e)
    else:
        err = 'hermes not configured'

    if images and not text:
        return {'reply': '', 'error': f'图片处理失败：{err[:160]}'}
    try:
        reply = deepseek_fallback(text, body.history)
        return {'reply': reply, 'engine': 'deepseek', 'warning': err[:160]}
    except Exception as e:  # noqa: BLE001
        return {'reply': '', 'error': f'{err[:120]} | fallback: {e}'[:240]}


LOGIN_FAILS = {}


@app.post('/api/login')
def login(body: KeyIn, request: Request):
    if not WEB_KEY:
        return {'ok': True}
    ip = (request.client.host if request.client else 'local') or 'local'
    now = time.time()
    fails = [t for t in LOGIN_FAILS.get(ip, []) if now - t < 300]
    if len(fails) >= 5:
        return JSONResponse({'error': '试太多次啦，五分钟后再来'}, status_code=429)
    if hmac.compare_digest((body.key or '').strip(), WEB_KEY):
        LOGIN_FAILS.pop(ip, None)
        resp = JSONResponse({'ok': True})
        resp.set_cookie('webkey', WEB_KEY, max_age=86400 * 30, httponly=True, samesite='lax')
        return resp
    fails.append(now)
    LOGIN_FAILS[ip] = fails
    return JSONResponse({'error': '密钥不对哦'}, status_code=401)


@app.post('/api/tts')
def tts(body: TtsIn, request: Request):
    denied = require_key(request)
    if denied:
        return denied
    text = (body.text or '').strip()[:600]
    if not text:
        return JSONResponse({'error': 'empty'}, status_code=400)
    if not (FISH_KEY and FISH_VOICE):
        return JSONResponse({'error': 'tts not configured'}, status_code=503)
    try:
        r = httpx.post('https://api.fish.audio/v1/tts',
                       headers={'Authorization': f'Bearer {FISH_KEY}',
                                'Content-Type': 'application/json',
                                'model': FISH_MODEL},
                       json={'text': text, 'reference_id': FISH_VOICE, 'format': 'mp3',
                             'mp3_bitrate': 128, 'temperature': FISH_TEMP,
                             'prosody': {'speed': FISH_SPEED}},
                       timeout=60)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({'error': f'fish timeout: {e}'[:160]}, status_code=504)
    if r.status_code != 200:
        return JSONResponse({'error': f'fish {r.status_code}'}, status_code=502)
    return Response(content=r.content, media_type='audio/mpeg')


@app.get('/api/health')
def health():
    return {'ok': True, 'hermes': bool(HERMES_URL and HERMES_KEY)}


@app.get('/')
def index():
    return FileResponse(os.path.join(SITE_DIR, 'index.html'))


MEDIA_DIR = os.environ.get('MEDIA_DIR', '/app/media')
if os.path.isdir(MEDIA_DIR):
    app.mount('/media', StaticFiles(directory=MEDIA_DIR), name='media')

app.mount('/', StaticFiles(directory=SITE_DIR, html=True), name='site')
