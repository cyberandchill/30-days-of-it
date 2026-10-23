"""Regression checks for false completion and preservation of existing days."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import render

class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original = render.ROOT
        render.ROOT = Path(self.temp.name)
        shutil.copytree(self.original/'projects', render.ROOT/'projects')
        # Use a planned slot so completion guards still test missing evidence after real days ship.
        self.day = render.ROOT/'projects/day-30'
        shutil.copytree(self.original/'assets', render.ROOT/'assets')
        (render.ROOT/'assets/day-30-card.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><title>Synthetic unit-test fixture</title></svg>')

    def tearDown(self):
        render.ROOT = self.original
        self.temp.cleanup()

    def edit(self, **fields):
        p = json.loads((self.day/'project.json').read_text()); p.update(fields)
        (self.day/'project.json').write_text(json.dumps(p))

    def test_all_30_slots(self):
        self.assertEqual(len(render.load()), 30)
        self.assertEqual(len(render.outputs(render.load())), 1 + sum(p['status']=='verified' for p in render.load()))

    def test_verified_without_evidence_rejected(self):
        self.edit(status='verified')
        with self.assertRaises(AssertionError): render.load()

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError): render.local(self.day, '../../README.md')

    def test_hash_mismatch_rejected(self):
        (self.day/'evidence/result.txt').write_text('Synthetic unit-test fixture, not lab evidence.')
        self.edit(evidence=[dict(path='evidence/result.txt', caption='Test fixture', captured='unit-test', source='unit-test', public_reviewed=True, sha256='0'*64)])
        with self.assertRaises(AssertionError): render.load()

    def test_other_day_and_notes_preserved(self):
        before=(render.ROOT/'projects/day-02/project.json').read_bytes()
        notes=(self.day/'NOTES.md').read_bytes()
        self.edit(title='Changed planned title')
        for path, content in render.outputs(render.load()).items(): path.write_text(content)
        self.assertEqual(before,(render.ROOT/'projects/day-02/project.json').read_bytes())
        self.assertEqual(notes,(self.day/'NOTES.md').read_bytes())

    def test_unreviewed_evidence_rejected(self):
        payload=b'Synthetic fixture'
        (self.day/'evidence/result.txt').write_bytes(payload)
        self.edit(evidence=[dict(path='evidence/result.txt', caption='Test fixture', captured='unit-test', source='unit-test', public_reviewed=False, sha256=hashlib.sha256(payload).hexdigest())])
        with self.assertRaises(AssertionError): render.load()

    def test_professional_gallery(self):
        text = render.outputs(render.load())[render.ROOT/'README.md']
        self.assertNotIn('/30 verified', text)
        self.assertNotIn('Upcoming days', text)
        self.assertNotIn('screenshots/', text)
        self.assertIn('projects/day-01/README.md', text)
        self.assertEqual(text.count('<a href="projects/'), sum(p['status']=='verified' for p in render.load()))

    def test_shared_readme_contract(self):
        for path, text in render.outputs(render.load()).items():
            if path == render.ROOT/'README.md': continue
            sections = ['## What I built', '## Why it matters', '## Architecture', '## Rebuild it yourself', '## Result', '<details>']
            positions = [text.index(x) for x in sections]
            self.assertEqual(positions, sorted(positions))
            self.assertNotIn('## Step ', text)
            self.assertNotIn('# Day ', text)
            self.assertIn('Technologies demonstrated:', text)

    def test_manual_first_flag_cannot_embed_walkthrough(self):
        records = render.load()
        records[0]['readme_layout']='manual-first'
        text=render.outputs(records)[render.ROOT/'projects/day-01/README.md']
        self.assertIn('## What I built', text)
        self.assertNotIn('## Step 1', text)

    def test_card_dimensions_and_no_challenge_text(self):
        import re
        import xml.etree.ElementTree as ET
        for p in render.load():
            if p['status']!='verified': continue
            link=render.card(p)
            asset=re.search(r'src="([^"]+)"',link).group(1)
            root=ET.parse(render.ROOT/asset).getroot()
            self.assertEqual((root.get('width'),root.get('height')),('760','850'))
            visible=' '.join(root.itertext())
            self.assertNotRegex(visible, r'(?i)\bday\s*0?\d+\b|30.days|challenge')

if __name__ == '__main__': unittest.main()
