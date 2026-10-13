# -*- coding: utf-8 -*-
"""读取 assets 里的素材，生成单文件「神圣奶蛙」跑酷游戏 (index.html)。

产物固定叫 index.html —— GitHub Pages / 静态托管默认找的就是它，
否则访问目录地址只会看到文件列表或 404。

镜像 Chrome 小恐龙的玩法：跳 / 下蹲 / 计分 / 昼夜 / 加速 / 触屏。
素材来自奶蛙合集里抓到的「奶斗罗」角色与敌兵（见 doc/README）。
"""
import base64, os, pathlib

# 相对此脚本的根目录 (此文件位于仓库根目录)
# 素材只从 art/ 读 —— 那是本作**实际用到**的 15 张贴图，随仓库一起提交，
# 所以干净检出后本脚本可以直接运行，不需要先抓素材。
# （art/ 的来源与上游仓库见 README.md；完整素材集由 fetch_assets.py 抓到 assets/，
#   那个目录很大且是他人版权内容，已 gitignore。）
ROOT = pathlib.Path(__file__).resolve().parent
A = ROOT / "art" / "douluo"      # 角色与敌兵，取自「奶斗罗」
# 「合成大奶蛙」的水果贴图：11 级是合成链最高产物，本作拿它当主角与开始页图标
# （源游戏里这一级写作「神奶蛙」，本作按用户要求统一叫「神圣奶蛙」）
H = ROOT / "art" / "bignaiwa"

# (game里引用名, 源文件, 用法)
IMGS = [
    ("run0", A / "baby-run-0.webp",  "跑帧 0"),
    ("run1", A / "baby-run-1.webp",  "跑帧 1"),
    ("run2", A / "baby-run-2.webp",  "跑帧 2"),
    ("jump", A / "baby-jump.webp",   "跳跃"),
    ("duck", A / "baby-double.webp", "下蹲"),
    ("hurt", A / "baby-hurt.webp",   "撞"),
    ("ob1",  A / "dog-foam.webp",    "障碍·泡沫狗"),
    ("ob2",  A / "dog-cheese.webp",  "障碍·芝士狗"),
    ("ob3",  A / "dog-guard.webp",   "障碍·护卫狗"),
    ("ob4",  A / "dog-rammer.webp",  "障碍·冲撞狗"),
    ("ob5",  A / "milk-egg.webp",    "障碍·奶蛋"),
    ("ob6",  A / "milk-baby.webp",   "障碍·奶娃瓶"),
    ("fly",  A / "dog-howler.webp",  "飞狗"),
    ("cloud", A / "milk-star.webp",  "云朵"),
    ("godfrog", H / "11-watermelon.webp", "开始页图标·神圣奶蛙（合成大奶蛙最高级产物）"),
]

def b64(p):
    return "data:image/webp;base64," + base64.b64encode(p.read_bytes()).decode()

ENC = {name: b64(path) for name, path, _ in IMGS}

# 左下角显示的**本项目**仓库地址。留空则显示占位提示；填上后自动渲染成可点链接。
# （素材的上游来源写在上面的 art/ 注释与 README 里，那是另一回事）
# 例：REPO_URL = "https://github.com/yourname/holy-naiwa"
REPO_URL = "https://github.com/Astenyx-Git/shenshengnaiwa"
CREDIT_HTML = (
    f'项目仓库：<a href="{REPO_URL}" target="_blank" rel="noreferrer">{REPO_URL}</a>'
    if REPO_URL else
    '项目仓库：GitHub 仓库地址（待填）'
)

