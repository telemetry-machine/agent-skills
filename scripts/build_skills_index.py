#!/usr/bin/env python3
"""Write index.json next to the skills, for agents that download them instead of installing the plugin.

telemetrymachine.com/docs/skills/ serves the skills directory from this repo's main branch, index.json
included, so it's committed; CI runs this with --check to catch an index that wasn't updated.
"""
import argparse
import json
import re
from pathlib import Path


DEFAULT_SKILLS_ROOT = Path("telemetry-machine/skills")


class SkillMetadataError(ValueError):
    pass


def _collapse_description(lines: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(line.strip() for line in lines).strip())


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_skill_metadata(skill_md: Path) -> dict[str, str]:
    lines = skill_md.read_text().splitlines()
    if not lines or lines[0] != "---":
        raise SkillMetadataError(f"{skill_md} is missing YAML frontmatter")

    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise SkillMetadataError(f"{skill_md} has unterminated YAML frontmatter") from exc

    frontmatter = lines[1:end]
    metadata: dict[str, str] = {}
    index = 0
    while index < len(frontmatter):
        line = frontmatter[index]
        if line.startswith("name:"):
            metadata["name"] = _strip_quotes(line.split(":", 1)[1].strip())
            index += 1
            continue

        if line.startswith("description:"):
            raw_value = line.split(":", 1)[1].strip()
            if raw_value in {">", ">-", "|", "|-"}:
                block_lines: list[str] = []
                index += 1
                while index < len(frontmatter):
                    next_line = frontmatter[index]
                    if next_line and not next_line.startswith((" ", "\t")):
                        break
                    block_lines.append(next_line)
                    index += 1
                metadata["description"] = _collapse_description(block_lines)
            else:
                metadata["description"] = _strip_quotes(raw_value)
                index += 1
            continue

        index += 1

    missing = [key for key in ("name", "description") if not metadata.get(key)]
    if missing:
        raise SkillMetadataError(f"{skill_md} is missing required metadata: {', '.join(missing)}")

    return metadata


def validate_relative_path(path: str) -> None:
    parts = path.split("/")
    if (
        path.startswith("/")
        or "\\" in path
        or "\x00" in path
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise ValueError(f"unsafe skill path: {path}")


def list_skill_files(skill_dir: Path) -> list[str]:
    files = [path for path in skill_dir.rglob("*") if path.is_file()]
    relative_paths = [path.relative_to(skill_dir).as_posix() for path in files]
    for path in relative_paths:
        validate_relative_path(path)

    if "SKILL.md" not in relative_paths:
        raise ValueError(f"{skill_dir} is missing SKILL.md")

    return sorted(relative_paths, key=lambda path: (path != "SKILL.md", path))


def build_index(skills_root: Path) -> dict[str, list[dict[str, object]]]:
    if not skills_root.is_dir():
        raise ValueError(f"skills root does not exist: {skills_root}")

    skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir() and not path.name.startswith("."))
    if not skill_dirs:
        raise ValueError(f"no skills found in {skills_root}")

    index = {"skills": []}
    for skill_dir in skill_dirs:
        validate_relative_path(skill_dir.name)
        metadata = parse_skill_metadata(skill_dir / "SKILL.md")
        name = metadata["name"]
        if name != skill_dir.name:
            raise ValueError(f"skill name {name!r} does not match directory {skill_dir.name!r}")

        index["skills"].append(
            {
                "name": name,
                "description": metadata["description"],
                "files": list_skill_files(skill_dir),
            }
        )

    return index


def render_index(index: dict[str, list[dict[str, object]]]) -> str:
    return json.dumps(index, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Write the Telemetry Machine skills index")
    parser.add_argument("--skills-root", type=Path, default=DEFAULT_SKILLS_ROOT)
    parser.add_argument("--check", action="store_true", help="fail if index.json is out of date instead of writing it")
    args = parser.parse_args()

    index_path = args.skills_root / "index.json"
    rendered = render_index(build_index(args.skills_root))
    if args.check:
        if not index_path.is_file() or index_path.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"{index_path} is out of date; run python3 scripts/build_skills_index.py")
        return

    index_path.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
