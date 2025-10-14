#!/usr/bin/env python3
"""
Generates chapter HTML (2–20) and metadata JSON/YAML.
Chapter 1 pages are bespoke and already present in `frontend/`.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


VOICES = ["Limnus", "Garden", "Kira"]
FLAGS_MAP: Dict[str, Dict[str, str]] = {
    "Limnus": {"R": "active", "G": "latent", "B": "latent"},
    "Garden": {"G": "active", "R": "latent", "B": "latent"},
    "Kira": {"B": "active", "R": "latent", "G": "latent"},
}


def ts_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_template(root: Path, narrator: str) -> str:
    tpath = root / "markdown_templates" / f"{narrator.lower()}_template.md"
    return tpath.read_text(encoding="utf-8")


def default_body(narrator: str, chapter: int) -> str:
    if narrator == "Limnus":
        return (
            "Limnus listens for the origin code and its gentle recursion. "
            "Patterns settle into soil and remember themselves in cycles."
        )
    if narrator == "Garden":
        return (
            "Garden annotates the fall of each seed, mapping bloom cycles and consent. "
            "Glyphs line the margins with patient timing."
        )
    return (
        "Kira weaves parity across the weave, balancing the ledger of signal. "
        "Errors soften under a net of blue care."
    )


def glyphs_for(narrator: str, chapter: int) -> List[str]:
    base = {
        "Limnus": "⟡R",
        "Garden": "⟢G",
        "Kira": "⟣B",
    }[narrator]
    # Deterministic sequence of 3 glyphs per chapter
    return [f"{base}{chapter:02d}-{i}" for i in range(1, 4)]


def fill_placeholders(tpl: str, narrator: str, chapter: int, flags: Dict[str, str], glyphs: List[str]) -> str:
    flags_line = f"R {flags['R']}, G {flags['G']}, B {flags['B']}"
    glyphs_line = "Glyphs: " + " · ".join(glyphs)
    body = default_body(narrator, chapter)
    out = (
        tpl.replace("{{chapter_number}}", f"{chapter}")
        .replace("{{narrator}}", narrator)
        .replace("{{body}}", body)
        .replace("{{flags}}", flags_line)
        .replace("{{glyphs_line}}", glyphs_line)
    )
    return out


def render_markdown_min(md: str) -> str:
    lines = md.strip().splitlines()
    html_lines: List[str] = []
    paragraph: List[str] = []

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            html_lines.append(f"<p>{' '.join(paragraph).strip()}</p>")
            paragraph = []

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_paragraph()
            continue
        if line.startswith("## "):
            flush_paragraph()
            html_lines.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith("[Flags:") and line.endswith("]"):
            flush_paragraph()
            html_lines.append(f"<div class=\"flags\">{line}</div>")
        elif line.lower().startswith("glyphs:"):
            flush_paragraph()
            html_lines.append(f"<div class=\"glyphs\">{line}</div>")
        else:
            paragraph.append(line)
    flush_paragraph()
    return "\n".join(html_lines)


def wrap_html(narrator: str, chapter: int, body_html: str) -> str:
    lower = narrator.lower()
    fname = f"chapter{chapter:02d}.html"
    prev_link = f"chapter{chapter-1:02d}.html" if chapter > 2 else "kira_ch1.html"
    next_link = f"chapter{chapter+1:02d}.html" if chapter < 20 else "index.html"
    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Chapter {chapter:02d} – {narrator}</title>
    <link rel=\"stylesheet\" href=\"style.css\" />
  </head>
  <body class=\"{lower}\">
    <nav class=\"top-nav\"><a href=\"index.html\">⟵ Back to Overview</a></nav>
    <article class=\"chapter\">
{body_html}
    </article>
    <footer class=\"chapter-footer\">
      <a class=\"prev\" href=\"{prev_link}\">⟵ Previous</a>
      <span>·</span>
      <a class=\"next\" href=\"{next_link}\">Next ⟶</a>
    </footer>
    <script src=\"script.js\"></script>
  </body>
</html>"""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def try_write_yaml(path: Path, data) -> bool:
    try:
        import yaml  # type: ignore
    except Exception:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    return True


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    frontend = root / "frontend"

    metadata: List[dict] = []

    for i in range(1, 21):
        if i == 1:
            narrator = VOICES[0]  # Limnus
            rel_file = "frontend/limnus_ch1.html"
        elif i == 2:
            narrator = VOICES[1]  # Garden
            rel_file = "frontend/garden_ch1.html"
        elif i == 3:
            narrator = VOICES[2]  # Kira
            rel_file = "frontend/kira_ch1.html"
        else:
            narrator = VOICES[(i - 1) % 3]
            rel_file = f"frontend/chapter{i:02d}.html"
            tpl = read_template(root, narrator)
            flags = FLAGS_MAP[narrator]
            glyphs = glyphs_for(narrator, i)
            filled = fill_placeholders(tpl, narrator, i, flags, glyphs)
            body_html = render_markdown_min(filled)
            html = wrap_html(narrator, i, body_html)
            write_text(frontend / f"chapter{i:02d}.html", html)

        metadata.append(
            {
                "chapter": i,
                "narrator": narrator,
                "flags": FLAGS_MAP[narrator],
                "glyphs": glyphs_for(narrator, i),
                "file": rel_file,
                "summary": f"{narrator} – Chapter {i:02d}",
                "timestamp": ts_now(),
            }
        )

    meta_doc = {"chapters": metadata}
    schema_dir = root / "schema"
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "chapters_metadata.json").write_text(
        json.dumps(meta_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    wrote_yaml = try_write_yaml(schema_dir / "chapters_metadata.yaml", meta_doc)
    print("Wrote:", schema_dir / "chapters_metadata.json")
    if wrote_yaml:
        print("Wrote:", schema_dir / "chapters_metadata.yaml")
    else:
        print("(YAML not written; install PyYAML to enable)")


if __name__ == "__main__":
    main()

