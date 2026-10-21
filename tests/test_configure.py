import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from configure import load_manifest, make_project, relative_path
from tools.check_report import artifact_name


class ProjectTests(unittest.TestCase):
    def test_names_and_sources_follow_tree(self):
        project = make_project(load_manifest())
        self.assertEqual(len(project["units"]), 4)
        for unit in project["units"]:
            self.assertEqual(unit["metadata"]["source_path"], f"src/{unit['name']}.cpp")
            self.assertFalse(unit["metadata"]["complete"])
        self.assertNotIn("progress_categories", project)

    def test_complete_requires_matched_and_linked(self):
        for matched, linked, complete in [(False, False, False), (True, False, False),
                                          (False, True, False), (True, True, True)]:
            manifest = copy.deepcopy(load_manifest())
            manifest["units"][0].update(matched=matched, linked_from_source=linked)
            self.assertEqual(make_project(manifest)["units"][0]["metadata"]["complete"], complete)

    def test_subset_artifact_is_not_ingested_as_progress(self):
        manifest = load_manifest()
        self.assertEqual(artifact_name(manifest), "0.36.5552_research")
        manifest["bytematch_ready"] = True
        with self.assertRaises(ValueError):
            artifact_name(manifest)
        manifest["scope"] = "whole-game"
        self.assertEqual(artifact_name(manifest), "0.36.5552_report")

    def test_reject_absolute_parent_and_windows_paths(self):
        for name in ["../escape", "/absolute", "C:/absolute", "a/../b", "a//b", "a\\b", "./local"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                relative_path(name)


if __name__ == "__main__":
    unittest.main()
