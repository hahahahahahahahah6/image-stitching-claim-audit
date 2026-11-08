import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from image_stitching_claim_audit import phrases as p
from image_stitching_claim_audit.audit import evidence, claims, scan, main

class AuditTests(unittest.TestCase):
    def test_oracle_imagestitching(self):
        self.assertEqual(p.IMAGESTITCHING, ['image stitching', 'image-stitching', 'imagestitching', 'panorama stitching', 'panorama-stitching', 'panoramic stitching', 'photo stitching', 'photo-stitching', 'stitch images', 'stitches images', 'stitching images', 'stitch photos', 'stitches photos', 'stitching photos', 'stitch panoramas', 'stitches panoramas', 'create panoramas', 'creates panoramas', 'create a panorama', 'creates a panorama', 'make panoramas', 'makes panoramas', 'panorama creation', 'create panoramic images', 'stitch images together', 'stitches images together', 'stitching images together', 'stitch multiple images', 'stitches multiple images', 'stitch images into a panorama', 'stitches images into a panorama', 'combine images into a panorama', 'combines images into a panorama', 'panorama stitcher', 'panorama stitchers', 'image stitcher', 'image stitchers', 'image stitching tool', 'image stitching library', 'image stitching feature', 'image stitching support', 'supports image stitching', 'image stitching capability', 'image stitching pipeline', 'image stitching algorithm', 'image stitching software', 'image stitching app', 'image stitching model', 'automatic image stitching', 'automated image stitching'])

    def test_oracle_noimagestitching(self):
        self.assertEqual(p.NOIMAGESTITCHING, ['does not support image stitching', 'do not support image stitching', "doesn't support image stitching", "don't support image stitching", 'no image stitching', 'without image stitching', 'never performs image stitching', 'does not perform image stitching', 'image stitching not supported', 'image stitching unsupported', 'no image stitching support', 'lacks image stitching', 'missing image stitching', 'image stitching disabled', 'no image stitching capability', 'without image stitching support', 'does not provide image stitching', 'no image stitching model', 'image stitching not available', 'does not use image stitching', 'no panorama stitching', 'without panorama stitching', 'does not support panorama stitching', 'no image stitching feature'])

    def test_oracle_generic_names(self):
        self.assertEqual(p.GENERIC_NAMES, ['stitch_images', 'stitch_photos', 'stitch_image', 'stitch_panorama', 'stitch_panoramas', 'stitch_frames', 'stitch_pictures', 'stitch_together', 'stitch_multiple_images', 'stitch_image_pair', 'stitch_and_blend', 'stitch_to_panorama', 'create_panorama', 'make_panorama', 'build_panorama', 'generate_panorama', 'assemble_panorama', 'panorama_stitch', 'panorama_stitching', 'create_panoramas', 'make_panoramas', 'build_panoramas', 'create_pano', 'make_pano'])

    def test_oracle_opencv_constructors(self):
        self.assertEqual(p.OPENCV_CONSTRUCTORS, ['Stitcher_create', 'createStitcher', 'Stitcher.create'])

    def test_oracle_stitching_classes(self):
        self.assertEqual(p.STITCHING_CLASSES, ['Stitcher'])

    def test_oracle_stitching_source(self):
        self.assertEqual(p.STITCHING_SOURCE, 'stitching')

    def test_oracle_stitching_methods(self):
        self.assertEqual(p.STITCHING_METHODS, ['stitch', 'stitch_verbose'])

    def test_oracle_detector_names(self):
        self.assertEqual(p.DETECTOR_NAMES, ['SIFT_create', 'ORB_create', 'AKAZE_create', 'BRISK_create'])

    def test_oracle_matcher_names(self):
        self.assertEqual(p.MATCHER_NAMES, ['BFMatcher', 'FlannBasedMatcher'])

    def test_oracle_homography_names(self):
        self.assertEqual(p.HOMOGRAPHY_NAMES, ['findHomography'])

    def test_oracle_warp_names(self):
        self.assertEqual(p.WARP_NAMES, ['warpPerspective'])

    def fixture(self, files, args=()):
        with tempfile.TemporaryDirectory() as tmp:
            for name, content in files.items():
                path=Path(tmp)/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content)
            out=io.StringIO(); err=io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code=main(['audit', tmp]+list(args))
            return code, out.getvalue(), err.getvalue()

    def test_cli(self):
        rule='documented-image-stitching-claim-false'
        denial='documented-no-image-stitching-claim-false'
        self.assertEqual(self.fixture({'README.md':'image stitching', 'app.py':'x.stitch_images()'})[0],0)
        code,out,_=self.fixture({'README.md':'IMAGE STITCHING'}, ['--json']); self.assertEqual(code,2)
        finding=json.loads(out)['findings'][0]
        self.assertEqual(finding['rule'],rule); self.assertEqual(finding['severity'],'high')
        self.assertIn('verdict',finding); self.assertIn('message',finding)
        for args, expected in [([],0), (['--fail-on','medium'],2)]:
            self.assertEqual(self.fixture({'tests/test_fixture.py':'"image stitching"'},args)[0],expected)
        code,out,_=self.fixture({'README.md':'no image stitching','app.py':'x.stitch_images()'}); self.assertEqual(code,2); self.assertIn(denial,out)
        self.assertEqual(self.fixture({'README.md':'hello'})[0],0)
        self.assertEqual(self.fixture({'README.md':'no image stitching'})[0],0)
        self.assertEqual(self.fixture({'docs/guide.md':'image stitching'},['--ignore','docs/'])[0],0)
        self.assertEqual(self.fixture({'README.md':'image stitching','a.py':'import cv2\nm=cv2.Stitcher_create()', 'b.py':'m.stitch(image)'})[0],2)
        self.assertEqual(self.fixture({'README.md':'image stitching','venv/a.py':'x.stitch_images()'})[0],2)
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,'README.md').write_text('hello')
            self.assertEqual(main(['audit','--ignore','docs/',tmp]),0)
        out=io.StringIO()
        with contextlib.redirect_stdout(out): self.assertEqual(main(['--version']),0)
        self.assertEqual(out.getvalue().strip(),'0.1.0')
        self.assertEqual(main(['audit','/nonexistent-claim-audit-path']),1)
        self.assertEqual(main(['--unknown']),1)

    def test_readme_self_audit(self):
        root=Path(__file__).resolve().parents[1]
        self.assertEqual(claims((root/'README.md').read_text()), ([],[]))
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,'README.md').write_text((root/'README.md').read_text())
            self.assertEqual(scan(Path(tmp))[0],[])

    def test_scope_and_collapse(self):
        code,out,_=self.fixture({'README.md':'image stitching image stitcher', 'docs/a.md':'stitches images'})
        self.assertEqual(code,2)
        self.assertEqual(out.count('documented-image-stitching-claim-false'),1)
        self.assertEqual(self.fixture({'other.md':'image stitching'})[0],0)
        self.assertEqual(self.fixture({'docs/deep/guide.md':'image stitching'})[0],2)
        self.assertEqual(self.fixture({'README.md':'image stitching', 'pkg/model.py':'x.stitch_images()'})[0],0)
        self.assertEqual(self.fixture({'README.md':'image stitching', '.git/model.py':'x.stitch_images()'})[0],2)
        self.assertEqual(self.fixture({'README.md':'image stitching', 'custom/pyvenv.cfg':'', 'custom/model.py':'x.stitch_images()'})[0],2)
        self.assertEqual(self.fixture({'README.md':'image stitching', 'ignored/model.py':'x.stitch_images()'}, ['--ignore','ignored/'])[0],2)
        self.assertEqual(self.fixture({'README.md':'image stitching','docs/a.md':'image stitching'}, ['--ignore','README','--ignore','docs/'])[0],0)
        code,out,err=self.fixture({'README.md':'hello'}, ['--verbose','--json'])
        self.assertEqual(code,0); self.assertEqual(json.loads(out)['verdict'],'PASS')
        self.assertIn('Scope:',err); self.assertIn('README.md:',err)

    def test_full_checkout_medium(self):
        root=Path(__file__).resolve().parents[1]
        findings,_=scan(root)
        self.assertEqual(len(findings),1)
        self.assertEqual(findings[0]['severity'],'medium')


