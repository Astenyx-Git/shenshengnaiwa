// _stub_run.cjs —— 在 Node 里用最小 DOM 桩真实执行 index.html 的游戏脚本与自检套件。
// 用途：沙箱里无法启动无头浏览器时的替代验证。纯逻辑断言（物理/输入/排行榜/校验）
// 全部真实运行；只有依赖 canvas 像素的断言（拖影/填色占比）是占位值，不作判据。
'use strict';
const fs = require('fs');

const htmlPath = process.argv[2] || 'index.html';
const search = process.argv[3] || '?selftest=1';
const html = fs.readFileSync(htmlPath, 'utf8');
// 页面里现在有多个 <script>（head 里有一个 ES5 错误陷阱 + 主脚本）。
// 贪婪正则会把中间的 </script>、HTML 一起吞进来 → 语法错误。
// 改为逐块非贪婪匹配，取【最长】的一块 = 游戏主脚本。
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x => x[1]);
if (!blocks.length) { console.error('FATAL: script block not found'); process.exit(1); }
const gameScript = blocks.reduce((a, b) => (b.length > a.length ? b : a));

// ---------- 事件注册表 ----------
const listeners = new Map(); // target -> Map(type -> [fn])
function addListener(target, type, fn) {
  if (!listeners.has(target)) listeners.set(target, new Map());
  const byType = listeners.get(target);
  if (!byType.has(type)) byType.set(type, []);
  byType.get(type).push(fn);
}
function fire(target, ev) {
  if (ev.target === undefined) ev.target = target;
  const byType = listeners.get(target);
  if (byType && byType.has(ev.type)) for (const fn of [...byType.get(ev.type)]) fn(ev);
}

// ---------- 假事件类 ----------
class FakeEvent {
  constructor(type, opts = {}) { this.type = type; Object.assign(this, opts); }
  preventDefault() { this.defaultPrevented = true; }
  stopPropagation() {}
  stopImmediatePropagation() {}
}
global.PointerEvent = FakeEvent;
global.KeyboardEvent = FakeEvent;
global.MouseEvent = FakeEvent;
global.Event = FakeEvent;
global.CustomEvent = FakeEvent;

// ---------- 元素桩 ----------
const byId = new Map();
let elSeq = 0;
function makeElement(tag) {
  const el = {
    tagName: (tag || 'div').toUpperCase(),
    style: {}, dataset: {}, children: [],
    hidden: false, value: '', textContent: '', className: '',
    scrollTop: 0, scrollHeight: 0, clientWidth: 1000, clientHeight: 560,
    offsetWidth: 1000, offsetHeight: 560, naturalWidth: 16, naturalHeight: 16,
    complete: true,
    classList: {
      _s: new Set(),
      add(...c) { c.forEach(x => this._s.add(x)); },
      remove(...c) { c.forEach(x => this._s.delete(x)); },
      toggle(c, f) { if (f === undefined) { this._s.has(c) ? this._s.delete(c) : this._s.add(c); } else { f ? this._s.add(c) : this._s.delete(c); } },
      contains(c) { return this._s.has(c); },
    },
    addEventListener(t, fn) { addListener(el, t, fn); },
    removeEventListener() {},
    dispatchEvent(ev) { fire(el, ev); return true; },
    appendChild(c) { el.children.push(c); return c; },
    setPointerCapture() {}, releasePointerCapture() {},
    getBoundingClientRect() { return { left: 0, top: 0, right: 1000, bottom: 560, width: 1000, height: 560 }; },
    querySelector() { return makeElement('div'); },
    querySelectorAll() { return []; },
    closest() { return null; },
    focus() {}, blur() {}, click() {},
  };
  Object.defineProperty(el, 'id', {
    get() { return el._idval || ''; },
    set(v) { el._idval = v; byId.set(v, el); },
  });
  return el;
}

// ---------- canvas 2D 桩（只保证不抛错，像素类断言结果无效） ----------
const canvasCtx = {
  setTransform() {}, fillRect() {}, fillText() {}, drawImage() {},
  beginPath() {}, moveTo() {}, lineTo() {}, closePath() {}, fill() {},
  save() {}, restore() {}, translate() {}, scale() {}, rotate() {},
  createLinearGradient() { return { addColorStop() {} }; },
  getImageData(x, y, w, h) { return { data: new Uint8ClampedArray(Math.max(1, w * h * 4)) }; },
  font: '', textAlign: '', fillStyle: '',
};
const canvasEl = makeElement('canvas');
canvasEl.getContext = () => canvasCtx;

// ---------- document / window ----------
global.document = {
  getElementById(id) {
    if (id === 'cv') return canvasEl;
    if (!byId.has(id)) {
      const el = makeElement('div');
      // 镜像静态 HTML 里的 hidden 属性（桩不解析 HTML，手动对齐）
      if (id === 'board' || id === 'nickRow') el.hidden = true;
      byId.set(id, el);
    }
    return byId.get(id);
  },
  createElement(tag) { return makeElement(tag); },
  querySelector() { return makeElement('div'); },
  querySelectorAll() { return []; },
  body: makeElement('body'),
  addEventListener(t, fn) { addListener(global.document, t, fn); },
};
global.window = globalThis;
global.self = globalThis;
global.addEventListener = (t, fn) => addListener(globalThis, t, fn);
global.removeEventListener = () => {};
global.dispatchEvent = (ev) => fire(globalThis, ev);
global.requestAnimationFrame = () => 0;   // 不跑 rAF 循环；step() 由自检/桩手动驱动
global.confirm = () => false;
global.localStorage = (() => {
  const s = new Map();
  return {
    getItem: k => (s.has(k) ? s.get(k) : null),
    setItem: (k, v) => s.set(k, String(v)),
    removeItem: k => s.delete(k),
  };
})();
global.location = { search, origin: 'null', href: 'file:///C:/stub/index.html' };
global.innerHeight = 600;   // padFitsViewport 断言用
global.Image = class { constructor() { this.complete = true; this.naturalWidth = 16; this.naturalHeight = 16; this.src = ''; } };
// 故意不提供 AudioContext / indexedDB：前者被 try/catch 兜住，后者会走 localStorage 降级分支

// ---------- 执行游戏脚本 ----------
(0, eval)(gameScript);

// ---------- 探针模式：直接验证 window 键盘事件通路 ----------
if (process.env.PROBE) {
  const ov = byId.get('ov');
  const before = ov.style.display;
  fire(globalThis, new FakeEvent('keydown', { code: 'Space' }));
  const after = ov.style.display;
  console.log('PROBE ovDisplay before=', JSON.stringify(before), 'after=', JSON.stringify(after));
  const lt = listeners.get(globalThis);
  if (lt) for (const [k, v] of lt) console.log('window listener:', k, 'x' + v.length);
  else console.log('window listener: NONE');
  process.exit(0);
}

// ---------- 轮询自检结果 ----------
const t0 = Date.now();
const timer = setInterval(() => {
  const pre = byId.get('selftest');
  const txt = pre ? pre.textContent : '';
  if (txt.includes('DONE=1')) {
    clearInterval(timer);
    console.log(txt);
    process.exit(txt.includes('WINDOW_ERROR') ? 3 : 0);
  }
  if (txt.includes('EXCEPTION') && txt.includes('localDB')) {
    // 异步段崩了也会把部分结果写进 DOM —— 打出来便于诊断
    clearInterval(timer); console.log('ASYNC-ERROR\n' + txt); process.exit(4);
  }
  if (Date.now() - t0 > 60000) { clearInterval(timer); console.log('TIMEOUT\n' + txt); process.exit(2); }
}, 200);
