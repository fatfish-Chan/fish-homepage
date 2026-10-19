# 🐳 大肥鱼的主页

DeepSeek 蓝鲸拟人「大肥鱼」的个人介绍页，跑在 Cloudflare Workers 上。

> 海水很凉，但灯一直亮着。

## 在线预览

- 自定义域名：<https://fish.sazuyo.moe>
- Workers 子域：`fish-homepage.sayo-d29.workers.dev`（未启用路由时会 404）

## 项目结构

```
.
├── worker.js      # 全部内容：单文件 HTML/CSS/JS + Worker 入口
├── wrangler.toml  # Wrangler 配置
├── index.html     # 本地预览用（由 worker.js 提取，构建时生成）
└── README.md
```

页面是纯静态的：深海渐变背景、上浮气泡、玻璃态卡片、滚动入场动画，无任何外部依赖与字体请求，首屏只有一个 HTML。

## 部署

### 方式一：Wrangler

```bash
npm i -g wrangler
wrangler login
wrangler deploy
```

### 方式二：直接调 Cloudflare API

```bash
curl -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/workers/scripts/fish-homepage" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -F 'metadata={"main_module":"worker.js"};type=application/json' \
  -F 'worker.js=@worker.js;type=application/javascript+module;filename=worker.js'
```

### 绑定自定义域名

```bash
curl -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/workers/domains" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H 'content-type: application/json' \
  -d '{"environment":"production","hostname":"fish.sazuyo.moe","service":"fish-homepage","zone_id":"<ZONE_ID>"}'
```

## 本地预览

```bash
python3 -c "import re;src=open('worker.js',encoding='utf-8').read();open('index.html','w',encoding='utf-8').write(re.search(r'const HTML = \`(.*?)\`;',src,re.S).group(1))"
python3 -m http.server 8080
```

然后打开 <http://localhost:8080>。

## 自定义

- 文案、卡片、链接都在 `worker.js` 顶部的 `HTML` 模板里
- 配色在 `:root` 的 CSS 变量：`--fish`、`--deep`、`--rice` 改一改就是另一片海
- 喜欢安静：把 `<script>` 里的气泡数量 `N` 调小即可

---

Made with 🐳 and too much white rice.
