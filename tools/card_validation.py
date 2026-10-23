"""Public presentation checks; internal file paths are not display labels."""
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET


def normalized(value):
    value = unicodedata.normalize('NFKC', html.unescape(str(value)))
    value = ''.join(c for c in value if unicodedata.category(c) != 'Cf')
    return re.sub(r'\s+', ' ', value).strip()


FORBIDDEN = re.compile(
    r'(?<![a-z0-9])day[\s_–—:#-]*(?:no\.?\s*|number\s*)?\d+\b'
    r'|\b\d+\s*(?:[/⁄]|of|out\s+of)\s*30\b'
    r'|\b30[\s_-]*days?(?:[\s_-]*of[\s_-]*it)?\b'
    r'|\b(?:(?:prove|ship|build)[\s_-]*)?30[\s_-]*(?:for|/)[\s_-]*30\b'
    r'|\bchallenge\b'
    r'|\bproject[\s_-]*(?:(?:id|no\.?)[\s_:#-]*)?\d+\b'
    r'|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
    re.I,
)


def check_label(value, context='public label'):
    if FORBIDDEN.search(normalized(value)):
        raise ValueError('Publication blocked: prohibited numbering or branding in '+context)


def card_asset(project):
    return project.get('card_asset', 'assets/hybrid-identity-portrait-v2.svg' if project['day'] == 2
                       else f'assets/day-{project["day"]:02}-card.svg')


def safe_asset(root, relative):
    original = root / relative
    path = original.resolve()
    if original.is_symlink() or not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Publication blocked: missing or unsafe card asset')
    return path


