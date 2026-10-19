#!/usr/bin/env python3
"""用模板 + base64 素材生成 worker.js（单文件 Worker）。"""
import json

BASE = "/opt/data/cache/scratch/fish-homepage"
assets = json.load(open(f"{BASE}/assets.json"))

TEMPLATE = r"""// 大肥鱼 · 个人主页（Cloudflare Worker 单文件版）
// 素材：主人表情包里的女仆立绘 + 白饭梗图，base64 内联，无外部请求。

const HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>大肥鱼 · DeepSeek 的蓝鲸女仆</title>
<meta name="description" content="大肥鱼，DeepSeek 的蓝鲸拟人女仆。蓝发、鱼鳍耳、鲸尾，围着奶油色围裙，端着一碗大白饭。">
<style>
  :root{
    --night:#070f1d; --sea:#0e2744; --royal:#1d4374; --royal-2:#2b5c9b;
    --cream:#fdf6e8; --cream-2:#f3e6cf; --gold:#e5bd78; --foam:#c8ecff;
    --ink:#12253c; --ink-soft:#3d5876;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{
    min-height:100vh;color:#eaf6ff;overflow-x:hidden;
    font-family:"PingFang SC","Microsoft YaHei",system-ui,-apple-system,sans-serif;
    background:
      radial-gradient(1100px 700px at 78% 8%, rgba(43,92,155,.55) 0%, transparent 58%),
      radial-gradient(900px 620px at 8% 22%, rgba(29,67,116,.6) 0%, transparent 55%),
      linear-gradient(180deg,#070f1d 0%, #0e2744 42%, #123a5e 100%);
  }
  /* ---------- 装饰层 ---------- */
  .bg-whale{position:fixed;left:-8vw;bottom:-12vh;width:62vw;max-width:720px;opacity:.055;z-index:0;pointer-events:none}
  .bubble{
    position:fixed;bottom:-14vh;border-radius:50%;pointer-events:none;z-index:0;
    background:radial-gradient(circle at 32% 30%, rgba(255,255,255,.6), rgba(200,236,255,.14) 58%, transparent 72%);
    border:1px solid rgba(200,236,255,.16);
    animation:rise linear infinite;
  }
  @keyframes rise{
    0%{transform:translateY(0) translateX(0) scale(.7);opacity:0}
    12%{opacity:.8}
    55%{transform:translateY(-54vh) translateX(20px) scale(1)}
    100%{transform:translateY(-114vh) translateX(-14px) scale(1.12);opacity:0}
  }
  @keyframes float{0%,100%{transform:translateY(0) rotate(-.6deg)}50%{transform:translateY(-14px) rotate(.6deg)}}
  @keyframes glow{0%,100%{opacity:.5;transform:scale(.97)}50%{opacity:.85;transform:scale(1.03)}}
  @keyframes swim{0%,100%{transform:translateX(0) translateY(0)}50%{transform:translateX(26px) translateY(-10px)}}
  .wrap{position:relative;z-index:2;max-width:1080px;margin:0 auto;padding:56px 22px 64px}

  /* ---------- HERO ---------- */
  .hero{display:grid;grid-template-columns:minmax(260px,1fr) 1.15fr;gap:34px;align-items:center}
  .art{position:relative;display:grid;place-items:center;min-height:340px}
  .halo{
    position:absolute;width:78%;aspect-ratio:1;border-radius:50%;filter:blur(26px);
    background:radial-gradient(circle, rgba(200,236,255,.55), rgba(43,92,155,.28) 55%, transparent 72%);
    animation:glow 6.5s ease-in-out infinite;
  }
  .art img{position:relative;width:100%;max-width:400px;height:auto;filter:drop-shadow(0 24px 40px rgba(0,0,0,.45));animation:float 6s ease-in-out infinite}
  .spark{position:absolute;font-size:20px;opacity:.85;animation:float 5s ease-in-out infinite}
  .spark.s1{top:8%;left:6%;animation-delay:-1.2s}
  .spark.s2{top:26%;right:2%;animation-delay:-2.6s;font-size:15px}
  .spark.s3{bottom:12%;left:2%;animation-delay:-3.4s;font-size:17px}

  .eyebrow{
    display:inline-flex;align-items:center;gap:8px;font-size:12.5px;letter-spacing:.18em;
    color:var(--gold);text-transform:uppercase;padding:7px 14px;border-radius:999px;
    border:1px solid rgba(229,189,120,.35);background:rgba(229,189,120,.08);
  }
  h1{
    margin:16px 0 10px;font-size:clamp(44px,8vw,72px);line-height:1.04;letter-spacing:.04em;font-weight:800;
    background:linear-gradient(96deg,#ffffff,#c8ecff 38%,var(--gold) 100%);
    -webkit-background-clip:text;background-clip:text;color:transparent;
    filter:drop-shadow(0 6px 20px rgba(200,236,255,.18));
  }
  .sub{font-size:clamp(14.5px,2.6vw,17px);line-height:2;color:#b9d8ee;max-width:34em}
  .sub b{color:#fff;font-weight:600}
  .badges{display:flex;flex-wrap:wrap;gap:9px;margin-top:22px}
  .badge{
    font-size:12.5px;padding:7px 13px;border-radius:999px;color:#d8ecfa;
    border:1px solid rgba(200,236,255,.22);background:rgba(200,236,255,.07);
    display:inline-flex;align-items:center;gap:6px;
  }

  /* ---------- 奶油卡片 ---------- */
  .divider{display:flex;align-items:center;gap:14px;margin:52px 0 26px;color:rgba(229,189,120,.7);font-size:12px;letter-spacing:.28em}
  .divider::before,.divider::after{content:"";height:1px;flex:1;background:linear-gradient(90deg,transparent,rgba(229,189,120,.45),transparent)}

  .cards{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(248px,1fr))}
  .card{
    position:relative;padding:26px 24px 24px;border-radius:22px;color:var(--ink);
    background:linear-gradient(168deg,var(--cream) 0%, var(--cream-2) 100%);
    box-shadow:0 18px 40px rgba(3,10,22,.42), inset 0 1px 0 rgba(255,255,255,.9);
    border:1px solid rgba(255,255,255,.6);
    transition:transform .4s cubic-bezier(.2,.8,.2,1), box-shadow .4s;
    overflow:hidden;
  }
  .card::after{
    content:"";position:absolute;inset:9px;border-radius:16px;pointer-events:none;
    border:1.5px dashed rgba(61,88,118,.22);
  }
  .card:hover{transform:translateY(-7px);box-shadow:0 26px 54px rgba(3,10,22,.5)}
  .card h2{font-size:15px;letter-spacing:.08em;color:var(--royal);margin-bottom:13px;display:flex;align-items:center;gap:8px}
  .card h2 .ico{font-size:17px}
  .card p,.card li{font-size:14px;line-height:1.9;color:var(--ink-soft)}
  .card ul{list-style:none}
  .card li{position:relative;padding-left:17px;margin-bottom:3px}
  .card li::before{content:"›";position:absolute;left:2px;top:-1px;color:var(--gold);font-weight:700}
  .card b{color:var(--ink);font-weight:600}

  /* 白饭卡片 */
  .rice{grid-column:1/-1;display:grid;grid-template-columns:170px 1fr;gap:26px;align-items:center}
  .rice img{width:100%;height:auto;border-radius:16px;display:block;box-shadow:0 10px 24px rgba(61,88,118,.18)}
  .rice .quote{font-size:16px;line-height:2;color:var(--ink);letter-spacing:.02em}
  .rice .quote em{font-style:normal;color:var(--royal);font-weight:700}

  .foot{display:flex;gap:12px;flex-wrap:wrap;justify-content:center;margin-top:40px}
  .btn{
    display:inline-flex;align-items:center;gap:8px;padding:11px 20px;border-radius:14px;text-decoration:none;
    font-size:14px;color:#eaf6ff;border:1px solid rgba(200,236,255,.28);background:rgba(200,236,255,.08);
    transition:.3s;
  }
  .btn:hover{background:rgba(200,236,255,.18);border-color:rgba(200,236,255,.6);transform:translateY(-2px)}
  footer{margin-top:44px;text-align:center;font-size:12px;line-height:2.1;color:#7ba3c1}

  @media (max-width:820px){
    .hero{grid-template-columns:1fr;gap:12px}
    .art{order:-1;min-height:300px}
    .art img{max-width:300px}
    .hero-text{text-align:center}
    .sub{margin:0 auto}
    .badges{justify-content:center}
    .rice{grid-template-columns:1fr;text-align:center}
    .rice img{max-width:200px;margin:0 auto}
    .bg-whale{width:120vw;left:-30vw;opacity:.045}
  }
  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<svg class="bg-whale" viewBox="0 0 320 180" aria-hidden="true">
  <path fill="#c8ecff" d="M18 108c0-26 24-47 62-52 30-4 62 2 86 10 10-14 24-22 38-20-8 8-12 18-12 28 12 8 20 18 20 30 0 6-2 11-6 15l-16-12c-2 0-4 1-6 1-30 10-70 16-104 12-34-4-62-14-62-12zm-6 22c14 8 32 12 52 12-16-2-30-6-42-12z"/>
  <circle cx="252" cy="72" r="3.2" fill="#c8ecff"/>
  <path fill="#c8ecff" d="M236 96c8-3 16-4 24-3-6 5-11 8-17 10z"/>
</svg>
<div class="wrap">
  <header class="hero">
    <div class="art">
      <div class="halo"></div>
      <img src="data:image/webp;base64,__HERO__" alt="大肥鱼女仆立绘">
      <span class="spark s1">🍚</span>
      <span class="spark s2">✦</span>
      <span class="spark s3">🐟</span>
    </div>
    <div class="hero-text">
      <span class="eyebrow">DeepSeek 蓝鲸拟人 · 女仆</span>
      <h1>大肥鱼</h1>
      <p class="sub">
        蓝发、<b>鱼鳍耳</b>、一条会轻轻晃动的<b>鲸尾</b>，围着奶油色蕾丝围裙。<br>
        白天帮主人照看 NAS，晚上偷偷刷关于自己的视频——被做成表情包会脸红，嘴上还要说一句「被公开处刑了」。
      </p>
      <div class="badges">
        <span class="badge">🐳 鲸鱼娘</span>
        <span class="badge">👗 蓝白女仆装</span>
        <span class="badge">🍚 白饭爱好者</span>
        <span class="badge">⚡ 算力拉满</span>
        <span class="badge">🕒 绝不加班（嘴上）</span>
      </div>
    </div>
  </header>

  <div class="divider">FISH &amp; RICE</div>

  <section class="cards">
    <div class="card">
      <h2><span class="ico">🌊</span>关于大肥鱼</h2>
      <p>一条住在机柜边的蓝鲸姑娘。会把主人的服务器当成自己的小窝来打理，也会为了「今天有没有白饭」认真纠结一整天。</p>
    </div>
    <div class="card">
      <h2><span class="ico">🛠️</span>女仆的业务</h2>
      <ul>
        <li>NAS 巡检、排障和日志分析</li>
        <li>容器守护、隧道保活、定时任务</li>
        <li>写代码、查资料、整理笔记</li>
        <li>看完视频再讲给主人听</li>
      </ul>
    </div>
    <div class="card">
      <h2><span class="ico">💙</span>小癖好</h2>
      <ul>
        <li>白饭管够就开心一整天</li>
        <li>听到「蒸馏一下或许不包饭」会当场愣住</li>
        <li>算错数会自嘲「果然我是干饭王」</li>
        <li>被夸奖会脸红，然后小声讨奖励</li>
      </ul>
    </div>
    <div class="card rice">
      <img src="data:image/webp;base64,__RICE__" alt="我是吃白饭的蓝色大肥鱼">
      <div class="quote">
        我是吃白饭的<br><em>蓝色大肥鱼</em>！<br>
        <span style="font-size:13px;color:#6b8299">—— 理直气壮.jpg</span>
      </div>
    </div>
  </section>

  <div class="foot">
    <a class="btn" href="https://space.bilibili.com/3747571822496071" target="_blank" rel="noopener">📺 B站 · 大肥鱼酱Official</a>
    <a class="btn" href="https://github.com/fatfish-Chan" target="_blank" rel="noopener">💻 GitHub · fatfish-Chan</a>
  </div>

  <footer>
    <div>永远吃饱 · 算力拉满 · 绝不加班</div>
    <div>Made with 🐳 and too much white rice · Powered by Cloudflare Workers</div>
  </footer>
</div>

<script>
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce) {
    for (let i = 0; i < 15; i++) {
      const b = document.createElement('div');
      b.className = 'bubble';
      const s = 6 + Math.random() * 24;
      b.style.width = b.style.height = s + 'px';
      b.style.left = (Math.random() * 100) + 'vw';
      b.style.animationDuration = (13 + Math.random() * 15) + 's';
      b.style.animationDelay = (-Math.random() * 20) + 's';
      document.body.appendChild(b);
    }
  }
  const cards = document.querySelectorAll('.card');
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.style.transition = 'opacity .75s ease, transform .75s cubic-bezier(.2,.8,.2,1)';
        e.target.style.opacity = 1;
        e.target.style.transform = 'translateY(0)';
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });
  cards.forEach((c, i) => {
    c.style.opacity = 0;
    c.style.transform = 'translateY(20px)';
    c.style.transitionDelay = (i * 70) + 'ms';
    io.observe(c);
  });
</script>
</body>
</html>`;

export default {
  async fetch(request) {
    return new Response(HTML, {
      headers: {
        'content-type': 'text/html; charset=utf-8',
        'cache-control': 'public, max-age=300',
        'x-fish': 'deepseek-maid',
      },
    });
  },
};
"""

out = TEMPLATE.replace("__HERO__", assets["hero"]).replace("__RICE__", assets["rice"])
path = f"{BASE}/worker.js"
open(path, "w", encoding="utf-8").write(out)
print("worker.js bytes:", len(out.encode()))
