"""Validate evidence references and render the technical portfolio. Standard library only."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
from card_validation import card_asset, check_label, validate_presentation

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
            local(ROOT, f'assets/day-{number:02}-card.svg')
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
        asset = card_asset(p)
        return (f'<a href="{prefix}/README.md"><img src="{asset}" '
                f'alt="{esc(p.get("gallery_alt", {1: "Active Directory lab architecture", 2: "Hybrid identity lab architecture"}.get(day, p["title"]+" architecture card")))}" width="360"></a>')
    return ''

def bullets(items, empty):
    return '\n'.join('- '+str(x) for x in items) if items else empty

def outputs(projects):
    featured = [p for p in projects if p['status'] == 'verified']
    # GitHub-native two-column gallery. Each card remains linked to the project's evidence.
    cards = [card(p) for p in featured]
    gallery = '\n'.join(
        '| ' + ' | '.join(cards[i:i+2] + [''] * (2-len(cards[i:i+2]))) + ' |'
        for i in range(0, len(cards), 2)
    ) if cards else '_No verified projects yet._'
    if cards:
        gallery = '| Featured build | Featured build |\n|:---:|:---:|\n' + gallery
    readme = f'''<div align="center">

# CyberAndChill

### Identity Engineering · Infrastructure · Security

**Enterprise IT projects, built and validated.**

A curated portfolio of identity and security systems, with the architecture, test evidence and documentation behind each build.

[Explore projects](#selected-projects) · [How the portfolio works](#behind-each-project) · [X](https://x.com/cyberandchill) · [Website](https://cyberandchill.com)

</div>

---

## Selected projects

Each architecture card opens a project with a technical summary, a reproducible guide and supporting evidence.

{gallery}

## Behind each project

| Architecture | Implementation | Evidence |
|:---|:---|:---|
| A clear picture of the systems and identity flow | What was configured and why it matters | Screenshots, tests, results and troubleshooting notes |

**Open a card** to explore the project. Implementation guides are linked from each project page. All evidence reflects recorded lab work; nothing here is a claim about a live production environment.

---

<sub>CyberAndChill · [Technical portfolio guide](docs/START-HERE.md) · [GitHub](https://github.com/cyberandchill)</sub>
'''
    result = {ROOT/'README.md': readme}
    for p in projects:
        base = ROOT/'projects'/f'day-{p["day"]:02}'
        visual = f'![Implementation result]({p["visual"]})' if p['visual'] else '![Placeholder — no implementation evidence](../../assets/awaiting-evidence.svg)'
        passing = sum(t['result'] == 'pass' for t in p['tests'])
        total = len(p['tests'])
        guide_name = p.get('manual_guide', 'GUIDE.md')
        guide = base / guide_name
        guide_link = f"[**Follow the manual GUI walkthrough →**]({guide_name})" if guide.is_file() else "Manual GUI walkthrough not published yet."
        if p['status'] == 'verified': local(base, guide_name)
        if p.get('extended_reference'): local(base, p['extended_reference'])
        diagram = f"![Architecture]({p['visual']})" if p['visual'] else "_No implementation visual recorded yet._"
        reference = p.get('extended_reference')
        reference_link = f'[Extended technical reference]({reference})' if reference else ''
        details = f"""<details>
<summary>Technical evidence, validation and troubleshooting</summary>

**Checks:** {passing}/{total} passed in the recorded implementation. Original evidence is historical, not a new health check.

**Evidence:** A selection of original screenshots is included in the manual walkthrough.



**Limitations:** {p.get('overview_limitations', 'This was a controlled lab validation, not a production deployment.')}

{reference_link}

</details>"""
        if p['status'] != 'verified': details = ''
        guide_summary = 'The guide gives numbered GUI clicks, settings, useful original screenshots and expected results. An extended technical reference is available when needed.' if guide.is_file() else 'A manual walkthrough will be linked after implementation.'
        text = f"""# {p['title']}

**{STATUSES[p['status']]}** · [CyberAndChill Portfolio](../../README.md)

## What I built

{p['built']}

## Why it matters

{p['problem']}

## Architecture

{diagram}

## Rebuild it yourself

{guide_link}

{guide_summary}

## Result

{p['outcome']}

**Technologies demonstrated:** {', '.join(p['technologies']) or 'None claimed yet.'}

{details}

[Additional notes](NOTES.md). This README is generated by `tools/render.py`.
"""
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
    projects = load()
    rendered = outputs(projects)
    presentation = validate_presentation(ROOT, projects, rendered)
    scan()
    for path, content in rendered.items():
        if args.check:
            assert path.read_text() == content, 'Generated file out of date: '+str(path)
        else: path.write_text(content)
    print('PASS: portfolio projects, evidence references, hashes, status gates, generated content, card numbering/branding gate, raster OCR, heuristic secret scan.')

if __name__ == '__main__': main()
