# Vault

Vault is a computer that only one person, and the successors they authorize, can use. It checks who is at the keyboard continuously, not just at login, and it knows what to do when that person is being coerced.

The first market is frontier AI labs: privileged-access terminals for model weights and training infrastructure.

This repo holds the Phase 1 architecture research report as a static site.

- **Read it:** https://pablopeniche.github.io/vault/
- **PDF:** [`vault-report.pdf`](vault-report.pdf)
- **Markdown source of the research:** [`reports/`](reports/)

The site is plain HTML and CSS, so GitHub Pages serves it with no build step. `index.html` is generated from the report markdown, the diagrams in `figures/`, and the page shell in `tools/shell.html`. After editing any of them, regenerate it with:

```bash
python3 tools/build.py
```

To preview it locally:

```bash
python3 -m http.server 8793
```

Draft, not for distribution. The site is served with `noindex`.
