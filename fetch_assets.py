# -*- coding: utf-8 -*-
"""奶蛙系列站点资源/素材全量抓取器。

用法:  python fetch_assets.py [--only slug1,slug2] [--max-files N] [--max-bytes MB]
输出:  assets/<slug>/<host>/<path>
"""
import os, re, sys, json, time, hashlib, subprocess, posixpath
from urllib.parse import urljoin, urlparse, unquote, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

ENTRIES = {
    "site":      "https://milkyfrog.com/",
    "hecheng":   "https://yhsome.github.io/BigNaiWa/",
    "shenpao":   "https://naiwa.me/",
    "yumaoqiu":  "https://www.bilibili.com/toy/naiwa-badminton/index.html",
    "jump":      "https://naiwai-jump.github.io/",
    "shenlong":  "https://naiwa.games/",
    "fangpi":    "https://naiwa-fart.pages.dev/",
    "zhua":      "https://yhsome.github.io/ZhuaNaiWa/",
    "tanchiwa":  "https://milkyfrogs.toolsbox.vip/",
    "n2048":     "https://game.0z.hk/game/2048/",
    "wuziqi":    "https://wudibaolongzhanshi1234.github.io/1335689.giyhub.io/",
    "nailegewa": "https://junjunya2020.github.io/nailegewa/",
    "tiao":      "https://naiwa-jump.pages.dev/",
    "douluo":    "https://nai-dou-luo.pages.dev/",
    "yanse":     "https://milkyfrog.toolsbox.vip/",
    "lvxing":    "https://www.bilibili.com/toy/TravelMilkyFrog/index.html",
    "kuaipao":   "https://e.233ly.com/1ABrH3",
    "gongchang": "https://66970010-boop.github.io/frog-miner/",
    "jiewu":     "https://nailong-dance.pages.dev/",
    "gugupeng":  "https://naiwa-gugupeng.pages.dev/",
    "xiaoxiaole":"https://chenckx0614.github.io/naiwaxxl/",
    "xiaowo":    "https://naiwaxiaowu.pages.dev/",
}

# 需要抓取/解析的资源后缀
MEDIA_EXT = ("png", "jpg", "jpeg", "webp", "gif", "bmp", "avif", "ico", "svg",
             "mp3", "ogg", "wav", "m4a", "aac", "flac", "opus",
             "mp4", "webm", "mov",
             "woff", "woff2", "ttf", "otf", "eot",
             "glb", "gltf", "bin", "ktx2", "basis", "hdr", "exr", "pvr")
CODE_EXT = ("js", "mjs", "cjs", "css", "json", "webmanifest", "map", "wasm")

MAX_FILES = int(os.environ.get("MF_MAX_FILES", "500"))
MAX_BYTES = int(os.environ.get("MF_MAX_BYTES", str(80 * 1024 * 1024)))
MAX_SINGLE = int(os.environ.get("MF_MAX_SINGLE", str(20 * 1024 * 1024)))

_cache = {}          # url -> (ok, bytes)
_seen = set()
_lock_count = [0]


BINARY_EXT = set("png jpg jpeg webp gif bmp avif ico mp3 ogg wav m4a aac flac opus "
                 "mp4 webm mov woff woff2 ttf otf eot glb gltf bin ktx2 basis".split())


def looks_broken(url, ctype, body):
    """识别「HTTP 200 但内容是被劫持的跳转 HTML」这类假响应。"""
    e = ext_of(url)
    if e in ("svg",):          # SVG 本身就是 XML 文本，跳过
        return False
    if e not in BINARY_EXT:
        return False
    # 只认「明确的假响应」：小体积 + 一看就是 HTML/跳转页。宁可放过，不可误删。
    if len(body) > 4096:
        return False
    ct = (ctype or "").split(";")[0].strip().lower()
    head = body[:400].lstrip().lower()
    if head.startswith(b"<") and (b"<html" in head or b"<!doctype" in head or b"<script" in head):
        return True
    if b"location.href" in body[:600] or b"location.replace" in body[:600]:
        return True
    if ct.startswith("text/html") and len(body) < 2048:
        return True
    return False


def _once(url, referer):
    cmd = ["curl", "-sk", "--compressed", "-L", "--max-time", "45",
           "-A", UA, "--retry", "2", "--retry-delay", "1"]
    if referer:
        cmd += ["-e", referer]
    cmd += ["-o", "-", "-w", "\n@@%{http_code}@@%{content_type}@@%{url_effective}", url]
    p = subprocess.run(cmd, capture_output=True, timeout=70)
    raw = p.stdout
    idx = raw.rfind(b"\n@@")
    if idx < 0:
        return None
    body = raw[:idx]
    tail = raw[idx + 3:].decode("utf-8", "replace").split("@@")
    if len(tail) < 3 or tail[0] != "200":
        return None
    return (tail[2], tail[1], body)


