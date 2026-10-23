# SANITIZED SOURCE EXAMPLE. Adapted from the script executed in this conversation.
# Example identities/endpoints replaced the actual values; this variant was not executed.
# Logon-role example accepts the approved lab password on stdin only; never place it in argv or files.
$ErrorActionPreference='Stop'
$s=Get-CimInstance Win32_ComputerSystem
if(!$s.PartOfDomain -or $s.Domain -ne 'training.example.test' -or $s.Name -ne 'EXAMPLE-CLIENT'){throw 'Wrong client membership or name'}
$secure=Test-ComputerSecureChannel;if(!$secure){throw 'Secure channel failed'}
$srv=@(Resolve-DnsName '_ldap._tcp.dc._msdcs.training.example.test' -Type SRV -Server 192.0.2.10 | Where-Object Type -eq SRV)
$dc=@(Resolve-DnsName EXAMPLE-DC.training.example.test -Type A -Server 192.0.2.10 | Where-Object Type -eq A)
if(!($dc | Where-Object IPAddress -eq '192.0.2.10') -or !$srv){throw 'DNS failure'}
$shares=Test-Path '\\EXAMPLE-DC.training.example.test\SYSVOL';if(!$shares){throw 'SYSVOL unavailable'}
$fw=@(Get-NetFirewallProfile | Select-Object Name,Enabled);if($fw | Where-Object {!$_.Enabled}){throw 'Firewall disabled'}
$defender=Get-Service WinDefend;if($defender.Status -ne 'Running'){throw 'Defender not running'}
$auth=Get-Content C:\ProgramData\ExampleLab\domain-auth-validation.json -Raw | ConvertFrom-Json
if(!$auth.Passed){throw 'Authentication tests missing'}
@{Passed=$true;VerifiedAtUTC=[DateTime]::UtcNow.ToString('o');Authentication=$auth;System=($s | Select-Object Name,Domain,PartOfDomain,UserName);OS=(Get-CimInstance Win32_OperatingSystem).Caption;SecureChannel=$secure;DNS=$dc;SYSVOL=$shares;Firewall=$fw;Defender='Running';IPv4=@(Get-NetIPAddress -AddressFamily IPv4 | Select-Object IPAddress,InterfaceIndex);Setup=(Get-ItemProperty 'HKLM:\SYSTEM\Setup' | Select-Object OOBEInProgress,SystemSetupInProgress)}|ConvertTo-Json -Depth 6
