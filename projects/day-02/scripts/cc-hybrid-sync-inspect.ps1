# SANITIZED SOURCE ADAPTATION: actual identifiers replaced with examples.
# This public variant was not executed; original helper was run in this conversation.
$ErrorActionPreference='Stop'
if($env:COMPUTERNAME -ne 'EXAMPLE-DC'){throw 'Wrong guest'}
$module='C:\Program Files\Microsoft Azure AD Sync\Bin\ADSync\ADSync.psd1'
if(Test-Path $module){Import-Module $module}else{Import-Module ADSync}
$connectors=@(Get-ADSyncConnector)
if($connectors.Count -lt 2){@{state='configuration-in-progress';connector_count=$connectors.Count;timestamp_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json;exit 0}
$scheduler=Get-ADSyncScheduler
$summary=@()
foreach($connector in $connectors){
 $summary+=@{name=$connector.Name;type=[string]$connector.ConnectorTypeName;included_containers=@($connector.Partitions | Where-Object Selected | ForEach-Object {$_.ConnectorPartitionScope.ContainerInclusionList});excluded_containers=@($connector.Partitions | Where-Object Selected | ForEach-Object {$_.ConnectorPartitionScope.ContainerExclusionList});pending_exports=(Get-ADSyncConnectorStatistics -ConnectorName $connector.Name | Select-Object ExportAdds,ExportUpdates,ExportDeletes)}
}
$credential=Get-ADSyncEntraConnectorCredential
@{scheduler=($scheduler | Select-Object StagingModeEnabled,SyncCycleEnabled,SyncCycleInProgress,SchedulerSuspended,NextSyncCyclePolicyType,NextSyncCycleStartTimeInUTC);connectors=$summary;running_connectors=@(Get-ADSyncConnectorRunStatus | Select-Object ConnectorName,RunState);connector_identity_type=[string]$credential.ConnectorIdentityType;service_certificate_present=[bool]$credential.CertificateCredential;services=@(Get-CimInstance Win32_Service -Filter "Name='ADSync'" | Select-Object Name,State,StartMode);timestamp_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Depth 6
