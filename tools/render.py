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
        return (f'<a href="{prefix}/README.md"><img src="assets/day-{day:02}-card.svg" '
                f'alt="{esc(p["title"])} architecture card" width="760"></a>')
    return f'- [Day {day:02}: {esc(p["title"])} — {STATUSES[p["status"]]}]({prefix}/README.md)'

def bullets(items, empty):
    return '\n'.join('- '+str(x) for x in items) if items else empty

def outputs(projects):
    completed = sum(p['status'] == 'verified' for p in projects)
    featured = [p for p in projects if p['status'] == 'verified']
    pending = [p for p in projects if p['status'] != 'verified']
    gallery = '\n\n'.join(card(p) for p in featured) or '_No verified projects yet._'
    upcoming = '\n'.join(card(p) for p in pending)
    readme = f'''# CyberAndChill | Technical Portfolio

**Identity Engineering · IT Infrastructure · Security**

I build and validate practical IT environments that demonstrate how enterprise technology works—from directory services and workstation management to hybrid identity.

This portfolio shows the architecture, problems solved, and verified outcomes behind each project. Open a project to explore its results, screenshots, and a step-by-step manual walkthrough.

**Connect:** [X / Twitter](https://x.com/cyberandchill) · [Website](https://cyberandchill.com) · [GitHub](https://github.com/cyberandchill)

## Selected projects

{gallery}
'''
    result = {ROOT/'README.md': readme}
    for p in projects:
        if p['status'] != 'verified':
            continue
        base = ROOT/'projects'/f'day-{p["day"]:02}'
        visual = f'![Implementation result]({p["visual"]})' if p['visual'] else '![Placeholder — no implementation evidence](../../assets/awaiting-evidence.svg)'
        passing = sum(t['result'] == 'pass' for t in p['tests'])
        total = len(p['tests'])
        guide = base / 'GUIDE.md'
        guide_link = "[**Follow the manual GUI walkthrough →**](GUIDE.md)" if guide.is_file() else "Manual GUI walkthrough not published yet."
        diagram = f"![Architecture]({p['visual']})" if p['visual'] else ""
        details = f"""<details>
<summary>Technical evidence, validation and troubleshooting</summary>

**Checks:** {passing}/{total} passed in the recorded implementation. Original evidence is historical, not a new health check.

**Evidence:** A selection of original screenshots is included in the manual walkthrough.



**Limitations:** Controlled lab validation, not a production deployment.

</details>"""
        text = f"""# Day {p['day']:02} · {p['title']}

**{STATUSES[p['status']]}** · [CyberAndChill Portfolio](../../README.md)

## What I built

{p['built']}

**Why it matters:** {p['problem']}

{diagram}

## Rebuild it yourself

{guide_link}

The guide gives numbered GUI clicks, settings, useful original screenshots and expected results. Historical evidence is available in the project archive.

## Result

{('Validated domain services, organized identities and groups, client domain membership, and administrative privilege separation.' if p['day'] == 1 else 'Verified scoped user synchronization, hybrid device registration and sign-in state.' if p['day'] == 2 else p['outcome'])}

**Technologies demonstrated:** {('Windows Server 2022, Windows 11 Pro, Active Directory, DNS' if p['day'] == 1 else 'Windows Server, Active Directory, DNS, Microsoft Entra ID, Windows 11' if p['day'] == 2 else ', '.join(x for x in p['technologies'] if x not in ('Ansible', 'Proxmox / QEMU', 'MSAL / GNOME Keyring')) or 'Not selected.')}

{details}


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
    rendered = outputs(load())
    for path, content in rendered.items():
        if args.check:
            assert path.read_text() == content, 'Generated file out of date: '+str(path)
        else: path.write_text(content)
    scan()
    print('PASS: portfolio projects, evidence references, hashes, status gates, generated content, heuristic secret scan.')

if __name__ == '__main__': main()
