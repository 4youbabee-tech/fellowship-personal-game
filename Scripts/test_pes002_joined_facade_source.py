"""Real OBJ topology regression for PES-002; source-only, not UE acceptance."""
from __future__ import annotations
import collections
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "Tools/CloudAssetBuild/generate_bag_end_hero_facade.py"
OBJ = ROOT / "SourceAssets/Production/World/Shire/SM_ShBagEndHeroFacade.obj"


def scan(path: Path):
    vertices = [None]
    uvs = [None]
    faces = collections.defaultdict(list)
    current = None
    smooth = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("v "):
            vertices.append(tuple(map(float,line.split()[1:])))
        elif line.startswith("vt "):
            uvs.append(tuple(map(float,line.split()[1:])))
        elif line.startswith("usemtl "):
            current = line.split()[1]
        elif line.startswith("s "):
            smooth = line.split()[1]
            if current == "BagEndTurf" and smooth != "1":
                raise AssertionError("PES002_TURF_SMOOTHING_MISSING")
        elif line.startswith("f "):
            assert current is not None
            r = [tuple(map(int,x.split("/"))) for x in line.split()[1:]]
            if len(r) != 3:
                raise AssertionError("PES002_NON_TRIANGLE")
            for index, uv in r:
                if index <= 0 or index >= len(vertices) or uv <= 0 or uv >= len(uvs):
                    raise AssertionError("PES002_INVALID_OBJ_INDEX")
            a,b,c = (vertices[index] for index,_ in r)
            u = [b[i]-a[i] for i in range(3)]
            v = [c[i]-a[i] for i in range(3)]
            cross = (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            if sum(x*x for x in cross) <= 1e-10:
                raise AssertionError("PES002_DEGENERATE_TRIANGLE")
            faces[current].append(tuple(index for index,_ in r))
    return vertices,faces


class JoinedBagEndSourceTest(unittest.TestCase):
    def test_reproducible_single_seven_material_source(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / OBJ.name
            subprocess.run([sys.executable,str(GENERATOR),"--output",str(output)],check=True)
            self.assertEqual(OBJ.read_bytes(),output.read_bytes())
        verts,faces = scan(OBJ)
        self.assertEqual(set(faces), {"BagEndPlaster","BagEndTurf","Stone","Wood","BagEndDoor","BagEndBrass","BagEndGlass"})
        self.assertLessEqual(sum(map(len,faces.values())),3000)
        self.assertGreater(sum(map(len,faces.values())),1000)
        self.assertLessEqual(len(verts),3000)

    def test_continuous_facade_and_roof_share_exact_crown_vertices(self):
        verts, faces = scan(OBJ)
        shared = set(i for f in faces["BagEndPlaster"] for i in f) & set(i for f in faces["BagEndTurf"] for i in f)
        crown = [i for i in range(1,len(verts)) if abs(verts[i][0]+15) < 1e-4 and
                 abs(verts[i][1]) <= 126.0001 and verts[i][2] >= 15.999]
        self.assertEqual(len(crown),33)
        self.assertEqual(set(crown),shared,"Roof must REUSE, not duplicate, the wall's 33 curved vertices")
        # If a future artist uses disconnected facade cubes, this shared-edge proof fails.
        front_edges = set()
        for f in faces["BagEndPlaster"]:
            for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):
                if a in crown and b in crown:
                    front_edges.add(tuple(sorted((a,b))))
        roof_edges = set()
        for f in faces["BagEndTurf"]:
            for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):
                if a in crown and b in crown:
                    roof_edges.add(tuple(sorted((a,b))))
        self.assertEqual(len(front_edges),32)
        self.assertEqual(front_edges,roof_edges)

    def test_lateral_aprons_buried_and_back_terminates_under_ground(self):
        verts, faces = scan(OBJ)
        grass = faces["BagEndTurf"]
        gverts = {i for tri in grass for i in tri}
        buried_left = [i for i in gverts if verts[i][1] < -135 and verts[i][2] <= -11]
        buried_right = [i for i in gverts if verts[i][1] > 135 and verts[i][2] <= -11]
        self.assertGreaterEqual(len(buried_left),6)
        self.assertGreaterEqual(len(buried_right),6)
        last_edge = {i for i in gverts if abs(verts[i][0]-380) < 1e-4}
        self.assertGreaterEqual(len(last_edge),33)
        self.assertTrue(all(verts[i][2] <= -7.999 for i in last_edge))
        # No exposed side row: each outer roof edge belongs to >=2 turf triangles
        # (roof + apron); the rear edge is hidden below the assumed ground plane.
        edges = collections.Counter(tuple(sorted((a,b))) for f in grass for a,b in
                                    ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])))
        for j in range(13-1):
            x0 = -15.0 +395*j/12
            x1 = -15.0 +395*(j+1)/12
            for side in (-1,1):
                endpoints=[]
                for x in (x0,x1):
                    row=[i for i in gverts if abs(verts[i][0]-x)<1e-3]
                    row=[i for i in row if verts[i][2] >= -8.001]
                    # Pick the roof edge by the highest |y| not buried outside.
                    # It has z at least -8 and sits inside the apron, not at its tip.
                    row=[i for i in row if (verts[i][1]<0 if side<0 else verts[i][1]>0)]
                    candidates=[i for i in row if abs(verts[i][2] - (16*(1-(x+15)/395)-8*((x+15)/395)))<0.003]
                    self.assertTrue(candidates)
                    endpoints.append(max(candidates,key=lambda i:abs(verts[i][1])))
                self.assertGreaterEqual(edges[tuple(sorted(endpoints))],2,(j,side,endpoints,verts[endpoints[0]],verts[endpoints[1]],edges.most_common(2)))


if __name__ == "__main__":
    unittest.main()
