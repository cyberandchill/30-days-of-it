# SANITIZED SOURCE ADAPTATION: actual identifiers replaced with examples.
# This public variant was not executed; original helper was run in this conversation.
$ErrorActionPreference='Stop'
Import-Module ActiveDirectory
if((Get-ADDomain).DNSRoot -ne 'example.com'){throw 'Wrong domain'}
New-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\DNS\Parameters' -Name PublishAddresses -PropertyType String -Value '192.0.2.10' -Force | Out-Null
& dnscmd.exe localhost /ResetListenAddresses 192.0.2.10 | Out-Null
if($LASTEXITCODE -ne 0){throw 'Cannot restrict DNS listening address'}
Restart-Service DNS
New-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\Netlogon\Parameters' -Name RegisterDnsARecords -PropertyType DWord -Value 0 -Force | Out-Null
Restart-Service Netlogon
foreach($zone in @('example.com','_msdcs.example.com')){
 foreach($record in @(Get-DnsServerResourceRecord -ZoneName $zone -RRType A -ErrorAction SilentlyContinue)){
  if($record.RecordData.IPv4Address.ToString() -eq '198.51.100.15'){Remove-DnsServerResourceRecord -ZoneName $zone -InputObject $record -Force}
 }
}
foreach($entry in @(@{zone='example.com';name='@'},@{zone='_msdcs.example.com';name='gc'})){
 if(!(Get-DnsServerResourceRecord -ZoneName $entry.zone -Name $entry.name -RRType A -ErrorAction SilentlyContinue | Where-Object {$_.RecordData.IPv4Address.ToString() -eq '192.0.2.10'})){
  Add-DnsServerResourceRecordA -ZoneName $entry.zone -Name $entry.name -IPv4Address '192.0.2.10' | Out-Null
 }
}
Clear-DnsServerCache -Force
Clear-DnsClientCache
@{dc_addresses=@(Get-DnsServerResourceRecord -ZoneName 'example.com' -Name EXAMPLE-DC -RRType A | ForEach-Object {$_.RecordData.IPv4Address.ToString()});listen_addresses=@((Get-DnsServerSetting -All).ListeningIPAddress | ForEach-Object {$_.ToString()});nat_dns_registration=$false;private_domain_and_gc_a_records_maintained=$true} | ConvertTo-Json -Depth 4
