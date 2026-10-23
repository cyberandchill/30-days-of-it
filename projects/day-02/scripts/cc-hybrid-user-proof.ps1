# SANITIZED SOURCE ADAPTATION: actual identifiers replaced with examples.
# This public variant was not executed; original helper was run in this conversation.
$ErrorActionPreference='Stop'
$cs=Get-CimInstance Win32_ComputerSystem
if($cs.Name -ne 'EXAMPLE-CLIENT' -or $cs.Domain -ne 'example.com' -or $cs.UserName -ne 'EXAMPLE\standard-user'){throw 'Require actual standard-user interactive desktop sign-in'}
$base='C:\ProgramData\ExampleLab\Hybrid'
$results=Join-Path $base 'results';New-Item $results -ItemType Directory -Force | Out-Null
$acl=Get-Acl $results;$acl.SetAccessRuleProtection($true,$false)
foreach($sid in 'S-1-5-18','S-1-5-32-544'){$identity=[Security.Principal.SecurityIdentifier]::new($sid);$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($identity,'FullControl','ContainerInherit,ObjectInherit','None','Allow'))}
$user=[Security.Principal.NTAccount]::new('EXAMPLE','standard-user').Translate([Security.Principal.SecurityIdentifier])
$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($user,'Modify','ContainerInherit,ObjectInherit','None','Allow'));Set-Acl $results $acl
$script=@'
$ErrorActionPreference='Stop'
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if($identity.IsSystem -or $identity.Name -ne 'EXAMPLE\standard-user'){throw 'Wrong interactive user context'}
$raw=(& dsregcmd.exe /status | Out-String)
$safe=@{}
foreach($key in @('AzureAdJoined','DomainJoined','DeviceAuthStatus','AzureAdPrt','WamDefaultSet','NgcSet','OnPremTgt','CloudTgt')){
 if($raw -match ('(?m)^\s*'+$key+'\s*:\s*(\S+)\s*$')){$safe[$key]=$Matches[1]}
}
$tenantMatches=$raw -match '(?m)^\s*TenantId\s*:\s*<PRIVATE-ID-OMITTED>\s*$'
$raw=$null
$principal=[Security.Principal.WindowsPrincipal]::new($identity)
@{execution_context='interactive-standard-domain-user';account='standard-user@example.com';system_context=$false;elevated_administrator_token=$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator);expected_tenant_matches=$tenantMatches;device_and_sso_state=$safe;secret_material_exported=$false;client_boot_utc=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString('o');timestamp_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Depth 4 | Set-Content 'C:\ProgramData\ExampleLab\Hybrid\results\user-state.json'
'@
Set-Content (Join-Path $base 'UserProof.ps1') $script -Encoding UTF8
$action=New-ScheduledTaskAction -Execute powershell.exe -Argument '-NoProfile -ExecutionPolicy Bypass -File C:\ProgramData\ExampleLab\Hybrid\UserProof.ps1'
$principal=New-ScheduledTaskPrincipal -UserId 'EXAMPLE\standard-user' -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName 'ExampleLab-Hybrid-UserProof' -Action $action -Principal $principal -Force | Out-Null
Start-ScheduledTask -TaskName 'ExampleLab-Hybrid-UserProof'
for($i=0;$i -lt 20;$i++){Start-Sleep -Seconds 1;if((Get-ScheduledTask -TaskName 'ExampleLab-Hybrid-UserProof').State -ne 'Running'){break}}
if(!(Test-Path (Join-Path $results 'user-state.json'))){throw 'User proof did not complete'}
Get-Content (Join-Path $results 'user-state.json') -Raw
Unregister-ScheduledTask -TaskName 'ExampleLab-Hybrid-UserProof' -Confirm:$false
