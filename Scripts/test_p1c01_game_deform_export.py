"""Source-only skeletal game export regression. Unreal/pose are separate gates."""
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'Scripts'/'p1c01_game_deform_export.py'
spec=importlib.util.spec_from_file_location('game_export',MOD)
game=importlib.util.module_from_spec(spec)
spec.loader.exec_module(game)

class GameDeformExportContract(unittest.TestCase):
    def setUp(self):
        parts={'pelvis': 'DEF-pelvis','spine':'DEF-spine','head':'DEF-head'}
        for side in ('L','R'):
            for k in ('upper_arm','forearm','hand','thigh','shin','foot'):
                parts[('left' if side=='L' else 'right')+'_'+k]='DEF-'+k+'.'+side
        self.parts=parts
        self.weights={v:3.0 for v in parts.values()}
        self.parents={'DEF-spine':'ORG-spine','ORG-spine':'DEF-pelvis', 'DEF-head':'ORG-head', 'ORG-head':'ORG-neck','ORG-neck':'ORG-spine'}
        for side in ('L','R'):
            for start,end in [('upper_arm','shoulder'),('forearm','upper_arm'),('hand','forearm'),('thigh','pelvis'),('shin','thigh'),('foot','shin')]:
                self.parents[f'DEF-{start}.{side}']=f'ORG-{start}.{side}'
                self.parents[f'ORG-{start}.{side}']=f'ORG-{end}.{side}' if end!='pelvis' else 'ORG-spine'
    def test_extract_control_rig_into_direct_game_chains(self):
        roles=game.choose_roles(self.weights,self.weights)
        self.assertEqual(roles,self.parts)
        mapping=game.build_parent_map(self.parents,self.weights,roles)
        self.assertEqual(mapping['DEF-forearm.L'],'DEF-upper_arm.L')
        self.assertEqual(mapping['DEF-hand.R'],'DEF-forearm.R')
        self.assertEqual(mapping['DEF-shin.L'],'DEF-thigh.L')
        self.assertEqual(mapping['DEF-foot.R'],'DEF-shin.R')
        self.assertEqual(mapping['DEF-head'],'DEF-spine')
        self.assertEqual(mapping['DEF-pelvis'],None)
        self.assertNotIn('ORG-', '\n'.join(str(v) for v in mapping.values()))
    def test_actual_rigify_segment_names_produce_continuous_limbs(self):
        weighted={"DEF-hips":3,"DEF-spine":2,"DEF-spine.001":1,
                  "DEF-chest":5,"DEF-chest.001":3,"DEF-head":2,"DEF-head.001":1,
                  "DEF-neck":1}
        source={"DEF-spine":"ORG-spine","ORG-spine":"root",
                "DEF-head":"ORG-head","ORG-head":"ORG-neck",
                "ORG-neck":"ORG-chest","ORG-chest":"ORG-spine"}
        for side in ("L","R"):
            for family in ("upper_arm","forearm","thigh","shin"):
                for seg in (1,2):
                    weighted[f"DEF-{family}.{seg:02d}.{side}"]=2+seg
                    source[f"DEF-{family}.{seg:02d}.{side}"]=f"ORG-{family}.{seg:02d}.{side}"
            for family in ("hand","foot","shoulder"):
                weighted[f"DEF-{family}.{side}"]=4
                source[f"DEF-{family}.{side}"]=f"ORG-{family}.{side}"
        roles=game.choose_roles(weighted,weighted)
        parents=game.build_parent_map(source,weighted,roles)
        for side in ("L","R"):
            self.assertEqual(parents[f"DEF-upper_arm.02.{side}"],f"DEF-upper_arm.01.{side}")
            self.assertEqual(parents[f"DEF-forearm.01.{side}"],f"DEF-upper_arm.02.{side}")
            self.assertEqual(parents[f"DEF-forearm.02.{side}"],f"DEF-forearm.01.{side}")
            self.assertEqual(parents[f"DEF-shin.01.{side}"],f"DEF-thigh.02.{side}")
            self.assertEqual(parents[f"DEF-foot.{side}"],f"DEF-shin.02.{side}")
        self.assertEqual(parents["DEF-chest"],"DEF-spine.001")
        self.assertEqual(parents["DEF-head"],"DEF-neck")

    def test_missing_weighted_role_is_a_real_failure(self):
        weights=dict(self.weights)
        weights.pop('DEF-forearm.L')
        with self.assertRaisesRegex(RuntimeError,'WEIGHTED_JOINT_ROLES_MISSING'):
            game.choose_roles(weights, self.weights)
    def test_reject_cycle_in_nonmandatory_deform_bones(self):
        weights={**self.weights,'DEF-finger.01.L':1,'DEF-finger.02.L':1}
        parents={**self.parents,'DEF-finger.01.L':'DEF-finger.02.L','DEF-finger.02.L':'DEF-finger.01.L'}
        with self.assertRaisesRegex(RuntimeError,'PARENT_CYCLE'):
            game.build_parent_map(parents,weights,self.parts)
    def test_mocked_original_org_parent_not_in_game_export(self):
        parents=game.build_parent_map(self.parents,self.weights,self.parts)
        self.assertTrue(all(v is None or v.startswith('DEF-') for v in parents.values()))
    def test_pr_workflow_and_blender_embed_must_use_game_source(self):
        stage=(ROOT/'Scripts'/'stage_p1c01_human_wave2.ps1').read_text(encoding='utf-8')
        self.assertIn('--rig-helper',stage)
        self.assertIn('make_game_deform_rig(source_armature, bound_meshes)',stage)
        self.assertIn('GAME_RIG_EXPORTED_HIERARCHY_PASS',stage)
        self.assertIn('GAME_RIG_REST_SKIN_MISMATCH',MOD.read_text())
        self.assertIn('runtime_integration_allowed', (ROOT/'Data'/'P1C01HumanDeformationGateV1.json').read_text())

if __name__=='__main__': unittest.main()
