#!/usr/bin/env python3
"""大肥鱼 Live2D 聊天后端：把消息交给 DeepSeek，返回大肥鱼口吻的回复。"""
import os

import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(APP_DIR, 'site')

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
    history: list[Msg] = []


@app.post('/api/chat')
def chat(body: ChatIn):
    msgs = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    for m in body.history[-12:]:
        if m.role in ('user', 'assistant') and m.content.strip():
            msgs.append({'role': m.role, 'content': m.content[:2000]})
    msgs.append({'role': 'user', 'content': body.text[:2000]})
    try:
        r = client.chat.completions.create(model=MODEL, messages=msgs, temperature=0.9, max_tokens=400)
        reply = (r.choices[0].message.content or '').strip()
    except Exception as e:  # noqa: BLE001
        return {'reply': '', 'error': str(e)[:200]}
    return {'reply': reply}


@app.get('/')
def index():
    return FileResponse(os.path.join(SITE_DIR, 'index.html'))


app.mount('/', StaticFiles(directory=SITE_DIR, html=True), name='site')
