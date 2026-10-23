# Portfolio publishing workflow

1. Read AGENTS.md, docs/EVIDENCE.md, current project records and actual evidence. Reuse the correct milestone; preserve other projects and NOTES.
2. Prepare public-safe metadata and genuine reviewed evidence. Never infer execution from plans or label derived procedures as manually tested.
3. Write the concise GUI manual using Days 1–2: Goal → Prerequisites → approximately 5–7 logical numbered steps → Verification. Include exact clicks/settings, safe example values, authentic captioned screenshots and expected results. Keep essential instructions even when more steps are necessary. State procedure-test boundaries.
4. Keep deeper conventional technical detail in an optional extended reference. Use manual_guide and extended_reference metadata to select links; retain Day 3's existing short-guide arrangement.
5. Render the exact concise README order specified in AGENTS.md. Keep walkthroughs and chronological history separate. Cards use the shared portrait design without challenge numbering; homepage remains a clickable architecture gallery.
6. Review every proposed public artifact and commit message for confidential and private operational material. Scan text, image metadata and OCR; visually inspect screenshots and diagrams. Keep private source records outside the repository. Automated checks supplement content review.
7. Run python3 tools/render.py, python3 tools/render.py --check and python3 -m unittest discover -s tools -p 'test_*.py'. Check links, hashes, claims, source/template consistency and the full diff. Stage only reviewed public paths.
8. When publication is explicitly requested, use existing authorized access, commit sanitized changes, push non-forced and verify remote commit/file bytes. Preserve concurrent work and report the actual branch. Draft social text only; do not post it.

This workflow does not authorize infrastructure changes. Preserve unrelated work and repository visibility.

The card-numbering gate in tools/card_validation.py runs before renderer writes and during --check. It rejects challenge numbering/branding and internal identifiers in public card labels, SVG text/metadata, alt text, homepage text and project headings. Numbered file paths remain valid. Raster derivatives require Pillow/tesseract; rendered SVG review requires rsvg-convert/tesseract. Missing dependencies fail publication rather than silently skipping review. No override is permitted. Use visual inspection alongside OCR.

Run the full unittest discovery command above for deliberate rejection fixtures and an isolated future-project workflow test. Synthetic fixtures are not real portfolio projects. The renderer never regenerates approved cards; raster refresh is an explicit reviewed maintenance operation. Keep conventional guide detail separate from the concise overview.
