# leptos-th

```
██╗     ███████╗██████╗ ████████╗ ██████╗ ███████╗       ████████╗██╗  ██╗
██║     ██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔════╝       ╚══██╔══╝██║  ██║
██║     █████╗  ██████╔╝   ██║   ██║   ██║███████╗█████╗    ██║   ███████║
██║     ██╔══╝  ██╔═══╝    ██║   ██║   ██║╚════██║╚════╝    ██║   ██╔══██║
███████╗███████╗██║        ██║   ╚██████╔╝███████║          ██║   ██║  ██║
╚══════╝╚══════╝╚═╝        ╚═╝    ╚═════╝ ╚══════╝          ╚═╝   ╚═╝  ╚═╝
```

---

## ◆ PULSE

[![GitHub Pages](https://img.shields.io/badge/Pages-live-2ea44f)](https://suradet-ps.github.io/leptos-th/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#-anatomy)

A Leptos app has a first signal, and a first render - leptos-th is
the Thai bridge to that exact moment. This is the complete Thai
translation of the official Leptos book: 59 chapters built with
mdbook, terminology locked by a single glossary, and every
code block byte-identical to the original. The links are checked
against the built book (706 anchors), the structure mirrors the
upstream repo file-for-file, and the license travels with the text.
Built for the Thai-speaking student of Leptos:
[suradet-ps.github.io/leptos-th](https://suradet-ps.github.io/leptos-th/).

| แปลครบ 60 ไฟล์ ▣ | Glossary ▣ | ลิงก์ 706/706 ▣ | Build ผ่าน ▣ |
|---|---|---|---|

*v1.0.0 - translation, glossary, verification, and the static build
are all sealed.*

> Built with mdbook 0.4 + mdbook-admonish + Markdown, translated from
> [leptos-rs/book](https://github.com/leptos-rs/book),
> verified by script and rendered as static HTML - a book with the
> pages on the page.
>
> **suradet-ps**, artifact keeper

---

## ◆ IGNITION

One runtime, two tools, three commands.

```
⟫ git clone https://github.com/suradet-ps/leptos-th.git
⟫ cd leptos-th
⟫ cargo install mdbook --version 0.4.36 --locked
⟫ cargo install mdbook-admonish --version 1.15.0 --locked
⟫ mdbook serve --open
```

Open [http://localhost:3000](http://localhost:3000).

```
⟫ mdbook build                                  # static HTML into book/
⟫ powershell scripts/check-links.ps1            # all anchors in the built book (pwsh on Linux/macOS)
⟫ powershell scripts/verify-translation.ps1     # byte-exact check vs upstream
```

> The book pins mdbook 0.4 and mdbook-admonish 1.15, the same pair
> the upstream Leptos book builds with. mdbook-admonish needs the
> 0.4.x protocol; newer mdbook versions are not compatible yet.
> On Linux or macOS, run the verification scripts using
> `pwsh scripts/<script>.ps1`. `verify-translation.ps1` checks
> against `leptos-rs/book` in adjacent directories or via
> `-Orig <path>`.

<details>
<summary>Translating a chapter</summary>

A chapter is a file: `src/<chapter>.md`, listed in
`src/SUMMARY.md`. The glossary lives in `GLOSSARY.md` - a term
is chosen once and reused everywhere. Code blocks, commands, links,
and filenames stay verbatim; only prose and headings are translated.
Prose inside `admonish` blocks is translated too, while the directive
and any code nested inside stay untouched. Heading anchors follow
mdbook's slug rules (Thai tone marks are stripped), so anchors are
copied from the built HTML, never guessed. Four upstream links that
pointed at non-existent paths or English anchors are fixed to their
Thai headings in `scripts/verify-translation.ps1` (see
`$knownLinkFixes`).

</details>

---

## ◆ ANATOMY

One stack, zero custom JS, several quiet helpers.

- **Translates** - the complete book: introduction, getting started,
  the view layer, reactivity, testing, async, router, global state,
  SSR, server functions, deployment, islands, and the appendices -
  Thai prose over untouched code.
- **Glossaries** - `GLOSSARY.md` locks the vocabulary (signal =
  สัญญาณ, component = คอมโพเนนต์, hydration = การไฮเดรต), so chapter
  nine agrees with chapter two.
- **Verifies** - `scripts/verify-translation.ps1` diffs every code
  block, admonish directive, heading level, and link target against
  upstream `leptos-rs/book` - byte-exact or it does not pass.
- **Checks** - `scripts/check-links.ps1` walks the built book and
  resolves every anchor link against real heading ids - 706 of them,
  all reachable.
- **Builds** - mdbook + mdbook-admonish renders static HTML into
  `book/`, zero server runtime, readable offline and searchable by
  the built-in static index.
- **Licenses** - MIT, inherited from upstream, with the LICENSE file
  shipped beside the text.

---

## ◆ RITUALS

**The core ceremony** - the translation pass:

1. Open a chapter in `src/`. The upstream `leptos-rs/book` repo sits
   beside it (clone `https://github.com/leptos-rs/book` alongside
   `leptos-th`) - structure is a contract.
2. Translate the prose; keep every code block and command as the
   original wrote it.
3. Consult `GLOSSARY.md` for every term that already has a canon.
   New terms get proposed in the glossary first.
4. Build, verify, check. The book builds clean, the diff is
   byte-exact, and the anchors resolve.

**The ceremony of the anchor** - mdbook slugs strip Thai tone marks
(`การเขียนสคริปต์` becomes `การเขียนสคริปต`). Anchors are read from
the built HTML, written into the source, and re-verified - a guessed
anchor is a broken link waiting to happen.

**The ceremony of the code block** - a translated command that is not
byte-identical to the original is a regression, not a translation.
The verifier is the conscience of the repo.

---

## ◆ ECHOES

**Where this artifact is heading**

```
P1 ▸ SUMMARY + introduction + getting started ────────────────────── ▸ sealed
P2 ▸ view, reactivity, testing, async ─────────────────────────────── ▸ sealed
P3 ▸ router, global state, styling, metadata, wasm-bindgen ────────── ▸ sealed
P4 ▸ SSR, server, progressive enhancement, deployment, islands ────── ▸ sealed
P5 ▸ glossary, license, link verification, mdbook build ───────────── ▸ sealed
```

**Raising the artifact** - the honest path lives in `GLOSSARY.md`
(term canon), `scripts/` (the verification gates), and `book.toml`
(book config). New chapters follow the contract of the `SUMMARY`.
Open an issue first to discuss a change.

**Status** - on every change: `mdbook build` must pass, the
translation verifier must report byte-exact code blocks across all
60 files (59 chapters + `SUMMARY.md`), and the link checker must
report `ALL ANCHOR LINKS OK`.
[Watch the gates](scripts).

---

```
  ─────────────────────────────────────────
   ทุกแอปมีสัญญาณแรกของมัน
   ทุกหนังสือมีหน้าแรกของมัน
  ─────────────────────────────────────────
```

Translated from the [Leptos book](https://github.com/leptos-rs/book),
which is licensed under [MIT](LICENSE).