def fetch(url, referer=None):
    """返回 (final_url, content_type, body_bytes)；失败重试 3 次后返回 (None,None,b'')。"""
    if url in _cache:
        return _cache[url]
    res = None
    for attempt in range(4):
        try:
            res = _once(url, referer)
        except Exception:
            res = None
        if res and res[2] and not looks_broken(url, res[1], res[2]):
            break
        res = None
        time.sleep(1.5 * (attempt + 1))
    res = res or (None, None, b"")
    # 只缓存成功结果，失败下次可重试
    if res[2]:
        _cache[url] = res
    return res


def local_path(slug, url):
    u = urlparse(url)
    host = u.netloc.replace(":", "_")
    path = unquote(u.path)
    if path.endswith("/") or path == "":
        path = posixpath.join(path, "index.html")
    # 查询串带版本号（?v=5）时加短哈希避免同名覆盖
    if u.query:
        h = hashlib.md5(u.query.encode()).hexdigest()[:6]
        base, dot, ext = path.rpartition(".")
        path = (base + "_q" + h + dot + ext) if dot else (path + "_q" + h)
    parts = [p for p in path.split("/") if p not in ("", "..")]
    safe = [re.sub(r'[<>:"|?*\x00-\x1f]', "_", p)[:120] for p in parts]
    return os.path.join(ROOT, slug, host, *safe)


def save(slug, url, body, ctype=""):
    _lock_count[0] += 1
    fp = local_path(slug, url)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    if os.path.exists(fp) and os.path.getsize(fp) == len(body):
        return fp
    with open(fp, "wb") as f:
        f.write(body)
    return fp


def ext_of(url, ctype=""):
    p = urlparse(url).path.lower()
    m = re.search(r"\.([a-z0-9]{2,5})$", p)
    return m.group(1) if m else ""


def is_asset(url, ctype=""):
    e = ext_of(url)
    if e in MEDIA_EXT or e in CODE_EXT:
        return True
    # 无后缀但看起来像静态资源（CDN 路径）
    if "/assets/" in url or "/static/" in url or "/_next/static/" in url or "/_nuxt/" in url:
        return True
    return False


def extract_html(base, body):
    """从 HTML 里抽资源链接 + 内联 style 的 url()。"""
    try:
        s = body.decode("utf-8", "replace")
    except Exception:
        return []
    out = []
    for m in re.finditer(r"""(?:src|href|data-src|data-url|poster)\s*=\s*["']([^"']+)["']""", s, re.I):
        out.append(m.group(1))
    for m in re.finditer(r"""(?:src|href|data-src)\s*=\s*([^\s"'<>]+)""", s, re.I):
        out.append(m.group(1))
    for m in re.finditer(r"srcset\s*=\s*[\"']([^\"']+)[\"']", s, re.I):
        for part in m.group(1).split(","):
            u = part.strip().split(" ")[0]
            if u:
                out.append(u)
    for m in re.finditer(r"<style[^>]*>(.*?)</style>", s, re.I | re.S):
        out += extract_css(base, m.group(1).encode())
    for m in re.finditer(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""", s, re.I):
        out.append(m.group(1))
    return [urljoin(base, u.strip()) for u in out if u.strip()]


def extract_css(base, body):
    try:
        s = body.decode("utf-8", "replace")
    except Exception:
        return []
    out = []
    for m in re.finditer(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""", s, re.I):
        out.append(m.group(1).strip())
    for m in re.finditer(r"""@import\s+['"]([^'"]+)['"]""", s, re.I):
        out.append(m.group(1).strip())
    return [urljoin(base, u) for u in out if u]


def extract_js(base, body):
    """从 JS 字符串字面量里抽素材路径（图片/音频/字体/模型）。"""
    try:
        s = body.decode("utf-8", "replace")
    except Exception:
        return []
    pat = r"""(?:["'`])([^"'`\n]{4,200}?\.(?:%s))(?:["'`])""" % "|".join(MEDIA_EXT)
    out = []
    for m in re.finditer(pat, s, re.I):
        v = m.group(1)
        # 过滤模板字符串 / 表达式残留：${i}、ARR[k]、a+b、含分号空格等
        if re.search(r"[\s$\{\}\[\]\(\);+=<>|\\]", v):
            continue
        if "%s" in v or "%%" in v:
            continue
        out.append(v)   # 返回原始（可能是相对）路径，由调用方解析多个基准
    return out


