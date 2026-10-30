#!/usr/bin/env python3
import argparse
import json
import re
import shutil
from pathlib import Path


DEFAULT_SKILLS_ROOT = Path("telemetry-machine/skills")
DEFAULT_OUTPUT_ROOT = Path("dist/skills")


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
        raise ValueError(f"unsafe bundle path: {path}")


def list_skill_files(skill_dir: Path) -> list[str]:
    files = [path for path in skill_dir.rglob("*") if path.is_file()]
    relative_paths = [path.relative_to(skill_dir).as_posix() for path in files]
    for path in relative_paths:
        validate_relative_path(path)

    if "SKILL.md" not in relative_paths:
        raise ValueError(f"{skill_dir} is missing SKILL.md")

    return sorted(relative_paths, key=lambda path: (path != "SKILL.md", path))


def build_bundle(skills_root: Path, output_root: Path) -> dict[str, list[dict[str, object]]]:
    if not skills_root.is_dir():
        raise ValueError(f"skills root does not exist: {skills_root}")

    skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir() and not path.name.startswith("."))
    if not skill_dirs:
        raise ValueError(f"no skills found in {skills_root}")

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    index = {"skills": []}
    for skill_dir in skill_dirs:
        validate_relative_path(skill_dir.name)
        metadata = parse_skill_metadata(skill_dir / "SKILL.md")
        name = metadata["name"]
        if name != skill_dir.name:
            raise ValueError(f"skill name {name!r} does not match directory {skill_dir.name!r}")

        files = list_skill_files(skill_dir)
        output_skill_dir = output_root / name
        for relative_path in files:
            source = skill_dir / relative_path
            destination = output_skill_dir / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        index["skills"].append(
            {
                "name": name,
                "description": metadata["description"],
                "files": files,
            }
        )

    (output_root / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the public Telemetry Machine skill bundle")
    parser.add_argument("--skills-root", type=Path, default=DEFAULT_SKILLS_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    build_bundle(args.skills_root, args.output)


if __name__ == "__main__":
    main()
