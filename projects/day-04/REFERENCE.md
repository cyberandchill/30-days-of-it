# AI-Assisted Onboarding — Extended Technical Reference

Conventional configuration reference derived from the completed lab. All namespaces and identity strings in examples are reserved or synthetic examples. The original integration is not distributed; the recipe below specifies an independent adapter. A complete fresh manual replay was not performed.

## Starting environment and responsibilities

Use an existing isolated AD forest and a separate application server. Preserve prior identities, existing OU/sync boundaries, persistent databases, the midPoint keystore and target data. Install midPoint's native PostgreSQL repository using the vendor's initialization process once. Reuse existing instances rather than importing a second copy for a status check.

midPoint is the provisioning/approval authority. Keycloak supplies application identities, group-derived realm roles and OIDC authentication. AD supplies real directory accounts and security groups. The HR integration validates records and requests catalog access; it does not approve elevated access. The recommender has no provisioning credentials and cannot read the protected credential store. Ollama produces explanations only.

## Software and reference sources

Recorded installation: midPoint 4.10.5; native AD LDAP connector 3.9.4; PostgreSQL 16; Keycloak 26.6.1; Python 3.14; scikit-learn as recorded in the [version receipt](evidence/versions.json); local Ollama with Qwen2.5 0.5B. The existing community Keycloak connector was built from a pinned revision and identifies itself as **2.0.1-SNAPSHOT**. The receipt contains the actual revision/digests; do not describe this as a released stable artifact.

