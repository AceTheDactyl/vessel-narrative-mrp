Codex CLI (Node 20+)

Usage
- From `vessel_narrative_system_final/`, run: `node tools/codex-cli/bin/codex.js --help`
- Optional PATH install: `(cd vessel_narrative_system_final/tools/codex-cli && npm link)` then `codex ...`

Commands
- Echo
  - `codex echo summon`
  - `codex echo mode <squirrel|fox|paradox|mix>`
  - `codex echo status`
  - `codex echo calibrate`

- Garden
  - `codex garden start`
  - `codex garden next`
  - `codex garden ledger`
  - `codex garden log`

- Limnus (LSB via Echo-Community-Toolkit)
  - `codex limnus init | state | update ...`
  - `codex limnus cache "text" [-l L1|L2|L3]`
  - `codex limnus recall <keyword> [--layer ...] [--since ...] [--until ...]`
  - `codex limnus memories [--layer ...] [--since ...] [--until ...] [--limit N] [--json]`
  - `codex limnus export-memories [-o file]` | `import-memories -i file [--replace]`
  - `codex limnus commit-block '<json-or-text>'`
  - `codex limnus view-ledger [--file path]`
  - `codex limnus export-ledger [-o file]` | `import-ledger -i file [--replace] [--rehash]`
  - `codex limnus rehash-ledger [--dry-run] [--file path] [-o out.json]`
  - `codex limnus encode-ledger [-i <ledger.json>] [--file path] -c <cover.png> -o <out.png> [--size 512]`
  - `codex limnus decode-ledger [-i <image.png>] [--file path]`
  - `codex limnus verify-ledger [-i <image.png>] [--file path]`

- Kira
  - `codex kira validate`
  - `codex kira sync`

State & Integration
- State lives in `vessel_narrative_system_final/state/` (shared with the Python CLI).
- LSB encode/decode imports Python modules from `vessel_narrative_system_final/Echo-Community-Toolkit/src`.
- See diagrams: `vessel_narrative_system_final/docs/SYSTEM_DIAGRAM_API_REFERENCE.md`.

