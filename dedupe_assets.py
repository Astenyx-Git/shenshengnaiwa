# -*- coding: utf-8 -*-
"""对 assets/ 做内容去重：同一份内容只保留路径最短的那一份，并清掉误抓的噪声文件。"""
import os, hashlib, collections, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
NOISE_SUBSTR = ("workbuddy-cloud-sdk", "/npm/@tencent-ai/")

removed_noise = 0
for dirpath, _, files in os.walk(ROOT):
    for f in files:
        fp = os.path.join(dirpath, f)
        rel = os.path.relpath(fp, ROOT).replace("\\", "/")
        if any(s in rel for s in NOISE_SUBSTR):
            try:
                os.remove(fp); removed_noise += 1
                print("noise:", rel)
            except OSError:
                pass

by_hash = collections.defaultdict(list)
for dirpath, _, files in os.walk(ROOT):
    for f in files:
        fp = os.path.join(dirpath, f)
        if f.startswith("_"):
            continue
        try:
            b = open(fp, "rb").read()
        except OSError:
            continue
        if not b:
            continue
        by_hash[hashlib.md5(b).hexdigest()].append((len(os.path.relpath(fp, ROOT)), fp))

dup = 0
saved = 0
for h, lst in by_hash.items():
    if len(lst) < 2:
        continue
    lst.sort()
    keep = lst[0][1]
    for _, fp in lst[1:]:
        try:
            sz = os.path.getsize(fp)
            os.remove(fp)
            dup += 1
            saved += sz
            rel = os.path.relpath(fp, ROOT).replace("\\", "/")
            krel = os.path.relpath(keep, ROOT).replace("\\", "/")
            print(f"dup: {rel}\n     == {krel}")
        except OSError:
            pass

# 清掉空目录
for dirpath, dirs, files in os.walk(ROOT, topdown=False):
    if not os.listdir(dirpath):
        try:
            os.rmdir(dirpath)
        except OSError:
            pass

print(f"\nremoved noise={removed_noise}  dup={dup}  saved={saved/1024/1024:.2f} MB")
