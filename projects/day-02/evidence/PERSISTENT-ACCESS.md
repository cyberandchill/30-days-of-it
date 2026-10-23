# Protected Entra automation access

Original workspace workflow; run playbooks from its ansible directory. The complete private workspace is not shipped in this public project.

This workflow lets maintained Ansible automation reuse a delegated Microsoft
Entra sign-in for cloud-admin@example.com. It stores the MSAL token cache in the
existing desktop user's encrypted GNOME keyring. Tokens are never saved in
workspace files, reports, command arguments, or screenshots. The Debian desktop
user must sign in and unlock that keyring after a reboot. This is not unattended
access before desktop sign-in. MFA, consent changes, revocation and Microsoft
session policies can require interactive authentication again.

The browser portal and automation authenticate separately. Signing into the
portal alone does not authorize Graph automation. This first setup requests
User.Read and Directory.Read.All to inspect identity and hybrid prerequisites.
Directory writes require additional task-specific permissions and appropriate
Entra roles. The directory synchronization agent will have its own supported
service identity after it is configured.

Manual setup from the existing Debian desktop

1. Keep the normal desktop session signed in, with the GNOME keyring unlocked.
   Do not disable MFA or change host authentication to make this work.
2. As root, in WORKSPACE, install the maintained dependency:
   ansible-playbook playbooks/cyber-chill-entra-auth-dependencies.yml
3. Launch the authentication helper:
   ansible-playbook playbooks/cyber-chill-entra-auth.yml
4. A private dialog displays a provider-issued code. In the Microsoft browser
   page at https://microsoft.com/devicelogin, enter that code. Sign in as
   cloud-admin@example.com, complete MFA, and review the Microsoft Graph Command
   Line Tools consent. Never copy the code, password, MFA or tokens into chat.
   Screenshots intentionally exclude this private dialog and authentication.
5. Read only sanitized completion metadata:
   ansible-playbook playbooks/cyber-chill-entra-auth-status.yml
   Successful setup reports state authenticated, graph_me_verified true,
   storage existing-encrypted-GNOME-keyring and keyring_readback_verified true.
6. Test a separate process with a forced silent token refresh:
   ansible-playbook playbooks/cyber-chill-entra-auth.yml -e entra_auth_operation=verify
   Then repeat the status command. Look for fresh_process_refresh_verified true.
   The verify operation never opens an interactive prompt. If it cannot refresh,
   it reports reauthentication-required, or a sanitized blocked state.
7. After an independently authorized reboot, sign into the same Debian desktop
   and unlock its existing keyring. Repeat step 6. A host reboot is not performed
   by any of these playbooks. A separate-process test is not a reboot test.

Recovery

If the desktop keyring is locked or unavailable, unlock it through the normal
desktop. The helper refuses plaintext fallback and does not unlock or alter host
authentication. If Microsoft requires sign-in, repeat the login playbook. A
device code expires after its provider-defined lifetime; inspect status before
starting another authentication operation. A process lock prevents concurrent
cache mutation. The identity is verified using Microsoft Graph /me before the
cache is saved. Signing into another account does not persist its cache.

Evidence and screenshots

Sanitized status is copied to reports/cyber-chill-entra-auth-status.json. Runtime
metadata is under /run/user/1000/cyber-chill-auth and is not the persistent token
store. The cache is a Secret Service entry labeled Cyber and Chill Entra
delegated automation. Do not export or screenshot its contents.

Capture instructional commands and sanitized success results for the eventual
hybrid setup guide. Do not capture the desktop while the private code dialog is
visible. Authentication secrets are intentionally excluded from screenshots.

References

Microsoft MSAL token cache persistence:
https://learn.microsoft.com/en-us/entra/msal/python/advanced/msal-python-token-cache-serialization
Microsoft Graph delegated and application authentication:
https://learn.microsoft.com/en-us/powershell/microsoftgraph/authentication-commands

Implementation journal

The normal portal launcher initially failed because the desktop user cannot
traverse /root. The maintained playbook was corrected to pass its credential-free
script through an Ansible lookup; host directory permissions were preserved.
python3-msal 1.32.3-1 was installed from the existing Debian trixie repository.
The dedicated authentication helper launched and received a 900-second device
challenge. Interactive sign-in completed at 2026-10-23 02:19:22 UTC. The expected
Graph account and encrypted keyring readback were verified. At 02:20:29 UTC a
separate process loaded the saved cache and forced a silent refresh successfully,
then verified the expected account through Graph again. No reboot was performed.
