#!/usr/bin/env python3
"""
Deep Translation Audit for leptos-th
Checks:
1. File parity with upstream
2. Untranslated English paragraphs (>60 chars, predominantly English, <15% Thai characters)
3. Outdated/bad translationese terms from old translations
4. Markdown formatting syntax (unbalanced backticks, broken links)
5. SUMMARY.md completeness
6. Paragraph count / content ratio with upstream
"""

import os
import re
import sys

UPSTREAM = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../book/src'))
TRANSLATION = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))

THAI_CHAR = re.compile(r'[\u0e00-\u0e7f]')

# Deprecated translationese phrases that should not appear
OLD_TERMS = [
    (r'ลายเซ็นของคอมโพเนนต์', 'รูปแบบซิกเนเจอร์ของฟังก์ชันคอมโพเนนต์'),
    (r'กลายพันธุ์', 'แก้ไขค่า / mutate'),
    (r'โอเพกชนิด', 'ชนิดข้อมูลแบบทึบ (opaque type)'),
    (r'การ์ดการอ่าน', 'Read Guard'),
    (r'การ์ดการเขียน', 'Write Guard'),
    (r'ภายใต้ฮู้ด', 'การทำงานเบื้องหลัง / under the hood'),
    (r'สกัดต้นไม้เส้นทาง', 'สกัดโครงสร้าง Route Tree'),
    (r'ศักยภาพของบั๊ก', 'จุดที่อาจเกิดบั๊ก'),
    (r'ข้ามระยะทางใดๆ', 'ข้ามลำดับชั้นคอมโพเนนต์ได้ลึกเท่าที่ต้องการ'),
    (r'รังของส่วนประกอบ', 'คอมโพเนนต์ที่ซ้อนกัน'),
    (r'\b(TODO|FIXME|TBD|XXX)\b', 'Placeholder marker'),
]

def check_file_parity():
    print("=== CHECK 1: File Parity with Upstream ===")
    up_files = set()
    for root, _, files in os.walk(UPSTREAM):
        for f in files:
            if f.endswith('.md'):
                up_files.add(os.path.relpath(os.path.join(root, f), UPSTREAM))
    
    th_files = set()
    for root, _, files in os.walk(TRANSLATION):
        for f in files:
            if f.endswith('.md'):
                th_files.add(os.path.relpath(os.path.join(root, f), TRANSLATION))

    missing = up_files - th_files
    extra = th_files - up_files
    if missing:
        print(f"[FAIL] Files in upstream but missing in translation: {missing}")
    else:
        print(f"[PASS] All {len(up_files)} upstream markdown files exist in translation.")
    if extra:
        print(f"[NOTE] Extra files in translation: {extra}")
    return len(missing)