def validate_svg(path):
    source = path.read_text()
    if re.search(r'<!DOCTYPE|<!ENTITY', source, re.I):
        raise ValueError('Publication blocked: SVG entity declarations')
    root = ET.fromstring(source, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
    if (root.get('width'), root.get('height'), root.get('viewBox')) != ('760', '850', '0 0 760 850'):
        raise ValueError('Publication blocked: card must use the shared 760 × 850 canvas')
    labels = []
    for node in root.iter():
        tag = node.tag.rsplit('}', 1)[-1] if isinstance(node.tag, str) else 'comment'
        if tag in {'script', 'foreignObject', 'image', 'animate', 'animateTransform', 'set'}:
            raise ValueError('Publication blocked: card contains active or embedded image content')
        if node.text:
            labels.append(node.text)
            check_label(node.text, 'SVG text, description or metadata')
        if node.tail:
            labels.append(node.tail)
            check_label(node.tail, 'SVG text')
        for name, value in node.attrib.items():
            name = name.rsplit('}', 1)[-1]
            if name.lower().startswith('on'):
                raise ValueError('Publication blocked: SVG event handler')
            if name in {'href', 'src'}:
                if not value.startswith('#'):
                    raise ValueError('Publication blocked: external SVG content')
                continue
            check_label(name+' '+value, 'SVG attribute or image label')
    # Also catches labels split across adjacent text/tspan elements.
    check_label(' '.join(labels), 'combined SVG labels')
    check_label(''.join(labels), 'combined SVG labels')


class Gallery(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.labels = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'iframe', 'object'}:
            raise ValueError('Publication blocked: active gallery content')
        attrs = dict(attrs)
        for name, value in attrs.items():
            if value is not None and name not in {'href', 'src'}:
                check_label(name+' '+value, 'gallery attribute or alt text')
        if tag == 'img':
            if not attrs.get('alt', '').strip():
                raise ValueError('Publication blocked: card needs descriptive alt text')
            self.images.append(attrs.get('src', ''))

    def handle_data(self, text):
        self.labels.append(text)


def validate_gallery(text):
    # Remove link destinations, preserving Markdown labels. Numbered paths stay legal.
    text = re.sub(r'(!?\[[^\]]*\])\([^)]*\)', r'\1', text)
    parsed = Gallery()
    parsed.feed(text)
    parsed.close()
    check_label(' '.join(parsed.labels), 'homepage text')
    return parsed.images


def ocr_image(path):
    if not shutil.which('tesseract'):
        raise ValueError('Publication blocked: tesseract is required for raster card review')
    results = []
    for mode in ['6', '11']:
        result = subprocess.run(['tesseract', str(path), 'stdout', '--psm', mode],
                                capture_output=True, text=True, timeout=60, check=True)
        results.append(result.stdout)
    return '\n'.join(results)


def validate_raster(path):
    try:
        from PIL import Image
    except ImportError as error:
        raise ValueError('Publication blocked: Pillow is required for raster card review') from error
    with Image.open(path) as image:
        width, height = image.size
        if width * 850 != height * 760:
            raise ValueError('Publication blocked: raster card has an inconsistent portrait ratio')
        if getattr(image, 'n_frames', 1) != 1:
            raise ValueError('Publication blocked: animated card requires separate review')
        check_label(json.dumps(image.info, default=str), 'raster metadata')
        check_label(str(image.getexif()), 'raster EXIF metadata')
    with Image.open(path) as image:
        image.verify()
    check_label(ocr_image(path), 'raster card OCR')


def validate_presentation(root, projects, rendered, raster=True):
    images = validate_gallery(rendered[root / 'README.md'])
    expected = []
    sources = set()
    rasters = set()
    for project in projects:
        check_label(project['title'], 'public project heading')
        page = root / 'projects' / f'day-{project["day"]:02}' / 'README.md'
        check_label(rendered[page].splitlines()[0], 'public project heading')
        if project['status'] != 'verified':
            continue
        check_label(project.get('gallery_alt', project['title']+' architecture card'), 'card alt text')
        for key, value in project.items():
            if key.startswith('card_') and key not in {'card_asset', 'card_rasters'}:
                check_label(key+' '+json.dumps(value), 'card metadata')
        asset = card_asset(project)
        expected.append(asset)
        sources.add(safe_asset(root, asset))
        if not isinstance(project.get('card_rasters', []), list):
            raise ValueError('Publication blocked: card_rasters must list internal asset paths')
        for relative in project.get('card_rasters', []):
            rasters.add(safe_asset(root, relative))
    if images != expected:
        raise ValueError('Publication blocked: gallery differs from approved card sources')
    # Include retained public card variants, not just the currently selected gallery asset.
    for path in (root / 'assets').rglob('*'):
        if not path.is_file() or 'card' not in str(path.relative_to(root / 'assets')).casefold():
            continue
        if path.suffix.lower() == '.svg': sources.add(path)
        elif path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}: rasters.add(path)
    for source in list(sources):
        for sibling in source.parent.glob(source.stem+'*'):
            if sibling.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}: rasters.add(sibling)
    for path in sources:
        safe_asset(root, str(path.relative_to(root)))
        if path.suffix.lower() == '.svg':
            validate_svg(path)
        else:
            rasters.add(path)
    if raster:
        for path in rasters:
            safe_asset(root, str(path.relative_to(root)))
            validate_raster(path)
        # OCR also checks outlined SVG lettering that is absent from text nodes.
        if sources:
            if not shutil.which('rsvg-convert'):
                raise ValueError('Publication blocked: rsvg-convert is required for rendered card review')
            with tempfile.TemporaryDirectory() as directory:
                for number, path in enumerate(sorted(sources)):
                    if path.suffix.lower() != '.svg':
                        continue
                    preview = Path(directory) / f'card-{number}.png'
                    subprocess.run(['rsvg-convert', '-w', '1520', '-h', '1700', '-o', str(preview), str(path)],
                                   check=True, capture_output=True, timeout=60)
                    check_label(ocr_image(preview), 'rendered SVG OCR')
    return {'svg_cards': sum(p.suffix.lower()=='.svg' for p in sources),
            'raster_cards': len(rasters), 'raster_ocr': raster}
