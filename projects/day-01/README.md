# Day 01 · Active Directory Lab: Build, Join and Verify

**✓ Verified** · [All projects](../../README.md)

## Objective and use case

Create a separate on-premises AD forest and domain-joined client, organize department identities and administrators, validate the result, and deliver beginner documentation without modifying unrelated lab guests.

**Problem:** Centralize user sign-in and onboard a workstation while preserving the existing environment.

## Built and outcome

Built an isolated Windows Server domain and joined Windows 11; verified 14 users, 5 groups, device trust and administrator separation.

Verified against October 21 implementation evidence: controller diagnostics passed, all 14 created users were enabled with requested non-expiring account/password settings, and the client passed trust, DNS, SYSVOL and endpoint-security checks. Both administrator roles and a standard role authenticated; only the administrators had elevation capability. One real administrator desktop sign-in was observed. The 13-page private guide and phone-accessible private handoff were delivered. Publication review on October 22 did not rerun or alter the infrastructure.

![Implementation result](screenshots/02-directory-organization.png)

## Environment and skills

**Technologies:** Windows Server 2022, Windows 11 Pro, Active Directory / DNS, PowerShell, Ansible, Proxmox / QEMU

**Skills demonstrated:** Identity administration, Domain join, DNS troubleshooting, UAC role validation, Evidence documentation

## Implementation

- Read the [complete chronological build story](evidence/BUILD-STORY.md) and [sanitized original request](evidence/request-and-scope.md). This entire conversation is Day 01; all 30 slots were unassigned at selection.
- Starting environment: generalized Server and Windows client templates; two new linked clones, each 2 vCPU / 4 GiB RAM / 64 GiB virtual disk. Recorded eight unrelated guest configuration hashes.
- Checked prerequisites with cyber-chill-template-preflight.yml, cyber-chill-access-preflight.yml and lab-secret-verify.yml; cloned only the two owned guests with cyber-chill-guests.yml and its two-guest variable set. Credentials remained in the approved private keyring/runtime flow.
- Used cyber-chill-domain-controller.yml to complete Server setup, install AD DS/DNS, promote the single-domain forest, restart and verify controller services and DNS. Added readiness waits after actual startup failures.
- Used cyber-chill-private-lan.yml and cyber-chill-dc-private-lan.yml for isolated guest Ethernet and private-only AD DNS registration. See the [conceptual architecture](diagrams/isolated-ad-lab.svg); real endpoints are omitted.
- Used cyber-chill-domain-users.yml for ten OUs, twelve department users, two administrators and five security groups. The owner requested non-expiring account/password settings; ordinary users remained unprivileged. See the [directory view](screenshots/02-directory-organization.png) and [actual account settings](screenshots/03-account-lifetime-settings.png).
- Used cyber-chill-client-join.yml to join the client into Workstations. Diagnosed interrupted OOBE renaming, corrected the local identity/setup state with maintained recovery, and repaired the owned machine trust with runtime credentials.
- Ran cyber-chill-client-auth-test.yml plus controller/client verification via cyber-chill-domain-inspect.yml. Corrected the administrator test to inspect linked elevated UAC tokens. Slowed console typing after dropped username characters, then confirmed an actual administrator desktop.
- Created the private guide/ZIP/diagram, ran cyber-chill-domain-guide.yml, cyber-chill-domain-qa.yml and cyber-chill-domain-finalize.yml, and confirmed all eight unrelated guest configuration hashes matched.
- Resolved remote-phone download failure through private Google Drive copies and a continuation handoff. Public portfolio copies omit private cloud links and identifiers. [Sanitized script adaptations](scripts/Test-ExampleClient.ps1) and [UAC role-check source](scripts/Test-ExampleLogonRoles.ps1) are examples, not independently replayed public variants.

Architecture diagrams, when applicable, belong in `diagrams/`. Actual screenshots belong in `screenshots/`; sanitized configuration examples in `configs/`; reusable code in `scripts/`. Link each used artifact in the evidence list. Unused folders are intentional.

## Validation

