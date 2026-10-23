# Start your own 30-day challenge

Copy this public starter into a new repository you control, or use GitHub's template feature if enabled. No lab platform, vendor account, paid service, or cloud infrastructure is required by this portfolio. Rendering requires Python 3.10 or later, with no third-party packages. GitHub displays the README directly; no hosting build or GitHub Actions is needed.

Choose work that fits your access and experience: troubleshoot a service, automate a task, restore a backup, analyze a dataset, investigate an alert, harden an application, repair a network, or document an accessibility improvement. These are ideas, not completed projects. A small validated outcome is enough for one day.

Connect Codex to your repository and provide access to the relevant lab evidence. Repository access alone does not provide guest, cloud, or workstation access. Authentication and MFA stay in the provider's private sign-in flow. Tell Codex what it may read and publish; setup never authorizes infrastructure changes.

Use this request:

> Maintain my 30-day IT portfolio. Review completed work in the sources I authorize. Select the next unused day, collect and sanitize actual evidence, document what I built and tested, update the card, validate the portfolio, then commit and push the public-safe changes. Preserve completed projects. Keep unverified outcomes explicit. Ask only for missing access or a material ambiguity.

You do not need to write Markdown. Codex maintains each day's `project.json`, artifacts, README, and the gallery. The same request works across specialties. Choose a specific day if desired; project slots do not impose a calendar schedule.

Maintainers can run `python3 tools/render.py` and `python3 tools/render.py --check` from a checkout. On systems with an Ansible-only access policy, invoke those commands through an approved playbook.
