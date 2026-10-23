"""Validate evidence references and render the 30-day GitHub portfolio. Standard library only."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {'planned': '○ Planned', 'in-progress': '◐ In progress', 'blocked': '! Blocked', 'verified': '✓ Verified'}

def local(base, value):
    path = (base / value).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file():
        raise ValueError('Missing or unsafe local evidence path')
    return path

def load():
    projects = []
    for number in range(1, 31):
        base = ROOT / 'projects' / f'day-{number:02}'
        p = json.loads((base / 'project.json').read_text())
        assert p['day'] == number and p['status'] in STATUSES
        for field in ('title', 'built', 'problem', 'objective', 'outcome', 'limitations'):
            assert isinstance(p[field], str) and p[field].strip(), field
        for field in ('technologies', 'skills', 'steps', 'tests', 'problems', 'evidence'):
            assert isinstance(p[field], list), field
        for test in p['tests']:
            assert all(test.get(k) for k in ('check', 'expected', 'observed', 'result', 'evidence'))
            assert test['result'] in ('pass', 'fail', 'not-tested')
            local(base, test['evidence'])
        for e in p['evidence']:
            assert all(e.get(k) for k in ('path', 'caption', 'captured', 'sha256', 'source', 'public_reviewed'))
            assert e['public_reviewed'] is True
            assert hashlib.sha256(local(base, e['path']).read_bytes()).hexdigest() == e['sha256']
        paths = {e['path'] for e in p['evidence']}
        assert all(t['evidence'] in paths for t in p['tests'])
        if p['visual']:
            local(base, p['visual'])
            assert p['visual'] in paths
        if p['status'] == 'verified':
            assert p['visual'] and p['tests'] and all(t['result'] == 'pass' for t in p['tests'])
            assert p['steps'] and p['technologies'] and p['skills'] and p['evidence']
        projects.append(p)
    return projects

def esc(value):
    return html.escape(str(value)).replace('|', '&#124;').replace('\n', ' ')

def card(p):
    day = p['day']
    prefix = f'projects/day-{day:02}'
    if p['status'] == 'verified':
        return (f'<a href="{prefix}/README.md"><img src="assets/day-{day:02}-card.svg" '
                f'alt="Day {day:02}: visual project card" width="420"></a>')
    return f'- [Day {day:02}: {esc(p["title"])} — {STATUSES[p["status"]]}]({prefix}/README.md)'

def bullets(items, empty):
    return '\n'.join('- '+str(x) for x in items) if items else empty

def outputs(projects):
    completed = sum(p['status'] == 'verified' for p in projects)
    featured = [p for p in projects if p['status'] == 'verified']
    pending = [p for p in projects if p['status'] != 'verified']
    gallery = '\n\n'.join(card(p) for p in featured) or '_No verified projects yet._'
    upcoming = '\n'.join(card(p) for p in pending)
    readme = f'''# 30 Days of IT · Build. Test. Show.

**{completed}/30 verified projects** · Visual proof backed by detailed documentation.

One clear architecture card per completed project. Click a card for real screenshots, build steps, troubleshooting, scripts and test evidence.

[Projects](#verified-projects) · [Challenge](docs/WORKFLOW.md) · [Starter](docs/START-HERE.md) · [Evidence](docs/EVIDENCE.md)

## Verified projects

{gallery}

<details>
<summary>Upcoming days ({len(pending)}) — planned or in progress</summary>

{upcoming}

</details>

This independent challenge is inspired by Ship 30 for 30; no affiliation. Detailed technical evidence and original screenshots remain in each linked project page.
'''
    result = {ROOT/'README.md': readme}
    for p in projects:
        base = ROOT/'projects'/f'day-{p["day"]:02}'
        visual = f'![Implementation result]({p["visual"]})' if p['visual'] else '![Placeholder — no implementation evidence](../../assets/awaiting-evidence.svg)'
        evidence = [f'[{e["path"]}]({e["path"]}) — {e["caption"]}; captured {e["captured"]}; source: {e["source"]}; SHA-256 `{e["sha256"]}`' for e in p['evidence']]
        tests = [f'{t["check"]}: expected {t["expected"]}; observed {t["observed"]}; **{t["result"]}**. [Evidence]({t["evidence"]})' for t in p['tests']]
        text = f'''# Day {p['day']:02} · {p['title']}

**{STATUSES[p['status']]}** · [All projects](../../README.md)

## Objective and use case

{p['objective']}

**Problem:** {p['problem']}

## Built and outcome

{p['built']}

{p['outcome']}

{visual}

## Environment and skills

**Technologies:** {', '.join(p['technologies']) or 'Not selected.'}

**Skills demonstrated:** {', '.join(p['skills']) or 'None claimed yet.'}

## Implementation

{bullets(p['steps'], 'No implementation recorded. Add reproducible steps and link relevant scripts/configuration examples.')}

Architecture diagrams, when applicable, belong in `diagrams/`. Actual screenshots belong in `screenshots/`; sanitized configuration examples in `configs/`; reusable code in `scripts/`. Link each used artifact in the evidence list. Unused folders are intentional.

## Validation

{bullets(tests, 'Not tested. No passing checks claimed.')}

## Problems and resolutions

{bullets(p['problems'], 'No troubleshooting recorded yet.')}

## Evidence

{bullets(evidence, 'No implementation evidence collected yet.')}

## Limitations and next steps

{p['limitations']}

[Additional notes](NOTES.md). This README is generated from `project.json`; Codex maintains both the metadata and linked artifacts.
'''
        result[base/'README.md'] = text
    return result

def scan():
    # Heuristic guard only; human/agent content and visual review is mandatory.
    patterns = [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{20,}', r'AKIA[A-Z0-9]{16}', r'(?i)(?:password|client_secret|access_token)\s*[:=]\s*["\x27][^"\x27]{4,}["\x27]']
    for path in ROOT.rglob('*'):
        if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:
            continue
        assert not path.is_symlink(), 'Symlinks are not publishable'
        assert path.suffix.lower() not in {'.pem', '.key', '.pfx', '.p12', '.kdbx'}, 'Private credential container'
        try: content = path.read_text()
        except UnicodeError: continue
        if any(re.search(pattern, content) for pattern in patterns):
            raise ValueError('Possible secret in '+str(path.relative_to(ROOT)))

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    rendered = outputs(load())
    for path, content in rendered.items():
        if args.check:
            assert path.read_text() == content, 'Generated file out of date: '+str(path)
        else: path.write_text(content)
    scan()
    print('PASS: 30 days, evidence references, hashes, status gates, generated content, heuristic secret scan.')

if __name__ == '__main__': main()