- Controller diagnostics: expected Connectivity, Advertising, Services, SysVolCheck, NetLogons and basic DNS pass; observed All six named diagnostic results passed in the original dcdiag output.; **pass**. [Evidence](evidence/measured-results.json)
- Directory identities and lifetime: expected 14 enabled created users; account and password expiration disabled; observed 14 enabled users; all PasswordNeverExpires true; all AccountExpirationDate null.; **pass**. [Evidence](evidence/measured-results.json)
- OU and group organization: expected 10 created OUs and 5 security groups; observed 10 OUs; 5 groups; four department groups each have 3 members; 2 domain administrators.; **pass**. [Evidence](evidence/measured-results.json)
- Computer membership: expected Enabled computer in Workstations, matching local name/domain; observed Enabled Workstations object; local and directory computer names/domains match; client PartOfDomain true.; **pass**. [Evidence](evidence/measured-results.json)
- Client trust and name resolution: expected Secure channel true, controller DNS record present, SYSVOL accessible; observed SecureChannel true; controller DNS record present; SYSVOL true.; **pass**. [Evidence](evidence/measured-results.json)
- Credential and privilege separation: expected Two administrators authenticate with elevation capability; standard user authenticates without administrator capability; observed 3 Windows interactive-logon API checks passed; linked elevated UAC-token capability true, true, false.; **pass**. [Evidence](evidence/measured-results.json)
- Actual desktop session: expected Domain administrator desktop observed; observed Original client report identifies an interactive administrator session; genuine console capture retained with identifier-bearing command output masked.; **pass**. [Evidence](evidence/measured-results.json)
- Endpoint protections and setup: expected Defender running; all firewall profiles enabled; setup finished; observed Defender Running; Domain/Private/Public profiles enabled; OOBE and system setup flags both 0.; **pass**. [Evidence](evidence/measured-results.json)
- Unrelated guest preservation: expected 8 unrelated guest configuration hashes unchanged; observed Final completion record confirms all 8 configurations matched their pre-build hashes.; **pass**. [Evidence](evidence/measured-results.json)
- Private beginner handoff: expected Complete guide with screenshots and no exported password; observed 13 PDF pages; 6 original final guide screenshots; password scan 0 hits; private phone delivery completed.; **pass**. [Evidence](evidence/measured-results.json)

## Problems and resolutions

- Server first boot: guest commands failed before agent/services were usable. Inspected the real setup screen, completed initial setup and added readiness waits; did not count failed launches as success.
- Post-network restart: a guest command timed out and ActiveDirectory module initialization failed during startup. Inspected actual network state and waited for domain services before configuring the private LAN.
- Built-in Administrator expiration: Windows rejected Clear-ADAccountExpiration on the protected built-in account. Verified its existing non-expiring state; cleared expiration only on created users.
- Client join idempotence: avoided NewName when unchanged and skipped already disabled adapters during DNS configuration. Reruns reused owned objects.
- OOBE identity drift: Windows assigned generated names after joining, breaking trust. Restored the registered computer identity and interrupted setup state, corrected an existing-key registry creation failure, then repaired owned machine-account trust without user-password resets.
- UAC test correction: an unelevated token initially hid administrator capability. Corrected the verification to inspect the linked elevated token; UAC remained enabled. Direct Domain Admins and explicit client admin-group membership were verified.
- Console sign-in: fast emulated typing dropped leading username characters. Slowed typing, inspected the nonsecret field, then submitted the password privately and confirmed a real desktop.
- Remote phone delivery: sandbox links were inaccessible. Uploaded private copies through the connected Google Drive and verified metadata; retained those sensitive infrastructure documents outside the public portfolio.
- Publication tooling: the Debian host had no Git executable and no Pillow installation. Used a commit-pinned source archive, connected GitHub Git-data tools, and deterministic standard-library PNG cropping/redaction; no host package installation or lab changes were needed.

## Evidence

