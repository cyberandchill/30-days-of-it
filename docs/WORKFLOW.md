# CyberAndChill Portfolio — Publishing Workflow

1. Read `AGENTS.md`, the repository and the current day's actual lab evidence. Select only the appropriate day; preserve every prior project.
2. Record the **real outcome**, concise project objective, honest status, relevant architecture and the essential passing checks in `project.json`. Never invent execution, evidence or screenshots.
3. Create or update that day's `GUIDE.md` as a **manual GUI walkthrough** someone can follow manually. Include prerequisites, exact UI paths, numbered clicks, settings/values (using safe placeholders), expected results and short troubleshooting where needed. Reuse prior days as prerequisites; avoid duplicates.
4. Integrate a few genuine redacted screenshots near the corresponding instructions. Keep sensitive automation details, command histories, implementation workflows, and private archives outside the public repository. Distinguish real captures from diagrams and examples.
5. Keep the landing gallery high-level: concise architecture cards for verified projects. Project README: objective/outcome, architecture, obvious walkthrough link, concise results and a short validation summary. Do not publish challenge branding, completion counts, or campaign day numbers.
6. Update `tools/render.py` if needed, run `python3 tools/render.py` and `python3 tools/render.py --check`. Verify changes, all links, image redactions, private information and any generated output.
7. Commit and push only reviewed, public-safe changes through authorized repository access. Never force-push. Verify the remote commit and report the resulting URL.

This workflow runs only when explicitly requested. A GitHub connection does not grant access to the lab. Never make unrelated infrastructure changes.