# ============ HTML ============
HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="theme-color" content="#f4ecd8">
<title>神圣奶蛙 · Naiwa Run</title>
<link rel="icon" href="__GODFROG__">
<style>
  :root{--bg:#f4ecd8;--ink:#3b2f1f;--mute:#a08a6a;--line:#d9c9a6;--day:#fff8e8;--night:#1a1f33}
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;height:100%;background:var(--bg);color:var(--ink);
    font-family:"Noto Sans SC","PingFang SC",system-ui,sans-serif;overflow:hidden}
  body{display:flex;flex-direction:column;align-items:center;justify-content:center;
    padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}
  .stage{position:relative;width:min(100vw,1000px);height:min(56vw,560px);
    max-height:calc(100vh - 80px);background:linear-gradient(to bottom,#fff7df 0%,#f4ecd8 60%,#e9dcb8 100%);
    border-radius:14px;overflow:hidden;box-shadow:0 10px 30px rgba(80,50,10,.15);user-select:none;cursor:pointer}
  .stage.night{background:linear-gradient(to bottom,#1f2540 0%,#14182a 70%,#0c0f1a 100%)}
  canvas{display:block;width:100%;height:100%}
  .hud{position:absolute;top:14px;right:18px;font:600 18px ui-monospace,Menlo,Consolas,monospace;
    color:var(--ink);text-shadow:0 1px 0 #fff8;letter-spacing:1px}
  .stage.night .hud{color:#fff;text-shadow:0 1px 0 #000}
  .hud small{font-size:11px;color:var(--mute);margin-left:8px;font-weight:500}
  .stage.night .hud small{color:#7a82a8}
  .hi{position:absolute;top:14px;left:18px;font:600 12px ui-monospace,Menlo,Consolas,monospace;color:var(--mute)}
  .stage.night .hi{color:#7a82a8}
  .overlay{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;
    background:rgba(255,247,223,.85);backdrop-filter:blur(2px);text-align:center;padding:0 24px}
  .stage.night .overlay{background:rgba(20,24,42,.85);color:#fff}
  .overlay h1{margin:0 0 8px;font-size:34px;letter-spacing:1px}
  .overlay h1 small{display:block;font-size:14px;color:var(--mute);margin-top:4px;letter-spacing:0;font-weight:500}
  .stage.night .overlay h1 small{color:#9aa3c8}
  .overlay h1 .logo{display:block;width:104px;height:104px;object-fit:contain;margin:0 auto 12px;
    filter:drop-shadow(0 8px 14px rgba(120,80,20,.30));
    animation:bob 2.6s ease-in-out infinite}
  @keyframes bob{0%,100%{transform:translateY(0) rotate(-2.5deg)}50%{transform:translateY(-9px) rotate(2.5deg)}}
  @media (prefers-reduced-motion:reduce){.overlay h1 .logo{animation:none}}
  .overlay .keys{display:flex;flex-direction:column;gap:7px;margin:16px 0 18px;align-items:center}
  .krow{display:flex;align-items:center;gap:5px;flex-wrap:wrap;justify-content:center;font-size:13px;color:#6b6355}
  .stage.night .krow{color:#a8b0d0}
  .krow b{font-size:12px;font-weight:700;color:var(--mute);min-width:34px;text-align:right;margin-right:3px}
  .stage.night .krow b{color:#7a82a8}
  .krow em{font-style:normal;font-weight:600;margin:0 8px 0 2px;color:var(--ink)}
  .stage.night .krow em{color:#e6ebff}
  .key{font:600 13px ui-monospace,Menlo,Consolas,monospace;background:#fff;border:1px solid var(--line);
    border-radius:8px;padding:4px 10px;color:#6b5635}
  .stage.night .key{background:#2a3055;color:#cdd5ec;border-color:#3a426a}
  .go{font:700 18px ui-monospace,Menlo,Consolas,monospace;color:var(--ink);
    background:var(--ink);color:#fff8;padding:10px 26px;border-radius:999px;border:0;
    margin-top:6px;cursor:pointer}
  .stage.night .go{background:#fff8;color:var(--ink)}
  .go:active{transform:scale(.97)}
  .boardbtn{font:600 13px ui-monospace,Menlo,Consolas,monospace;margin-top:10px;
    padding:7px 18px;border-radius:999px;cursor:pointer;
    background:transparent;color:var(--mute);border:1px solid var(--line)}
  .boardbtn:hover{color:var(--ink);border-color:var(--ink)}
  .stage.night .boardbtn{color:#8f98bd;border-color:#3a426a}
  .stage.night .boardbtn:hover{color:#fff;border-color:#6a76a8}
  /* ---------- 本地排行榜面板 ---------- */
  .board{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
    justify-content:center;gap:12px;padding:26px 20px;
    background:rgba(255,247,223,.94);backdrop-filter:blur(3px)}
  .stage.night .board{background:rgba(18,22,38,.94)}
  .board[hidden]{display:none}
  .board h2{margin:0;font-size:20px}
  .board h2 small{display:block;font-size:11.5px;color:var(--mute);font-weight:500;margin-top:3px}
  .stage.night .board h2 small{color:#8f98bd}
  .board .empty{font-size:13px;color:var(--mute);padding:18px 0}
  .board ol{margin:0;padding:0;list-style:none;width:min(420px,100%);max-height:46%;
    overflow-y:auto;background:#fff;border:1px solid var(--line);border-radius:12px}
  .stage.night .board ol{background:#222948;border-color:#3a426a}
  .board li{display:flex;align-items:center;gap:10px;padding:8px 14px;font-size:13.5px;
    border-bottom:1px solid var(--line)}
  .stage.night .board li{border-color:#333b5e}
  .board li:last-child{border-bottom:none}
  .board li .rk{width:22px;font:700 12px ui-monospace,monospace;color:var(--mute);flex:none}
  .board li.top1 .rk{color:#f0b429}
  .board li .sc{font:700 15px ui-monospace,monospace;flex:1;text-align:left}
  .board li .nm{font-size:12.5px;color:var(--mute);max-width:120px;overflow:hidden;
    text-overflow:ellipsis;white-space:nowrap}
  .stage.night .board li .nm{color:#8f98bd}
  .board li .dur{font:600 11.5px ui-monospace,monospace;color:var(--mute);flex:none}
  .stage.night .board li .dur{color:#8f98bd}
  .board li .dt{font-size:11px;color:var(--mute);flex:none;min-width:74px;text-align:right}
  .board .tabs{display:flex;gap:6px}
  .board .tab{font:600 13px ui-monospace,monospace;padding:6px 20px;border-radius:999px;
    border:1px solid var(--line);background:transparent;color:var(--mute);cursor:pointer}
  .board .tab.is-on{background:var(--ink);color:#fff8;border-color:var(--ink)}
  .stage.night .board .tab{color:#8f98bd;border-color:#3a426a}
  .stage.night .board .tab.is-on{background:#e6ebff;color:#1a1f33;border-color:#e6ebff}
  .board .nickrow{display:flex;align-items:center;gap:8px;font-size:12.5px;color:var(--mute)}
  .board .nickrow[hidden]{display:none}
  .board .nickrow input{font:600 13px ui-monospace,monospace;width:130px;padding:6px 10px;
    border-radius:8px;border:1px solid var(--line);background:#fff;color:var(--ink)}
  .stage.night .board .nickrow input{background:#222948;color:#e6ebff;border-color:#3a426a}
  .board .nickrow button{font:700 15px ui-monospace,monospace;padding:4px 12px;border-radius:8px;
    border:1px solid var(--line);background:#fff;color:#6b5635;cursor:pointer}
  .stage.night .board .nickrow button{background:#2a3055;color:#cdd5ec;border-color:#3a426a}
  .board .boardmsg{margin:0;font-size:12px;color:var(--mute);min-height:16px}
  .board .boardmsg.ok{color:#15803d}
  .board .boardmsg.bad{color:#b42318}
  .board .acts{display:flex;gap:10px}
  .board button{font:600 13px ui-monospace,monospace;padding:8px 18px;border-radius:999px;
    border:1px solid var(--line);background:#fff;color:#6b5635;cursor:pointer}
  .stage.night .board button{background:#2a3055;color:#cdd5ec;border-color:#3a426a}
  .board button.primary{background:var(--ink);color:#fff8;border-color:var(--ink)}
  .board button:active{transform:scale(.97)}
  .credit{position:absolute;bottom:6px;left:10px;font-size:10.5px;color:var(--mute)}
  .credit a{color:inherit;text-decoration:underline;text-underline-offset:2px}
  .credit a:hover{color:var(--ink)}
  .stage.night .credit{color:#7a82a8}
  .stage.night .credit a:hover{color:#fff}
  .hint{position:absolute;bottom:8px;right:14px;font:500 11.5px ui-monospace,monospace;color:var(--mute)}
  .stage.night .hint{color:#7a82a8}
</style>
</head>
<body>
<div class="stage" id="stage">
  <canvas id="cv"></canvas>
  <div class="hi">HI <span id="hi">0</span></div>
  <div class="hud"><span id="score">0</span><small id="unit">分</small></div>
  <div class="overlay" id="ov">
    <h1 id="title">
      <img class="logo" src="__GODFROG__" alt="神圣奶蛙">
      <span id="titleText">神圣奶蛙</span>
      <small id="titleSub">Naiwa Run</small>
    </h1>
    <div class="keys">
      <div class="krow"><b>键盘</b>
        <span class="key">Space</span><span class="key">↑</span><span class="key">W</span><em>跳</em>
        <span class="key">↓</span><span class="key">S</span><em>下蹲</em>
      </div>
      <div class="krow"><b>触屏</b>
        <span class="key">点屏幕</span><em>跳</em>
        <span class="key">向下滑</span><em>下蹲</em>
      </div>
    </div>
    <button class="go" id="go">开 始 狂 奔</button>
    <button class="boardbtn" id="boardBtn">🏆 本地排行榜</button>
  </div>
  <div class="board" id="board" hidden>
    <h2>排行榜<small id="boardSub"></small></h2>
    <div class="tabs">
      <button class="tab is-on" data-tab="local">本机</button>
      <button class="tab" data-tab="remote">全网</button>
    </div>
    <ol id="boardList"></ol>
    <div class="nickrow" id="nickRow" hidden>
      <label for="nickInput">昵称</label>
      <input id="nickInput" maxlength="12" placeholder="匿名玩家" autocomplete="off" spellcheck="false">
      <button id="boardRefresh" title="刷新">↻</button>
    </div>
    <p class="boardmsg" id="boardMsg"></p>
    <div class="acts">
      <button class="primary" id="boardClose">关 闭</button>
      <button id="boardClear">清空本机记录</button>
    </div>
  </div>
  <div class="hint">速度 <span id="spd">5.0</span></div>
  <div class="credit">__CREDIT__</div>
</div>

<script>
// ===================== 资源 =====================
const IMG = __IMGS__;

// ===================== 配置 =====================
const W = 1000, H = 560;
const GROUND_Y = 460;          // 地面 y 坐标
const PLAYER_X = 110;          // 主角屏幕 x
const GRAVITY = 0.26;
// 跳跃的两个旋钮是独立的：
//   顶点高度 h = v²/(2g)   —— 决定越障能力
//   滞空帧数 t = 2|v|/g    —— 决定手感（滞空感）
// 想「同样高、但飘得久」就【同时】降 v 和降 g；只降一个会变成又矮又急的弹跳。
// 当前：顶点 169px / 滞空 72 帧(1.20s)，跳跃是固定高度（无长按变高）。
// ⚠️ 跳跃顶点决定「高飞障碍」的顶边上限：
//    顶点时玩家盒底边 = 458 - 169 = 289，所以障碍顶边必须低于 289（实际取 267）。
//    **改跳跃参数后必须回头复核**，否则高飞障碍会变成可以跳过去。
//    自检里有 tallFlyMarginPx 把余量直接打出来。
// 注：离散模拟的实测顶点比解析解 h=v²/(2g) 低约 4px，调参请按实测值搜。
const JUMP_V = -9.5;
const DUCK_H = 50;             // 下蹲后的身高。物理 / 碰撞 / 绘制三处必须共用这一个值，
                               // 否则会出现「看着蹲下了、判定还是站着」的错位
// 开局滚动速度。7px/帧（420px/s）时从右边缘到角色只要 2.2 秒，一上来就手忙脚乱；
// 降到 5（300px/s）留出约 2.9 秒的反应时间，之后再靠分数慢慢加速。
const SPEED0 = 5;
const SPEED_MAX = 16;
const SPEEDUP_PER_SCORE = 0.0011;
// 算障碍间距用的滞空帧数。一次跳跃期间障碍要横向走 speed × JUMP_FRAMES 像素，
// 间距必须大于它，否则「跳起来落地正好砸在下一个障碍上」。
// 跳跃已无长按变高，所以这就是实际滞空（自检里用 JUMP_FRAMES_ok 断言守住）。
const JUMP_FRAMES = 74;
const NIGHT_AT = [700, 1400, 2100];   // 达到这些分数后切换一次昼夜

// ===================== 本地数据库 =====================
// 纯前端持久化，不依赖任何后端。表 runs{ id, score, ts, dur, spd }。
// 首选 IndexedDB（真正的浏览器数据库，可索引、可查询）；
// 但 Chrome 在 file:// 协议下把页面当作 opaque origin，会直接禁用 IndexedDB ——
// 而本作主打「双击即玩」，所以必须能降级。降级目标是 localStorage（file:// 下可用）。
// 两个后端暴露同一套 API，上层代码不关心底层是哪个。
//
// ⚠️ 验证边界（别误以为自检覆盖了全部）：自检里 localDB* 那几条断言，
//    在无头浏览器里跑的都是 **localStorage 分支** —— 因为
//    `--dump-dom` 不加虚拟时钟会立刻取 DOM，加了虚拟时钟又会把定时器瞬间跳过、
//    却**不等 IndexedDB 的回调**（IndexedDB 不走网络栈，虚拟时钟不等它）。
//    所以 IndexedDB 分支是靠代码审查确认的，不是靠自检跑出来的。
//    真实浏览器打开 http(s) 页面时会走 IndexedDB；面板上会写明当前用的是哪个后端，
//    打开排行榜一眼就能看到，这是最直接的验证方式。
const LDB = (() => {
  const NAME = 'naiwa_run', VER = 1, STORE = 'runs', LSKEY = 'naiwa_run_log';
  let kind = null, dbp = null;

  function openIDB(){
    if (dbp) return dbp;
    dbp = new Promise((res, rej) => {
      if (!self.indexedDB) return rej(new Error('no indexedDB'));
      let rq;
      try { rq = indexedDB.open(NAME, VER); }
      catch (e) { return rej(e); }                 // file:// 下会同步抛 SecurityError
      rq.onupgradeneeded = () => {
        const d = rq.result;
        if (!d.objectStoreNames.contains(STORE)){
          const os = d.createObjectStore(STORE, {keyPath:'id', autoIncrement:true});
          os.createIndex('score', 'score');
          os.createIndex('ts', 'ts');
        }
      };
      rq.onsuccess = () => res(rq.result);
      rq.onerror = () => rej(rq.error);
      rq.onblocked = () => rej(new Error('blocked'));
    });
    return dbp;
  }

  const idbTx = async (mode, fn) => {
    const d = await openIDB();
    return new Promise((res, rej) => {
      let out;
      let t;
      try { t = d.transaction(STORE, mode); } catch (e) { return rej(e); }
      const rq = fn(t.objectStore(STORE));
      if (rq) rq.onsuccess = () => { out = rq.result; };
      t.oncomplete = () => res(out);
      t.onerror = () => rej(t.error);
      t.onabort = () => rej(t.error);
    });
  };

  // ---- localStorage 后端（降级用）----
  const lsRead = () => { try { return JSON.parse(localStorage.getItem(LSKEY) || '[]'); } catch(e){ return []; } };
  const lsWrite = a => { try { localStorage.setItem(LSKEY, JSON.stringify(a)); } catch(e){} };

  // 探测一次，决定用哪个后端。
  // ⚠️ 这里有个坑：file:// 协议下 Chrome/Edge 的 indexedDB.open() 会
  //    **既不触发 onsuccess 也不触发 onerror**，请求就那么挂着 ——
  //    所以既不能靠 try/catch（它不抛），也不能干等（会卡死初始化）。
  //    做法：先按协议直接判定，再给探测加一个超时兜底，两条路都不会卡。
  async function init(){
    if (kind) return kind;
    if (location.protocol === 'file:'){ kind = 'localstorage'; return kind; }
    try {
      const probe = idbTx('readonly', os => os.count()).then(() => 'ok');
      const timeout = new Promise(r => setTimeout(() => r('timeout'), 1500));
      kind = (await Promise.race([probe, timeout])) === 'ok' ? 'indexeddb' : 'localstorage';
    } catch (e) { kind = 'localstorage'; }
    return kind;
  }

  return {
    init,
    get kind(){ return kind; },
    async add(rec){
      await init();
      if (kind === 'indexeddb') return idbTx('readwrite', os => os.add(rec));
      const a = lsRead();
      a.push({ ...rec, id: (a.length ? Math.max(...a.map(x=>x.id||0)) : 0) + 1 });
      lsWrite(a);
    },
    async all(){
      await init();
      if (kind === 'indexeddb') return (await idbTx('readonly', os => os.getAll())) || [];
      return lsRead();
    },
    async clear(){
      await init();
      if (kind === 'indexeddb') return idbTx('readwrite', os => os.clear());
      lsWrite([]);
    },
  };
})();

// ===================== 全网排行榜（TinyWebDB）=====================
// 这是「纯前端联机」：不写也不部署任何后端代码，页面直接 POST 到一个第三方
// key-value 存储。合成大奶蛙用的就是这套（接口同为 tinywebdb.appinventor.space）。
//
// 之所以可行，关键在它返回 `Access-Control-Allow-Origin: *`，
// 所以 GitHub Pages 甚至 file:// 都能直接读写。
//
// ⚠️ 安全边界（必须清楚，别当成有保障的服务）：
//   前端没有可信身份，user/secret 也必然能从源码里还原出来 —— 它防不住恶意用户。
//   所以这里靠的是【设计】而不是保密：
//     · 滚动时间窗：只展示最近 N 条提交，不是历史最高分榜 → 卡榜首没意义，
//       也天然避开并发写冲突（每人只写自己那条，全程没有任何 delete）
//     · 提交限频、分数范围校验
//     · 昵称清洗 + 全部 textContent 渲染（防 XSS）
//     · 网络失败只影响排行榜，绝不阻断游戏
//   真要防住作弊必须有服务端校验，那就不是纯静态了。
//
// 配置留空 = 纯本地模式：不联网、不报错、功能照旧。
const REMOTE = {
  url:      'https://tinywebdb.appinventor.space/api',
  user:     'shensheng',    // 在 https://tinywebdb.appinventor.space 申请的库
  secret:   'b78d47c5',     // 申请时拿到的【密钥】——注意不是注册时设的密码
  prefix:   'hnw_',  // 命名空间前缀，别蹭别人的
  // 允许提交 / 收录的来源白名单（`location.origin`）。
  //   · 留空数组 = 只挡 file:// 这类无来源的情况，任何 http(s) 站点都可提交
  //   · 填了内容 = 严格只认这些来源
  // ⚠️ GitHub Pages 的**项目页**共用 <user>.github.io 这个 origin，
  //    所以同一账号下的其它项目也在白名单内 —— 要更精确得连 pathname 一起判。
  origins: [
    'https://astenyx-git.github.io',   // 正式站点（仓库 Astenyx-Git/shenshengnaiwa 的 Pages）
    // ↓ 本地开发用。上线后可以删掉这两行，删掉后本地就也提交不了了。
    'http://localhost:8765',
    'http://127.0.0.1:8765',
  ],
  window:   20,      // 只展示最近 20 条提交
  minGap:   3000,    // 两次提交的最小间隔
  maxScore: 99999999,
};
// 写成函数而不是常量：配置可能被运行时改动，也让自检能临时打开开关
const remoteOn = () => !!(REMOTE.user && REMOTE.secret);
const NAME_KEY  = 'hnw.name';
const SCAN_MAX  = 60;   // 读取时最多校验多少条，防垃圾记录拖慢

// ---------- 记录格式规范与校验 ----------
// 目的：让「直接往库里写一条记录」这种做法大概率被读端剔除。
// 手段不是保密（源码公开，藏不住），而是【让记录必须自洽】：
//
// 本作的分数完全由「计分帧数」决定 —— 全代码只有一处 score 修改点：
//     score += 0.18 + speed * 0.002;   speed = min(16, 5 + score * 0.0011)
// 没有任何随机、没有道具加成。所以给定帧数 f，分数是唯一确定的。
// 于是「分数 ↔ 帧数」构成一条物理不变量：瞎填的分数必然对不上。
//
// 记录字段（v2）：
//   v  格式版本
//   n  昵称
//   s  分数（整数）
//   f  计分帧数（整数）
//   t  提交时间戳（ms，整数）
//   c  校验码（对上面字段 + 盐值算 FNV-1a）
//
// ⚠️ 这仍然是「提高作弊成本」，不是「防住作弊」：
//    盐值和公式都在源码里，有心人照着实现一遍就能造出合法记录。
//    它挡住的是【盲写】——只看到字段名、没读源码就想直接 POST 的人，
//    以及手抖改分数的人。真要防住必须有服务端校验。
const REC_VER   = 3;
// 这些来源一律不许读写全网榜：本地文件、被沙箱隔离的页面等。
// 用户明确要求「不需要 file 能联机」。
const BLOCKED_ORIGINS = ['file://', 'null', ''];

// 当前页面来源（拿不到时给空串，一律按不允许处理）
const currentOrigin = () => location.origin || '';

// 来源是否允许读写全网榜
function originAllowed(o){
  if (!o || BLOCKED_ORIGINS.indexOf(o) >= 0) return false;
  if (!/^https?:\/\//.test(o)) return false;              // 只认正经的 http(s)
  if (!REMOTE.origins.length) return true;                // 未配白名单：放行所有 http(s)
  return REMOTE.origins.indexOf(o) >= 0;
}
const originLabel = o => o || 'file://（本地文件）';
const MAX_PLAY_FRAMES = 180000;        // 约 50 分钟，再长不合常理
const MIN_REC_TS = 1704067200000;      // 2024-01-01，比这更早的戳视为异常
const MAX_TS_SKEW = 86400000;          // 允许比本机时间快 1 天（时钟误差）
const SALT = 'hnw-2026';               // 校验码盐值（源码可见，只挡盲写）

// 给定计分帧数，算出分数。必须与 step() 里的累加**逐位一致**，
// 否则合法记录会被误杀 —— 自检里有断言直接对比两者。
function scoreAfter(frames){
  let score = 0, speed = SPEED0;
  const n = Math.min(frames | 0, MAX_PLAY_FRAMES);
  for (let i = 0; i < n; i++){
    score += 0.18 + speed * 0.002;
    speed = Math.min(SPEED_MAX, SPEED0 + score * SPEEDUP_PER_SCORE);
  }
  return score;
}

function recChecksum(rec){
  const s = rec.v + '|' + rec.n + '|' + rec.s + '|' + rec.f + '|' + rec.t + '|' +
            rec.o + '|' + SALT;
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++){
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h.toString(16).padStart(8, '0');
}

function makeRecord(name, score, frames, ts, origin){
  const rec = { v: REC_VER, n: cleanName(name) || '匿名玩家',
                s: Math.floor(score), f: Math.floor(frames),
                t: Math.floor(ts || Date.now()),
                o: origin === undefined ? currentOrigin() : origin };
  rec.c = recChecksum(rec);
  return rec;
}

// 返回 null = 合法；否则返回拒绝原因（用于诊断显示）
function verifyRecord(raw){
  let rec;
  try { rec = JSON.parse(raw); } catch(e){ return '不是 JSON'; }
  if (!rec || typeof rec !== 'object' || Array.isArray(rec)) return '不是对象';
  if (rec.v !== REC_VER)                return '版本不符';
  if (typeof rec.n !== 'string' || !rec.n.trim()) return '昵称缺失';
  if (!Number.isInteger(rec.s) || rec.s < 1)      return '分数非法';
  if (!Number.isInteger(rec.f) || rec.f < 1 || rec.f > MAX_PLAY_FRAMES) return '帧数越界';
  if (!Number.isInteger(rec.t) || rec.t < MIN_REC_TS || rec.t > Date.now() + MAX_TS_SKEW)
    return '时间戳非法';
  if (typeof rec.o !== 'string')        return '缺来源';
  if (!originAllowed(rec.o))            return '来源不允许（' + originLabel(rec.o) + '）';
  if (typeof rec.c !== 'string')        return '缺校验码';
  if (recChecksum(rec) !== rec.c)       return '校验码不符';
  // 核心：分数必须能由帧数精确复现
  if (Math.floor(scoreAfter(rec.f)) !== rec.s) return '分数与帧数不自洽';
  return null;
}

const cleanName = raw => {
  let n = String(raw == null ? '' : raw).replace(/[\u0000-\u001f\u007f]/g, '').trim();
  return n.length > 12 ? n.slice(0, 12) : n;
};
const loadName = () => { try { return cleanName(localStorage.getItem(NAME_KEY) || ''); } catch(e){ return ''; } };
const saveName = n => { try { localStorage.setItem(NAME_KEY, cleanName(n)); } catch(e){} };
const myName   = () => loadName() || '匿名玩家';

let lastSubmitAt = 0, submitting = false;
// 自检 / 自动游玩模式下禁止向全网榜提交 ——
// 那两个模式里的 AI 会撞死几十次，否则会把一堆假分数灌进真实榜单。
let allowRemoteSubmit = true;

async function remotePost(params){
  const body = new URLSearchParams();
  body.set('user', REMOTE.user);
  body.set('secret', REMOTE.secret);
  for (const k in params) body.set(k, params[k]);
  const once = async () => {
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), 8000);   // 别让一个卡住的请求拖死界面
    try {
      const res = await fetch(REMOTE.url, { method:'POST', body, signal: ac.signal });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const text = (await res.text()).trim();
      if (!text) return {};
      try { return JSON.parse(text); }
      catch(e){ throw new Error('返回内容无法解析：' + text.slice(0, 40)); }
    } finally { clearTimeout(timer); }
  };
  try { return await once(); }
  catch (e) {
    await new Promise(r => setTimeout(r, 700));         // 偶发抖动重试一次
    return once();
  }
}

async function remoteSubmit(name, score, frames, origin){
  const o = origin === undefined ? currentOrigin() : origin;
  if (!remoteOn()) throw new Error('未配置全网榜单');
  if (!originAllowed(o)) throw new Error('当前来源不允许联机（' + originLabel(o) + '）');
  if (submitting) return false;
  if (Date.now() - lastSubmitAt < REMOTE.minGap) throw new Error('刚提交过啦，稍等一下');
  if (!(score > 0) || score > REMOTE.maxScore) throw new Error('分数不在合理范围');
  if (!Number.isInteger(frames) || frames < 1 || frames > MAX_PLAY_FRAMES)
    throw new Error('帧数不在合理范围');
  submitting = true;
  try {
    const rec = makeRecord(name, score, frames, undefined, o);
    const tag = REMOTE.prefix + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 6);
    await remotePost({ action:'update', tag, value: JSON.stringify(rec) });
    lastSubmitAt = Date.now();
    return true;
  } finally { submitting = false; }
}

async function remoteTop(origin){
  const o = origin === undefined ? currentOrigin() : origin;
  if (!remoteOn()) throw new Error('未配置全网榜单');
  if (!originAllowed(o)) throw new Error('当前来源不允许联机（' + originLabel(o) + '）');
  const bag = {};
  let no = 1;
  for (let page = 0; page < 2; page++){          // 扫两页足够覆盖最近 20 条
    const obj = await remotePost({ action:'search', no:String(no), count:'100',
                                   tag:REMOTE.prefix, type:'both' });
    for (const k in obj)
      if (k.indexOf(REMOTE.prefix) === 0 && typeof obj[k] === 'string') bag[k] = obj[k];
    no += 100;
  }
  // 先按提交时间倒序，再逐条校验，凑够 window 条合法记录就停。
  // 扫描条数封顶（SCAN_MAX）是为了防「灌一堆垃圾记录把读取拖慢」。
  const entries = [];
  for (const tag in bag){
    let rec = null, bad = false;
    try { rec = JSON.parse(bag[tag]); } catch(e){ bad = true; }
    entries.push({ tag, rec, bad, t: bad ? 0 : (Number(rec && rec.t) || 0) });
  }
  entries.sort((a,b) => b.t - a.t);

  const rows = [];
  let rejected = 0, scanned = 0;
  for (const e of entries){
    if (rows.length >= REMOTE.window || scanned >= SCAN_MAX) break;
    scanned++;
    if (e.bad){ rejected++; continue; }
    if (verifyRecord(bag[e.tag])){ rejected++; continue; }   // 不自洽 / 缺字段 / 校验码不符
    rows.push({ name: String(e.rec.n).slice(0, 16), score: e.rec.s,
                frames: e.rec.f, t: e.rec.t });
  }
  rows.sort((a,b) => b.score - a.score || b.t - a.t);   // 窗口内再按分数排
  return { rows, rejected, scanned, total: entries.length };
}

// ===================== 工具 =====================
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d', {alpha:false});
const stage = document.getElementById('stage');
const ov = document.getElementById('ov');
const scoreEl = document.getElementById('score');
const hiEl = document.getElementById('hi');
const goBtn = document.getElementById('go');
const spdEl = document.getElementById('spd');

function fitCanvas(){
  const r = stage.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio||1, 2);
  cv.width = Math.round(r.width * dpr);
  cv.height = Math.round(r.height * dpr);
  ctx.setTransform(r.width/W * dpr, 0, 0, r.height/H * dpr, 0, 0);
}
window.addEventListener('resize', fitCanvas);

const imgCache = {};
for (const k in IMG){
  const i = new Image();
  i.src = IMG[k];
  imgCache[k] = i;
}
function drawImg(name, x, y, w, h, flip=false){
  const i = imgCache[name]; if (!i || !i.complete) return;
  if (flip){ ctx.save(); ctx.translate(x+w, y); ctx.scale(-1,1); ctx.drawImage(i,0,0,w,h); ctx.restore(); }
  else ctx.drawImage(i, x, y, w, h);
}
function rand(a,b){ return a + Math.random()*(b-a); }
function pick(arr){ return arr[(Math.random()*arr.length)|0]; }

// ===================== 状态 =====================
let player, obs, clouds_, groundX, speed, score, hi, state, frames, playFrames, dayMode, nextNight, nightFlash;
let groundDeco = [];   // 地面装饰（草/奶滴），预先随机排布滚动
// 必须声明在 reset() 之前：reset() 在模块顶层就会被调用一次，
// 而 let 有暂时性死区，声明在后面会直接抛 ReferenceError 让整个脚本挂掉
let distSinceSpawn = 1e9;
let nextGap = 0;    // 下一次生成的间距（随机），在 reset / 每次生成后重新掷一次

function reset(){
  player = {x:PLAYER_X, y:GROUND_Y-90, w:74, h:90, vy:0, onGround:true,
    frame:0, frameT:0, duck:false, duckT:0, dead:false, hurtT:0};
  obs = []; clouds_ = [];
  groundX = 0; speed = SPEED0; score = 0; frames = 0; playFrames = 0; distSinceSpawn = 1e9;
  rollNextGap();
  dayMode = true; nextNight = NIGHT_AT[0]; nightFlash = 0;
  // 必须同步 CSS 类：reset 只把 dayMode 置回白天，但 stage 上的 .night 类不会自己消失。
  // 漏了这行的话，在夜里撞死再重开，背景会残留夜色，而 dayMode 说白天 ——
  // 远山/地面按白天色画在深色背景上，颜色对不上。
  stage.classList.toggle('night', !dayMode);
  // 地面装饰
  groundDeco = [];
  for (let i=0;i<60;i++) groundDeco.push({x: i*Math.floor(rand(40,90)) + rand(0,40), kind: Math.random()<.18?'grass':'dot'});
  state = 'ready';
}
reset();

// 读最高分
try{ hi = parseInt(localStorage.getItem('naiwa_run_hi')||'0',10) || 0; }catch(e){ hi=0; }
hiEl.textContent = hi;

// ===================== 障碍 =====================
// 生成节奏用「走过的距离」计量，跟障碍在屏幕上的位置解耦，
// 这样间距完全由 speed × JUMP_FRAMES 决定，速度快时自动变稀。
// 越障窗口：抛物线 y = v·t - g·t²/2，升到 rise 像素的进出时刻。
// 玩家底边 y+88 要高于障碍顶边 GROUND_Y-h+6，站立位是 GROUND_Y-90，故 rise = h-8。
// 所有跟「什么时候跳得过去」有关的判断（簇宽预算、AI 起跳时机）都从这一个函数取，
// 不要再手调帧数 —— 跳跃物理一改，写死的数字就会全线失效。
function clearanceWindow(rise){
  const v = Math.abs(JUMP_V), g = GRAVITY;
  const d = Math.sqrt(Math.max(0, v*v - 2*g*rise));
  return { t1: (v-d)/g, t2: (v+d)/g, width: 2*d/g };
}

// 一次跳跃能横跨的距离 + 落地后的反应余量 = 安全下限。低于它就必撞。
function gapMin(){ return speed * JUMP_FRAMES * 0.95 + 100; }

// 真正的间距是【随机】的，不能再是常量 —— 常量间距会让障碍以固定节拍到达，
// 玩家的最优解退化成「落地即起跳」的节拍器，手感很机械。
function rollNextGap(){
  const D = speed * JUMP_FRAMES;
  // 用「跳跃距离 + 若干帧的地面奔跑」来定间距。
  // 写成 D + k*speed 而不是 D*k：这样「落地后还能跑几帧」是恒定的，
  // 快慢速手感一致（早先用百分比时，速度一高地面时间就被压到只剩 4 帧）。
  const lo = D + 16 * speed;              // 落地后至少还能跑 16 帧
  const hi = D + 55 * speed;              // 最多 55 帧，留出纯奔跑的喘息
  // 18% 概率来个更长的空档，进一步打散节奏
  nextGap = (Math.random() < 0.18) ? rand(hi, hi + 40 * speed) : rand(lo, hi);
}

// 飞行类障碍（共用「见飞狗就蹲」的处理）
const FLY_TYPES = {fly:1, fly2:1};

// 生成统计，供自检断言「紧挨组合确实会出现」（必须声明在 spawnObs 之前）
const spawnStats = {tight:0, maxN:0, minInner:999, maxSpan:0, flyKinds:{fly:0, fly2:0},
                    single:0, clusters:0};

// 连排组合的出现概率：开局少、随分数阶梯式上升。
// 开局只有 10%，前 400 分维持在 22% 以下，让玩家先熟悉单只障碍的节奏。
function clusterChance(){
  const s = score;
  if (s < 150)  return 0.10;
  if (s < 400)  return 0.22;
  if (s < 800)  return 0.35;
  if (s < 1500) return 0.50;
  if (s < 2500) return 0.62;
  return 0.72;
}

function spawnObs(){
  const x0 = W + 40;
  const D  = speed * JUMP_FRAMES;
  // 连排簇的横向预算：整簇必须能被【一次跳跃】越过。
  // 连排簇最高 66px → 需要升高 58px；整簇必须在越障窗口内通过：
  //   S ≤ (窗口宽 - 4) * speed - 62
  // ⚠️ 早先我手写成 23*speed - 62，比真实上限小了一半：speed=5 时算出 53，
  //    而两只小怪至少要 64px → 每次都走「退化成单只」的兜底分支，
  //    结果低速段根本刷不出连排组合（自检里 tightPairs=0 才发现的）。
  const win = clearanceWindow(58);
  const budget = Math.max(64, Math.min(0.45 * D, (win.width - 4) * speed - 62));
  const r = Math.random();

  if (r < 0.20){
    // 飞狗两种，共用同一张 dog-howler 贴图（img 字段指定图片，type 区分判定）
    //   ① 低飞 y=360 h=50：可以跳过去，也可以蹲下躲
    //   ② 高飞（障碍盒 267~410）：跳不过去。
    //      跳跃顶点玩家盒 221~303，与 267~410 重叠
    //      → 无论怎么跳都躲不掉，唯一解是蹲下（蹲姿 416~458 从底边 410 下钻过）。
    //      顶边 267 不是随便定的：必须 < 跳跃顶点时的玩家盒底边 = 458 - 跳跃顶点升高。
    //      **改跳跃参数后必须重算这个值**，否则一跳就能蹭过去。
    // 两者的底边都是 410，所以「蹲下都能过」；区别在顶边，也就是能不能跳过去。
    if (Math.random() < 0.5){
      obs.push({type:'fly', img:'fly', x:x0, y:GROUND_Y-100, w:78, h:50, kind:'fly'});
      spawnStats.flyKinds.fly++;
    } else {
      obs.push({type:'fly2', img:'fly', x:x0, y:GROUND_Y-199, w:173, h:149, kind:'fly2'});
      spawnStats.flyKinds.fly2++;
    }
    return;
  }

  // 连排组合的出现概率随分数【阶梯式】上升 —— 开局只偶尔来一对，
  // 不能一上来就满屏连排（用户反馈「两个连着的障碍偏多」）。
  if (Math.random() > clusterChance()){
    // 单只（含偶尔的大奶瓶）
    if (Math.random() < 0.3){
      // 最高的单只障碍：92px。再高就只有顶点附近几帧能过，等于变相必死
      obs.push({type:'ground', x:x0, y:GROUND_Y-92, w:54, h:92, kind:'ob6'});
    } else {
      // 高度分档：矮的(40)轻点一跳就过、中的(62)、高的(70)，
      // 需要的按键时长不同，节奏就不会像节拍器
      const r2 = Math.random();
      const h1 = r2 < 0.28 ? 40 : (r2 < 0.66 ? 62 : 70);
      obs.push({type:'ground', x:x0, y:GROUND_Y-h1, w:56+rand(0,18), h:h1,
        kind: pick(['ob1','ob2','ob3','ob4','ob5'])});
    }
    spawnStats.single++;
    return;
  }

  // 连排组：速度越快组越大，但总宽受 budget 限制，保证一跳过得去
  // 连排簇：2~3 只【紧挨着】的障碍，内部只隔 8~20px —— 必须一次跳过去，
  // 落地再跳第二下是来不及的。这是和「单只障碍」完全不同的题型。
  const kinds = ['ob1','ob2','ob3','ob4','ob5'];
  const n = (speed > 13 && Math.random() < 0.45) ? 3 : 2;

  // 内部间距先定下来，剩下的预算才分给各只的宽度
  const innerGaps = [];
  let gapSum = 0;
  for (let i=0;i<n-1;i++){ const g = 8 + rand(0,12); innerGaps.push(g); gapSum += g; }

  const wAvail = budget - gapSum;
  if (wAvail < n * 26){          // 每只至少 26px 才看得出是独立障碍
    // 预算太窄塞不下 n 只，退化成单只（低速时可能发生，绝不能硬塞成必死组合）
    const h1 = Math.random()<.5 ? 62 : 70;
    obs.push({type:'ground', x:x0, y:GROUND_Y-h1, w:48, h:h1, kind:pick(kinds)});
    return;
  }

  const wEach = Math.min(56, Math.max(26, wAvail / n));
  let cx = x0;
  for (let i=0;i<n;i++){
    const w1 = Math.round(wEach - rand(0, 8));
    const h1 = pick([56, 60, 66]);
    obs.push({type:'ground', x:cx, y:GROUND_Y-h1, w:w1, h:h1, kind:pick(kinds)});
    cx += w1 + (innerGaps[i] || 0);
  }
  spawnStats.tight++;                       // 统计：生成了几次「紧挨组合」
  spawnStats.clusters++;
  spawnStats.maxN = Math.max(spawnStats.maxN, n);
  spawnStats.minInner = Math.min(spawnStats.minInner, Math.min(...innerGaps));
  spawnStats.maxSpan = Math.max(spawnStats.maxSpan, cx - x0);
}

// ===================== 输入 =====================
let keyJump=false, keyDown=false;
window.addEventListener('keydown', e=>{
  // 排行榜打开时吞掉按键，只留 Esc 关闭（否则空格会把游戏开起来）
  if (!boardEl.hidden){
    if (e.code === 'Escape') closeBoard();
    if (e.code === 'Space' || e.code === 'ArrowUp' || e.code === 'ArrowDown') e.preventDefault();
    return;
  }
  if (e.code==='Space' || e.code==='ArrowUp' || e.code==='KeyW'){ keyJump=true; e.preventDefault(); }
  if (e.code==='ArrowDown' || e.code==='KeyS'){ keyDown=true; e.preventDefault(); }
  if (state==='ready' || state==='over') startRun();   // startRun 内部负责 reset
});
window.addEventListener('keyup', e=>{
  if (e.code==='Space' || e.code==='ArrowUp' || e.code==='KeyW') keyJump=false;
  if (e.code==='ArrowDown' || e.code==='KeyS') keyDown=false;
});

// 触屏：点屏跳；从屏中部向下划 = 下蹲
let touchStartY = null, touchStartT = 0, touchDucking = false;
stage.addEventListener('pointerdown', e=>{
  e.preventDefault();
  if (state==='ready' || state==='over'){ startRun(); return; }
  touchStartY = e.clientY; touchStartT = performance.now();
  keyJump = true;     // 按下立即给一次起跳
  touchDucking = false;
});
stage.addEventListener('pointermove', e=>{
  if (touchStartY==null) return;
  if (e.clientY - touchStartY > 30) touchDucking = true;
});
stage.addEventListener('pointerup', e=>{
  keyJump = false; touchStartY = null;
  if (touchDucking) touchDucking=false;
});
goBtn.addEventListener('click', e=>{ e.stopPropagation(); startRun(); });

function startRun(){
  if (state==='playing') return;
  if (state==='over'){ reset(); restoreTitle(); }
  state = 'playing';
  ov.style.display = 'none';
}

// ===================== 主循环 =====================
function step(){
  frames++;

  if (state==='playing'){
    score += 0.18 + speed*0.002;
    playFrames++;          // 计分帧数：分数完全由它决定（见 scoreAfter），用于校验记录真伪
    scoreEl.textContent = Math.floor(score);

    // 速度
    speed = Math.min(SPEED_MAX, SPEED0 + score * SPEEDUP_PER_SCORE);
    // 右下角实时速度（每 12 帧刷一次，避免每帧改 DOM）
    if (spdEl && frames % 12 === 0) spdEl.textContent = speed.toFixed(1);

    // 主角
    const p = player;
    if (p.dead){
      p.hurtT++; p.vy += GRAVITY*0.5; p.y += p.vy;
      if (p.y > GROUND_Y + 50){ state = 'over'; onGameOver(); }
    } else {
      // 跳跃：固定高度，没有长按变高（原版小恐龙也是固定高度）
      if (p.onGround){
        if (keyJump){
          p.vy = JUMP_V; p.onGround = false;
          sfx.jump();
        } else {
          p.duck = !!keyDown || touchDucking;
          // 蹲下是「瞬间缩身」，不是自由落体掉下去 —— 必须直接吸附到蹲姿高度，
          // 否则按下蹲后主角还会以重力慢慢下沉好几帧，判定盒也跟着乱飘
          if (p.duck){ p.y = GROUND_Y - DUCK_H; p.vy = 0; }
        }
      } else {
        p.duck = false;
      }
      p.vy += GRAVITY; p.y += p.vy;
      const restY = GROUND_Y - (p.duck ? DUCK_H : p.h);
      if (p.y >= restY){
        p.y = restY; p.vy = 0; p.onGround = true;
        // 注意：这里【不能】顺手把 p.duck 清成 false。
        // 蹲姿每帧都会落到这里，清掉的话按下蹲键后 duck 活不过一帧就失效了。
        // duck 的取值来源是每帧开头读按键，落地的清空由 airborne 分支负责。
      }
      // 帧动画
      p.frameT++; if (p.frameT >= 6){ p.frameT=0; p.frame = (p.frame+1)%3; }
    }

    // 生成障碍：按「走过的距离」计时，间距随机（下限由跳跃距离决定）
    distSinceSpawn += speed;
    if (distSinceSpawn >= nextGap){ spawnObs(); distSinceSpawn = 0; rollNextGap(); }

    // 障碍移动
    for (const o of obs) o.x -= speed;
    obs = obs.filter(o => o.x > -200);

    // 碰撞
    if (!p.dead){
      const px = p.x + 6, py = p.y + 6, pw = p.w - 12, ph = (p.duck ? DUCK_H : p.h) - 8;
      for (const oo of obs){
        const ox = oo.x + 6, oy = oo.y + 6, ow = oo.w - 12, oh = oo.h - 6;
        if (px < ox+ow && px+pw > ox && py < oy+oh && py+ph > oy){
          p.dead = true; p.vy = -8; p.hurtT = 0;
          sfx.hurt();
        }
      }
    }

    // 云
    if (Math.random() < 0.012) clouds_.push({x: W+30, y: 60 + Math.random()*180, s: 0.4 + Math.random()*0.6});
    for (const c of clouds_) c.x -= speed * c.s * 0.5;
    clouds_ = clouds_.filter(c => c.x > -120);

    // 地面
    groundX = (groundX + speed) % 240;

    // 昼夜
    if (score >= nextNight){
      dayMode = !dayMode; nightFlash = 12;
      nextNight = score + 700 + Math.random()*200;
      stage.classList.toggle('night', !dayMode);
      if (!dayMode) sfx.night();
    }
    if (nightFlash>0) nightFlash--;
  }

  draw();
}
function loop(){ step(); requestAnimationFrame(loop); }

function draw(){
  // 天空：canvas 是 alpha:false 的不透明画布，必须每帧用【不透明】色铺满，
  // 否则上一帧的精灵会残留成拖影（用 rgba(..,0) 半透明填充等于没擦除）。
  const grd = ctx.createLinearGradient(0,0,0,H);
  if (dayMode){
    grd.addColorStop(0,   '#fff7df');
    grd.addColorStop(0.6, '#f4ecd8');
    grd.addColorStop(1,   '#e9dcb8');
  } else {
    grd.addColorStop(0,   '#1f2540');
    grd.addColorStop(0.6, '#14182a');
    grd.addColorStop(1,   '#0c0f1a');
  }
  ctx.fillStyle = grd; ctx.fillRect(0,0,W,H);

  // 云
  for (const c of clouds_){
    drawImg('cloud', c.x, c.y, 50*c.s, 50*c.s, true);
  }

  // 远景山
  ctx.fillStyle = dayMode?'#dcc9a0':'#262d4a';
  ctx.beginPath(); ctx.moveTo(0, 420);
  for (let x=0; x<=W; x+=24){
    const h = 30 + Math.sin((x+frames*0.4)*0.02)*14 + Math.cos(x*0.05)*8;
    ctx.lineTo(x, 420 - h);
  }
  ctx.lineTo(W, 420); ctx.closePath(); ctx.fill();

  // 地面
  ctx.fillStyle = dayMode?'#cbb887':'#3a3a55';
  ctx.fillRect(0, GROUND_Y, W, H-GROUND_Y);
  // 地面条纹
  ctx.fillStyle = dayMode?'#b8a36a':'#2d2d44';
  const gx = -groundX;
  for (let x=gx; x<W; x+=24) ctx.fillRect(x, GROUND_Y+6, 12, 3);
  // 地面装饰
  for (const d of groundDeco){
    const sx = ((d.x - groundX*0.8) % (W+200) + W+200) % (W+200) - 100;
    if (d.kind==='grass'){
      ctx.fillStyle = dayMode?'#a0924d':'#4a4a6a';
      ctx.fillRect(sx, GROUND_Y-6, 3, 8); ctx.fillRect(sx+5, GROUND_Y-4, 2, 6);
    } else {
      ctx.fillStyle = dayMode?'#bba672':'#44445e';
      ctx.fillRect(sx, GROUND_Y+18, 4, 2);
    }
  }

  // 障碍（img 优先于 kind：高飞和低飞共用同一张贴图）
  for (const oo of obs) drawImg(oo.img || oo.kind, oo.x, oo.y, oo.w, oo.h, !!FLY_TYPES[oo.type]);

  // 主角
  const p = player;
  let key = 'run0';
  if (p.dead) key = 'hurt';
  else if (!p.onGround) key = 'jump';
  else if (p.duck) key = 'duck';
  else key = ['run0','run1','run2'][p.frame];
  drawImg(key, p.x, p.y, p.w, (p.duck && p.onGround) ? DUCK_H : p.h, false);

  // 分数提示
  if (state==='ready'){
    ctx.fillStyle = dayMode?'#7a6a45':'#a0a8c8';
    ctx.font = '600 16px ui-monospace,monospace';
    ctx.textAlign='center'; ctx.fillText('点击屏幕 / 按空格 开始狂奔 🐤', W/2, 300);
  }
}

// 只改文字节点，不动 h1 里的 <img>（否则重开时图标会丢）
const titleTextEl = document.getElementById('titleText');
const titleSubEl  = document.getElementById('titleSub');
const keysEl  = ov.querySelector('.keys');

// ---------- 排行榜面板 ----------
const boardEl     = document.getElementById('board');
const boardBtn    = document.getElementById('boardBtn');
const boardListEl = document.getElementById('boardList');
const boardSubEl  = document.getElementById('boardSub');

const nickRowEl = document.getElementById('nickRow');
const nickInput = document.getElementById('nickInput');
const boardMsgEl = document.getElementById('boardMsg');
let boardTab = 'local', lastRemoteMsg = '';

const fmtDur = f => {
  if (!f || f < 1) return '—';
  const sec = Math.round(f / 60);
  return Math.floor(sec / 60) + ':' + String(sec % 60).padStart(2, '0');
};
const fmtTs = ts => {
  const d = new Date(ts), p = n => String(n).padStart(2, '0');
  return p(d.getMonth()+1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
};
function setMsg(text, kind){
  boardMsgEl.textContent = text || '';
  boardMsgEl.className = 'boardmsg' + (kind ? ' ' + kind : '');
}

// ⚠️ 全部用 createElement + textContent —— 昵称是用户输入，拼 innerHTML 就是 XSS 洞
function renderRows(rows, emptyText){
  boardListEl.textContent = '';
  if (!rows.length){
    const li = document.createElement('li');
    li.className = 'empty';
    li.textContent = emptyText;
    boardListEl.appendChild(li);
    return;
  }
  rows.forEach((r, i) => {
    const li = document.createElement('li');
    if (i === 0) li.className = 'top1';
    const rk = document.createElement('span'); rk.className = 'rk'; rk.textContent = String(i + 1);
    const sc = document.createElement('span'); sc.className = 'sc'; sc.textContent = String(r.score);
    li.appendChild(rk); li.appendChild(sc);
    if (r.name){
      const nm = document.createElement('span'); nm.className = 'nm'; nm.textContent = r.name;
      li.appendChild(nm);
    }
    if (r.frames){
      const du = document.createElement('span'); du.className = 'dur'; du.textContent = fmtDur(r.frames);
      li.appendChild(du);
    }
    const dt = document.createElement('span'); dt.className = 'dt';
    const ts = r.ts || r.t || 0;
    dt.textContent = ts ? fmtTs(ts) : '—';
    li.appendChild(dt);
    boardListEl.appendChild(li);
  });
}

async function showTab(tab){
  boardTab = tab;
  document.querySelectorAll('.board .tab').forEach(b =>
    b.classList.toggle('is-on', b.dataset.tab === tab));
  nickRowEl.hidden = (tab !== 'remote') || !remoteOn() || !originAllowed(currentOrigin());

  if (tab === 'local'){
    let rows = [];
    try { rows = await LDB.all(); } catch(e){}
    rows.sort((a,b) => b.score - a.score || b.ts - a.ts);
    boardSubEl.textContent = '存在本机浏览器（' + (LDB.kind === 'indexeddb' ? 'IndexedDB' : 'localStorage')
      + '）· 共 ' + rows.length + ' 条 · 换设备不同步';
    renderRows(rows.slice(0, 10), '还没有记录，先跑一局吧');
    setMsg('');
    return;
  }

  if (!remoteOn()){
    boardSubEl.textContent = '未配置';
    renderRows([], '全网榜单未配置');
    setMsg('需要先填 REMOTE.user / REMOTE.secret（见 README）', 'bad');
    return;
  }

  if (!originAllowed(currentOrigin())){
    boardSubEl.textContent = '当前来源不可联机';
    renderRows([], '只有部署后的正式域名可以联机');
    setMsg('当前来源：' + originLabel(currentOrigin()) + ' —— 本地文件不支持联机', 'bad');
    return;
  }

  boardSubEl.textContent = '最近 ' + REMOTE.window + ' 次提交 · 全网共享';
  renderRows([], '正在读取…');
  setMsg(lastRemoteMsg || '正在读取…');
  try {
    const res = await remoteTop();
    renderRows(res.rows, '最近还没有人提交，快去玩一局');
    boardSubEl.textContent = '最近 ' + REMOTE.window + ' 次提交 · 全网共享'
      + (res.rejected ? ' · 已剔除 ' + res.rejected + ' 条不自洽记录' : '');
    if (!lastRemoteMsg) setMsg('已读取 ' + res.rows.length + ' 条合法记录', 'ok');
  } catch(e){
    renderRows([], '读取失败');
    setMsg('读取失败：' + ((e && e.message) || e), 'bad');
  }
}

function openBoard(){ boardEl.hidden = false; showTab(boardTab); }
function closeBoard(){ boardEl.hidden = true; }

// ⚠️ 按钮的 pointerdown 必须拦住，不能冒泡到 stage：
//   stage 上的 pointerdown 会 startRun()（顺手把游戏开起来），
//   而且它调了 preventDefault，在真实浏览器里会连带抑制随后的 click ——
//   表现就是「点了排行榜按钮毫无反应」。自检里有 boardBtnNoStart 断言守着。
[goBtn, boardBtn].forEach(el =>
  el.addEventListener('pointerdown', e => e.stopPropagation()));

boardBtn.addEventListener('click', e => { e.stopPropagation(); openBoard(); });
document.getElementById('boardClose').addEventListener('click', e => { e.stopPropagation(); closeBoard(); });
document.querySelectorAll('.board .tab').forEach(b =>
  b.addEventListener('click', e => { e.stopPropagation(); showTab(b.dataset.tab); }));
document.getElementById('boardRefresh').addEventListener('click', e => {
  e.stopPropagation(); lastRemoteMsg = ''; showTab('remote');
});
document.getElementById('boardClear').addEventListener('click', async e => {
  e.stopPropagation();
  if (!confirm('确定清空本机的全部成绩记录？此操作不可撤销。')) return;
  await LDB.clear();
  showTab('local');
});
nickInput.addEventListener('change', () => { saveName(nickInput.value); nickInput.value = loadName(); });
nickInput.addEventListener('blur',   () => { saveName(nickInput.value); nickInput.value = loadName(); });
// 面板内的点击不要冒泡到 stage（否则会触发跳跃 / 开始游戏）
boardEl.addEventListener('pointerdown', e => e.stopPropagation());

function onGameOver(){
  const final = Math.floor(score);
  const isBest = final > hi;
  if (isBest){ hi = final; hiEl.textContent = hi; try{localStorage.setItem('naiwa_run_hi',hi)}catch(e){} }
  ov.style.display = 'flex';
  titleTextEl.textContent = isBest ? '新纪录！' : '撞上了';
  titleSubEl.textContent  = '本局 ' + final + ' 分 · 最高 ' + hi + ' 分';
  // 存进本地数据库（失败也不影响玩，只是没记录）
  const who = myName();
  LDB.add({score: final, name: who, ts: Date.now(), dur: frames, spd: +speed.toFixed(1)}).catch(()=>{});
  // 配了全网榜就顺带提交一份。未配置 / 网络失败都只写提示，绝不阻断游戏。
  lastRemoteMsg = '';
  if (remoteOn() && allowRemoteSubmit && final > 0 && !originAllowed(currentOrigin())){
    lastRemoteMsg = '本地文件不支持联机，本局只存本机';
  } else if (remoteOn() && allowRemoteSubmit && final > 0){
    lastRemoteMsg = '正在提交到全网榜…';
    remoteSubmit(who, final, playFrames)
      .then(() => { lastRemoteMsg = '已上榜 ✓ ' + who + ' · ' + final + ' 分'; })
      .catch(err => { lastRemoteMsg = '提交失败：' + ((err && err.message) || err); });
  }
  goBtn.textContent = '再 来 一 局';
  keysEl.style.display = 'none';
}

// 重开时把文案恢复成初始状态
function restoreTitle(){
  titleTextEl.textContent = '神圣奶蛙';
  titleSubEl.textContent  = 'Naiwa Run';
  goBtn.textContent = '开 始 狂 奔';
  keysEl.style.display = 'flex';
}

// ===================== 音效（WebAudio 实时合成） =====================
const sfx = (()=>{
  let ac = null;
  function env(){
    if (!ac){ try{ ac = new (window.AudioContext||window.webkitAudioContext)(); }catch(e){} }
    if (ac && ac.state==='suspended') ac.resume();
  }
  function blip(freq, dur, type='square', vol=0.06){
    if (!ac) return;
    const t = ac.currentTime;
    const osc = ac.createOscillator(); const g = ac.createGain();
    osc.type = type; osc.frequency.setValueAtTime(freq, t);
    g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.0001, t+dur);
    osc.connect(g); g.connect(ac.destination);
    osc.start(t); osc.stop(t+dur);
  }
  return {
    init: env,
    jump(){ env(); blip(660, 0.08, 'square', 0.05); setTimeout(()=>blip(990,0.06,'square',0.04), 50); },
    hurt(){ env(); blip(180,0.25,'sawtooth',0.08); blip(120,0.4,'square',0.07); },
    night(){ env(); blip(440,0.1,'triangle',0.04); setTimeout(()=>blip(330,0.1,'triangle',0.04),110);
            setTimeout(()=>blip(220,0.2,'triangle',0.04),220); },
  };
})();

// 第一次交互后再开 audio（避免无交互警告）
window.addEventListener('pointerdown', ()=>sfx.init(), {once:true});
window.addEventListener('keydown', ()=>sfx.init(), {once:true});

fitCanvas();
requestAnimationFrame(loop);

// 调试用：?auto=1 直接开跑，?auto=1&t=500 跑 500 帧（无头截图用）
// ?selftest=1 跑渲染自检并把结果写进 <pre id="selftest">，配合 headless --dump-dom 读取
const QS = new URLSearchParams(location.search);
// 自检 / 自动游玩都是机器人在玩，绝不能把它们的分数写进真实榜单
if (QS.get('selftest') || QS.get('auto')) allowRemoteSubmit = false;
const _scale = () => cv.width / W;   // 逻辑坐标 → 设备像素

function _px(lx, ly, lw, lh){
  const s = _scale();
  return ctx.getImageData(Math.round(lx*s), Math.round(ly*s),
                          Math.max(1,Math.round(lw*s)), Math.max(1,Math.round(lh*s))).data;
}
function _uniq(d){
  const set = new Set();
  for (let i=0;i<d.length;i+=4) set.add(d[i]+','+d[i+1]+','+d[i+2]);
  return set;
}

function runSelfTest(){
  const R = [];
  let pre = document.getElementById('selftest');
  if (!pre){ pre = document.createElement('pre'); pre.id='selftest'; document.body.appendChild(pre); }
  pre.textContent = 'SELFTEST start';
  // 每加一条立刻写进 DOM：即使后面某步卡住/抛错，也能看到已完成的部分
  const add = (k,v)=>{ R.push(k+'='+v); pre.textContent = 'SELFTEST ' + R.join(' | '); };
  try {
    // 1) 素材是否全部解码完成
    let loaded=0, total=0;
    for (const k in imgCache){ total++; if (imgCache[k].complete && imgCache[k].naturalWidth>0) loaded++; }
    add('imgs', loaded+'/'+total);

    // 1b) 开始页图标（神圣奶蛙）真的加载出来了
    const logoEl = document.querySelector('.overlay h1 .logo');
    add('logoLoaded', (logoEl && logoEl.complete && logoEl.naturalWidth > 0)
        ? 'yes ' + logoEl.naturalWidth + 'x' + logoEl.naturalHeight : 'NO');
    add('logoAlt', logoEl ? logoEl.alt : '?');

    // 1b2) 游戏名在两处定义（HTML 初始文案 + restoreTitle 里的常量），
    //      很容易改了一处忘了另一处 → 重开时名字会变回去。断言守住一致性。
    const titleInit = titleTextEl.textContent, subInit = titleSubEl.textContent;
    restoreTitle();
    add('titleOk', (titleInit === '神圣奶蛙' && titleTextEl.textContent === titleInit)
        ? 'yes 「' + titleInit + '」' : 'NO 初始=' + titleInit + ' 重开后=' + titleTextEl.textContent);
    add('subtitle', JSON.stringify(subInit) +
        (subInit === titleSubEl.textContent ? ' 一致' : ' 重开后=' + JSON.stringify(titleSubEl.textContent)));
    add('credit', JSON.stringify(document.querySelector('.credit').textContent.trim()));

    // 1c) 键位映射：界面上写的每个键都必须真的触发对应动作。
    //     （文案和实现脱节是很容易犯的错 —— 比如漏写 W/S、或改了绑定没改说明）
    function keyEffect(code){
      reset(); startRun(); obs = [];
      keyJump = false; keyDown = false;
      window.dispatchEvent(new KeyboardEvent('keydown', {code}));
      step(); step();
      const res = !player.onGround ? 'jump' : (player.duck ? 'duck' : 'none');
      window.dispatchEvent(new KeyboardEvent('keyup', {code}));
      keyJump = false; keyDown = false;
      return res;
    }
    add('keyMap', ['Space','ArrowUp','KeyW','ArrowDown','KeyS']
      .map(c => c + '=' + keyEffect(c)).join(' '));

    startRun();
    add('speed0', SPEED0 + ' px/frame (' + (SPEED0*60) + ' px/s)');
    // 第一个障碍从右边缘走到角色面前需要多久
    add('firstObstacleEta', ((W+40) - (player.x+player.w)) / SPEED0 / 60 + ' s');
    for (let i=0;i<300;i++) step();
    add('state', state);
    add('score', Math.floor(score));
    add('obs', obs.length);
    add('speed', speed.toFixed(2));

    // 2) 天空带：应只有 1~3 种颜色（纯背景 + 可能一朵云），出现很多种 = 有拖影
    const sky = _uniq(_px(0, 10, W, 60));
    add('skyColors', sky.size);

    // 3) 地面带：主色（地面填充）占比应 >85%。
    //    注意【不能】用「颜色种数」当指标：装饰点用小数坐标 fillRect 会产生
    //    几百种抗锯齿边缘色（每种仅 1~2 像素），颜色种数会虚高到 700+ 但完全正常。
    const gndRaw = _px(0, GROUND_Y+4, W, 30);
    const gcnt = new Map();
    for (let i=0;i<gndRaw.length;i+=4){
      const k = gndRaw[i]+','+gndRaw[i+1]+','+gndRaw[i+2];
      gcnt.set(k,(gcnt.get(k)||0)+1);
    }
    let gmax = 0; for (const v of gcnt.values()) gmax = Math.max(gmax, v);
    add('groundFillShare', (100*gmax/(gndRaw.length/4)).toFixed(1) + '%');

    // 4) 拖影检测（正确的对照组）：
    //    a. 清场后先画一帧「无角色」的干净背景 clean
    //    b. 角色放在 A 再画一帧 withP   → withP 与 clean 的差异 = 角色确实画出来了
    //    c. 角色挪到 B 再画一帧 afterP  → afterP 必须与 clean 完全一致，否则就是拖影
    //    （不能拿横向另一块区域当参照：远山是起伏的，同高度不同 x 本来就不一样）
    obs = []; clouds_ = [];
    player.dead = false; player.duck = false; player.onGround = true;
    player.y = GROUND_Y - player.h;
    const REG = [200, GROUND_Y-player.h, player.w, player.h];

    player.x = -9999; draw();
    const clean = _px(...REG);

    player.x = 200; draw();
    const withP = _px(...REG);

    player.x = 760; draw();
    const afterP = _px(...REG);

    let drawn = 0, ghost = 0;
    for (let i=0;i<clean.length;i+=4){
      if (Math.abs(withP[i]-clean[i])  > 6) drawn++;
      if (Math.abs(afterP[i]-clean[i]) > 6) ghost++;
    }
    add('playerDrawnPixels', drawn);   // 应远大于 0
    add('ghostPixels', ghost);         // 必须为 0

    // 5) 主角脚底应贴地
    add('playerBottom', (player.y + player.h) + ' vs ground ' + GROUND_Y);

    // 6) 跳跃：按住跳应离地，且最终能落回地面
    reset(); startRun(); obs = [];
    keyJump = true;
    let peak = GROUND_Y, airborne = 0;
    for (let i=0;i<40;i++){ step(); if (!player.onGround){ airborne++; peak = Math.min(peak, player.y); } }
    add('jumpAirborneFrames', airborne);
    add('jumpPeakRise', Math.round(GROUND_Y - player.h - peak));  // >0 说明真跳起来了
    keyJump = false;
    let landed = 0;
    for (let i=0;i<200;i++){ step(); if (player.onGround){ landed++; break; } }
    add('jumpLanded', landed ? 'yes' : 'NO');

    // 6b) 轻点跳（只按 1 帧）：高度应 ≈130px，且不能飞出画面顶部
    reset(); startRun(); obs = [];
    keyJump = true; step(); keyJump = false;
    let peak2 = GROUND_Y, topY = GROUND_Y;
    for (let i=0;i<200;i++){ step(); topY = Math.min(topY, player.y); if (player.onGround && i>8) break; }
    add('tapJumpRise', Math.round(GROUND_Y - player.h - topY));
    add('tapJumpTopY', Math.round(topY));            // 必须 > 0，否则是飞出屏幕了
    add('jumpTopY', Math.round(peak));                // 顶点不能飞出屏幕顶部

    // 6c) 飞狗判定：站着必撞、蹲下必须能过
    function flyHit(ducking){
      reset(); startRun(); obs = [];
      keyDown = ducking;
      for (let i=0;i<3;i++) step();                  // 先进入下蹲状态
      obs = [{type:'fly', x:player.x+6, y:GROUND_Y-100, w:78, h:50, kind:'fly', dead:false}];
      step();
      const p = player, o = obs[0];
      const box = 'duck=' + p.duck +
                  ' pY=' + Math.round(p.y) + ' pTop=' + Math.round(p.y+6) +
                  ' pBot=' + Math.round(p.y+6+((p.duck?p.h-24:p.h)-8)) +
                  ' oTop=' + Math.round(o.y+6) + ' oBot=' + Math.round(o.y+6+(o.h-6));
      keyDown = false;
      return {dead: p.dead, box: box};
    }
    const fs = flyHit(false), fd = flyHit(true);
    add('flyHitsStanding', fs.dead ? 'yes' : 'NO');
    add('  boxStanding', fs.box);
    add('flyMissesDucking', fd.dead ? 'NO' : 'yes');   // 期望不撞 → 输出 yes
    add('  boxDucking', fd.box);

    // 6d) 真实模拟按键跑一次跳跃，量出顶点与滞空。
    // 历史教训：断言曾经把顶点硬编码成一个坐标，结果漏判（玩家按住不放时
    // 顶点完全不同）。现在一律【真跑一遍物理】，不再填数字。
    function measureJump(){
      reset(); startRun(); obs = [];
      keyJump = true; keyDown = false;      // 按住不放（跳跃已无长按变高，按多久都一样）
      let peak = player.y, air = 0;
      for (let i=0;i<200;i++){
        obs = [];                            // 清掉自动生成的障碍，只测跳跃轨迹
        step();
        peak = Math.min(peak, player.y);
        if (!player.onGround) air++;
        if (i > 4 && player.onGround) break;
      }
      keyJump = false;
      return {peak, air};
    }
    const jm = measureJump();
    add('jumpRisePx', Math.round(GROUND_Y-player.h-jm.peak));
    add('jumpAirtimeFrames', jm.air + ' (' + (jm.air/60).toFixed(2) + 's)');
    // JUMP_FRAMES（算间距用）必须 ≥ 实际滞空，否则会「落地正好砸在下一个障碍上」
    add('JUMP_FRAMES_ok', JUMP_FRAMES >= jm.air ? 'yes' : 'NO');
    // 水平跳跃距离 = 滞空帧数 × 滚动速度（角色 x 固定，世界在滚）
    add('jumpDistPx', Math.round(jm.air*SPEED0) + 'px@起速 ~ ' +
                      Math.round(jm.air*SPEED_MAX) + 'px@满速');
    // 固定高度：按住不放和只点一下必须完全一致
    function measureTap(){
      reset(); startRun(); obs = [];
      keyJump = true; keyDown = false;
      let peak = player.y;
      for (let i=0;i<200;i++){
        obs = []; step();
        peak = Math.min(peak, player.y);
        if (i === 0) keyJump = false;        // 只按第一帧
        if (i > 4 && player.onGround) break;
      }
      keyJump = false;
      return peak;
    }
    add('fixedHeightOk', Math.abs(measureTap() - jm.peak) < 0.01 ? 'yes' : 'NO');

    // 把玩家放到指定状态/高度，正面撞上障碍，看判定
    function flyHitAt(tall, y, ducking){
      reset(); startRun(); obs = [];
      keyJump = false; keyDown = !!ducking;
      if (ducking){
        // 蹲姿必须在 onGround 上才会保持；把 onGround 设 false 会直接被 airborne 分支清掉
        player.onGround = true;
        for (let i=0;i<2;i++){ obs = []; step(); }
      } else {
        player.onGround = false; player.vy = 0; player.y = y;
      }
      obs = [ tall
        ? {type:'fly2', img:'fly', x:player.x+6, y:GROUND_Y-199, w:173, h:149, kind:'fly2'}
        : {type:'fly',  img:'fly', x:player.x+6, y:GROUND_Y-100, w:78,  h:50,  kind:'fly'} ];
      step();
      const dead = player.dead;
      keyDown = false;
      return dead;
    }
    add('tallFlyHitsStanding',  flyHitAt(true, GROUND_Y-player.h, false) ? 'yes' : 'NO');
    add('tallFlyHitsJumpApex',  flyHitAt(true, jm.peak, false) ? 'yes' : 'NO');   // 跳到顶点也躲不掉
    add('tallFlyMissesDucking', flyHitAt(true, 0, true) ? 'NO' : 'yes');
    // 反过来确认低飞障碍仍然「跳得过去」
    add('lowFlyClearableByJump', flyHitAt(false, jm.peak, false) ? 'NO' : 'yes');
    // 高飞障碍顶边与跳跃顶点的余量（越小越脆，改跳跃参数时必须复核）
    add('tallFlyMarginPx', Math.round((458 - (GROUND_Y-player.h-jm.peak)) - (GROUND_Y-199+6)));

    // 7) 下蹲：onGround 且按下时 duck 应为 true，且绘制高度变小
    reset(); startRun(); obs = [];
    keyDown = true; step(); step();
    add('duck', player.duck ? 'yes' : 'NO');
    keyDown = false; step(); step();
    add('duckReleased', player.duck ? 'NO' : 'yes');

    // 7b) 自动游玩：写个只会「看到障碍就跳 / 见飞狗就蹲」的傻 AI，
    //     跑几千帧看会不会被撞死 —— 这是「障碍密度是否合理」的客观判据
    function autoPlay(limit, initScore){
      reset(); startRun();
      score = initScore || 0;          // 可以直接把分数拉高，用来验证高速段
      let deaths = 0, best = 0, jumps = 0;
      const deathLog = [];
      // 节奏指标：起跳间隔 / 每次落地后在地面停留的帧数。
      // 如果这两个的 min 和 max 贴得很近，说明节奏还是「节拍器」。
      const intervals = [], groundRuns = [];
      let lastJumpAt = -1, groundRun = 0;
      for (let i=0;i<limit;i++){
        const p = player;
        let wantJump = false, wantDuck = false;
        if (!p.dead && p.onGround){
          const front = p.x + p.w - 6;
          // 1) 收集前方还没过去的障碍，按 x 排序后合并成「簇」（间隔 <60px 视为同一簇）
          const ahead = obs.filter(o => o.x + o.w > p.x + 6 && o.x < W + 400)
                           .sort((a,b)=>a.x-b.x);
          if (ahead.length){
            let l = ahead[0].x, r = ahead[0].x + ahead[0].w;
            let isFly = !!FLY_TYPES[ahead[0].type];
            let maxH = ahead[0].h;
            for (let k=1;k<ahead.length;k++){
              const o = ahead[k];
              if (o.x - r >= 60) break;              // 断开，后面的算下一簇
              r = Math.max(r, o.x + o.w);
              maxH = Math.max(maxH, o.h);
              if (!FLY_TYPES[o.type]) isFly = false;
            }
            const S = r - l, d = l - front;
            if (isFly){
              // 飞狗：蹲下即可，提前一点进入蹲姿
              if (d < speed * 25) wantDuck = true;
            } else {
              // 起跳时机必须【跟着物理常量算】，不能写死帧数 ——
              // 之前这里写死 34 帧，跳跃物理一改（越障窗口 37→46 帧）就全线起跳过晚。
              // 抛物线 y = v·t - g·t²/2，升高到 RISE 的进出时刻：
              //   t = (v ± √(v²-2g·RISE)) / g
              // 所需升高要按【这一簇里最高的障碍】算，不能写死：
              // 玩家底边 y+88 要高于障碍顶边 GROUND_Y-h+6，站立位是 GROUND_Y-90，
              // 所以需要升高 h-8 像素。70px 的障碍要 62，92px 的奶瓶要 84。
              // 用和游戏同一份越障窗口推导，别再自己写一套
              const cw = clearanceWindow(Math.max(30, maxH - 8));
              const t1 = cw.t1, t2 = cw.t2;
              // 起跳时簇头距离 d 的可行区间：
              //   下界 t1*speed          —— 太近则还没升够高障碍就撞上来
              //   上界 t2*speed-S-62     —— 太远则整簇还没过完就落地了
              // 取【中点】起跳，两侧余量相等。
              // （早先写成「d ≤ 上界」= 在上界那一刻起跳，t2 侧余量为 0，
              //   高速段就会以 1~2px 的差距撞在障碍上。）
              const lo = t1 * speed;
              const hi = t2 * speed - S - 62;
              const target = hi >= lo ? (lo + hi) / 2 : hi;
              if (d <= target) wantJump = true;
            }
          }
        }
        if (wantJump) jumps++;
        if (wantJump && player.onGround && !player.dead){
          if (lastJumpAt >= 0) intervals.push(i - lastJumpAt);
          lastJumpAt = i;
          if (groundRun > 0) groundRuns.push(groundRun);
          groundRun = 0;
        }
        keyJump = wantJump; keyDown = wantDuck && !wantJump;
        const wasDead = p.dead;
        step();
        groundRun = (player.onGround && !player.dead) ? groundRun + 1 : 0;
        if (!wasDead && player.dead && deathLog.length < 6){
          // 记录死亡现场：到底是撞到什么、当时是站着/蹲着/空中
          let near = null;
          for (const o of obs){
            const d = Math.abs(o.x - (player.x + player.w/2));
            if (!near || d < near.d) near = {o, d};
          }
          // 注意：分隔符别用 '|'，外层 shell 会按 '|' 切分导致后半段被吞掉
          deathLog.push(
            'sp=' + speed.toFixed(1) +
            ' air=' + (!player.onGround) +
            ' duck=' + player.duck +
            ' y=' + Math.round(player.y) +
            ' <- ' + (near ? near.o.type + ' x=' + Math.round(near.o.x) +
                      ' w=' + Math.round(near.o.w) + ' h=' + Math.round(near.o.h) +
                      ' top=' + Math.round(near.o.y) : '?')
          );
        }
        if (state === 'over'){ deaths++; best = Math.max(best, Math.floor(score)); reset(); startRun(); }
      }
      keyJump = false; keyDown = false;
      const st = a => a.length ? {min: Math.min(...a), max: Math.max(...a),
        avg: Math.round(a.reduce((x,y)=>x+y,0)/a.length), n: a.length} : null;
      const rhythm = {interval: st(intervals), ground: st(groundRuns)};
      return {deaths, score: Math.floor(score), best, jumps, deathLog, rhythm,
              speed: speed.toFixed(1), gap: Math.round(nextGap),
              gapMin: Math.round(gapMin()), rhythm: rhythm};
    }
    const ap = autoPlay(4000, 0);                     // 低速段
    add('slowDeaths', ap.deaths);                     // 应为 0
    add('slowScore', ap.score);
    add('slowSpeed', ap.speed);
    add('slowGapPx', ap.gap + ' (min ' + ap.gapMin + ')');
    add('slowJumpPx', Math.round(parseFloat(ap.speed) * JUMP_FRAMES));
    add('tightPairs', spawnStats.tight);              // 「紧挨组合」出现次数，应 > 0
    add('singleVsCluster', spawnStats.single + ' 单只 / ' + spawnStats.clusters + ' 连排');
    add('tightMaxN', spawnStats.maxN);                // 最多几只挨在一起
    add('tightMinInnerGapPx', Math.round(spawnStats.minInner));   // 内部最小间距
    add('tightMaxSpanPx', Math.round(spawnStats.maxSpan));        // 组合最大总宽
    add('slowJumpIntervalFrames', JSON.stringify(ap.rhythm.interval));
    add('slowGroundRunFrames', JSON.stringify(ap.rhythm.ground));
    ap.deathLog.forEach((s,i)=>add('slowDeath'+i, s));

    const ap2 = autoPlay(4000, 8000);                 // 高速段（分数直接拉高，速度到上限）
    add('fastDeaths', ap2.deaths);                    // 应为 0
    add('fastScore', ap2.score);
    add('fastSpeed', ap2.speed);
    add('fastGapPx', ap2.gap + ' (min ' + ap2.gapMin + ')');
    add('fastJumpPx', Math.round(parseFloat(ap2.speed) * JUMP_FRAMES));
    add('flyVariants', JSON.stringify(spawnStats.flyKinds));  // 两种飞狗各刷出几次（累计）
    // 连排概率的阶梯：开局必须低，随分数逐级上升
    add('clusterChanceLadder', [0,100,300,600,1200,2000,3000].map(v=>{
      const old = score; score = v; const c = clusterChance(); score = old;
      return v + '分:' + Math.round(c*100) + '%';
    }).join(' → '));
    add('fastTightPairs', spawnStats.tight);          // 累计（含高速段）
    add('fastTightMaxN', spawnStats.maxN);            // 高速段应能出现 3 联
    add('fastJumpIntervalFrames', JSON.stringify(ap2.rhythm.interval));
    add('fastGroundRunFrames', JSON.stringify(ap2.rhythm.ground));
    ap2.deathLog.forEach((s,i)=>add('fastDeath'+i, s));

    // 8) 昼夜：① reset 后 CSS 类必须和 dayMode 一致（否则重开会残留夜色）
    //          ② 分数推过阈值后 class 应翻转
    reset(); startRun();
    add('nightClassInSync', (stage.classList.contains('night') === !dayMode) ? 'yes' : 'NO');
    const beforeNight = stage.classList.contains('night');
    score = 720; step();
    add('nightToggle', (stage.classList.contains('night') !== beforeNight) ? 'yes' : 'NO');
    add('nightClassAfter', stage.classList.contains('night') ? 'on' : 'off');
    add('nightSchedule', '首次 ' + NIGHT_AT[0] + ' 分，之后每 ~700 分切换一次');
  } catch(e){
    add('EXCEPTION', (e && (e.stack || e.message)) || e);
  }

  // 9) 本地数据库：真实走一遍「写入 → 读回 → 还原」。
  //    先快照原有记录，测完还原，绝不把用户真实成绩清掉。
  (async () => {
    try {
      const k = await LDB.init();
      add('localDBkind', k);
      const snap = await LDB.all();
      const MARK = 987654;
      await LDB.add({score: MARK, ts: 1791800000000, dur: 1, spd: 1});
      const after = await LDB.all();
      add('localDBwriteRead', (after.length === snap.length + 1 &&
          after.some(r => r.score === MARK)) ? 'yes' : 'NO');
      await LDB.clear();
      for (const r of snap) await LDB.add({score:r.score, ts:r.ts, dur:r.dur, spd:r.spd});
      const back = await LDB.all();
      add('localDBrestored', (back.length === snap.length) ? 'yes' : 'NO');
      // 渲染一次面板，确认列表能正常出内容
      await showTab('local');
      add('boardRows', boardListEl.children.length);

      // 12) 排行榜按钮真的能用：模拟一次真实点击，并检查它有没有误把游戏开起来
      reset(); ov.style.display = ''; boardEl.hidden = true;
      const bb = document.getElementById('boardBtn');
      bb.dispatchEvent(new PointerEvent('pointerdown', { bubbles:true, cancelable:true }));
      bb.dispatchEvent(new MouseEvent('click', { bubbles:true, cancelable:true }));
      add('boardBtnOpens', boardEl.hidden ? 'NO(没打开)' : 'yes');
      add('boardBtnNoStart', state === 'ready' ? 'yes' : 'NO(顺带把游戏开起来了)');
      // 关闭按钮同样要能用
      const bc = document.getElementById('boardClose');
      bc.dispatchEvent(new PointerEvent('pointerdown', { bubbles:true, cancelable:true }));
      bc.dispatchEvent(new MouseEvent('click', { bubbles:true, cancelable:true }));
      add('boardCloseWorks', boardEl.hidden ? 'yes' : 'NO');
    } catch(e){
      add('localDB', 'EXCEPTION ' + (e && e.message));
    }

    // 10) 全网榜协议自检：把 fetch 换成桩件，验证请求构造 / 响应过滤 / 限频 / 分数校验。
    //     绝不碰真实服务（那是别人的公益服务，不该被测试流量打）。
    const realFetch = window.fetch;
    const reqs = [];
    let mode = 'write';
    const sUser = REMOTE.user, sSecret = REMOTE.secret;
    const sOrigins = REMOTE.origins.slice();
    const TO = 'https://example.github.io';   // 测试用来源（声明在外层，桩件和断言都要用）
    window.fetch = (url, opt) => {
      reqs.push({ url, body: opt && opt.body });
      if (mode === 'write') return Promise.resolve({ ok:true, text: () => Promise.resolve('{}') });
      // 混入两类伪造记录，验证校验器能把它们剔掉
      const g1 = makeRecord('阿花', scoreAfter(3000), 3000, 1791800005000, TO);   // 合法
      const g2 = makeRecord('阿狗', scoreAfter(6000), 6000, 1791800009000, TO);   // 合法
      const f1 = JSON.parse(JSON.stringify(g2));                              // 手改分数
      f1.n = '改分党'; f1.s = f1.s * 10; f1.t = 1791800008000;                // → 校验码不符
      const f2 = { v: REC_VER, n:'自洽党', s: 999999, f: 100, t: 1791800007000 };
      f2.c = recChecksum(f2);                                                 // 校验码对，但分数与帧数不自洽
      return Promise.resolve({ ok:true, text: () => Promise.resolve(JSON.stringify({
        'hnw_g1_aaaa': JSON.stringify(g1),
        'hnw_g2_bbbb': JSON.stringify(g2),
        'hnw_f1_cccc': JSON.stringify(f1),
        'hnw_f2_dddd': JSON.stringify(f2),
        'hnw_f3_eeee': '这不是 JSON',
        'other_x':     JSON.stringify({ n:'别人的', s:1, t:1 }),   // 前缀不符 → 应被忽略
      })) });
    };
    try {
      REMOTE.user = 'tu'; REMOTE.secret = 'ts';
      // 把测试来源临时加进白名单，否则下面的写入链路测试会被来源校验挡住
      REMOTE.origins = sOrigins.concat([TO]);
      add('remoteConfigured', remoteOn() ? 'yes(测试态)' : 'NO');

      // 分数 / 帧数校验（此时还没成功提交过，不会被限频挡住）
      const F = 1000, S = Math.floor(scoreAfter(F));
      let guard = 'NO';
      try { await remoteSubmit('测试蛙', 0, F, TO); } catch(e){ guard = /范围/.test(e.message) ? 'yes' : 'NO:' + e.message; }
      add('remoteScoreGuard', guard);
      let fguard = 'NO';
      try { await remoteSubmit('测试蛙', S, 0, TO); } catch(e){ fguard = /帧数/.test(e.message) ? 'yes' : 'NO:' + e.message; }
      add('remoteFramesGuard', fguard);

      // 写入：检查 POST 体里带齐了自洽字段
      await remoteSubmit('测试蛙', S, F, TO);
      const b1 = new URLSearchParams(reqs[reqs.length-1].body);
      add('remoteWriteAction', b1.get('action') + ' user=' + b1.get('user'));
      add('remoteWriteTag', String(b1.get('tag')||'').indexOf(REMOTE.prefix) === 0 ? 'yes' : 'NO');
      const v = JSON.parse(b1.get('value'));
      add('remoteWriteValue', 'v=' + v.v + ' s=' + v.s + ' f=' + v.f + ' n=' + v.n +
                              ' c=' + (v.c ? 'ok' : 'NO'));
      add('remoteWriteSelfCheck', verifyRecord(b1.get('value')) === null ? 'yes' : 'NO');

      // 限频：立刻再提一次应被拒
      let gap = 'NO';
      try { await remoteSubmit('测试蛙', S, F, TO); } catch(e){ gap = /稍等/.test(e.message) ? 'yes' : 'NO:' + e.message; }
      add('remoteRateLimit', gap);

      // 读取：脏数据过滤 + 排序
      mode = 'read';
      const res = await remoteTop(TO);
      add('remoteReadRows', res.rows.length);                          // 应为 2（只留合法的）
      add('remoteReadRejected', res.rejected);                         // 应为 3（改分 / 不自洽 / 非 JSON）
      add('remoteReadOrderDesc', (res.rows.length >= 2 && res.rows[0].score > res.rows[1].score) ? 'yes' : 'NO');

      // 校验器逐条体检：合法记录必须放行，三类伪造必须各自命中原因
      // 来源判断
      add('originHere', JSON.stringify(currentOrigin()) + ' → ' +
          (originAllowed(currentOrigin()) ? '允许' : '拦截'));
      let ob = 'NO';
      try { await remoteSubmit('测试蛙', S, F, 'file://'); }
      catch(e){ ob = /来源/.test(e.message) ? 'yes' : 'NO:' + e.message; }
      add('originBlockFile', ob);
      let ob2 = 'NO';
      try { await remoteTop('file://'); }
      catch(e){ ob2 = /来源/.test(e.message) ? 'yes' : 'NO:' + e.message; }
      add('originBlockFileRead', ob2);
      // 白名单：临时收紧后，名单外的来源要被拒
      const savedList = REMOTE.origins.slice();
      REMOTE.origins = [TO];
      add('originAllowlist', (originAllowed(TO) && !originAllowed('https://evil.example')) ? 'yes' : 'NO');
      REMOTE.origins = savedList;
      // 记录里带被拦来源 → 校验器要剔除
      const badO = makeRecord('来源不对', scoreAfter(500), 500, 1791800000000, 'file://');
      add('verifyBadOrigin', verifyRecord(JSON.stringify(badO)) || 'NO(未拦住)');

      const okRec = makeRecord('正常', scoreAfter(2000), 2000, 1791800000000, TO);
      add('verifyValid', verifyRecord(JSON.stringify(okRec)) === null ? 'yes' : 'NO');
      const tampered = JSON.parse(JSON.stringify(okRec)); tampered.s += 1;
      add('verifyTampered', verifyRecord(JSON.stringify(tampered)) || 'NO(未拦住)');
      const selfConsistent = { v: REC_VER, n:'x', s: 999999, f: 100, t: 1791800000000, o: TO };
      selfConsistent.c = recChecksum(selfConsistent);
      add('verifyInconsistent', verifyRecord(JSON.stringify(selfConsistent)) || 'NO(未拦住)');
      const noVer = JSON.parse(JSON.stringify(okRec)); noVer.v = 1;
      add('verifyOldVersion', verifyRecord(JSON.stringify(noVer)) || 'NO(未拦住)');
      const hugeF = JSON.parse(JSON.stringify(okRec)); hugeF.f = MAX_PLAY_FRAMES + 1;
      add('verifyFramesGuard', verifyRecord(JSON.stringify(hugeF)) || 'NO(未拦住)');

      // 关键不变量：scoreAfter(frames) 必须与 step() 里逐帧累加的分数完全一致，
      // 否则合法记录会被自己的校验器误杀
      reset(); startRun(); obs = [];
      for (let i=0;i<1500;i++) step();
      add('scoreAfterMatchesLive',
        Math.floor(scoreAfter(playFrames)) === Math.floor(score) ? 'yes'
          : 'NO live=' + Math.floor(score) + ' calc=' + Math.floor(scoreAfter(playFrames)) +
            ' frames=' + playFrames);
      const rb = new URLSearchParams(reqs[reqs.length-1].body);
      add('remoteReadAction', rb.get('action') + ' tag=' + rb.get('tag'));
    } catch(e){
      add('remoteTest', 'EXCEPTION ' + (e && e.message));
    } finally {
      REMOTE.user = sUser; REMOTE.secret = sSecret;   // 还原，别把测试态带出去
      REMOTE.origins = sOrigins;
      window.fetch = realFetch;
    }

    // 11) 真实联网验证（可选）：?selftest=1&net=1
    //     只做【读】，不写 —— 不往真实榜单灌测试数据。用来确认浏览器
    //     从当前 origin（file:// 或 http(s)）跨域读写真的通。
    if (QS.get('net')){
      if (!remoteOn()) add('remoteLive', '未配置凭据');
      else if (!originAllowed(currentOrigin()))
        add('remoteLive', '来源被拦：' + originLabel(currentOrigin()) + '（符合预期）');
      else {
        try {
          const res = await remoteTop();
          add('remoteLive', 'ok 读到 ' + res.rows.length + ' 条合法 / 剔除 ' + res.rejected + ' 条');
        } catch(e){
          add('remoteLive', 'FAIL ' + ((e && e.message) || e));
        }
      }
    }
    add('DONE', '1');
  })();
}

// 全局兜底：任何没被 catch 的错误也写进 DOM，方便无头读取
window.addEventListener('error', e=>{
  let pre = document.getElementById('selftest');
  if (!pre){ pre = document.createElement('pre'); pre.id='selftest'; document.body.appendChild(pre); }
  pre.textContent += ' || WINDOW_ERROR: ' + (e.message || e);
});

if (QS.get('selftest')){
  const wait = setInterval(()=>{
    let ok = true; for (const k in imgCache) if (!imgCache[k].complete) ok = false;
    if (!ok) return;
    clearInterval(wait);
    runSelfTest();
  }, 50);
} else if (QS.get('auto')){
  const wait = setInterval(()=>{
    let ok = true; for (const k in imgCache) if (!imgCache[k].complete) ok = false;
    if (!ok) return;
    clearInterval(wait);
    startRun();
    const n = parseInt(QS.get('t')||'0',10);
    if (n) for (let i=0;i<n;i++) step();
  }, 50);
}
</script>
</body>
</html>"""

# 注入 base64
HTML = HTML.replace('__IMGS__', repr(ENC).replace('"','').replace("'", '"'))
# 开始页图标 / favicon：单独注入（base64 字符集里没有引号，直接塞进 HTML 属性是安全的）
_n = HTML.count('__GODFROG__')
assert _n >= 2, f'__GODFROG__ 占位符只出现 {_n} 次，图标或 favicon 可能漏了'
HTML = HTML.replace('__GODFROG__', ENC['godfrog'])
assert HTML.count('__CREDIT__') == 1, '__CREDIT__ 占位符数量不对'
HTML = HTML.replace('__CREDIT__', CREDIT_HTML)
out = ROOT / "index.html"
out.write_text(HTML, encoding='utf-8')
print(f"已生成 {out} ({out.stat().st_size/1024:.1f} KB)")
for name, path, usage in IMGS:
    print(f"  · {name:6s} {path.name:20s} → {usage}")