# Supporting technical record

## Original objective and design decisions

Build an open-source service provider that accepts an existing synchronized identity through SAML, then demonstrate an actual application login and permission separation. Reuse the working identity environment, preserve existing identities and protections, and keep the conventional reproduction guide independent of the original implementation mechanism.

Jenkins was selected because it is a real open-source application with a maintained SAML integration and visible authentication/authorization controls. The demonstration uses an existing hybrid-joined Windows client, a dedicated local HTTPS endpoint and no build jobs. The browser and application share that computer; public hosting is unnecessary. A shared production service would require a different capacity, endpoint and certificate design.

The [manual walkthrough](GUIDE.md) documents the conventional implementation. It is not a transcript of the original build. Jenkins GUI controls were exercised through automated interaction; equivalent Entra portal steps and the fresh attended bootstrap commands are identified as derived rather than manually replayed.

## Nonproprietary configuration reference

| Area | Recorded setting / safe example |
|---|---|
| Endpoint | `https://localhost:8443/`; HTTPS loopback only |
| ACS | `/securityRealm/finishLogin` on that exact endpoint |
| SP identifier | A unique URL under the operator's verified domain; must match on both sides |
| Identity provider | Microsoft Entra non-gallery enterprise application, SAML mode |
| User scope | Two directly assigned identities: ordinary reader and separate application administrator |
| Signing trust | Active IdP signing certificate obtained through app-specific HTTPS metadata |
| SAML request | HTTP-Redirect; unspecified NameID policy; Force Authentication off |
| Response | HTTP-POST to ACS; signed assertion required |
| Username mapping | Signed `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name`, lowercase |
| Ordinary-user permission | Overall/Read only |
| Administrator permission | Overall/Administer for the separate assigned administrator |
| Anonymous/general authenticated grants | No broad application grants |
| Training workload | Zero build executors; inbound agents disabled |

Examples are substitutions, not disclosed production identifiers. No account passwords, signing private keys, assertion bodies, cookies, tenant identifiers or private infrastructure configuration are included.

## Implementation chronology — October 23, 2026

1. Reviewed the existing synchronized identity and healthy Windows domain/hybrid joins. Distinguished machine join from application SAML federation.
2. Selected Jenkins, bounded the authentication-only workload and chose a local HTTPS endpoint. Obtained the application, supported Java and required plugins from official sources and checked their checksums.
3. Encountered incomplete Windows runtime assets at one vendor's current release source. A usable initial runtime allowed setup; a newer Microsoft OpenJDK 21.0.12.1 build was then verified, activated and the unused older runtime removed. The recorded final software versions are in the walkthrough.
4. Created one non-gallery enterprise application, set its Identifier/ACS/sign-on URL, enabled SAML, supplied an active signing certificate and required direct user assignment. An initial generic role assignment was rejected because the template exposed its own role; selecting the real supported role corrected the assignment.
5. Initialized Jenkins on loopback HTTPS with restricted local execution and no build executors. Corrected Windows text-encoding problems and an outdated startup configuration call. Restarted only the application; the final startup was healthy.
6. Diagnosed a Windows console sign-in failure without resetting an established account password. The existing domain credential validated through the native logon interface; explicit domain-user selection and slower input resolved the interactive sign-in. This troubleshooting event was not a SAML result.
7. Opened Jenkins' real Security UI. Entered app-specific IdP metadata, matching SP identifier, signed username claim, request binding and signed-assertion requirement. Added the reader and separate administrator to the matrix, then saved the realm switch. Removed the bootstrap administration grant and temporary bootstrap material.
8. Performed a real ordinary-user browser login through Entra. Independently checked the browser-carried assertion signature against the metadata signing certificate, plus issuer, audience, destination, time and request correlation. The signed username claim matched the intended user.
9. Confirmed that the ordinary application identity had read access but received HTTP403 for administration. An independent anonymous session received403 for protected application data. A synthetic unsigned, unsolicited response did not authenticate that anonymous session.
10. Restarted Jenkins and repeated the real SAML flow successfully. Preserved authentic UI captures, prepared conspicuous privacy masks and verified the guide links. Publication preparation uses this historical evidence; it does not rerun the lab or claim current service health.

## Troubleshooting and corrections

