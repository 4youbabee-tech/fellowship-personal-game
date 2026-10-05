import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class P1C01MaterialLfsHydrationContract(unittest.TestCase):
    def test_hydration_helper_is_targeted_and_fail_closed(self):
        helper = (ROOT / "Scripts" / "hydrate_p1c01_material_lfs.ps1").read_text(encoding="utf-8")
        for token in (
            "git lfs pull",
            "SourceAssets/Production/Imported/P1C01Materials/**",
            "P1C01_LFS_TEXTURE_HYDRATION_PASS",
            "git-lfs-pointer",
            "0x89, 0x50, 0x4E, 0x47",
        ):
            self.assertIn(token, helper)

    def test_expensive_ue4_lanes_hydrate_before_build(self):
        unreal = (ROOT / ".github" / "workflows" / "unreal-build-validation.yml").read_text(encoding="utf-8")
        render = (ROOT / ".github" / "workflows" / "p1c01-shire-render-capture.yml").read_text(encoding="utf-8")
        marker = "hydrate_p1c01_material_lfs.ps1"
        self.assertIn(marker, unreal)
        self.assertIn(marker, render)
        self.assertLess(unreal.index(marker), unreal.index("- name: Build ShireJourneyEditor"))
        self.assertLess(render.index(marker), render.index("- name: Build ShireJourneyEditor for capture"))

    def test_importer_rejects_unhydrated_lfs_pointer_sources(self):
        cpp = (
            ROOT
            / "Source"
            / "ShireJourneyEditorTools"
            / "Private"
            / "ShireProductionImportCommandlet.cpp"
        ).read_text(encoding="utf-8")
        self.assertIn("IsGitLfsPointerFile", cpp)
        self.assertIn("GIT_LFS_POINTER_SOURCE", cpp)
        self.assertLess(
            cpp.index("IsGitLfsPointerFile(Filename)"),
            cpp.index("AssetTools.Get().ImportAssetTasks(Tasks)"),
        )


if __name__ == "__main__":
    unittest.main()