class EvidenceTests(unittest.TestCase):
    def test_opencv(self):
        for ctor in ['x.Stitcher_create', 'x.createStitcher', 'x.Stitcher.create', 'Stitcher.create', 'C']:
            imp='from cv2 import Stitcher_create as C\n'
            for code in [f's={ctor}()\ns.stitch(images)', f'{ctor}().stitch(images)', f's={ctor}()\na=s\na.stitch(images)']:
                with self.subTest(code=code): self.assertTrue(evidence(imp+code))
        for name in ['Stitcher_create','createStitcher']:
            self.assertTrue(evidence(f'from cv2 import {name}\n{name}().stitch(images)'))

    def test_package(self):
        for imp,ctor in [('from stitching import Stitcher','Stitcher'), ('from stitching import Stitcher as S','S'), ('import stitching','stitching.Stitcher'), ('import stitching as st','st.Stitcher')]:
            for method in ['stitch','stitch_verbose']:
                for code in [f's={ctor}()\ns.{method}(images)',f'{ctor}().{method}(images)']:
                    self.assertTrue(evidence(imp+'\n'+code),code)

    def test_manual(self):
        for detector in ['SIFT_create','ORB_create','AKAZE_create','BRISK_create']:
            for matcher in ['BFMatcher','FlannBasedMatcher']:
                names=[detector,matcher,'findHomography','warpPerspective']
                for form in ['attribute','bare','alias']:
                    code=''
                    for i,name in enumerate(names):
                        if form=='attribute': code+=f'x.{name}()\n'
                        elif form=='bare': code+=f'from cv2 import {name}\n{name}()\n'
                        else: code+=f'from cv2 import {name} as f{i}\nf{i}()\n'
                    self.assertTrue(evidence(code),code)
                for missing in range(4):
                    self.assertFalse(evidence('\n'.join('x.'+n+'()' for i,n in enumerate(names) if i!=missing)))

    def test_generic(self):
        for name in p.GENERIC_NAMES:
            for code in [f'x.{name}()',f'from anywhere import {name}\n{name}()',f'from anywhere import {name} as f\nf()']:
                self.assertTrue(evidence(code),code)
            self.assertFalse(evidence(name+'()'))

    def test_rejections(self):
        cases=['import cv2, stitching','x.Stitcher_create()', 'x.createStitcher()', 'x.Stitcher.create()', 'from stitching import Stitcher\nStitcher()', 'Stitcher().stitch()', 'other.Stitcher().stitch()', 'stitching.Stitcher().stitch()', 's.stitch()', 'x.SIFT_create()\nx.BFMatcher()', '"x.stitch_images()" # x.stitch_images()', '"""x.stitch_images()"""', 'x.stitch_images', 'import subprocess\nsubprocess.run(["stitch"])','invalid syntax !']
        for call in ['SIFT_create','ORB_create','AKAZE_create','BRISK_create','BFMatcher','FlannBasedMatcher','findHomography','warpPerspective','addWeighted','alpha_composite','Blender','imshow','stabilize','capture360','read_exif','classify','caption','generate','upscale','inpaint','colorize','remove_background','detect_objects']:
            cases.append('x.'+call+'()')
        for code in cases:
            with self.subTest(code=code): self.assertFalse(evidence(code))

    def test_shadowing(self):
        cases=[('Stitcher_create','from cv2 import Stitcher_create\nStitcher_create().stitch()'),('createStitcher','from cv2 import createStitcher\ncreateStitcher().stitch()'),('Stitcher','from stitching import Stitcher\nStitcher().stitch()'),('stitch_images','from x import stitch_images\nstitch_images()')]
        for name in ['SIFT_create','ORB_create','AKAZE_create','BRISK_create','BFMatcher','FlannBasedMatcher','findHomography','warpPerspective']:
            detector=name if name in p.DETECTOR_NAMES else 'SIFT_create'
            matcher=name if name in p.MATCHER_NAMES else 'BFMatcher'
            cases.append((name,'\n'.join('x.'+n+'()' for n in [detector,matcher,'findHomography','warpPerspective'])))
        for name,code in cases:
            for definition in [f'def {name}(): pass',f'class {name}: pass']:
                self.assertFalse(evidence(code+'\n'+definition),code)
        for code in ['from stitching import Stitcher as S\nclass S: pass\nS().stitch()', 'from cv2 import SIFT_create as f\ndef f(): pass\nf()\nx.BFMatcher()\nx.findHomography()\nx.warpPerspective()']:
            self.assertFalse(evidence(code))

    def test_matching(self):
        self.assertEqual(claims('does not support image stitching'), ([],['does not support image stitching']))
        for phrase in ['image stitching model','stitch images into a panorama']:
            self.assertEqual(claims(phrase)[0],[phrase])
        self.assertEqual(claims('IMAGE STITCHING')[0],['image stitching'])
        self.assertEqual(claims('we stitch images together by hand in Photoshop')[0],['stitch images together'])
        self.assertEqual(claims('create a panorama with your phone camera')[0],['create a panorama'])
        self.assertEqual(claims('```py\nimage stitching\n```'),([],[]))
        self.assertEqual(claims('`image stitching`')[0],['image stitching'])
        self.assertEqual(claims('image--stitching')[0],[])

if __name__ == '__main__': unittest.main()
