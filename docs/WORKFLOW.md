# Daily updates maintained by Codex

1. Fetch the latest repository state. Read `AGENTS.md` and all 30 day records. Reuse the relevant unfinished day or select the next planned slot; never replace a completed project with unrelated work.
2. Review authorized work records and source evidence. Distinguish a planned task, a completed implementation, and a verified outcome. Do not provision or rerun destructive labs just to populate this portfolio. If access is missing, document the gap and request only the necessary access.
3. Collect the smallest useful set of genuine screenshots, sanitized logs, configuration examples, diagrams and reusable scripts. Describe provenance, dates, redactions, and limitations. Store public-safe artifacts only in that day's folders.
4. Update that day's `project.json` with short recruiter-readable descriptions, actual steps, problems and resolutions, tools, skills, tests and evidence records. Set `visual` to a reviewed relative artifact path. Each artifact hash must match the final sanitized bytes.
5. Run `python3 tools/render.py`, then `python3 tools/render.py --check`. Inspect the changed README, gallery, images, scripts and configurations for accuracy and sensitive content. Review the diff to confirm unrelated days and notes were preserved.
6. Commit only the reviewed portfolio changes. Push through the connected GitHub tools when supported, or an approved local Git authentication flow. Fetch the remote branch first, preserve newer commits, and stop on conflicts rather than force-push. Verify the remote commit and links after pushing. Report the day, status, evidence and commit URL.

This is an on-request workflow. It does not continuously monitor your lab or run on a schedule. A connected repository and access to the relevant evidence are required each time; provider sign-in can expire. No GitHub Actions, paid API calls, or automatic infrastructure changes are part of the starter.

The gallery and day READMEs are generated; `project.json` is the source of truth. `NOTES.md` and artifacts are preserved. Update an existing project in place when correcting evidence, and explain material corrections in the commit. Keep all 30 day directories visible throughout the challenge.