- [Official midPoint container deployment](https://docs.evolveum.com/midpoint/get-started/install/containers/)
- [AD connector configuration and delegation](https://docs.evolveum.com/connectors/resources/active-directory/active-directory-ldap/)
- [Current native-reference AD sample](https://github.com/Evolveum/midpoint-samples/blob/master/samples/resources/ad-ldap/ad-ldap-medusa-native-references.xml)
- [Entitlements and associations](https://docs.evolveum.com/midpoint/reference/master/resources/entitlements/)
- [Existing Keycloak connector source](https://github.com/openstandia/connector-keycloak)
- [Ollama generate API](https://docs.ollama.com/api/generate)
- [midPoint approval REST operations](https://docs.evolveum.com/midpoint/reference/master/interfaces/rest/endpoints/cases/)
- [Microsoft LDAPS certificate requirements](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-over-ssl-3rd-certification-authority)

## Entitlement and job specification

Every hire receives `collaboration` and its own department application. The remaining entitlements follow the independently frozen job matrix.

| Department | Department application | Additional Manager entitlement |
|---|---|---|
| IT | `it-portal` | `platform-admin`, requires approval |
| Finance | `finance-erp` | `finance-approver`, requires approval |
| Sales | `sales-crm` | None |
| HR | `hr-records` | None |
| Operations | `operations-logistics` | None |

| Job category | Access level | Additional ordinary access |
|---|---:|---|
| Specialist | 1 | None |
| Analyst | 2 | `project-analytics` |
| Senior Analyst | 3 | `project-analytics`, `reporting` |
| Manager | 4 | `reporting` |

There are five existing peers per department/job combination: 100 peers. One peer in each combination has a historical cross-department overgrant; another lacks its department membership; five Specialist records have unnecessary reporting. These deliberately inconsistent fixtures were actually provisioned and preserved for review. The model flags their abnormalities without autonomously revoking access. The two approved elevated manager cases demonstrate controlled exceptions to ordinary department provisioning.

## Conventional service inputs and execution

The integration is a small conventional REST adapter, not a replacement IGA engine. Implement it with Python, an authenticated input endpoint and a durable unique employee key. It must use a restricted midPoint requester rather than a setup administrator. Do not give provisioning or approval credentials to the recommender.

1. Validate the seven HR fields, enforce the title/level matrix and reject extra fields. Normalize the username from a synthetic employee key, and hash the canonical input. Store the key/hash before calling external services. A conflicting hash is an error; an identical retry inspects existing state.
2. Create or locate the midPoint user using a stable locally generated UUID per employee. Store the UUID with the event. Map `employeeNumber`, `organizationalUnit` and `title`; assign only the base account role initially. Capture the result before retrying a timeout.
3. Query comparable peer observations with the calculation below. Submit **only numeric threshold recommendations from the fixed ten-item catalog** as role assignments. LLM text is displayed to a reviewer and never executed.
4. Let native eligibility rules and approval cases control assignment execution. Pending roles must stay absent from both targets. Do not resend a pending assignment on replay; find its existing case first.
5. Compare actual AD and Keycloak users, enabled states and membership sets against the approved assignments. Return `completed` only after both targets match. Otherwise retain `pending-review`, `failed` or `reconciliation-required` and the existing identity key.
6. On recovery reconcile the existing midPoint identity, then recheck both targets and replay the same record. Use a database transaction/unique constraint so two simultaneous events cannot create two users. Roll back and close failed transactions.

Use the supported [midPoint REST interface](https://docs.evolveum.com/midpoint/reference/master/interfaces/rest/) for this adapter. An initial user body can be saved as `employee.xml` after replacing the uppercase role placeholder with your own role UUID:

```xml
<user xmlns="http://midpoint.evolveum.com/xml/ns/public/common/common-3"
      xmlns:c="http://midpoint.evolveum.com/xml/ns/public/common/common-3">
  <name>example-hire</name>
  <givenName>Example</givenName><familyName>Employee</familyName>
  <employeeNumber>EXAMPLE-001</employeeNumber>
  <organizationalUnit>IT</organizationalUnit><title>Specialist</title>
  <activation><administrativeStatus>enabled</administrativeStatus></activation>
  <assignment><targetRef oid="YOUR-BASE-ROLE-UUID" type="c:RoleType"/></assignment>
</user>
```

Set an initial password using a protected credential channel or the native password policy before testing target authentication. Do not put actual passwords in a saved public XML file. In an attended terminal, the following prompts privately for the requester's password; use your own trusted HTTPS URL:

```sh
curl --fail-with-body --user hr-requester \
  -H 'Content-Type: application/xml' -H 'Accept: application/xml' \
  --data-binary @employee.xml https://iga.lab.example.com/midpoint/ws/rest/users
```

Store the returned identity location. To request a role, PATCH `users/YOUR-USER-UUID` with `Content-Type: application/xml` and this body, substituting your role UUID:

```xml
<objectModification xmlns="http://midpoint.evolveum.com/xml/ns/public/common/api-types-3"
 xmlns:c="http://midpoint.evolveum.com/xml/ns/public/common/common-3"
 xmlns:t="http://prism.evolveum.com/xml/ns/public/types-3"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <t:itemDelta><t:modificationType>add</t:modificationType><t:path>assignment</t:path>
  <t:value xsi:type="c:AssignmentType">
   <c:targetRef oid="YOUR-ACCESS-ROLE-UUID" type="c:RoleType"/>
  </t:value>
 </t:itemDelta>
</objectModification>
```

A 2xx response is not final target verification. Inspect pending cases and the nested operation result, then verify the real target. For AD, use **AD Users and Computers → user → Member Of** or conventional `Get-ADUser -Properties MemberOf,Enabled`. For Keycloak, open the dedicated realm → **Users → user → Groups / Role mapping** or use its supported Admin REST API. Compare exact sets rather than counting linked projections.

### Reproduce the numeric recommendation

Prepare a JSON array of verified peers with the fields below plus an `entitlements` list. Install `scikit-learn==1.7.2` and use this conventional Python calculation. Expected-access labels must be a separate file and must never enter `features` or the training matrix.

```python
from sklearn.feature_extraction import DictVectorizer
from sklearn.neighbors import NearestNeighbors

def recommend(peers, hire, catalog):
    def features(person):
        return {key: str(person[key])
                for key in ("department", "job_title", "access_level")}
    encoder = DictVectorizer()
    matrix = encoder.fit_transform([features(p) for p in peers])
    model = NearestNeighbors(n_neighbors=5, metric="cosine").fit(matrix)
    distances, indices = model.kneighbors(encoder.transform([features(hire)]))
    selected = [peers[int(i)] for i in indices[0]]
    scores = {role: sum(role in p["entitlements"] for p in selected) / 5
              for role in catalog}
    return {"scores": scores,
            "recommendations": [role for role, score in scores.items() if score >= .6],
            "distances": distances[0].tolist()}
```

Build the 100 peers deterministically from the five departments and four job categories: five peers per combination. Start with the job matrix below; add one cross-department extra to the first peer and remove department access from the second peer in each combination. Give the fifth Specialist peer in each department unnecessary reporting. Use separate synthetic usernames and never real personnel data. For the 20 hires, create one per department/job combination without modifying the frozen expected labels. A baseline recommends collaboration, department access and reporting for everybody; compare its raw output to the same labels before native policy filtering.

Send the numeric output to local Ollama using `/api/generate` with model `qwen2.5:0.5b`, `stream: false` and a prompt asking for an explanation of minority entitlements. Use a timeout; model failure must never bypass policy. Capture the model response separately from the numeric recommendation. The implementation used actual peer observations and the same feature/threshold approach; the excerpt is a conventional explanatory adaptation, not a released copy of the original adapter or a separately replayed build.

The HR event contract has exactly seven fields:

```json
{
  "employee_id": "EXAMPLE-001",
  "username": "example-hire",
  "given_name": "Example",
  "family_name": "Employee",
  "department": "IT",
  "job_title": "Specialist",
  "access_level": 1
}
```

This is a synthetic example shape, not a credential. Use a documented one-to-one username derivation for your synthetic employee IDs. Unexpected fields, unknown categories, incompatible title/level values and conflicting duplicates are rejected before any new provisioning. An exact replay returns the existing verified result. A unique employee key and payload hash prevent duplicate identities; failed duplicate inserts must be rolled back and their connection closed.

The recommendation API accepts the same identity attributes, returns the five peer IDs, cosine distances, per-entitlement prevalence, the `>=0.6` recommendations, minority anomalies and the local model explanation. Expected labels are not model features. The result is advisory; only numeric entitlement names from the fixed catalog are submitted to native policy. Explanations are not parsed into permissions.

## Native resource settings

AD uses TLS on 636 with hostname validation and the specific trusted public server certificate. Base context covers only the owned IGA containers. Account attributes include DN, login/UPN, employee identifier, names, department/title, activation and password. The service account has no Domain Admin or other directory administration membership.

AD reference configuration:

```xml
<managedAssociationPairs>"user"+memberOf -# "group"+member</managedAssociationPairs>
```

After changing connector references, clear/refresh only the cached resource schema. Define account/default and entitlement/group, mark the group intent as appropriate, and use a resource-level association type. Its subject association is `ri:group`; its outbound mapping uses:

```xml
<expression>
  <associationConstruction>
    <objectRef>
      <mapping>
        <expression><associationFromLink/></expression>
      </mapping>
    </objectRef>
  </associationConstruction>
</expression>
```

Each owned AD group is linked to its entitlement role projection. Business access roles induce those group roles. This is conventional role-to-entitlement modeling; obsolete account-level association mappings were removed. Set the association's tolerance to false within this scoped lab so revoked grants disappear.

The Keycloak connector authenticates through a confidential service account restricted to the dedicated realm. User object class is `user`, not a generic `AccountObjectClass`; attributes include `username`, `firstName`, `lastName`, `email`, activation, password and `groups`. Group values are IDs. The `groups` attribute must have **fetchStrategy explicit** and **tolerant false**; otherwise existing memberships can escape reconciliation. Enable the connector's password-reset API mode to keep raw passwords out of administrative event details. Group role mappings produce the realm roles checked by the application.

## Requester and approval configuration

Use exact immutable catalog IDs, not role-name prefixes. The requester can add/read only synthetic hire identities. Its assign authorization is **request phase only**, targeted to the base role plus the ten access-role IDs. Assignment modification is **execution phase only**. Target-shadow read/add/modify/delete permissions are execution-only and scoped to the two owned resources. No raw-operation, superuser-role, reviewer-role or case-completion authority is granted.

Eligibility rules enforce department, title and ordinary access restrictions. The final elevated approval rule is a native system global policy rule with:

- An assignment-add constraint and `evaluationTarget = assignment`.
- A focus selector restricted to synthetic new hires.
- A target selector containing exactly the two elevated application-role IDs.
- A named approval stage pointing to the distinct reviewer, `firstDecides`, and `outcomeIfNoApprovers = reject`.

An initial approval-rule placement failed to gate assignment execution. Temporary grants were removed and revocation verified before the final tests. Test native cases and real target membership before accepting the gate.

For conventional reviewer operation, open **Cases → All approvals**, inspect the request and choose Approve/Reject using the separate reviewer account. The supported REST equivalent completes the work item at `cases/{case-id}/workItems/{item-id}/complete`; the output type must explicitly be `AbstractWorkItemOutputType`. The recorded reviewer actions were automated tests. The requester received 403 for each of the three decision attempts.

## Protected application

The application uses authorization code with PKCE S256; direct password grants are disabled. It checks OAuth state and validates the signed ID token's issuer, audience, expiry and nonce against the expected Keycloak realm/client. Session cookies contain minimal signed session state, not bearer tokens. Every department/elevated route checks the required role.

The browser uses the same canonical identity/application URLs as the callback registration. For this local lab the application address is `http://127.0.0.1:18082` and identity service is `http://127.0.0.1:18081`; these are accessible on the designated desktop. HTTP loopback/development mode is a lab boundary, not production TLS/HA hardening.

## Failure and recovery

A real Keycloak stop was used for the final hire. The HR endpoint returned 503 while the midPoint identity and real AD account existed. After Keycloak was restored, the existing identity was reconciled through midPoint's supported recompute action with reconciliation, and the same HR request was replayed. No manual target user creation, disk recreation or duplicate account was used. Final target inspection and the recovered employee's browser session passed.

HTTP success alone does not prove the final state. midPoint can return handled/partial outcomes; inspect the operation result and both real targets. A two-link user is not evidence that both resources contain correct identities. Do not duplicate a still-running operation after a timeout. Preserve the failed result and current identity state first.

## Measured comparison and limitations

The independently frozen expected-access specification contains 200 binary decisions (20 hires × 10 entitlements) and 62 expected grants. Its SHA-256 is `7b2aeb151b121410f2a5d18fedb109929014f4f580d793c86164fe673777105c`.

| Raw recommendations | Coarse department RBAC | Peer recommendations |
|---|---:|---:|
| True positives | 50 | 62 |
| False positives / excessive recommendations | 10 | 0 |
| False negatives | 12 | 0 |
| True negatives | 128 | 138 |
| Precision | 83.33% | 100% |
| Recall | 80.65% | 100% |
| Accuracy | 89% | 100% |

Native policy blocked the conventional baseline's ten excessive reporting requests, so its effective excessive grants were also zero. AI improves recommendation coverage on this fixture; authorization remains native and deterministic in both cases.

The conventional fixture batch took 10.55 seconds including actual target checks. Successful AI HR request durations totaled 29.13 seconds, averaging 1.46 seconds per hire. These are single-run lab observations with different recovery/approval timing boundaries. They are not a matched production benchmark and do not show an AI provisioning speedup.

Three distinct-reviewer test decisions were recorded: two approvals and one rejection. The baseline had 22 raw entitlement discrepancies needing correction; AI had zero on this fixture. Human review minutes and human productivity savings were not measured. Peer anomaly analysis is in-sample, and the synthetic hire categories deliberately have matching historical peers. No broader model-generalization claim is supported.

## Evidence and procedure boundaries

[Measured results](evidence/measured-results.json), [versions](evidence/versions.json), and [image provenance](evidence/image-provenance.json) are selected, privacy-reviewed records of the October 24, 2026 implementation. Originals are retained separately. Screenshots preserve observed outcomes with labeled identifier masks; the advisory data image is explicitly a view of saved measured fields.

Configuration used supported interfaces and conventional tooling; native console navigation and all application sign-ins were exercised through automated browser interaction. The complete independent manual procedure, public example snippets and a newly implemented third-party adapter have not been replayed end to end. The separate reviewer decisions were automated REST tests, not human review sessions. To use the reviewer's GUI, also configure the built-in Approver role and suitable self-service UI rights; that GUI setup is a derived alternative.

The lab uses development-mode Keycloak and local HTTP endpoints. Production TLS, availability, secret rotation, bootstrap-admin removal and broader model validation are outside the recorded acceptance. The community connector is a pinned snapshot. This project demonstrates a working integration and its evidence; it is not a production deployment package.
