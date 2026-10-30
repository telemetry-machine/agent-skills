import json
import stat
import tempfile
import unittest
from pathlib import Path

import build_skills_bundle


class BuildSkillsBundleTest(unittest.TestCase):
    def test_builds_index_and_copies_skill_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills_root = root / "skills"
            output_root = root / "dist"
            skill = skills_root / "otel-instrumentation"
            references = skill / "references"
            scripts = skill / "scripts"
            references.mkdir(parents=True)
            scripts.mkdir()

            (skill / "SKILL.md").write_text(
                "---\n"
                "name: otel-instrumentation\n"
                "description: >\n"
                "  Add OpenTelemetry instrumentation —\n"
                "  validate it in Telemetry Machine.\n"
                "---\n"
                "# Skill\n"
            )
            (references / "verification-checklist.md").write_text("# Verify\n")
            script = scripts / "start-collector.sh"
            script.write_text("#!/usr/bin/env bash\n")
            script.chmod(script.stat().st_mode | stat.S_IXUSR)

            build_skills_bundle.build_bundle(skills_root, output_root)

            index_text = (output_root / "index.json").read_text()
            self.assertIn("\\u2014", index_text)
            self.assertNotIn("—", index_text)
            index = json.loads(index_text)
            self.assertEqual(
                index,
                {
                    "skills": [
                        {
                            "name": "otel-instrumentation",
                            "description": "Add OpenTelemetry instrumentation — validate it in Telemetry Machine.",
                            "files": [
                                "SKILL.md",
                                "references/verification-checklist.md",
                                "scripts/start-collector.sh",
                            ],
                        }
                    ]
                },
            )
            self.assertEqual(
                (output_root / "otel-instrumentation/references/verification-checklist.md").read_text(),
                "# Verify\n",
            )
            mode = (output_root / "otel-instrumentation/scripts/start-collector.sh").stat().st_mode
            self.assertTrue(mode & stat.S_IXUSR)

    def test_rejects_skill_name_that_does_not_match_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = root / "skills" / "actual-dir"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: other-name\ndescription: Example.\n---\n# Skill\n"
            )

            with self.assertRaisesRegex(ValueError, "does not match directory"):
                build_skills_bundle.build_bundle(root / "skills", root / "dist")


if __name__ == "__main__":
    unittest.main()
