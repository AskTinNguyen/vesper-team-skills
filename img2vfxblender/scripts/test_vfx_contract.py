"""Contract behavior tests; synthetic fixtures are not rendered visual evidence."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from vfx_contract import ContractError, digest, from_study, init_contract, validate, verify, write_new


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="img2vfxblender-contract-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / "contract.json"
        self.source = self.root / "source.png"
        self.source.write_bytes(b"synthetic source evidence, not a render")
        self.catalog = self.root / "catalog.json"
        self.catalog.write_text(json.dumps({
            "sources": [{"id": "board-01", "path": self.source.name}],
            "effects": [{
                "id": "FX-01",
                "name": "Synthetic opening",
                "source": {"board_id": "board-01", "region": "full"},
                "gameplay_intent_proposed": "Identify an opening",
                "author_notes_paraphrased": ["Synthetic study note"],
                "unresolved": ["Exact timing"],
                "visible_read": "A readable primary opening",
                "implementation_hypotheses": ["Layered emissive curve"],
                "timing": {"sequence": ["before", "event", "clear"]},
                "lite_variant": "Keep the primary opening and remove accents",
                "design_layers_proposed": [
                    {"layer": "L1", "priority": "essential", "description": "Primary opening"},
                    {"layer": "L2", "priority": "support", "description": "Directional motion"},
                ],
            }],
        }), encoding="utf-8")
        self.c = init_contract("test", [self.source], self.path)
        self.c.update(gameplay_intent="Identify opening", coverage_note="Synthetic contract test", coverage_confirmed=True)
        self.c["features"] = [{"id": l, "layer": l, "priority": "essential" if l == "L1" else "optional", "description": "Test layer " + l, "evidence_class": "proposed", "reference_ids": ["ref-01"], "phase": "event", "targets": [l], "disposition": "implement", "reason": ""} for l in ("L1", "L2", "L3", "L4")]
        (self.root / "fixture.blend").write_bytes(b"synthetic checkpoint; not a Blender asset")
        samples=[]
        for role in ("before", "event", "clear", "oblique", "lite", "no-accents", "isolate-l1", "isolate-l2", "isolate-l3", "isolate-l4"):
            s={"id":role,"scene":"Lite" if role=="lite" else role,"camera":"Oblique" if role=="oblique" else "Main","frame":1 if role=="before" else 20 if role=="clear" else 10,"role":role,"variant":"Lite" if role=="lite" else "Standard","scenario":"normal"}
            if role in ("before","event","clear"):
                s['anchor']=role
            samples.append(s)
        self.c['prototype']={"fps":30,"frame_start":1,"frame_end":30,"seed":7,"timing_basis":"proposed","scale_basis":"test proxy","builder_id":"test-builder","checkpoint":"fixture.blend","events":[{"name":n,"frame":f,"basis":"proposed"} for n,f in [("before",1),("event",10),("clear",20)]],"samples":samples,"required_roles":[s['role'] for s in samples],"expected_clear_samples":["before","clear"],"required_feature_samples":{l:["event","isolate-"+l.lower()] for l in ('L1','L2','L3','L4')}}
        self.mpath=self.root/'manifest.json'
        self.save()
        self.m={"schema_version":1,"blender_version":"synthetic-test","contract_sha256":digest(self.path),"checkpoint_sha256":digest(self.root/'fixture.blend'),"reference_hashes":{"ref-01":digest(self.source)},"samples":[]}
        for s in samples:
            p=self.root/(s['id']+'.png')
            p.write_bytes(b"synthetic frame "+s['id'].encode())
            layers=[] if s['role'] in ('before','clear') else [s['role'].removeprefix('isolate-').upper()] if s['role'].startswith('isolate-') else ['L1','L2','L3'] if s['role'] in ('lite','no-accents') else ['L1','L2','L3','L4']
            matrix=[[1,0,0,1 if s['role']=='oblique' else 0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
            self.m['samples'].append({**s,"path":p.name,"sha256":digest(p),"scene_variant":s['variant'],"scene_scenario":s['scenario'],"variant_signature":s['variant'],"seed":7,"fps":30,"engine":"CYCLES","resolution":[640,400,100],"camera_matrix":matrix,"camera_lens":50,"camera_type":"PERSP","color_management":{"display":"sRGB","view":"AgX","look":"None","exposure":0,"gamma":1},"compositor_enabled":False,"visible_targets":layers,"visible_layers":layers})

    def save(self):
        self.path.write_text(json.dumps(self.c),encoding='utf-8')
        if hasattr(self,'m'):
            self.m['contract_sha256']=digest(self.path)

    def row(self,name):
        return next(r for r in self.m['samples'] if r['id']==name)

    def reject(self, fragment, prototype=False):
        with self.assertRaisesRegex(ContractError,fragment):
            if prototype:
                validate(self.c,self.path,'prototype')
            else:
                verify(self.c,self.path,self.m,self.mpath)

    def test_complete_fixture(self):
        verify(self.c,self.path,self.m,self.mpath)

    def test_study_does_not_need_blender(self):
        self.c['prototype']=None
        self.c['coverage_confirmed']=False
        for f in self.c['features']:
            f['targets']=[]
        validate(self.c,self.path,'study')

    def test_study_import(self):
        output=self.root/'FX-01.json'
        c=from_study(self.catalog,'FX-01',output)
        validate(c,output,'study')
        self.assertEqual(c['effect_id'],'FX-01')
        self.assertEqual(c['source_notes'],['Synthetic study note'])
        self.assertIsNone(c['prototype'])

    def test_unknown_study_rejected(self):
        with self.assertRaisesRegex(ContractError,'Unknown'):
            from_study(self.catalog,'FX-99',self.path)

    def test_duplicate_ids(self):
        self.c['features'].append(copy.deepcopy(self.c['features'][0]))
        self.reject('Duplicate',True)

    def test_unadmitted_source(self):
        self.c['features'][0]['reference_ids']=['missing']
        self.reject('Unadmitted',True)

    def test_derivative_only_essential(self):
        self.c['references'][0]['kind']='derivative'
        self.reject('Derivative-only',True)

    def test_essential_omission(self):
        self.c['features'][0].update(disposition='omitted',reason='skip')
        self.reject('essential primary',True)

    def test_unsupported_measured_time(self):
        self.c['prototype']['timing_basis']='measured'
        self.reject('timestamp evidence',True)

    def test_missing_feature_bindings(self):
        self.c['features'][0]['targets']=[]
        self.reject('targets missing',True)

    def test_missing_required_sample(self):
        self.c['prototype']['samples']=[s for s in self.c['prototype']['samples'] if s['role']!='oblique']
        self.reject('Missing required',True)

    def test_no_standard(self):
        for s in self.c['prototype']['samples']:
            s['variant']='Lite'
        self.reject('Standard/normal',True)

    def test_reversed_temporal_samples(self):
        self.c['prototype']['samples'][0]['frame']=20
        self.reject('event anchor',True)

    def test_reversed_anchors(self):
        self.c['prototype']['events'][0]['frame']=25
        self.reject('before < event < clear',True)

    def test_lite_uses_same_time(self):
        next(s for s in self.c['prototype']['samples'] if s['role']=='lite')['frame']=25
        self.reject('normal event frame',True)

    def test_stale_reference(self):
        self.source.write_bytes(b'changed source')
        self.reject('Stale reference',True)

    def test_stale_contract(self):
        self.path.write_text(self.path.read_text()+' ')
        self.reject('contract hash')

    def test_stale_checkpoint(self):
        (self.root/'fixture.blend').write_bytes(b'changed checkpoint')
        self.reject('checkpoint hash')

    def test_stale_frame(self):
        (self.root/'event.png').write_bytes(b'changed frame')
        self.reject('stale rendered image')

    def test_missing_clear_audit(self):
        del self.row('clear')['visible_targets']
        self.reject('audit list')

    def test_uncleared_vfx(self):
        self.row('clear')['visible_targets']=['L3']
        self.reject('remains render-eligible')

    def test_missing_camera_matrix(self):
        del self.row('oblique')['camera_matrix']
        self.reject('4x4 camera')

    def test_same_oblique(self):
        self.row('oblique')['camera_matrix']=self.row('event')['camera_matrix']
        self.reject('duplicates event camera')

    def test_nan_camera(self):
        self.row('oblique')['camera_matrix'][0][0]=float('nan')
        self.reject('4x4 camera')

    def test_missing_color_settings(self):
        del self.row('event')['color_management']
        self.reject('Color management')

    def test_drifted_resolution(self):
        self.row('lite')['resolution']=[320,200,100]
        self.reject('settings drift')

    def test_false_isolation(self):
        self.row('isolate-l1')['visible_layers']=['L1','L2']
        self.reject('isolation')

    def test_false_no_accents(self):
        self.row('no-accents')['visible_layers'].append('L4')
        self.reject('still contains accents')

    def test_compositor_still_on(self):
        self.row('no-accents')['compositor_enabled']=True
        self.reject('still contains accents')

    def test_absent_feature_in_claimed_sample(self):
        self.row('event')['visible_targets'].remove('L1')
        self.reject('Feature targets absent')

    def test_no_overwrite(self):
        with self.assertRaises(FileExistsError):
            write_new(self.path,{})


if __name__=='__main__':
    unittest.main(verbosity=2)
