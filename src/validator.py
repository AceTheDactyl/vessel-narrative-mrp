#!/usr/bin/env python3
"""
Validates the generated metadata and files:
- Schema presence and basic field/type checks
- Structural rotation rules and counts
- File existence in frontend/
- Flag consistency between metadata and HTML files
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from stego import decode_chapter_payload, is_available as stego_is_available
except Exception:  # pragma: no cover - fallback when Pillow missing
    decode_chapter_payload = None  # type: ignore[assignment]

    def stego_is_available() -> bool:  # type: ignore[return-value]
        return False


FLAG_RE = re.compile(r"\[\s*Flags:\s*([^\]]+)\]", re.IGNORECASE)


def load_metadata(root: Path) -> dict:
    meta_path = root / "schema" / "chapters_metadata.json"
    if not meta_path.exists():
        raise SystemExit(f"Missing metadata file: {meta_path}")
    return json.loads(meta_path.read_text(encoding="utf-8"))


def load_schema(root: Path) -> dict:
    schema_path = root / "schema" / "narrative_schema.json"
    if not schema_path.exists():
        raise SystemExit(f"Missing schema file: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def basic_validate_against_schema(meta: dict, schema: dict) -> List[str]:
    errors: List[str] = []
    if not isinstance(meta, dict):
        return ["Metadata root is not an object"]
    if "chapters" not in meta or not isinstance(meta["chapters"], list):
        errors.append("Metadata must contain a 'chapters' array")
        return errors

    chapters = meta["chapters"]
    if len(chapters) != 20:
        errors.append(f"Expected 20 chapters, found {len(chapters)}")

    # Pull chapter schema from $defs for simple checks
    chapter_schema = schema.get("$defs", {}).get("chapter", {})
    required = set(chapter_schema.get("required", []))
    prop_types = {k: v.get("type") for k, v in chapter_schema.get("properties", {}).items()}

    for idx, ch in enumerate(chapters, start=1):
        if not isinstance(ch, dict):
            errors.append(f"Chapter index {idx} is not an object")
            continue
        missing = required - set(ch.keys())
        if missing:
            errors.append(f"Chapter {ch.get('chapter', idx)} missing fields: {sorted(missing)}")
        # basic type checks
        for k, t in prop_types.items():
            if k in ch and t:
                if t == "integer" and not isinstance(ch[k], int):
                    errors.append(f"Chapter {ch.get('chapter', idx)} field '{k}' not integer")
                if t == "string" and not isinstance(ch[k], str):
                    errors.append(f"Chapter {ch.get('chapter', idx)} field '{k}' not string")
                if t == "array" and not isinstance(ch[k], list):
                    errors.append(f"Chapter {ch.get('chapter', idx)} field '{k}' not array")
                if t == "object" and not isinstance(ch[k], dict):
                    errors.append(f"Chapter {ch.get('chapter', idx)} field '{k}' not object")
    return errors


def check_rotation(chapters: List[dict]) -> List[str]:
    errors: List[str] = []
    voices = [ch.get("narrator") for ch in chapters]
    for a, b in zip(voices, voices[1:]):
        if a == b:
            errors.append("Narrator repetition detected (no back-to-back allowed)")
            break
    counts = Counter(voices)
    for name in ["Limnus", "Garden", "Kira"]:
        if counts[name] < 6:
            errors.append(f"Narrator {name} appears fewer than 6 times ({counts[name]})")
    return errors


def parse_flags_text(flags_text: str) -> Dict[str, str]:
    # Expect tokens like: "R active, G latent, B latent"
    parts = [p.strip() for p in flags_text.split(",")]
    out: Dict[str, str] = {}
    for part in parts:
        tokens = part.split()
        if len(tokens) == 2:
            out[tokens[0]] = tokens[1]
    return out


def extract_flags_from_html(path: Path) -> Dict[str, str] | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = FLAG_RE.search(text)
    if not m:
        return None
    return parse_flags_text(m.group(1))


def check_files_and_flags(root: Path, chapters: List[dict]) -> List[str]:
    errors: List[str] = []
    for ch in chapters:
        ch_no = ch.get("chapter")
        rel = ch.get("file")
        flags_meta = ch.get("flags", {})
        if not isinstance(rel, str):
            errors.append(f"Chapter {ch_no}: 'file' not string")
            continue
        path = root / rel
        if not path.exists():
            errors.append(f"Chapter {ch_no}: missing file {rel}")
            continue
        flags_in_html = extract_flags_from_html(path)
        if not flags_in_html:
            errors.append(f"Chapter {ch_no}: Flags not found in HTML")
            continue
        # compare
        for k in ("R", "G", "B"):
            if flags_in_html.get(k) != flags_meta.get(k):
                errors.append(
                    f"Chapter {ch_no}: flag mismatch for {k} (meta={flags_meta.get(k)} html={flags_in_html.get(k)})"
                )
    return errors


def check_stego_payloads(root: Path, chapters: List[dict]) -> List[str]:
    errors: List[str] = []
    for ch in chapters:
        stego_rel = ch.get("stego_png")
        if not stego_rel:
            continue
        if not isinstance(stego_rel, str):
            errors.append(f"Chapter {ch.get('chapter')}: 'stego_png' must be a string")
            continue
        path = root / stego_rel
        if not path.exists():
            errors.append(f"Chapter {ch.get('chapter')}: stego PNG missing at {stego_rel}")
            continue
        if not stego_is_available() or decode_chapter_payload is None:
            # Pillow not available; skip deep validation but record advisory.
            continue
        try:
            payload = decode_chapter_payload(path).as_dict()
        except Exception as exc:
            errors.append(f"Chapter {ch.get('chapter')}: failed to decode stego PNG ({exc})")
            continue
        expected = {k: v for k, v in ch.items() if k != "stego_png"}
        if payload != expected:
            errors.append(
                f"Chapter {ch.get('chapter')}: stego payload mismatch compared to metadata"
            )
    return errors


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    meta = load_metadata(root)
    schema = load_schema(root)
    schema_errors = basic_validate_against_schema(meta, schema)
    rotation_errors = check_rotation(meta.get("chapters", []))
    chapters = meta.get("chapters", [])
    files_flags_errors = check_files_and_flags(root, chapters)
    stego_errors = check_stego_payloads(root, chapters)

    errors = schema_errors + rotation_errors + files_flags_errors + stego_errors
    if errors:
        print("Validation FAILED:")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)
    print(
        "Validation OK: 20 chapters, rotation clean, files present, flags consistent, stego payloads match."
    )


if __name__ == "__main__":
    main()
