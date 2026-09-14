#!/usr/bin/env python3
"""
Verify translation files against upstream book.
Checks:
1. All markdown files present
2. Code block count, language info tag, and exact body match (100% byte-exact)
3. Admonish directive kinds and count match
4. Heading count and hierarchy levels match (#, ##, ###)
5. Reference links and inline link targets match
"""

import os
import re
import sys

def get_paths():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    orig_candidates = [
        os.path.normpath(os.path.join(script_dir, '../../book/src')),
        os.path.normpath(os.path.join(script_dir, '../upstream/src')),
        os.path.normpath(os.path.join(os.getcwd(), 'upstream/src')),
        os.path.normpath(os.path.join(os.getcwd(), '../book/src')),
    ]
    orig = None
    for cand in orig_candidates:
        if os.path.isdir(cand):
            orig = cand
            break
    trans = os.path.normpath(os.path.join(script_dir, '../src'))
    return orig, trans

def parse_blocks(content):
    lines = content.replace('\r\n', '\n').split('\n')
    code_blocks = []
    admonish_kinds = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^\s{0,3}(`{3,})(.*)$', line)
        if m:
            fence = m.group(1)
            fence_len = len(fence)
            info = m.group(2).strip()
            body_lines = []
            i += 1
            while i < len(lines):
                l = lines[i]
                end_m = re.match(r'^\s{0,3}(`{3,})\s*$', l)
                if end_m and len(end_m.group(1)) >= fence_len:
                    break
                body_lines.append(l)
                i += 1
            body = '\n'.join(body_lines)
            tokens = [t for t in info.split() if t]
            first = tokens[0] if tokens else ''
            if first in ('admonish', 'sandbox'):
                kind = f"{tokens[0]} {tokens[1]}" if len(tokens) > 1 else tokens[0]
                admonish_kinds.append(kind)
                sub_code, sub_adm = parse_blocks(body)
                code_blocks.extend(sub_code)
                admonish_kinds.extend(sub_adm)
            else:
                code_blocks.append({'info': info, 'body': body})
        i += 1
    return code_blocks, admonish_kinds

def get_headings(content):
    return re.findall(r'(?m)^#{1,6} .*$', content.replace('\r\n', '\n'))

def get_ref_links(content):
    return [re.sub(r'\s+$', '', m) for m in re.findall(r'(?m)^\[[^\]]+\]:\s+\S+.*$', content.replace('\r\n', '\n'))]

def get_inline_link_targets(content):
    return [re.sub(r'\s+$', '', m) for m in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content.replace('\r\n', '\n'))]

def normalize_link_target(url):
    trimmed = url.strip()
    if not trimmed:
        return ''
    if trimmed.startswith('#'):
        return '#anchor'
    m = re.match(r'^([^#]+)#(.+)$', trimmed)
    if m:
        return m.group(1)
    return trimmed

known_link_fixes = {
    'view/09_component_children.md': {'/view/06_control_flow.html': '06_control_flow.md'},
    '15_global_state.md': {'../view/04b_iteration.md': 'view/04b_iteration.md'},
    'web_sys.md': {'/view/05_forms.html?highlight=NodeRef': 'view/05_forms.html?highlight=NodeRef'},
}

def main():
    orig, trans = get_paths()
    if not orig or not os.path.isdir(orig):
        print(f"Error: Upstream book src directory not found. Candidates checked: {orig}", file=sys.stderr)
        sys.exit(1)

    print("Comparing translation against upstream:")
    print(f"  Upstream:    {orig}")
    print(f"  Translation: {trans}")

    orig_files = []
    for root, _, files in os.walk(orig):
        for f in files:
            if f.endswith('.md'):
                rel = os.path.relpath(os.path.join(root, f), orig)
                orig_files.append(rel)
    orig_files.sort()

    fail = 0
    total = 0
    for rel in orig_files:
        total += 1
        opath = os.path.join(orig, rel)
        tpath = os.path.join(trans, rel)
        if not os.path.exists(tpath):
            print(f"[FAIL] {rel} : missing translated file")
            fail += 1
            continue

        with open(opath, 'r', encoding='utf-8') as f:
            ocontent = f.read()
        with open(tpath, 'r', encoding='utf-8') as f:
            tcontent = f.read()

        oc, oa = parse_blocks(ocontent)
        tc, ta = parse_blocks(tcontent)

        if len(oc) != len(tc):
            print(f"[FAIL] {rel} : code block count differs (orig={len(oc)} trans={len(tc)})")
            fail += 1
        else:
            for idx, (ob, tb) in enumerate(zip(oc, tc)):
                if ob['info'] != tb['info']:
                    print(f"[FAIL] {rel} : code block #{idx+1} info differs (orig='{ob['info']}' trans='{tb['info']}')")
                    fail += 1
                elif ob['body'] != tb['body']:
                    print(f"[FAIL] {rel} : code block #{idx+1} body differs")
                    fail += 1

        if len(oa) != len(ta):
            print(f"[FAIL] {rel} : admonish count differs (orig={len(oa)} trans={len(ta)})")
            fail += 1
        else:
            for idx, (o_adm, t_adm) in enumerate(zip(oa, ta)):
                if o_adm != t_adm:
                    print(f"[FAIL] {rel} : admonish #{idx+1} kind differs (orig='{o_adm}' trans='{t_adm}')")
                    fail += 1

        oh = get_headings(ocontent)
        th = get_headings(tcontent)
        if len(oh) != len(th):
            print(f"[FAIL] {rel} : heading count differs (orig={len(oh)} trans={len(th)})")
            fail += 1
        else:
            for idx, (oh_line, th_line) in enumerate(zip(oh, th)):
                ol = oh_line.split()[0]
                tl = th_line.split()[0]
                if ol != tl:
                    print(f"[FAIL] {rel} : heading #{idx+1} level differs (orig='{oh_line}' trans='{th_line}')")
                    fail += 1

        or_links = get_ref_links(ocontent)
        tr_links = get_ref_links(tcontent)
        if len(or_links) != len(tr_links):
            print(f"[FAIL] {rel} : ref links count differs (orig={len(or_links)} trans={len(tr_links)})")
            fail += 1
        else:
            for idx, (ol, tl) in enumerate(zip(or_links, tr_links)):
                ourl = normalize_link_target(ol.split(':', 1)[1].strip())
                turl = normalize_link_target(tl.split(':', 1)[1].strip())
                if ourl != turl:
                    print(f"[FAIL] {rel} : ref-link #{idx+1} url differs (orig='{ourl}' trans='{turl}')")
                    fail += 1

        olinks = [normalize_link_target(x) for x in get_inline_link_targets(ocontent)]
        tlinks = [normalize_link_target(x) for x in get_inline_link_targets(tcontent)]
        oset = sorted(set(olinks))
        tset = sorted(set(tlinks))
        missing = [x for x in oset if x not in tset]
        extra = [x for x in tset if x not in oset]

        rel_key = rel.replace('\\', '/')
        if rel_key in known_link_fixes:
            fix = known_link_fixes[rel_key]
            missing = [x for x in missing if x not in fix]
            extra = [x for x in extra if x not in fix.values()]

        if missing or extra:
            print(f"[FAIL] {rel} : inline links differ (missing={missing} extra={extra})")
            fail += 1

    print("---")
    print(f"Checked {total} files, {fail} problem(s)")
    if fail == 0:
        print("ALL OK: code blocks, admonish blocks, headings, links match 100%")
    return fail

if __name__ == '__main__':
    sys.exit(main())