def crawl(slug, entry):
    stat = {"slug": slug, "files": 0, "bytes": 0, "skipped": 0, "cached": 0,
            "urls": [], "failed": []}
    seen = set()
    parsed_sig = set()          # 已解析过的 CSS/JS 内容签名，防嵌套重复递归
    queue = [(entry, "html", 0)]
    done = 0
    while queue and stat["files"] < MAX_FILES and stat["bytes"] < MAX_BYTES:
        url, kind, depth = queue.pop(0)
        url = url.split("#")[0]
        if not url.startswith(("http://", "https://")):
            if url.startswith("//"):
                url = "https:" + url
            else:
                continue
        if url in seen:
            continue
        seen.add(url)
        if url.startswith(("data:", "javascript:", "mailto:", "tel:")):
            continue
        if not is_asset(url):
            # 页面本体也抓（无后缀的目录页）
            if kind != "html":
                continue
        # 断点续传：本地已有且内容合法就直接复用，不重复下载
        cached_fp = local_path(slug, url)
        if os.path.exists(cached_fp):
            try:
                body0 = open(cached_fp, "rb").read()
            except OSError:
                body0 = b""
            if body0 and not looks_broken(url, "", body0):
                stat["cached"] += 1
                fin, ctype, body = url, "", body0
                e = ext_of(fin, ctype)
                ct = ""
                if depth >= 3:
                    continue
                if kind == "html" or e == "html" or b"<html" in body[:400].lower():
                    for u in extract_html(fin, body):
                        if u not in seen:
                            queue.append((u, "asset", depth + 1))
                elif e == "css":
                    for u in extract_css(fin, body):
                        if u not in seen:
                            queue.append((u, "asset", depth + 1))
                elif e in ("js", "mjs", "cjs"):
                    root = "%s://%s/" % (urlparse(fin).scheme, urlparse(fin).netloc)
                    pagebase = entry if entry.endswith("/") else posixpath.dirname(entry) + "/"
                    cands = []
                    for raw in extract_js(fin, body):
                        if raw.startswith(("http://", "https://", "//")):
                            cands.append(raw); continue
                        for b in dict.fromkeys([fin, pagebase, root]):
                            cands.append(urljoin(b, raw))
                    for u in cands:
                        if u not in seen and not has_dup_seg(u):
                            queue.append((u, "asset", depth + 1))
                continue
            else:
                os.remove(cached_fp)   # 损坏文件，删掉重抓

        fin, ctype, body = fetch(url, referer=entry)
        if fin is None or not body:
            stat["skipped"] += 1
            stat["failed"].append(url)
            continue
        if len(body) > MAX_SINGLE:
            stat["skipped"] += 1
            stat["failed"].append(url + "  [TOO BIG]")
            continue
        try:
            fp = save(slug, fin, body, ctype)
        except Exception:
            continue
        stat["files"] += 1
        stat["bytes"] += len(body)
        stat["urls"].append({"url": url, "file": os.path.relpath(fp, ROOT), "bytes": len(body)})

        e = ext_of(fin, ctype)
        ct = (ctype or "").split(";")[0].strip().lower()
        if depth >= 3:
            done += 1
            continue
        if kind == "html" or ct == "text/html" or e == "html":
            for u in extract_html(fin, body):
                if u not in seen:
                    queue.append((u, "asset", depth + 1))
        elif e == "css" or ct == "text/css":
            sig = hashlib.md5(body).hexdigest()
            if sig in parsed_sig:
                done += 1
                continue
            parsed_sig.add(sig)
            for u in extract_css(fin, body):
                if u not in seen:
                    queue.append((u, "asset", depth + 1))
        elif e in ("js", "mjs", "cjs") or "javascript" in ct:
            sig = hashlib.md5(body).hexdigest()
            if sig in parsed_sig:
                done += 1
                continue
            parsed_sig.add(sig)
            # JS 里的相对路径基准不确定（可能相对 JS 自身 / 页面 / 站根），三种都试
            root = "%s://%s/" % (urlparse(fin).scheme, urlparse(fin).netloc)
            pagebase = entry if entry.endswith("/") else posixpath.dirname(entry) + "/"
            cands = []
            for raw in extract_js(fin, body):
                if raw.startswith(("http://", "https://", "//")):
                    cands.append(raw)
                    continue
                for b in dict.fromkeys([fin, pagebase, root]):
                    cands.append(urljoin(b, raw))
            for u in cands:
                if u not in seen and not has_dup_seg(u):
                    queue.append((u, "asset", depth + 1))
        done += 1
    return stat


def has_dup_seg(url):
    """路径里出现连续重复目录（如 /js/js/、/assets/assets/）→ 是基准解析错误产生的垃圾。"""
    segs = [s for s in urlparse(url).path.split("/") if s]
    for i in range(len(segs) - 1):
        if segs[i] == segs[i + 1]:
            return True
    return False


def main():
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    tasks = [(k, v) for k, v in ENTRIES.items() if not only or k in only]
    os.makedirs(ROOT, exist_ok=True)
    report = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(crawl, k, v): k for k, v in tasks}
        for fu in as_completed(futs):
            k = futs[fu]
            try:
                st = fu.result()
            except Exception as ex2:
                st = {"slug": k, "error": str(ex2), "files": 0, "bytes": 0}
            report.append(st)
            print(f"[{st['slug']:11s}] new={st.get('files',0):3d} cached={st.get('cached',0):4d} "
                  f"{st.get('bytes',0)/1024/1024:7.2f} MB  skip={st.get('skipped',0)}", flush=True)
    report.sort(key=lambda x: x["slug"])
    with open(os.path.join(ROOT, "_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    tot_f = sum(r.get("files", 0) for r in report)
    tot_b = sum(r.get("bytes", 0) for r in report)
    print(f"\n合计 {tot_f} 个文件, {tot_b/1024/1024:.1f} MB -> {ROOT}")


if __name__ == "__main__":
    main()
