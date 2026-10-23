# Jenkins SAML — Manual Setup Guide

**Goal:** Sign in to a local Jenkins application using Microsoft Entra SAML 2.0, while allowing a standard user to read Jenkins but not administer it. These are conventional reproduction instructions with example values—not a claim that the original deployment was performed by clicking through the GUI.

**Original verified outcome:** SAML login succeeded, administration returned HTTP 403, and login worked again after Jenkins restarted.

## Prerequisites
- A Windows 11 Pro test computer with local admin access, a browser, outbound HTTPS, and 4 GB or more of RAM for this demonstration.
- A Microsoft Entra tenant with a verified domain, an Application Administrator (or equivalent permitted role), and a standard test user.
- To reproduce the *hybrid* starting point, first complete [Active Directory](../day-01/GUIDE.md) and [Hybrid identity](../day-02/GUIDE.md). Cloud-only identities can test SAML, but are not the same recorded starting state.
- Supported Jenkins LTS, Java 21 or 25 as supported by your Jenkins version, and the Jenkins **SAML** and **Matrix Authorization Strategy** plugins.
- Use a trusted, local-only HTTPS endpoint for testing; don't expose the service to the Internet.

The recorded test used Jenkins LTS 2.580.1, Microsoft OpenJDK 21.0.12.1+1, the SAML plugin 4.623.v7875d61cd9f5, and a loopback-only endpoint at `https://localhost:8443/`. Check current Jenkins compatibility and plugin security notices before recreating it.

## Step 1 — Prepare a local Jenkins installation
1. Download the official [Jenkins WAR](https://www.jenkins.io/download/) and supported [Microsoft OpenJDK](https://learn.microsoft.com/en-us/java/openjdk/download).
2. In **File Explorer**, create `C:\SamlLab`, with `java` and `home` subfolders. Extract Java and place `jenkins.war` in the root.
3. Use an unprivileged application account with access to this folder. Verify downloaded checksums.
4. Configure a local certificate for `localhost`; import only its public certificate using **certmgr.msc → Trusted Root Certification Authorities → Certificates → All Tasks → Import**. Keep the private key and password private.
5. Start Jenkins over loopback HTTPS using the attended launch commands in the [extended technical reference](REFERENCE.md#5-start-jenkins-over-loopback-https). A Java WAR launch and local certificate creation require commands; there is no equivalent standard Windows point-and-click installer for this exact method.
6. On the same PC, open `https://localhost:8443/` in Edge.

**Verify:** Jenkins displays the initial setup page over trusted HTTPS, with the service listening only on `127.0.0.1:8443`. If not, check the certificate, Java version, port, permissions, and terminal errors.

## Step 2 — Install the Jenkins plugins
1. On **Unlock Jenkins**, obtain the one-time bootstrap password privately from `C:\SamlLab\home\secrets\initialAdminPassword` and enter it only in the local browser.
2. On **Customize Jenkins**, choose **Select plugins to install**.
3. Install **SAML** and **Matrix Authorization Strategy**, including required dependencies.
4. Complete **Create First Admin User**, then open **Manage Jenkins → Plugins → Installed plugins**.
5. Open **Manage Jenkins → System → Jenkins Location** and set the URL to `https://localhost:8443/`. Under **Nodes**, set built-in node executors to **0**; disable inbound agents under **Security**.

**Verify:** Both plugins are listed, the Jenkins URL matches, and no build executors or inbound agents are active.

## Step 3 — Configure SAML in Microsoft Entra
1. Sign in to [Microsoft Entra admin center](https://entra.microsoft.com) as the authorized application administrator.
2. Open **Entra ID → Enterprise applications → New application → Create your own application**.
3. Name it `Jenkins SAML Lab`, select **Integrate any other application you don't find in the gallery**, and create it.
4. Open **Single sign-on → SAML → Basic SAML Configuration → Edit**.
5. Enter these safe example values, replacing `YOUR-VERIFIED-DOMAIN` with a domain verified in your tenant:

   | Setting | Value |
   |---|---|
   | Identifier (Entity ID) | `https://YOUR-VERIFIED-DOMAIN/jenkins-saml-lab` |
   | Reply URL (ACS) | `https://localhost:8443/securityRealm/finishLogin` |
   | Sign-on URL | `https://localhost:8443/` |

6. Under **Attributes & Claims**, map the intended username claim to the test user's UPN. Confirm the signing certificate is active, and copy the application's federation metadata URL.
7. Under **Users and groups → Add user/group**, assign your standard test user and a separate application administrator.

**Verify:** Reopen Basic SAML Configuration and compare the exact Identifier and ACS strings. Both users appear assigned. If configuration is unavailable, verify tenant permissions, application type, and licensing.

## Step 4 — Configure SAML and permissions in Jenkins
1. Open **Manage Jenkins → Security**.
2. Under **Security Realm**, select **SAML 2.0** and enter the Entra federation metadata URL.
3. Configure the username claim and service-provider Entity ID to match the Entra application. Require signed assertions. Use the documented options in the [extended reference](REFERENCE.md#11-configure-jenkins-saml-realm).
4. On the **same Security page**, set **Authorization → Matrix-based security** *before saving the SAML realm*.
5. Add the normal user and grant only **Overall → Read**. Add a separate designated Jenkins administrator with required administrative permissions. Avoid broad anonymous permissions.
6. Review both accounts and click **Save**.

![Actual Jenkins SAML metadata configuration, with tenant details masked](screenshots/12-saml-provider-settings.png)

*Jenkins Security: real SAML metadata configuration captured during the build; private tenant details are masked.*

![Actual Jenkins signing requirement option](screenshots/14-signed-assertion-required.png)

*Jenkins Security: require the signed SAML assertion. This screenshot shows the resulting configuration, not proof of manual clicks.*

**Verify:** The SAML realm and authorization matrix are saved. If you become locked out, use the documented recovery procedure, not broad anonymous administrator permissions.

## Step 5 — Test sign-in and least privilege
1. In a private browser window on the **same host**, open `https://localhost:8443/`.
2. Choose sign-in, follow the Microsoft Entra prompt, and authenticate as the assigned **standard** user.
3. Confirm Jenkins opens and the user can read the application.
4. Attempt to open **Manage Jenkins** or another admin-only endpoint; verify the standard user receives **HTTP 403**.
5. Restart the attended Jenkins process and repeat SAML login.

**Verify:** Standard-user sign-in succeeds, admin access is denied, and a new login succeeds after restart. Record screenshots of the real browser result, with sensitive identifiers removed.

## If something fails
- **ACS / audience mismatch:** Recheck the Entity ID and `/securityRealm/finishLogin` character for character.
- **Login redirects endlessly:** Confirm HTTPS, local browser hostname, signing certificate, time, claims, and Jenkins URL.
- **Assigned user denied:** Confirm assignment, UPN mapping, lowercase normalization, and matching Jenkins authorization entry.
- **Standard user can administer:** Stop and review the Matrix Authorization Strategy immediately.
- **Jenkins unavailable:** Diagnose the Java process, certificate trust, and loopback listener before blaming SAML.

## Detailed reference and evidence
This is the quick, manual-first path. The [extended technical guide](REFERENCE.md) contains full configuration notes, command exceptions, test boundaries, and detailed troubleshooting. See [project overview](README.md) and its linked original screenshots and evidence.

**Documentation status:** The implementation and SAML login were verified. The equivalent complete point-and-click reproduction path was not independently replayed end to end. Screenshots are authentic historical evidence of the actual resulting state.
