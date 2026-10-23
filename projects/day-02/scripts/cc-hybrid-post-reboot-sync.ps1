# SANITIZED SOURCE ADAPTATION: actual identifiers replaced with examples.
# This public variant was not executed; original helper was run in this conversation.
$ErrorActionPreference='Stop'
if($env:COMPUTERNAME -ne 'EXAMPLE-DC'){throw 'Wrong guest'}
$cs=Get-CimInstance Win32_ComputerSystem
$service=Get-CimInstance Win32_Service -Filter "Name='ADSync'"
if(!$service -or $service.StartMode -ne 'Auto' -or $service.State -ne 'Running'){throw 'Sync service has not automatically returned to Running yet'}
Import-Module 'C:\Program Files\Microsoft Azure AD Sync\Bin\ADSync\ADSync.psd1'
$scheduler=Get-ADSyncScheduler
if($scheduler.StagingModeEnabled -or !$scheduler.SyncCycleEnabled -or $scheduler.SchedulerSuspended){throw 'Expected active automatic sync scheduler'}
$identity=Get-ADSyncEntraConnectorCredential
if([string]$identity.ConnectorIdentityType -ne 'Application' -or !$identity.CertificateCredential){throw 'Expected persistent application-certificate connector identity'}
if(!(Get-ADSyncConnectorRunStatus)){$request=Start-ADSyncSyncCycle -PolicyType Delta}else{$request=@{Result='AlreadyRunning'}}
@{dc_boot_utc=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString('o');verified_at_utc=[DateTime]::UtcNow.ToString('o');service_automatic=$true;service_running=$true;dc_interactive_user_absent=(!$cs.UserName);connector_identity_type=[string]$identity.ConnectorIdentityType;service_certificate_present=[bool]$identity.CertificateCredential;staging_mode=$false;sync_cycle_enabled=$true;post_reboot_sync_request=[string]$request.Result;personal_cloud_password_required=$false;host_reboot_performed=$false} | ConvertTo-Json
