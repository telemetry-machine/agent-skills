import hashlib
import json
import os
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

import build_claude_marketplace


def write_repo(root: Path) -> None:
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps(
            {
                "name": "telemetry-machine-plugins",
                "owner": {"name": "Telemetry Machine"},
                "plugins": [
                    {
                        "name": "telemetry-machine",
                        "source": "./telemetry-machine",
                        "description": "Skills",
                        "version": "1.2.3",
                    }
                ],
            }
        )
    )
    plugin = root / "telemetry-machine"
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / ".claude-plugin" / "plugin.json").write_text('{"name": "telemetry-machine", "version": "1.2.3"}')
    (plugin / ".codex-plugin").mkdir()
    (plugin / ".codex-plugin" / "plugin.json").write_text("{}")
    scripts = plugin / "skills" / "otel-instrumentation" / "scripts"
    scripts.mkdir(parents=True)
    (plugin / "skills" / "otel-instrumentation" / "SKILL.md").write_text("# Skill\n")
    script = scripts / "start-collector.sh"
    script.write_text("#!/usr/bin/env bash\n")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)


class BuildClaudeMarketplaceTest(unittest.TestCase):
    def test_points_each_plugin_at_a_pinned_zip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_repo(root)
            output = root / "dist"

            build_claude_marketplace.build_marketplace(root, output, "https://example.com/docs/skills/")

            marketplace = json.loads((output / "marketplace.json").read_text())
            entry = marketplace["plugins"][0]
            zip_path = output / "telemetry-machine-1.2.3.zip"
            self.assertEqual(
                entry["source"],
                {
                    "source": "archive",
                    "url": "https://example.com/docs/skills/releases/1.2.3/telemetry-machine-1.2.3.zip",
                    "sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
                },
            )
            self.assertNotIn("version", entry)
            self.assertEqual(entry["description"], "Skills")

    def test_zip_holds_only_the_claude_plugin(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_repo(root)
            zip_path = root / "plugin.zip"

            build_claude_marketplace.build_plugin_zip(root / "telemetry-machine", zip_path)

            with zipfile.ZipFile(zip_path) as archive:
                self.assertEqual(
                    archive.namelist(),
                    [
                        ".claude-plugin/plugin.json",
                        "skills/otel-instrumentation/SKILL.md",
                        "skills/otel-instrumentation/scripts/start-collector.sh",
                    ],
                )
                mode = archive.getinfo("skills/otel-instrumentation/scripts/start-collector.sh").external_attr >> 16
                self.assertTrue(mode & stat.S_IXUSR)

    def test_same_files_give_the_same_sha256(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_repo(root)

            skill = root / "telemetry-machine" / "skills" / "otel-instrumentation" / "SKILL.md"
            first = build_claude_marketplace.build_plugin_zip(root / "telemetry-machine", root / "a.zip")
            os.utime(skill, (0, 0))
            second = build_claude_marketplace.build_plugin_zip(root / "telemetry-machine", root / "b.zip")

            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
