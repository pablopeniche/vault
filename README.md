# Vault

Vault is a computer that only one person, and the successors they authorize, can use, and that knows what to do when that person is being coerced.

Vault is not a login gate. It is an always-on loop of several channels at once (wearables, an attested camera and fingerprint sensor, the input devices, the room) that keeps proving a living human is at the keyboard, which human it is, and that every input comes from them. It is designed for everyday laptops and desktops as well as AI-lab terminals.

This repo holds the architecture research report (v2) as a static site. v1, the earlier gate-based design, is kept as [`vault-report-v1.pdf`](vault-report-v1.pdf).

- **The rig (start here):** https://pablopeniche.github.io/vault/ · PDF [`vault-rig.pdf`](vault-rig.pdf)
- **Full research report (v2):** https://pablopeniche.github.io/vault/report.html · PDF [`vault-report.pdf`](vault-report.pdf)
- **Markdown source of the research:** [`reports/`](reports/)

The site is plain HTML and CSS, so GitHub Pages serves it with no build step. `index.html` is the hand-written rig page. `report.html` is generated from the report markdown, the diagrams in `figures/`, and the page shell in `tools/shell.html`. After editing any of them, regenerate it with:

```bash
python3 tools/build.py
```

To preview it locally:

```bash
python3 -m http.server 8793
```

Draft, not for distribution. The site is served with `noindex`.
