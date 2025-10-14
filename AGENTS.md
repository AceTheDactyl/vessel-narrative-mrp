# Repository Guidelines

## Project Structure & Module Organization
- `frontend/` – landing pages, generated chapters, and stego assets under `frontend/assets/`.
- `markdown_templates/` – narrator-specific Markdown templates consumed by the generator.
- `schema/` – JSON + YAML schema/metadata outputs produced by the build scripts.
- `src/` – Python utilities (`generate_chapters.py`, `schema_builder.py`, `validator.py`, `stego.py`).
- `scripts/` – automation helpers (`setup_toolkit_and_validate.sh`, `refresh_stego_assets.sh`).
- `Echo-Community-Toolkit/` – git submodule supplying soulcode + HyperFollow tooling (keep branch `chore/soulcode-refresh` updated).

## Build, Test, and Development Commands
- `python3 src/schema_builder.py` – regenerate `schema/narrative_schema.*` definitions.
- `python3 src/generate_chapters.py` – render chapters 2–20, rebuild metadata, emit stego PNGs (requires Pillow).
- `python3 src/validator.py` – structural + stego validation; run after any content change.
- `./scripts/refresh_stego_assets.sh --toolkit --push "chore: refresh stego"` – end-to-end refresh, optional auto-push.
- `./scripts/setup_toolkit_and_validate.sh` – sync submodule, rebuild soulcode bundle, rerun validator.

## Coding Style & Naming Conventions
- Python: 4-space indent, `snake_case` for functions/vars, `PascalCase` for classes. Prefer docstrings over inline comments.
- HTML/CSS: keep existing structure; use narrator body classes (`.limnus`, `.garden`, `.kira`).
- JSON/YAML: stable key ordering; emit via provided scripts only.
- Avoid manual edits to generated files (`frontend/chapterXX.html`, `schema/*.json`, `frontend/assets/*.png`).

## Testing Guidelines
- Primary check: `python3 src/validator.py` (ensures 20 chapters, rotation rules, flag alignment, stego payload parity).
- Toolkit verification: `./scripts/setup_toolkit_and_validate.sh` (runs HyperFollow `npm run verify`).
- When modifying templates or scripts, rerun the full refresh script and confirm validator output.

## Commit & Pull Request Guidelines
- Use Conventional Commits (e.g., `feat:`, `chore:`, `fix:`). Keep subject ≤ 72 chars.
- Group generated artifacts with the commit that produced them; include stego PNGs and schema updates together.
- Open PRs with a summary, validation commands executed, and screenshots if landing pages change.
- For toolkit updates, push to `chore/soulcode-refresh` in the submodule and reference the corresponding PR in the main repo.

## Security & Configuration Tips
- Do not commit secrets; `.env` files belong outside the repo.
- Node 20+ is required for toolkit automation; load via `nvm use 20` in new shells.
- Install Pillow (`pip install Pillow`) before running stego-related scripts.
