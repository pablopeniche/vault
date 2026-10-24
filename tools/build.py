#!/usr/bin/env python3
"""Build the site pages from the report markdown: index.html (the rig) and report.html.

Stdlib only. Usage: python3 tools/build.py
Markdown lives in reports/, diagrams in figures/, page shells in tools/.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "figures"

PAGES = [
    {
        "source": ROOT / "reports" / "rig.md",
        "shell": ROOT / "tools" / "rig-shell.html",
        "out": ROOT / "index.html",
        "toc": {
            1: "The rig",
            2: "Five checks",
            3: "Dictation",
            4: "Typing",
            5: "Commands and agents",
            6: "If a piece is missing",
            7: "Options scored",
            8: "In reserve",
            9: "Not proven yet",
            10: "Sources",
        },
        # Short sections that continue on the same printed page.
        "flow": {5, 8},
        # Figure file -> prefix of the block it follows.
        "figures": {
            "rig-checks.html": "Five checks run at once",
            "rig-dictation.html": "The check runs on the earbud itself",
            "rig-keystroke.html": "Forearm muscles fire about 150 ms before",
        },
    },
    {
        "source": ROOT / "reports" / "agents.md",
        "shell": ROOT / "tools" / "agents-shell.html",
        "out": ROOT / "agents.html",
        "toc": {
            1: "The chain",
            2: "Five rules",
            3: "When you get asked",
            4: "One trace record",
            5: "What exists, what's new",
            6: "Open problems",
            7: "Sources",
        },
        "figures": {
            "command-chain.html": "The master agent is the only agent that receives commands",
        },
    },
    {
        "source": ROOT / "reports" / "Vault always on verification loop.md",
        "shell": ROOT / "tools" / "shell.html",
        "out": ROOT / "report.html",
        "toc": {
            1: "Executive summary",
            2: "Why a gate fails",
            3: "The loop",
            4: "Channels",
            5: "Cross-modal binding",
            6: "Proof of human input",
            7: "Fusion",
            8: "Two reference builds",
            9: "Duress",
            10: "Succession & heirs",
            11: "Law & privacy",
            12: "Market",
            13: "Roadmap",
            14: "Sources",
        },
        "figures": {
            "gate-vs-loop.html": "Five of these eight threats can proceed while the verified owner is present.",
            "loop-architecture.html": "**Anchoring** is the recurring ceremony",
            "cross-modal-binding.html": "The resolution lies in the loop's structure",
            "trust-model.html": "Three refinements make the arithmetic work in practice",
            "two-builds.html": "The signed loop state replaces the presence heartbeat.",
            "duress-layers.html": "The loop's channels give the owner more ways to signal duress covertly",
            "heir-protocol.html": "**Designation** is an owner-signed delegation",
        },
    },
]

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://(?:[^()\s]|\([^()\s]*\))+|[\w-]+\.html(?:#[\w-]+)?)\)")
CITE_RE = re.compile(r"\s*\[(\d+(?:\s*,\s*\d+)*)\](?!\()")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def inline(text):
    text = html.escape(text, quote=False)
    links = []

    def stash_link(m):
        links.append(f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>')
        return f"\x00{len(links) - 1}\x00"

    text = LINK_RE.sub(stash_link, text)

    def cite(m):
        nums = [n.strip() for n in m.group(1).split(",")]
        inner = ", ".join(f'<a href="#ref-{n}">{n}</a>' for n in nums)
        return f'<sup class="cite">[{inner}]</sup>'

    text = CITE_RE.sub(cite, text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = ITALIC_RE.sub(r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: links[int(m.group(1))], text)


def table(lines):
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines]
    head, body = rows[0], rows[2:]
    wide = " wide" if len(head) >= 6 else ""
    out = [f'<div class="table-wrap{wide}"><table>', "<thead><tr>"]
    out += [f'<th scope="col">{inline(c)}</th>' for c in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>")
        out.append(f'<th scope="row">{inline(r[0])}</th>')
        out += [f"<td>{inline(c)}</td>" for c in r[1:]]
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def blocks(md_lines):
    """Group lines into (kind, payload) blocks."""
    i = 0
    while i < len(md_lines):
        line = md_lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("|"):
            j = i
            while j < len(md_lines) and md_lines[j].startswith("|"):
                j += 1
            yield "table", md_lines[i:j]
            i = j
        elif re.match(r"\d+\. ", line):
            j = i
            while j < len(md_lines) and re.match(r"\d+\. ", md_lines[j]):
                j += 1
            yield "ol", md_lines[i:j]
            i = j
        elif line.startswith("- "):
            j = i
            while j < len(md_lines) and md_lines[j].startswith("- "):
                j += 1
            yield "ul", md_lines[i:j]
            i = j
        elif line.startswith("#"):
            yield "heading", line
            i += 1
        else:
            yield "p", line
            i += 1


def figure_for(text, figures):
    for name, prefix in figures.items():
        if text.startswith(prefix):
            return (FIGURES / name).read_text()
    return ""


def render_body(md_lines, toc_labels, figures, flow=()):
    out, toc = [], []
    in_section = False
    section_num = 0
    for kind, payload in blocks(md_lines):
        if kind == "heading":
            level = len(payload) - len(payload.lstrip("#"))
            text = payload.lstrip("#").strip()
            if level == 2:
                m = re.match(r"(\d+)\. (.+)", text)
                section_num, title = int(m.group(1)), m.group(2)
                label = toc_labels[section_num]
                sid = slug(label)
                toc.append((sid, label))
                headline = title
                if ": " in title:
                    headline = title.split(": ", 1)[1]
                    headline = headline[0].upper() + headline[1:]
                if in_section:
                    out.append("</section>")
                cls = ' class="flow"' if section_num in flow else ""
                out.append(f'<section id="{sid}"{cls} aria-labelledby="{sid}-h">')
                out.append(f'<span class="section-num">{section_num:02d} · {html.escape(label)}</span>')
                out.append(f'<h2 id="{sid}-h">{inline(headline)}</h2>')
                in_section = True
            elif level == 3:
                out.append(f'<h3 id="{slug(text)}">{inline(text)}</h3>')
        elif kind == "table":
            out.append(table(payload))
        elif kind == "ul":
            out.append("<ul>" + "".join(f"<li>{inline(item[2:])}</li>" for item in payload) + "</ul>")
        elif kind == "ol":
            if toc_labels[section_num] == "Sources":
                out.append('<ol class="sources">')
                for item in payload:
                    n, rest = item.split(". ", 1)
                    out.append(f'<li id="ref-{n}" value="{n}">{inline(rest)}</li>')
            else:
                out.append('<ol class="findings">')
                out += [f"<li><div>{inline(item.split('. ', 1)[1])}</div></li>" for item in payload]
            out.append("</ol>")
        else:
            out.append(f"<p>{inline(payload)}</p>")
            out.append(figure_for(payload, figures))
    if in_section:
        out.append("</section>")
    return "\n".join(o for o in out if o), toc


def build(page):
    lines = page["source"].read_text().splitlines()
    title = lines[0].lstrip("#").strip()
    # Front matter: the bottom-line paragraph and the labelling note sit before section 1.
    first_section = next(i for i, l in enumerate(lines) if l.startswith("## "))
    front = [l for l in lines[1:first_section] if l.strip()]
    bottom_line, note = front[0], front[1].strip("*")

    body, toc = render_body(lines[first_section:], page["toc"], page["figures"], page.get("flow", ()))
    toc_html = "\n".join(f'<li><a href="#{sid}">{html.escape(label)}</a></li>' for sid, label in toc)

    out = page["shell"].read_text()
    out = out.replace("{{TITLE}}", inline(title))
    out = out.replace("{{BOTTOM_LINE}}", inline(bottom_line))
    out = out.replace("{{NOTE}}", inline(note))
    out = out.replace("{{TOC}}", toc_html)
    out = out.replace("{{SOURCE_COUNT}}", str(len(re.findall(r'<li id="ref-', body))))
    out = out.replace("{{BODY}}", body)
    page["out"].write_text(out)
    cites = len(re.findall(r'class="cite"', body))
    print(f"wrote {page['out'].relative_to(ROOT)}: {len(toc)} sections, {cites} citation groups")


def main():
    for page in PAGES:
        build(page)


if __name__ == "__main__":
    main()