| Observation | Diagnosis and correction | What this does not prove |
|---|---|---|
| A vendor lookup was denied or lacked current Windows assets | Used official alternate distribution metadata and verified a supported Windows runtime's checksum | All mirrors/vendors were tested |
| Generic application role assignment failed | Selected the actual role exposed by the non-gallery template | A directory role was assigned to the learner |
| Startup text or configuration call failed | Corrected encoding/API compatibility and restarted the application | A fresh manual bootstrap was replayed |
| Windows sign-in failed at a saved account tile | Validated the existing credential, chose the intended domain user and corrected input handling | A password reset or SAML fault occurred |
| New federated names appeared unknown in the bootstrap realm | Matched the signed claim to explicit application permissions and completed SAML login | Another local password account was required |
| NameID was opaque rather than the UPN | Used the explicitly configured, signed `name` claim as the username | NameID-UPN equality was required or passed |
| Anonymous token reported `authenticated: true` | Checked `anonymous`, effective identity and protected-resource access | That field alone establishes a user session |
| A certificate was not found by its friendly name | Compared the exact public certificate thumbprint; friendly names need not survive export | Working certificate trust needed replacement |
| An inactive display produced a blank capture | Excluded the blank image and captured the real browser page through its screenshot API | A screenshot was reconstructed |

## Actual validation results

These are selected public-safe observations from the original October 23 implementation. The [measured results](evidence/measured-results.json) contain only application/protocol facts; no live authentication data is included.

| Check | Expected | Observed |
|---|---|---|
| SP-initiated request | Redirect to Entra with matching issuer and ACS | Matched |
| SAML response | Browser HTTP-POST to exact ACS | Observed |
| Assertion signature | Valid against configured IdP metadata certificate | Cryptographically valid |
| Assertion checks | Intended issuer/audience/destination, valid time and correlated request | Matched |
| Username | Signed configured claim maps to intended ordinary identity | Matched; NameID remained opaque |
| Application identity | Authenticated, nonanonymous ordinary user | Confirmed |
| Ordinary-user administration | Denied | HTTP403 |
| Anonymous protected API | Denied | HTTP403 |
| Synthetic unsigned unsolicited response | Must not authenticate fresh anonymous session | Session remained anonymous; response302 |
| Restart persistence | New SAML flow works after Jenkins restart | Passed |
| Fresh complete manual deployment | Independently replayed from a new environment | Not performed |

A successful login and a valid assertion signature are separate observations; both were checked. The synthetic negative response tests combined invalid conditions and does not isolate signature validation from request correlation. It is not a replay test. The separate administrator's permissions were configured and inspected, but its own browser login was not tested.

## Evidence and conventional commands

The seven authentic screenshots are embedded beside their corresponding [manual steps](GUIDE.md). The [image provenance record](evidence/image-provenance.json) identifies capture dates, source/copy hashes and privacy-mask coordinates. Hashes identify bytes, not truth; source images and claims were also reviewed.

The walkthrough includes conventional Java launch, checksum, localhost certificate and certificate-trust procedures. Those example commands are a reproduction path, not a claim that the published placeholder version was executed. Do not copy an assertion, cookie, password or private PFX into a report or repository. No original operational scripts or private build logs are needed to reproduce the demonstrated federation.

## Lessons learned

- Device join, SAML authentication and application authorization are separate controls.
- Keep the root URL, ACS and logical Entity ID explicit and consistent.
- Map the signed claim you actually receive; opaque NameID is not automatically an error.
- Validate ordinary-user denial as deliberately as successful login.
- Check anonymous identity and effective permissions, not one ambiguously named status field.
- Keep certificate trust, signature checking and optional encryption conceptually separate.
- Real screenshots show a state; protocol measurements and a repeat login substantiate the result.

## Limitations and next steps

The complete fresh-environment manual path, Entra GUI click sequence, separate administrator login, real unassigned-user login, replay resistance, certificate rollover, MFA-policy changes, federated logout and Windows/host reboot were not tested. Jenkins restart and a subsequent real login were tested. No production performance, shared endpoint, build pipeline or permanent prompt-free authentication claim is made.

Useful next exercises are a safe full manual replay, a separate administrator sign-in, an ordinary unassigned-user denial test, and controlled certificate rollover. They are future work, not results of this project. Existing browser/Entra sessions may expire or require reauthentication under tenant policy.
