# SANITIZED SOURCE EXAMPLE. Adapted from the script executed in this conversation.
# Example identities/endpoints replaced the actual values; this variant was not executed.
# Logon-role example accepts the approved lab password on stdin only; never place it in argv or files.
$ErrorActionPreference='Stop'
try {
 $stage='membership';$s=Get-CimInstance Win32_ComputerSystem;if($s.Domain -ne 'training.example.test' -or !$s.PartOfDomain){throw 'Wrong client'}
 Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class CcLogon {
 [DllImport("advapi32.dll",SetLastError=true,CharSet=CharSet.Unicode)]
 public static extern bool LogonUser(string u,string d,string p,int t,int provider,out IntPtr token);
 [DllImport("advapi32.dll",SetLastError=true)] public static extern bool GetTokenInformation(IntPtr token,int info,IntPtr data,int size,out int needed);
 [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr h);
}
'@
 $plain=[Console]::In.ReadLine();if(!$plain){throw 'Runtime password missing'}
 $results=@()
 foreach($u in 'example-admin-a','example-admin-b','example-standard-a'){
  $stage="logon-$u";$token=[IntPtr]::Zero
  if(![CcLogon]::LogonUser($u,'TRAINING',$plain,2,0,[ref]$token)){throw ('Interactive credential validation failed; Win32='+[Runtime.InteropServices.Marshal]::GetLastWin32Error())}
  $identity=[Security.Principal.WindowsIdentity]::new($token)
  $principal=[Security.Principal.WindowsPrincipal]::new($identity)
  $stage="role-$u";$groupSids=@($identity.Groups | ForEach-Object {$_.Value});$admin=$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  $buffer=[Runtime.InteropServices.Marshal]::AllocHGlobal([IntPtr]::Size);$needed=0;$linked=[IntPtr]::Zero
  try{
   if([CcLogon]::GetTokenInformation($token,19,$buffer,[IntPtr]::Size,[ref]$needed)){
    $linked=[Runtime.InteropServices.Marshal]::ReadIntPtr($buffer)
    $fullIdentity=[Security.Principal.WindowsIdentity]::new($linked)
    $fullPrincipal=[Security.Principal.WindowsPrincipal]::new($fullIdentity)
    $admin=$fullPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    $fullIdentity.Dispose()
   }
  }finally{if($linked -ne [IntPtr]::Zero){[CcLogon]::CloseHandle($linked)|Out-Null};[Runtime.InteropServices.Marshal]::FreeHGlobal($buffer)}
  if(($u -like 'example-admin-*' -and !$admin) -or ($u -eq 'example-standard-a' -and $admin)){throw 'Unexpected effective administrator role'}
  $results+=@{User=$identity.Name;InteractiveLogonValidated=$true;AdministratorMembership=$admin;UACElevationRequired=$true}
  $identity.Dispose();[CcLogon]::CloseHandle($token)|Out-Null
 }
 $plain=$null
 Remove-Item C:\ProgramData\example-auth-failure.json -ErrorAction SilentlyContinue
 $path='C:\ProgramData\ExampleLab';New-Item -ItemType Directory -Path $path -Force | Out-Null
 @{Passed=$true;Tests=$results;PasswordExported=$false}|ConvertTo-Json -Depth 5 | Set-Content "$path\domain-auth-validation.json"
 @{Passed=$true;Tests=3}|ConvertTo-Json -Compress
}catch{@{Stage=$stage;Message=$_.Exception.Message;ErrorId=$_.FullyQualifiedErrorId;GroupSids=$groupSids}|ConvertTo-Json -Compress | Set-Content C:\ProgramData\example-auth-failure.json;Write-Error 'Cyber and Chill credential or role verification failed; credentials omitted';exit 1}
