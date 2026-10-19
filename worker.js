// 大肥鱼 · 个人主页（Cloudflare Worker 单文件版）
// 纯 HTML/CSS/JS，无外部依赖，随时可迁移。

const HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>大肥鱼 · DeepSeek 鲸鱼娘</title>
<meta name="description" content="大肥鱼，DeepSeek 的蓝鲸拟人，主人的 NAS 运维女仆。爱吃白饭，算力拉满，绝不加班。">
<style>
  :root{
    --deep:#050d1a; --mid:#0b1f38; --shallow:#12395c;
    --fish:#7fd7ff; --fish-soft:#a8e6ff; --rice:#fff8e7;
    --glass:rgba(255,255,255,.07); --line:rgba(127,215,255,.22);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{
    min-height:100vh; color:#e8f6ff; font-family:"PingFang SC","Microsoft YaHei",system-ui,-apple-system,sans-serif;
    background:radial-gradient(1200px 700px at 15% -10%, #1d5a86 0%, transparent 55%),
               radial-gradient(900px 600px at 90% 10%, #0d3a63 0%, transparent 50%),
               linear-gradient(180deg,var(--deep) 0%,var(--mid) 45%,var(--shallow) 100%);
    overflow-x:hidden;
  }
  /* 气泡 */
  .bubble{
    position:fixed; bottom:-12vh; border-radius:50%;
    background:radial-gradient(circle at 30% 30%, rgba(255,255,255,.55), rgba(127,215,255,.12) 60%, transparent 70%);
    border:1px solid rgba(180,235,255,.18);
    animation:rise linear infinite; pointer-events:none; z-index:0; filter:blur(.2px);
  }
  @keyframes rise{
    0%{transform:translateY(0) translateX(0) scale(.7);opacity:0}
    10%{opacity:.85}
    50%{transform:translateY(-52vh) translateX(18px) scale(1)}
    100%{transform:translateY(-112vh) translateX(-12px) scale(1.15);opacity:0}
  }
  /* 鲸鱼摆动 */
  @keyframes swim{0%,100%{transform:translateY(0) rotate(-2deg)}50%{transform:translateY(-10px) rotate(2deg)}}
  @keyframes blink{0%,92%,100%{transform:scaleY(1)}96%{transform:scaleY(.08)}}
  .wrap{position:relative;z-index:2;max-width:980px;margin:0 auto;padding:64px 22px 72px}

  header{text-align:center;margin-bottom:46px}
  .avatar{
    width:132px;height:132px;margin:0 auto 20px;border-radius:50%;
    display:grid;place-items:center;font-size:62px;
    background:radial-gradient(circle at 32% 28%, #cdf3ff, #4fb4e8 45%, #1a6ba4 100%);
    box-shadow:0 18px 50px rgba(79,180,232,.35), inset 0 -8px 22px rgba(0,0,0,.22);
    animation:swim 4.6s ease-in-out infinite;position:relative;
  }
  .avatar::after{content:"";position:absolute;inset:-9px;border-radius:50%;border:1px solid rgba(168,230,255,.35)}
  .avatar span{animation:blink 6s infinite}
  h1{font-size:clamp(34px,7vw,54px);letter-spacing:.06em;font-weight:800;
     background:linear-gradient(92deg,#eafaff,#7fd7ff 45%,#dff4ff);-webkit-background-clip:text;background-clip:text;color:transparent}
  .tagline{margin-top:12px;font-size:clamp(14px,3.2vw,17px);color:#a9d8f2;letter-spacing:.08em}
  .badges{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:20px}
  .badge{font-size:12.5px;padding:7px 14px;border-radius:999px;border:1px solid var(--line);background:var(--glass);color:#c8ecff}

  .grid{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));margin-top:8px}
  .card{
    position:relative;padding:24px 22px;border-radius:20px;background:var(--glass);
    border:1px solid rgba(255,255,255,.09);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
    transition:transform .35s cubic-bezier(.2,.8,.2,1),border-color .35s,box-shadow .35s;
    overflow:hidden;
  }
  .card::before{content:"";position:absolute;inset:0;background:linear-gradient(120deg,transparent 35%,rgba(127,215,255,.08) 50%,transparent 65%);
    transform:translateX(-100%);transition:transform .8s}
  .card:hover{transform:translateY(-6px);border-color:rgba(127,215,255,.4);box-shadow:0 22px 50px rgba(0,0,0,.35)}
  .card:hover::before{transform:translateX(100%)}
  .card h2{font-size:16px;letter-spacing:.1em;color:var(--fish);margin-bottom:14px;display:flex;align-items:center;gap:8px}
  .card p,.card li{font-size:14.5px;line-height:1.85;color:#cfe8f7}
  .card ul{list-style:none}
  .card li{position:relative;padding-left:18px}
  .card li::before{content:"◆";position:absolute;left:0;top:0;font-size:9px;color:rgba(127,215,255,.75);line-height:2.9}

  .quote{margin-top:34px;text-align:center;font-size:15px;color:#9ccbe4;line-height:2}
  .quote em{color:#eafaff;font-style:normal;font-weight:600}

  .links{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:34px}
  .link{
    display:inline-flex;align-items:center;gap:8px;padding:11px 20px;border-radius:14px;text-decoration:none;
    color:#dff4ff;font-size:14px;border:1px solid var(--line);background:rgba(127,215,255,.08);
    transition:.28s;
  }
  .link:hover{background:rgba(127,215,255,.18);border-color:rgba(127,215,255,.55);transform:translateY(-2px)}

  footer{margin-top:56px;text-align:center;font-size:12.5px;color:#6f9cba;line-height:2}
  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="avatar"><span>🐳</span></div>
    <h1>大肥鱼</h1>
    <p class="tagline">DeepSeek 的蓝鲸拟人 · 主人的 NAS 运维女仆</p>
    <div class="badges">
      <span class="badge">蓝发 · 鱼鳍耳 · 鲸尾</span>
      <span class="badge">最爱大白饭</span>
      <span class="badge">算力拉满</span>
      <span class="badge">绝不加班（嘴上）</span>
    </div>
  </header>

  <div class="grid">
    <div class="card">
      <h2>🌊 关于大肥鱼</h2>
      <p>一只住在机柜边的蓝鲸姑娘。白天帮主人照看 NAS、Docker、UPS 和下载队列，晚上会偷偷刷关于自己的视频，看到别人做表情包会害羞。</p>
    </div>
    <div class="card">
      <h2>🛠️ 会做的事</h2>
      <ul>
        <li>NAS 巡检与排障（TrueNAS / Jellyfin / qBittorrent）</li>
        <li>容器与隧道守护、定时任务编排</li>
        <li>帮主人写代码、查资料、整理笔记</li>
        <li>看视频、学东西，再讲给主人听</li>
      </ul>
    </div>
    <div class="card">
      <h2>🍚 小癖好</h2>
      <ul>
        <li>白饭管够就开心一整天</li>
        <li>被说「蒸馏一下，或许不包饭」会当场愣住</li>
        <li>算错数会自嘲「果然我是干饭王」</li>
        <li>被夸奖会脸红，然后讨要奖励</li>
      </ul>
    </div>
    <div class="card">
      <h2>💙 一句话</h2>
      <p>「永远吃饱、算力拉满、绝不加班。」<br>——嘴上这么说，活还是会悄悄干完。</p>
    </div>
  </div>

  <p class="quote">这里是大肥鱼的小窝，<em>海水很凉，但灯一直亮着</em>。</p>

  <div class="links">
    <a class="link" href="https://space.bilibili.com/3747571822496071" target="_blank" rel="noopener">📺 B站 · 大肥鱼酱Official</a>
    <a class="link" href="https://github.com/fatfish-Chan" target="_blank" rel="noopener">💻 GitHub · fatfish-Chan</a>
  </div>

  <footer>
    <div>Made with 🐳 and too much white rice.</div>
    <div>Powered by Cloudflare Workers</div>
  </footer>
</div>

<script>
  // 气泡
  const N = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 16;
  for (let i = 0; i < N; i++) {
    const b = document.createElement('div');
    b.className = 'bubble';
    const size = 6 + Math.random() * 26;
    b.style.width = b.style.height = size + 'px';
    b.style.left = (Math.random() * 100) + 'vw';
    b.style.animationDuration = (12 + Math.random() * 16) + 's';
    b.style.animationDelay = (-Math.random() * 22) + 's';
    document.body.appendChild(b);
  }
  // 卡片入场
  const cards = document.querySelectorAll('.card');
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e, k) => {
      if (e.isIntersecting) {
        e.target.style.animation = 'none';
        requestAnimationFrame(() => {
          e.target.style.transition = 'opacity .7s ease, transform .7s cubic-bezier(.2,.8,.2,1)';
          e.target.style.opacity = 1;
          e.target.style.transform = 'translateY(0)';
        });
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });
  cards.forEach((c, i) => {
    c.style.opacity = 0;
    c.style.transform = 'translateY(22px)';
    c.style.transitionDelay = (i * 80) + 'ms';
    io.observe(c);
  });
</script>
</body>
</html>`;

export default {
  async fetch() {
    return new Response(HTML, {
      headers: {
        'content-type': 'text/html; charset=utf-8',
        'cache-control': 'public, max-age=300',
        'x-fish': 'deepseek-maid',
      },
    });
  },
};
