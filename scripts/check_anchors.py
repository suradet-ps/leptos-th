#!/usr/bin/env python3
"""
Check all internal and anchor links in the built mdbook HTML files.
Mirroring scripts/check-links.ps1.
"""

import os
import re
import sys
import urllib.parse

def check_anchors(book_dir='book'):
    if not os.path.isdir(book_dir):
        print(f"Error: Built book directory '{book_dir}' not found.", file=sys.stderr)
        return 1

    files = []
    for root, _, fs in os.walk(book_dir):
        for f in fs:
            if f.endswith('.html'):
                files.append(os.path.join(root, f))

    total = 0
    broken = []

    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        ids = set(re.findall(r'id="([^"]+)"', content))
        rel = os.path.relpath(fpath, book_dir).replace('\\', '/')

        for m in re.finditer(r'href="([^"]*)"', content):
            href = m.group(1)
            if href.startswith('http') or href.startswith('javascript') or not href:
                continue

            if href.startswith('#'):
                total += 1
                target = urllib.parse.unquote(href[1:])
                if target not in ids:
                    broken.append(f"{rel} -> #{target} (id not found in page)")
            elif '.html' in href or 'print.html' in href:
                page = href.split('?')[0].split('#')[0]
                resolved = os.path.normpath(os.path.join(os.path.dirname(fpath), page))
                if not os.path.exists(resolved):
                    broken.append(f"{rel} -> {href} (target HTML file missing)")
                    continue
                if '#' in href:
                    total += 1
                    target = urllib.parse.unquote(href.split('#')[1])
                    with open(resolved, 'r', encoding='utf-8') as rf:
                        rcontent = rf.read()
                    rids = set(re.findall(r'id="([^"]+)"', rcontent))
                    if target not in rids:
                        broken.append(f"{rel} -> {href} (anchor #{target} not found in target)")

    print(f"Checked {total} anchor links")
    if not broken:
        print("ALL ANCHOR LINKS OK")
        return 0
    else:
        for b in broken:
            print(f"[BROKEN] {b}")
        return len(broken)

if __name__ == '__main__':
    book_path = sys.argv[1] if len(sys.argv) > 1 else 'book'
    sys.exit(check_anchors(book_path))
