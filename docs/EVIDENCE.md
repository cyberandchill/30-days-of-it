# Evidence standard

A verified project needs a concise outcome, reproducible implementation steps, actual result visual, technologies, skills, and passing checks with expected and observed results. Every check and result visual must reference a public-reviewed evidence artifact. Record each artifact's relative path, caption, capture date, source description, and SHA-256. Hashes establish file identity, not the truth of a claim; Codex must inspect the source and compare the claim to the evidence.

Use native screenshots or genuine command output. A diagram may explain architecture but must not masquerade as an implementation screenshot. For work without a GUI, a genuine terminal capture or clearly labeled visual of measured results is appropriate. Never generate a synthetic screenshot or invent logs, configuration, test output, capture dates, or successful execution.

Statuses: `planned` means no outcome claimed; `in-progress` means implementation is underway; `blocked` records the blocker; `verified` means the project's stated checks passed. A partially successful project stays in progress or blocked until its documented objective is validated. Report remaining limitations and cleanup honestly. Historical evidence must retain its original date and must not imply a current-state check.

Before publication inspect text AND every image. Remove credentials, keys, tokens, authorization headers, cookies, recovery codes, emails, account identifiers, private hostnames, addresses, tenant IDs, serial numbers, and other sensitive details unless explicitly approved for public disclosure. Use sanitized copies, never overwrite source evidence. Mark redactions and label example configuration as an example. Do not publish raw infrastructure dumps or authentication files. Keep sensitive originals outside this repository and its Git history.

`tools/render.py` checks references, artifact hashes, completion requirements and some common secret patterns. It cannot determine authenticity or detect every secret, especially in images. Content review remains required. If a secret is accidentally committed, stop publication and follow provider revocation and repository-history remediation procedures.

An evidence record in `project.json` has fields `path`, `caption`, `captured` (ISO date/time of actual capture), `source` (public-safe provenance), `sha256`, and `public_reviewed: true`. A test has `check`, `expected`, `observed`, `result` (`pass`, `fail`, or `not-tested`), and `evidence` (matching evidence path). No sample result is evidence of execution.