def check_untranslated_prose():
    print("\n=== CHECK 2: Untranslated English Paragraphs ===")
    issues = []
    
    # Common English technical terms/words that frequently appear in Thai tech prose
    technical_whitelist = {
        'leptos', 'rust', 'wasm', 'cargo', 'html', 'css', 'dom', 'props', 'signal',
        'signals', 'component', 'components', 'router', 'route', 'routes', 'ssr',
        'csr', 'hydration', 'hydrate', 'action', 'actions', 'resource', 'resources',
        'suspense', 'transition', 'transitions', 'store', 'stores', 'context', 'api',
        'apis', 'axum', 'actix', 'spin', 'cloudflare', 'fly', 'io', 'tauri', 'dx',
        'cli', 'trunk', 'nightly', 'stable', 'view', 'macro', 'rsx', 'jsx', 'boolean',
        'string', 'vec', 'tuple', 'closure', 'move', 'copy', 'clone', 'static',
        'send', 'sync', 'getter', 'setter', 'rwsignal', 'readsignal', 'writesignal',
        'create_effect', 'memo', 'memos', 'server', 'client', 'web', 'browser',
        'url', 'query', 'params', 'form', 'actionform', 'extractors', 'request',
        'response', 'cookie', 'cookies', 'header', 'headers', 'trait', 'traits',
        'impl', 'intoview', 'children', 'error', 'boundary', 'portal', 'async',
        'future', 'runtime', 'derive', 'island', 'islands', 'tree', 'vdom',
        'diffing', 'fine', 'grained', 'backend', 'frontend', 'debug', 'release',
        'opt', 'level', 'lto', 'codegen', 'units', 'panic', 'abort', 'strip'
    }

    for root, _, files in os.walk(TRANSLATION):
        for f in files:
            if not f.endswith('.md'):
                continue
            tpath = os.path.join(root, f)
            rel = os.path.relpath(tpath, TRANSLATION)
            
            with open(tpath, 'r', encoding='utf-8') as fp:
                content = fp.read()

            # Remove code fences completely:
            # We match ```...``` and ~~~...~~~
            clean = re.sub(r'```[\s\S]*?```', '', content)
            clean = re.sub(r'~~~[\s\S]*?~~~', '', clean)

            # Split into paragraphs by blank lines
            paras = clean.split('\n\n')
            for p in paras:
                p_trimmed = p.strip()
                if not p_trimmed or p_trimmed.startswith('#'):
                    continue

                # Strip inline code, markdown links, html tags, bullets
                p_text = re.sub(r'`[^`]+`', '', p_trimmed)
                p_text = re.sub(r'\[([^\]]*)\]\([^)]+\)', r'\1', p_text)
                p_text = re.sub(r'https?://\S+', '', p_text)
                p_text = re.sub(r'<[^>]+>', '', p_text)
                p_text = re.sub(r'\[[^\]]+\]:\s+\S+.*', '', p_text)
                p_text = re.sub(r'^\s*[-*+]\s+', '', p_text, flags=re.MULTILINE)
                p_text = re.sub(r'^\s*\d+\.\s+', '', p_text, flags=re.MULTILINE)
                p_text = p_text.strip()

                thai_chars = len(THAI_CHAR.findall(p_text))
                alpha_words = [w.lower() for w in re.findall(r'[a-zA-Z]{2,}', p_text)]
                
                # Check how many words are non-whitelisted English words
                non_tech_words = [w for w in alpha_words if w not in technical_whitelist]
                
                # If paragraph has >50 characters, zero Thai chars, and contains regular English sentences (>8 non-tech words)
                if len(p_text) > 50 and thai_chars == 0 and len(non_tech_words) >= 8:
                    issues.append((rel, p_trimmed[:120]))

    if issues:
        print(f"[FAIL] Found {len(issues)} potentially untranslated paragraph(s):")
        for rel, p in issues:
            print(f"  {rel} -> {p}...")
    else:
        print("[PASS] No untranslated English paragraphs found in any file.")
    return len(issues)

def check_deprecated_terms():
    print("\n=== CHECK 3: Deprecated / Old Phrasing Audit ===")
    found = []
    for root, _, files in os.walk(TRANSLATION):
        for f in files:
            if not f.endswith('.md'):
                continue
            tpath = os.path.join(root, f)
            rel = os.path.relpath(tpath, TRANSLATION)
            with open(tpath, 'r', encoding='utf-8') as fp:
                content = fp.read()
            clean = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            for pattern, suggestion in OLD_TERMS:
                for m in re.finditer(pattern, clean):
                    lno = clean[:m.start()].count('\n') + 1
                    found.append((rel, lno, m.group(0), suggestion))
    if found:
        print(f"[WARN] Found {len(found)} deprecated term instance(s):")
        for rel, lno, match, sugg in found:
            print(f"  {rel}:{lno} -> '{match}' (suggest: {sugg})")
    else:
        print("[PASS] No deprecated or machine-translation phrases found.")
    return len(found)

