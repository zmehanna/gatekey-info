param(
  [Parameter(Mandatory=$true)][string]$DemoApkPath,
  [Parameter(Mandatory=$true)][string]$Version,
  [Parameter(Mandatory=$true)][string]$MetadataPath
)
$ErrorActionPreference = "Stop"
if ($Version -notmatch '^\d+\.\d+\.\d+([-.][A-Za-z0-9.-]+)?$') { throw "Version invalide" }
if ([string]::IsNullOrWhiteSpace($env:APPETIZE_API_TOKEN)) {
  throw "APPETIZE_API_TOKEN manquant (ne jamais le publier dans le site web)"
}
if (!(Test-Path -LiteralPath $DemoApkPath -PathType Leaf)) { throw "APK de demonstration introuvable" }
$apk = (Resolve-Path -LiteralPath $DemoApkPath).Path
if ([IO.Path]::GetFileName($apk) -notmatch '(?i)(preview|demo).*\.apk$') {
  throw "Refus: seul un APK preview/demo peut etre publie dans l'emulateur"
}
if ((Get-Item -LiteralPath $apk).Length -lt 1000000) { throw "APK de demonstration suspect" }

# Verify the COMPILED binary AndroidManifest using Python standard-library only.
# A separate appId and absence of the INTERNET permission are mandatory.
& python (Join-Path $PSScriptRoot "verify_preview_apk.py") $apk $Version
if ($LASTEXITCODE -ne 0) { throw "Verification du manifeste hors ligne echouee : aucun upload Appetize" }
$previous = $null
if (Test-Path -LiteralPath $MetadataPath) {
  $previous = Get-Content -LiteralPath $MetadataPath -Raw | ConvertFrom-Json
}
$key = $env:APPETIZE_PUBLIC_KEY
if (!$key -and $previous -and $previous.publicKey) { $key = [string]$previous.publicKey }
if ($key -and $key -notmatch '^[A-Za-z0-9_-]{8,128}$') { throw "Identifiant Appetize invalide" }
$endpoint = "https://api.appetize.io/v1/apps/"
if ($key) { $endpoint += $key }

$boundary = "----PGK" + [Guid]::NewGuid().ToString("N")
$crlf = [Environment]::NewLine
$stream = New-Object System.IO.MemoryStream
try {
  function WritePartText([string]$value) {
    $bytes = [Text.Encoding]::UTF8.GetBytes($value)
    $stream.Write($bytes, 0, $bytes.Length)
  }
  WritePartText ("--" + $boundary + $crlf + 'Content-Disposition: form-data; name="platform"' + $crlf + $crlf + "android" + $crlf)
  WritePartText ("--" + $boundary + $crlf + 'Content-Disposition: form-data; name="fileType"' + $crlf + $crlf + "apk" + $crlf)
  WritePartText ("--" + $boundary + $crlf + 'Content-Disposition: form-data; name="note"' + $crlf + $crlf + "PrivateGateKey offline demo $Version" + $crlf)
  WritePartText ("--" + $boundary + $crlf + 'Content-Disposition: form-data; name="file"; filename="PrivateGateKey-Preview.apk"' + $crlf + "Content-Type: application/vnd.android.package-archive" + $crlf + $crlf)
  $apkBytes = [IO.File]::ReadAllBytes($apk)
  $stream.Write($apkBytes, 0, $apkBytes.Length)
  WritePartText ($crlf + "--" + $boundary + "--" + $crlf)
  $auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($env:APPETIZE_API_TOKEN + ":"))
  $response = Invoke-RestMethod -Uri $endpoint -Method Post -Headers @{Authorization = "Basic $auth"} -ContentType "multipart/form-data; boundary=$boundary" -Body $stream.ToArray() -TimeoutSec 240
} finally {
  $stream.Dispose()
}
if (!$response.publicKey -or [string]$response.publicKey -notmatch '^[A-Za-z0-9_-]{8,128}$') {
  throw "Appetize n'a pas retourne d'identifiant valide. Metadonnees non modifiees."
}
$metadata = [ordered]@{
  provider = "appetize"
  mode = "offline-demo"
  status = "ready"
  publicKey = [string]$response.publicKey
  version = $Version
  updatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}
[IO.File]::WriteAllText($MetadataPath, (($metadata | ConvertTo-Json) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
Write-Output "Appetize: demonstration hors ligne $Version publiee"
