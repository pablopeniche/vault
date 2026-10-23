#!/usr/bin/env python3
"""Build index.html from the research report markdown.

Stdlib only. Usage: python3 tools/build.py
The report lives in reports/, diagrams in figures/, and the page shell below.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "Vault biometric access architectures.md"
FIGURES = ROOT / "figures"
OUT = ROOT / "index.html"

TOC_LABELS = {
    1: "Executive summary",
    2: "Threat model",
    3: "Architectures",
    4: "Identity modalities",
    5: "Liveness & injection",
    6: "Duress & coercion",
    7: "Succession & heirs",
    8: "Law & ethics",
    9: "Market & competitors",
    10: "v0 architecture & next steps",
    11: "Sources",
}

# Figure file -> prefix of the block it follows.
FIGURE_AFTER = {
    "session-timeline.html": "The human half does not exist as a product.",
    "trust-model.html": "The literature on continuous authentication converges",
    "duress-layers.html": "The notes turn these lessons into a proposed response policy",
    "heir-protocol.html": "No standard exists for \"biometric heirs,\"",
    "v0-architecture.html": "The v0 design below assembles the evidence",
}

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://(?:[^()\s]|\([^()\s]*\))+)\)")
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
        elif line.startswith("#"):
            yield "heading", line
            i += 1
        else:
            yield "p", line
            i += 1


def figure_for(text):
    for name, prefix in FIGURE_AFTER.items():
        if text.startswith(prefix):
            return (FIGURES / name).read_text()
    return ""


def render_body(md_lines):
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
                label = TOC_LABELS[section_num]
                sid = slug(label)
                toc.append((sid, label))
                headline = title
                if ": " in title:
                    headline = title.split(": ", 1)[1]
                    headline = headline[0].upper() + headline[1:]
                if in_section:
                    out.append("</section>")
                out.append(f'<section id="{sid}" aria-labelledby="{sid}-h">')
                out.append(f'<span class="section-num">{section_num:02d} · {html.escape(label)}</span>')
                out.append(f'<h2 id="{sid}-h">{inline(headline)}</h2>')
                in_section = True
            elif level == 3:
                out.append(f'<h3 id="{slug(text)}">{inline(text)}</h3>')
        elif kind == "table":
            out.append(table(payload))
        elif kind == "ol":
            if section_num == 11:
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
            out.append(figure_for(payload))
    if in_section:
        out.append("</section>")
    return "\n".join(o for o in out if o), toc


def main():
    lines = REPORT.read_text().splitlines()
    title = lines[0].lstrip("#").strip()
    # Front matter: the bottom-line paragraph and the labelling note sit before section 1.
    first_section = next(i for i, l in enumerate(lines) if l.startswith("## "))
    front = [l for l in lines[1:first_section] if l.strip()]
    bottom_line, note = front[0], front[1].strip("*")

    body, toc = render_body(lines[first_section:])
    toc_html = "\n".join(f'<li><a href="#{sid}">{html.escape(label)}</a></li>' for sid, label in toc)

    page = (ROOT / "tools" / "shell.html").read_text()
    page = page.replace("{{TITLE}}", inline(title))
    page = page.replace("{{BOTTOM_LINE}}", inline(bottom_line))
    page = page.replace("{{NOTE}}", inline(note))
    page = page.replace("{{TOC}}", toc_html)
    page = page.replace("{{BODY}}", body)
    OUT.write_text(page)
    cites = len(re.findall(r'class="cite"', body))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(toc)} sections, {cites} citation groups")


if __name__ == "__main__":
    main()
