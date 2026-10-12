# 神圣奶蛙 · Naiwa Run

仿 Chrome 小恐龙的奶蛙主题跑酷小游戏。**单文件 HTML5，零依赖，双击即玩。**

`dino.html` 把全部贴图以 base64 内嵌，脱离任何外部资源都能独立运行，断网也行。

---

## 玩法

跳过迎面而来的狗子和奶瓶。半空中的飞狗分两种：

| 障碍 | 应对 |
|---|---|
| 低飞狗 | 跳过去 **或** 蹲下躲 |
| **高飞狗** | **跳不过去，只能蹲下从底下钻过去** |

- 起速偏慢（5 px/帧），分数越高滚得越快，封顶 16
- 障碍间距随滚动速度自动缩放，连排组合的出现概率随分数阶梯上升（10% → 72%）
- 约每 700 分昼夜交替一次
- 每局成绩自动记进**本地数据库**，点开始页的「🏆 本地排行榜」看 Top 10

## 本地数据库

不依赖任何后端，纯前端持久化，用的是浏览器自带的两种存储：

| 后端 | 何时使用 | 说明 |
|---|---|---|
| **IndexedDB** | 通过 `http(s)` 打开 | 真正的浏览器数据库，带索引 |
| `localStorage` | 通过 `file://` 双击打开 | 降级方案 |

之所以要降级：Chrome/Edge 在 `file://` 下把页面当作 opaque origin，会禁用 IndexedDB。
而本作主打「双击即玩」，所以必须能在两种环境下都正常记录。

排行榜面板的副标题会写明当前用的是哪个后端，打开即可核对。

> 数据存在**本机浏览器**里，换设备/换浏览器不会同步，清浏览器数据会丢失。
> 想要跨设备同步就需要真正的后端（本项目没有）。

## 操作

| | 跳 | 下蹲 |
|---|---|---|
| 键盘 | `Space` / `↑` / `W` | `↓` / `S` |
| 触屏 | 点屏幕 | 向下滑 |

> 跳跃是**固定高度**（顶点 169px、滞空 72 帧），没有长按变高。

---

## 文件结构

```
dino.html                  游戏本体（由生成器产出，可直接双击运行）
make_dino_game.py          生成器：读 art/ 里的 webp → base64 → 产出 dino.html
art/                       本作实际用到的 15 张贴图（随仓库提交）
  douluo/                    角色与敌兵，取自「奶斗罗」
  bignaiwa/                  开始页图标，取自「合成大奶蛙」
fetch_assets.py            素材抓取脚本（递归镜像各站点的图片/音频/字体/模型）
dedupe_assets.py           素材内容去重 + 清理误抓的假响应
make_manifest.py           素材清单页生成器
milkyfrog-source-map.html  22 个奶蛙小游戏的源码地图调研报告
```

## 运行

游戏本体不需要构建：

```bash
# 直接双击 dino.html 即可；或起个静态服务
python -m http.server 8080
```

改动 `make_dino_game.py` 后重新生成：

```bash
python make_dino_game.py     # → dino.html
```

因为素材已随仓库放在 `art/`，**干净检出后无需任何额外步骤即可重新生成**。

---

## 素材来源（上游标注）

本作的全部美术素材都取自他人制作的奶蛙小游戏，仅作学习与娱乐用途。
这些游戏最初是通过奶蛙合集站 **<https://milkyfrog.com/>** 找到的。

### 1. 角色与敌兵 —— 「奶斗罗」

`art/douluo/` 下 14 张，来自网页游戏「奶斗罗」：

| 文件 | 用途 |
|---|---|
| `baby-run-0/1/2.webp` | 主角奔跑三帧 |
| `baby-jump.webp` | 跳跃 |
| `baby-double.webp` | 下蹲 |
| `baby-hurt.webp` | 撞击 |
| `dog-foam.webp` `dog-cheese.webp` `dog-guard.webp` `dog-rammer.webp` | 地面障碍 |
| `milk-egg.webp` `milk-baby.webp` | 地面障碍 |
| `dog-howler.webp` | 飞狗（低飞 / 高飞共用一张贴图） |
| `milk-star.webp` | 云朵 |

- 在线地址：<https://nai-dou-luo.pages.dev/>（托管于 Cloudflare Pages）
- **上游源码仓库：未公开**（作者未开源，站内也未标注仓库地址）

### 2. 开始页图标 —— 「合成大奶蛙」

`art/bignaiwa/11-watermelon.webp`，来自「合成大奶蛙」合成链的**最高级产物**。

该作的合成链共 11 级：

```
葡萄 → 樱桃 → 橘子 → 柠檬 → 猕猴桃 → 番茄 → 桃子 → 菠萝 → 椰子 → 半奶蛙 → 神奶蛙
```

- 在线地址：<https://yhsome.github.io/BigNaiWa/>
- **上游仓库：<https://github.com/yhsome/BigNaiWa>**（作者 YHSome）
- 说明：上游仓库里这一级的名称写作「**神奶蛙**」；本作按项目需要统一称为「神圣奶蛙」。

### 版权说明

- 上述素材版权归**各自作者**所有。上游作品大多未附明确的开源许可
  （「合成大奶蛙」仓库注明"仅供学习娱乐使用"）。
- 本仓库仅为个人学习与娱乐目的的再创作，**不主张对这些美术素材的任何权利**。
- 若你是素材作者且不希望被使用，请联系删除。

### 关于 `assets/`

`fetch_assets.py` 会把各站点的**完整**素材集镜像到 `assets/`（约 69MB，含大量本作
没用到的图片、字体、音乐、3D 模型）。该目录**已被 `.gitignore` 排除**，不随仓库分发。

`art/` 就是从这个目录里挑出的本作实际用到的 15 张。想重新抓取：

```bash
python fetch_assets.py       # → assets/   （耗时较长）
python dedupe_assets.py      # 内容去重 + 清理误抓的假响应
```

---

## 自检

`dino.html` 内置了一套渲染与玩法自检，供无头浏览器读取（纯文本，不依赖截图）：

```
dino.html?selftest=1    跑自检，结果写进 <pre id="selftest">
dino.html?auto=1&t=300  自动开跑 300 帧（截图用）
```

自检覆盖：贴图加载、图标、键位映射、拖影、跳跃高度与滞空、下蹲判定、
高飞狗「跳不过去 / 蹲得过去」、障碍密度与节奏、昼夜切换，
以及一个会自己玩 4000 帧的简易 AI（用来验证关卡是可通关的）。

用本机 Edge 跑一遍：

```bash
msedge --headless=new --disable-gpu --virtual-time-budget=30000 \
  --dump-dom "file:///path/to/dino.html?selftest=1" | grep -oE 'SELFTEST[^<]*'
```

## 相关

- `milkyfrog-source-map.html` —— 奶蛙合集 22 个小游戏的源码地图调研
  （各作的真实托管地址、技术栈、GitHub 仓库）
