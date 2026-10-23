# Day 01 — Build Active Directory through the GUI

**Goal:** Create a Windows Server domain controller, organize users and groups, and domain-join Windows 11 Pro. These are manual instructions adapted from the completed automated lab; the example configuration has not been independently replayed.

## Prerequisites
Two connected VMs (Windows Server 2022 and Windows 11 Pro), local admin access, a private network, and a static private IP for the domain controller. Use a domain name you control (example: `ad.lab.example.com`); substitute your own values. Complete Windows first-run setup before joining the client.

## Step 1 — Install AD DS and DNS
1. Sign in to the Windows Server VM and open **Server Manager**.
2. Select **Manage → Add Roles and Features → Role-based or feature-based installation**.
3. Choose the local server, select **Active Directory Domain Services** and **DNS Server**, and accept their required features.
4. Click **Next → Install**.

**Verify:** Server Manager offers **Promote this server to a domain controller**.

## Step 2 — Create the domain
1. Click the Server Manager notification flag → **Promote this server to a domain controller**.
2. Select **Add a new forest** and enter your lab domain.
3. Select the DNS option and set a unique Directory Services Restore Mode password.
4. Continue through the wizard, review prerequisite checks, click **Install**, and restart.
5. Open **Server Manager → Tools → Active Directory Users and Computers**.

**Verify:** Your new domain appears in the directory tree.

## Step 3 — Create OUs, users, and groups
1. In **Active Directory Users and Computers**, right-click the domain → **New → Organizational Unit**. Create a training root.
2. Under that root, create **Users**, **Admins**, **Groups**, **Workstations**, and **Servers** OUs.
3. Create department OUs beneath **Users**.
4. Right-click a department OU → **New → User**. Enter identity fields and a unique lab password.
5. Right-click **Groups → New → Group**; choose **Global** and **Security**.
6. Open a new group → **Members → Add** and select the appropriate users.

![Actual directory structure, identifying values masked](screenshots/02-directory-organization.png)

![Actual department group membership, identifying values masked](screenshots/05-department-group-members.png)

**Verify:** The OU tree, 12 standard users, two separate lab admin users and five groups are organized as expected in the original build. Use least privilege; the original isolated lab's shared/non-expiring password choices are not recommended for production.

## Step 4 — Join Windows 11 to the domain
1. Start Windows 11 Pro and complete initial setup.
2. Open **Control Panel → Network and Sharing Center → Change adapter settings** (or run `ncpa.cpl`).
3. Right-click the lab adapter → **Properties → Internet Protocol Version 4 → Properties**.
4. Set **Preferred DNS server** to your domain controller's private IP address.
5. Press **Win+R**, enter `sysdm.cpl`, and choose **Computer Name → Change**.
6. Select **Domain**, enter your lab domain, provide an authorized domain account, and restart.
7. On the server, locate the computer in **Active Directory Users and Computers** and move it into **Workstations** if necessary.

![Actual joined Windows client, identifying values masked](screenshots/06-windows-domain-membership.png)

**Verify:** System Properties displays the domain, and a standard domain user can sign in without administrative privilege.

## Step 5 — Check the result
1. On the server open **Server Manager → Tools → DNS** and confirm the AD DNS zone exists.
2. On the client open **Command Prompt** and run `whoami`, then `echo %LOGONSERVER%`.
3. Confirm that your account belongs to the domain and that the logon server is the intended controller.
4. If the join fails, check client DNS, VM connectivity, clock synchronization and the domain name.

![Actual signed-in desktop, private output masked](screenshots/07-domain-desktop-session.png)

**Next:** [Day 02: Hybrid identity](../day-02/GUIDE.md). Full original automation, deviations and measured evidence remain in [the build record](evidence/BUILD-STORY.md).