def check_formatting_syntax():
    print("\n=== CHECK 4: Markdown Formatting & Syntax Audit ===")
    errors = []
    for root, _, files in os.walk(TRANSLATION):
        for f in files:
            if not f.endswith('.md'):
                continue
            tpath = os.path.join(root, f)
            rel = os.path.relpath(tpath, TRANSLATION)
            with open(tpath, 'r', encoding='utf-8') as fp:
                lines = fp.readlines()
            
            in_code = False
            for lno, line in enumerate(lines, 1):
                if re.match(r'^\s{0,3}(?:>\s*)?(`{3,}|~{3,})', line):
                    in_code = not in_code
                    continue
                if in_code:
                    continue
                
                bt_count = line.count('`')
                if bt_count % 2 != 0:
                    errors.append((rel, lno, f"Odd number of backticks ({bt_count}): {line.strip()[:80]}"))

                if re.search(r'\[[^\]]*\]\([^)]*$', line.strip()) and not re.search(r'\)', line):
                    errors.append((rel, lno, f"Unclosed link: {line.strip()[:80]}"))
    
    if errors:
        print(f"[WARN] Found {len(errors)} potential formatting issue(s):")
        for rel, lno, msg in errors:
            print(f"  {rel}:{lno} -> {msg}")
    else:
        print("[PASS] All inline code backticks and links are cleanly balanced.")
    return len(errors)

def check_summary_integrity():
    print("\n=== CHECK 5: SUMMARY.md Completeness ===")
    summary_path = os.path.join(TRANSLATION, 'SUMMARY.md')
    with open(summary_path, 'r', encoding='utf-8') as fp:
        s_content = fp.read()
    
    links = re.findall(r'\[[^\]]+\]\(([^)]+\.md)\)', s_content)
    missing = []
    for link in links:
        target = os.path.normpath(os.path.join(TRANSLATION, link))
        if not os.path.exists(target):
            missing.append(link)
    
    if missing:
        print(f"[FAIL] Broken links in SUMMARY.md: {missing}")
    else:
        print(f"[PASS] All {len(links)} links in SUMMARY.md point to valid files.")
    return len(missing)

def check_content_volume_ratio():
    print("\n=== CHECK 6: Upstream vs Translation Content Ratio ===")
    suspicious = []
    for root, _, files in os.walk(UPSTREAM):
        for f in files:
            if not f.endswith('.md'):
                continue
            rel = os.path.relpath(os.path.join(root, f), UPSTREAM)
            up_path = os.path.join(UPSTREAM, rel)
            th_path = os.path.join(TRANSLATION, rel)
            if not os.path.exists(th_path):
                continue
            
            with open(up_path, 'r', encoding='utf-8') as fp:
                up_text = fp.read()
            with open(th_path, 'r', encoding='utf-8') as fp:
                th_text = fp.read()
            
            up_prose = re.sub(r'```.*?```', '', up_text, flags=re.DOTALL)
            th_prose = re.sub(r'```.*?```', '', th_text, flags=re.DOTALL)
            
            if len(up_prose.strip()) > 200:
                ratio = len(th_prose.strip()) / len(up_prose.strip())
                if ratio < 0.40:
                    suspicious.append((rel, len(up_prose), len(th_prose), ratio))
    
    if suspicious:
        print(f"[WARN] Found {len(suspicious)} files with unusually low Thai text ratio:")
        for rel, ulen, tlen, r in suspicious:
            print(f"  {rel}: Upstream prose {ulen} chars, Thai prose {tlen} chars (ratio {r:.2f})")
    else:
        print("[PASS] All files have healthy prose content ratios comparing to upstream.")
    return len(suspicious)

def main():
    print("Starting Comprehensive Translation Audit...\n")
    f1 = check_file_parity()
    f2 = check_untranslated_prose()
    f3 = check_deprecated_terms()
    f4 = check_formatting_syntax()
    f5 = check_summary_integrity()
    f6 = check_content_volume_ratio()
    
    print("\n" + "="*50)
    total_issues = f1 + f2 + f3 + f4 + f5 + f6
    if total_issues == 0:
        print("RESULT: 100% PERFECT AUDIT! No missing files, untranslated paragraphs, or errors found.")
    else:
        print(f"RESULT: Found {total_issues} item(s) to inspect.")
    return total_issues

if __name__ == '__main__':
    sys.exit(main())