- [screenshots/01-windows-first-start.png](screenshots/01-windows-first-start.png) — Starting condition: the new Windows client was still in regional first-start setup.; captured 2026-10-21; source: Native guest console screenshot; captured during original implementation, public copy cropped/redacted on 2026-10-22.; SHA-256 `3698bae524ae9206000662679d0722e76241312253b99d8b6c3411cf27469406`
- [screenshots/02-directory-organization.png](screenshots/02-directory-organization.png) — Active Directory Users and Computers: department OUs and dedicated containers; private namespace and root OU label masked.; captured 2026-10-21; source: Native guest console screenshot; captured during original implementation, public copy cropped/redacted on 2026-10-22.; SHA-256 `b813649380d0166fdeee157e13bb781ddc8cdf10a9bbb812d1a915cf403b5615`
- [screenshots/03-account-lifetime-settings.png](screenshots/03-account-lifetime-settings.png) — Native Account tab: Password never expires selected, Account expires set to Never. Actual account and domain identifiers masked.; captured 2026-10-21; source: Native guest console screenshot; captured during original implementation, public copy cropped/redacted on 2026-10-22.; SHA-256 `6fbddb49aa427fd49b73a9b72410a7dad48fbd46781ae1178fb21c1991b89605`
- [screenshots/04-domain-admin-membership.png](screenshots/04-domain-admin-membership.png) — Native administrator account properties: direct Domain Admins and dedicated admin-group membership; account and directory paths masked.; captured 2026-10-21; source: Native guest console screenshot; captured during original implementation, public copy cropped/redacted on 2026-10-22.; SHA-256 `f9fbc48247f9cd47f995a844c2b725fa79c55042d0790a990f73578d5465b37c`
- [screenshots/05-department-group-members.png](screenshots/05-department-group-members.png) — Native department security group: three member rows; member identities and directory paths masked.; captured 2026-10-21; source: Native guest console screenshot; captured during original implementation, public copy cropped/redacted on 2026-10-22.; SHA-256 `3ade8bdf4cff132f738ceb47c832044b4bea6bf282ffd9838e619bf2fb0f3655`
- [screenshots/06-windows-domain-membership.png](screenshots/06-windows-domain-membership.png) — Native System Properties shows domain membership; the private computer FQDN and namespace are masked.; captured 2026-10-21; source: Native guest console screenshot; captured during original implementation, public copy cropped/redacted on 2026-10-22.; SHA-256 `b15740c6ff317129f628435a45c6dd2b7614e5053c759a8d72a7424da38b3c59`
- [screenshots/07-domain-desktop-session.png](screenshots/07-domain-desktop-session.png) — Actual signed-in administrator desktop running hostname, whoami and logon-server commands. Three identifier-bearing result lines are redacted; matching session validation is in the measured-results extract.; captured 2026-10-21; source: Native guest console screenshot; captured during original implementation, public copy cropped/redacted on 2026-10-22.; SHA-256 `1641da3e7fafdb53f1b0408a4845527272a33920cfa311be69c29c4a540b3fdf`
- [evidence/image-provenance.json](evidence/image-provenance.json) — Original-image hashes, crop/redaction coordinates and final public-image hashes.; captured 2026-10-22; source: Derived from the preserved native screenshot bytes; originals retained privately.; SHA-256 `3fd541160da7f06ce1494846580aecb399308836e2f781a28684c13227b80e70`
- [evidence/measured-results.json](evidence/measured-results.json) — Allowlisted historical measured results: directory, DNS, trust, endpoint security, credential roles and unrelated-VM preservation.; captured 2026-10-22T02:30:58.9114482Z; source: Selected fields from original controller/client verification and completion reports; source hashes retained; private identifiers removed.; SHA-256 `64e494eb464b01534d585e374b26fc33322c42c75e2cfb6b9502fba892c5c163`
- [diagrams/isolated-ad-lab.svg](diagrams/isolated-ad-lab.svg) — Conceptual topology derived from this conversation’s verified build; private endpoints omitted.; captured 2026-10-22; source: New vector explanation based on original configuration; not implementation screenshot evidence.; SHA-256 `50ff4fc48f87479c79e5878d6b9beb05cca9d4553d0d8be198e1ec48de7788c3`
- [configs/example-values.json](configs/example-values.json) — Reserved documentation namespace and TEST-NET addresses; configuration examples, not real endpoints.; captured 2026-10-22; source: Adapted public example of the implemented two-guest configuration; not execution evidence.; SHA-256 `78e8c9f267df7ccd52b5ce803582b174ac1df5b123195c52a2d99cc398c9a9eb`
- [scripts/Test-ExampleClient.ps1](scripts/Test-ExampleClient.ps1) — Sanitized adaptation of the maintained client verification script; public variant not run.; captured 2026-10-22; source: Original maintained PowerShell implementation from this conversation; identifiers replaced with reserved examples.; SHA-256 `7a2495c66c74645becce851ec97b397be0b198f59f53156ee3ccff84c32e65d5`
- [scripts/Test-ExampleLogonRoles.ps1](scripts/Test-ExampleLogonRoles.ps1) — Sanitized adaptation of the maintained Windows credential/UAC role verification script; public variant not run.; captured 2026-10-22; source: Original maintained PowerShell implementation from this conversation; identifiers replaced with reserved examples.; SHA-256 `dd7fd61b75f56729e56db3242b778bdc598acfea983137fd058b41af817b28cd`
- [evidence/BUILD-STORY.md](evidence/BUILD-STORY.md) — Chronological build story, reproducible manual reference, troubleshooting, screenshots and lessons.; captured 2026-10-22; source: Prepared from this conversation and inspected historical source evidence; narrative is not independent test output.; SHA-256 `041696a44e4ff6752d84983fb0017c92ccad83efbc86520062172faae3e7bea0`
- [evidence/request-and-scope.md](evidence/request-and-scope.md) — Sanitized original voice request and chronological phone-delivery/publication follow-ups.; captured 2026-10-22; source: Prepared from this conversation and inspected historical source evidence; narrative is not independent test output.; SHA-256 `ac4d013c4bfd5c528549077722f8677b566cd8e8e730a6ad9451c13b4cd29511`
- [evidence/publication-review.json](evidence/publication-review.json) — Current public-documentation checks and disclosed starter unit-test fixture limitation; not a fresh lab execution.; captured 2026-10-22; source: Actual renderer/check, private-value scan, preserved-file comparison, isolated baseline regression run and local card preview.; SHA-256 `8c3987537c37104c983b4f686b01df88687fea84b69920d62bc46ebc17690edd`

## Limitations and next steps

Historical verification from the implementation session, not a current-state health check. Only one administrator had a graphical desktop observed; three roles were checked with the Windows interactive-logon API. Shared/non-expiring passwords and Domain Admin rights were explicitly requested isolated-lab choices, not production guidance. One controller/client only; evaluation media; no backup/restore, HA, Entra, SAML, public DNS or cross-hypervisor claims. Sanitized example scripts were not independently rerun. Interim error-screen images were overwritten; seven surviving genuine captures are published with opaque identifier redactions. See BUILD-STORY for the evidence gap and lessons. No remaining blocker for the documented on-premises lab objective.

[Additional notes](NOTES.md). This README is generated from `project.json`; Codex maintains both the metadata and linked artifacts.
