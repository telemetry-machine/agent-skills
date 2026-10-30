import json
import tempfile
import unittest
from pathlib import Path

import build_skills_index


class BuildSkillsIndexTest(unittest.TestCase):
    def test_indexes_each_skill_and_its_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills_root = root / "skills"
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
            (scripts / "start-collector.sh").write_text("#!/usr/bin/env bash\n")

            index_text = build_skills_index.render_index(build_skills_index.build_index(skills_root))
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

    def test_rejects_skill_name_that_does_not_match_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = root / "skills" / "actual-dir"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: other-name\ndescription: Example.\n---\n# Skill\n"
            )

            with self.assertRaisesRegex(ValueError, "does not match directory"):
                build_skills_index.build_index(root / "skills")


if __name__ == "__main__":
    unittest.main()
