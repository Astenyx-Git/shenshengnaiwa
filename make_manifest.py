# -*- coding: utf-8 -*-
"""把 assets/ 里抓到的素材汇总成一份可浏览的清单页 assets/_index.html"""
import os, re, json, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
NAMES = {
 "site":"奶蛙官网 milkyfrog.com","hecheng":"合成大奶蛙","shenpao":"奶蛙神跑",
 "yumaoqiu":"奶蛙羽毛球","jump":"奶蛙jump","shenlong":"召唤神龙","fangpi":"奶蛙放屁",
 "zhua":"抓奶蛙","tanchiwa":"奶蛙贪吃蛙","n2048":"奶蛙2048超级版","wuziqi":"奶蛙五子棋",
 "nailegewa":"奶了个蛙","tiao":"奶蛙一跳","douluo":"奶斗罗","yanse":"奶蛙颜色大挑战",
 "lvxing":"旅行奶蛙","kuaipao":"奶蛙快跑","gongchang":"奶蛙工厂","jiewu":"奶蛙街舞",
 "gugupeng":"奶蛙鼓鼓碰","xiaoxiaole":"奶蛙消消乐","xiaowo":"奶蛙的小窝",
}
CAT = {
 "图片":"png jpg jpeg webp gif bmp avif ico svg",
 "音频":"mp3 ogg wav m4a aac flac opus",
 "视频":"mp4 webm mov",
 "字体":"woff woff2 ttf otf eot",
 "3D模型":"glb gltf bin ktx2 basis hdr",
 "代码":"js mjs cjs css json webmanifest map wasm",
 "页面":"html htm",
}
CAT_OF = {}
for c, exts in CAT.items():
    for e in exts.split():
        CAT_OF[e] = c

rows = []
for slug in sorted(os.listdir(ROOT)):
    d = os.path.join(ROOT, slug)
    if not os.path.isdir(d) or slug.startswith("_"):
        continue
    stat = collections.Counter()
    size = collections.Counter()
    total = 0
    n = 0
    for dirpath, _, files in os.walk(d):
        for f in files:
            fp = os.path.join(dirpath, f)
            try:
                b = os.path.getsize(fp)
            except OSError:
                continue
            ext = f.rsplit(".", 1)[-1].lower() if "." in f else ""
            cat = CAT_OF.get(ext, "其他")
            stat[cat] += 1
            size[cat] += b
            total += b
            n += 1
    rows.append({"slug": slug, "name": NAMES.get(slug, slug), "n": n,
                 "bytes": total, "cat": dict(stat), "size": dict(size)})

rows.sort(key=lambda r: -r["bytes"])
grand_n = sum(r["n"] for r in rows)
grand_b = sum(r["bytes"] for r in rows)

def mb(b):
    return f"{b/1024/1024:.2f} MB" if b >= 1024*1024 else f"{b/1024:.0f} KB"

CAT_ORDER = ["图片", "音频", "视频", "字体", "3D模型", "代码", "页面", "其他"]
CAT_COLOR = {"图片":"#15803d", "音频":"#b45309", "视频":"#be185d",
             "字体":"#6d28d9", "3D模型":"#0369a1", "代码":"#475569",
             "页面":"#0f766e", "其他":"#9ca3af"}

trs = []
for r in rows:
    cells = "".join(
        f'<td class="num">{r["cat"].get(c,0) or "·"}</td>' for c in CAT_ORDER)
    trs.append(f'''<tr>
      <td class="nm"><b>{r["name"]}</b><span class="sl">{r["slug"]}</span></td>
      {cells}
      <td class="num tot">{r["n"]}</td>
      <td class="num tot">{mb(r["bytes"])}</td>
    </tr>''')

tot_cat = {c: sum(r["cat"].get(c, 0) for r in rows) for c in CAT_ORDER}
tot_cells = "".join(f'<td class="num">{tot_cat[c] or "·"}</td>' for c in CAT_ORDER)

html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>奶蛙素材包 · 清单</title><style>
:root{{--bg:#fbf9f4;--card:#fff;--ink:#1f2430;--mute:#6b7280;--line:#e8e2d6;--gold:#f0b429}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;line-height:1.6}}
.wrap{{max-width:1180px;margin:0 auto;padding:36px 20px 70px}}
h1{{font-size:27px;margin:0 0 4px}}
.sub{{color:var(--mute);font-size:14px;margin-bottom:24px}}
.kpis{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:22px}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 20px}}
.kpi b{{display:block;font-size:22px}} .kpi span{{font-size:12px;color:var(--mute)}}
table{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);
 border-radius:12px;overflow:hidden;font-size:13.5px}}
th,td{{padding:9px 10px;border-bottom:1px solid var(--line);text-align:center}}
th{{background:#f6f2e9;font-size:12px;color:#6b6355;font-weight:700}}
th.c,td.nm{{text-align:left}}
td.num{{font-variant-numeric:tabular-nums;font-size:13px;color:#4b5563}}
td.tot{{font-weight:700;color:var(--ink);background:#fcfaf5}}
td.nm b{{font-weight:600}}
.sl{{display:block;font-family:ui-monospace,Consolas,monospace;font-size:11px;color:#9aa1ae}}
tr:last-child td{{border-bottom:none}}
tfoot td{{background:#f6f2e9;font-weight:700}}
.legend{{margin-top:26px;font-size:13px;color:var(--mute)}}
.legend b{{color:""}}
code{{background:#f2eee4;padding:1px 6px;border-radius:5px;font-size:12.5px;font-family:ui-monospace,Consolas,monospace}}
</style></head><body><div class="wrap">
<h1>🐸 奶蛙素材包 · 清单</h1>
<p class="sub">22 个站点 + 官网本体，共 {grand_n} 个文件 / {mb(grand_b)}，按 <code>assets/&lt;游戏&gt;/&lt;域名&gt;/&lt;路径&gt;</code> 原样镜像</p>
<div class="kpis">
<div class="kpi"><b>{grand_n}</b><span>文件总数</span></div>
<div class="kpi"><b>{mb(grand_b)}</b><span>总体积</span></div>
<div class="kpi"><b>{len(rows)}</b><span>站点数</span></div>
<div class="kpi"><b>{tot_cat.get('图片',0)}</b><span>图片</span></div>
<div class="kpi"><b>{tot_cat.get('音频',0)}</b><span>音频</span></div>
<div class="kpi"><b>{tot_cat.get('3D模型',0)}</b><span>3D 模型</span></div>
</div>
<table>
<thead><tr>
<th class="c">站点</th>
{''.join(f'<th>{c}</th>' for c in CAT_ORDER)}
<th>合计</th><th>体积</th>
</tr></thead>
<tbody>{''.join(trs)}</tbody>
<tfoot><tr><td class="nm">总计</td>{tot_cells}
<td class="num">{grand_n}</td><td class="num">{mb(grand_b)}</td></tr></tfoot>
</table>
<p class="legend">
目录说明：<code>assets/site/</code> = milkyfrog.com 官网本体；其余目录名即游戏 slug。
二级目录是资源所在域名（同一游戏可能跨 GitHub Pages + CDN 两个域）。
带 <code>_q&lt;hash&gt;</code> 后缀的文件是同一路径不同 <code>?v=</code> 版本的区分命名。
逐条 URL 明细见 <code>assets/_report.json</code>。
</p>
</div></body></html>"""

out = os.path.join(ROOT, "_index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote", out)
for r in rows:
    print(f"  {r['slug']:11s} {r['n']:5d} files  {mb(r['bytes']):>10s}  {dict(r['cat'])}")
print(f"TOTAL {grand_n} files {mb(grand_b)}")
