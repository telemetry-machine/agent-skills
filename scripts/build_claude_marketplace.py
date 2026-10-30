#!/usr/bin/env python3
"""Build the hosted Claude Code marketplace: a plugin zip and a marketplace.json that points at it.

Users add the hosted marketplace by URL, so Claude Code downloads only marketplace.json.
Relative plugin sources can't resolve there, so each plugin becomes an `archive` source:
a zip pinned by its sha256.
"""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


DEFAULT_REPO_ROOT = Path(".")
DEFAULT_OUTPUT_ROOT = Path("dist/claude-plugin")
DEFAULT_BASE_URL = "https://telemetrymachine.com/docs/skills"

# Only what Claude Code loads goes into the zip; the Codex and Cursor manifests stay out.
PLUGIN_CONTENT = (".claude-plugin", "skills")

# A fixed timestamp makes the zip, and so its sha256, depend only on the files.
ZIP_DATE_TIME = (1980, 1, 1, 0, 0, 0)


def build_plugin_zip(plugin_root: Path, destination: Path) -> str:
    files = sorted(
        path
        for top in PLUGIN_CONTENT
        for path in (plugin_root / top).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    if not (plugin_root / ".claude-plugin" / "plugin.json").is_file():
        raise ValueError(f"{plugin_root} has no .claude-plugin/plugin.json")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(plugin_root).as_posix(), ZIP_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            executable = path.stat().st_mode & 0o111
            info.external_attr = (0o100755 if executable else 0o100644) << 16
            archive.writestr(info, path.read_bytes())

    return hashlib.sha256(destination.read_bytes()).hexdigest()


def build_marketplace(repo_root: Path, output_root: Path, base_url: str) -> dict:
    marketplace = json.loads((repo_root / ".claude-plugin" / "marketplace.json").read_text())
    output_root.mkdir(parents=True, exist_ok=True)

    for entry in marketplace["plugins"]:
        source = entry["source"]
        if not isinstance(source, str) or not source.startswith("./"):
            raise ValueError(f"plugin {entry['name']!r} needs a relative source to package")

        plugin_root = repo_root / source
        version = json.loads((plugin_root / ".claude-plugin" / "plugin.json").read_text())["version"]
        zip_name = f"{entry['name']}-{version}.zip"
        sha256 = build_plugin_zip(plugin_root, output_root / zip_name)

        entry["source"] = {
            "source": "archive",
            "url": f"{base_url.rstrip('/')}/releases/{version}/{zip_name}",
            "sha256": sha256,
        }
        # plugin.json inside the zip carries the version; Claude Code warns when both set it.
        entry.pop("version", None)

    (output_root / "marketplace.json").write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
    return marketplace


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the hosted Telemetry Machine Claude Code marketplace")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="URL of the skills prefix that hosts releases/")
    args = parser.parse_args()

    build_marketplace(args.repo_root, args.output, args.base_url)


if __name__ == "__main__":
    main()
