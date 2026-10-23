"""Deliberately invalid labels are synthetic fixtures, never portfolio evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import card_validation as cards
import render

SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="850" viewBox="0 0 760 850">{}</svg>'


class CardGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.svg = self.root / 'card.svg'

    def tearDown(self):
        self.temp.cleanup()

    def test_prohibited_numbering_and_branding(self):
        for label in ['Day 04', 'day04', 'DAY-04', 'Day #04', '04/30', '4 / 30',
                      '30 Days of IT', 'Prove 30 for 30', 'Ship 30 for 30', '30for30', '2 of 30', '30-for-30',
                      'project-04', 'projects/day-04', 'Published 2026-10-23',
                      'Ｄａｙ ０４', 'Da\u200by 04', 'Day&#32;04']:
            with self.subTest(label=label), self.assertRaises(ValueError):
                cards.check_label(label)

    def test_svg_text_title_description_metadata_and_attributes_rejected(self):
        for body in ['<text>Day 04</text>', '<title>Day 04</title>', '<desc>04/30</desc>',
                     '<metadata>Prove 30 for 30</metadata>', '<g aria-label="Day 04"/>',
                     '<g data-day="04"/>', '<g id="day-04"/>',
                     '<text><tspan>Day</tspan><tspan>04</tspan></text>',
                     '<text>D&#97;y 04</text>', '<!-- Day 04 -->']:
            self.svg.write_text(SVG.format(body))
            with self.subTest(body=body), self.assertRaises(ValueError):
                cards.validate_svg(self.svg)

    def test_clean_architecture_card_accepted(self):
        self.svg.write_text(SVG.format('<title>Application SSO</title><text>SAML 2.0 · Windows 11</text>'))
        cards.validate_svg(self.svg)

    def test_gallery_labels_and_alt_text_rejected_but_numbered_paths_allowed(self):
        good='<a href="projects/day-04/README.md"><img src="assets/day-04-card.svg" alt="Application SSO"></a>'
        self.assertEqual(cards.validate_gallery(good), ['assets/day-04-card.svg'])
        for bad in [good.replace('Application SSO','Day 04'), good+'\n## Day 04',
                    good+'\n[04/30](projects/day-04/README.md)',
                    good.replace('alt=', 'title="Day 04" alt=')]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                cards.validate_gallery(bad)

    def test_dimensions_and_embedded_screenshot_rejected(self):
        for source in [SVG.format('<image href="data:image/png;base64,AAAA"/>'),
                       SVG.format('<text>SSO</text>').replace('width="760"','width="700"')]:
            self.svg.write_text(source)
            with self.assertRaises(ValueError):cards.validate_svg(self.svg)

    def test_raster_ocr_uses_same_rejection_rule(self):
        from PIL import Image
        p=self.root/'card.png';Image.new('RGB',(760,850),'white').save(p)
        with patch.object(cards,'ocr_image',return_value='Day 04'), self.assertRaises(ValueError):
            cards.validate_raster(p)
        with patch.object(cards,'ocr_image',return_value='Application SSO · SAML 2.0'):
            cards.validate_raster(p)

    def test_raster_metadata_rejected(self):
        from PIL import Image,PngImagePlugin
        p=self.root/'card.png';info=PngImagePlugin.PngInfo();info.add_text('Description','Day 04')
        Image.new('RGB',(760,850),'white').save(p,pnginfo=info)
        with self.assertRaises(ValueError):cards.validate_raster(p)

    def test_real_raster_ocr_rejects_drawn_numbering(self):
        from PIL import Image, ImageDraw, ImageFont
        image=Image.new('RGB',(760,850),'white')
        ImageDraw.Draw(image).text((70,300),'Day 04',fill='black',font=ImageFont.truetype('DejaVuSans.ttf',80))
        p=self.root/'card.png';image.save(p)
        with self.assertRaises(ValueError):cards.validate_raster(p)

    def test_raster_review_cannot_silently_skip_missing_tool(self):
        with patch.object(cards.shutil,'which',return_value=None), self.assertRaises(ValueError):
            cards.ocr_image(self.root/'card.png')


class FutureProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.original=render.ROOT
        shutil.copytree(self.original/'projects',self.root/'projects')
        shutil.copytree(self.original/'assets',self.root/'assets')
        shutil.copytree(self.original/'tools',self.root/'tools',ignore=shutil.ignore_patterns('__pycache__'))
        render.ROOT=self.root
        self.day=self.root/'projects/day-04'
        guide=self.day/'GUIDE.md'
        guide.write_text('# Synthetic workflow fixture\n\nGoal: test publishing, not a real lab.\n\n## Prerequisites\nTest fixture only.\n\n## Step 1 — Inspect\n1. Open the synthetic example.\n\nExpected and Verify: fixture exists.\n\n## Verification\nSynthetic only.\n')
        visual=self.day/'diagrams/fixture.svg';visual.parent.mkdir(exist_ok=True)
        visual.write_text(SVG.format('<text>Application SSO</text>'))
        (self.root/'assets/day-04-card.svg').write_text(SVG.format('<text>Application SSO</text>'))
        record=json.loads((self.day/'project.json').read_text())
        record.update(title='Application SSO',status='verified',built='Synthetic workflow fixture.',
                      problem='Exercise the publishing gate.',objective='Test workflow only.',
                      outcome='Synthetic fixture passed; no lab claim.',limitations='Synthetic fixture only.',
                      technologies=['SAML 2.0'],skills=['Validation'],steps=['Inspect the fixture.'],
                      visual='diagrams/fixture.svg',gallery_alt='Application SSO architecture',
                      tests=[dict(check='Fixture exists',expected='exists',observed='exists',result='pass',evidence='diagrams/fixture.svg')],
                      evidence=[dict(path='diagrams/fixture.svg',caption='Synthetic fixture, not lab evidence.',captured='unit-test',
                                     source='Synthetic unit-test fixture',public_reviewed=True,sha256=hashlib.sha256(visual.read_bytes()).hexdigest())])
        (self.day/'project.json').write_text(json.dumps(record))
        self.records=render.load()

    def tearDown(self):
        render.ROOT=self.original;self.temp.cleanup()

    def test_future_slot_passes_source_gate_and_internal_numbering_survives(self):
        output=render.outputs(self.records)
        cards.validate_presentation(self.root,self.records,output,raster=False)
        self.assertIn('projects/day-04/README.md',output[self.root/'README.md'])
        self.assertIn('assets/day-04-card.svg',output[self.root/'README.md'])

    def test_public_heading_alt_and_card_metadata_rejected(self):
        for field in ['title','gallery_alt','card_summary']:
            records=[dict(p) for p in self.records];records[3][field]='Day 04'
            with self.subTest(field=field),self.assertRaises(ValueError):
                cards.validate_presentation(self.root,records,render.outputs(records),raster=False)

    def test_full_renderer_rejects_bad_card_before_writing_any_output(self):
        bad=self.root/'assets/day-04-card.svg';bad.write_text(SVG.format('<text>Day 04</text>'))
        before=(self.root/'projects/day-01/README.md').read_bytes()
        result=subprocess.run([sys.executable,'tools/render.py'],cwd=self.root,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Publication blocked',result.stderr)
        self.assertEqual(before,(self.root/'projects/day-01/README.md').read_bytes())

    def test_render_never_replaces_approved_card_designs(self):
        before={p:p.read_bytes() for p in (self.root/'assets').glob('*') if p.is_file()}
        for path,text in render.outputs(self.records).items():path.write_text(text)
        self.assertEqual(before,{p:p.read_bytes() for p in before})


if __name__=='__main__':unittest.main()
