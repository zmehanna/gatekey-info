param(
  [Parameter(Mandatory=$true)][string]$ApkPath,
  [Parameter(Mandatory=$true)][string]$Version,
  [string]$Repository = "zmehanna/gatekey-info"
)
$ErrorActionPreference = "Stop"
if (!(Test-Path -LiteralPath $ApkPath -PathType Leaf)) { throw "APK introuvable: $ApkPath" }
if ($Version -notmatch '^\d+\.\d+\.\d+([-.][A-Za-z0-9.-]+)?$') { throw "Version invalide" }
$apk = (Resolve-Path -LiteralPath $ApkPath).Path
if ((Get-Item -LiteralPath $apk).Length -lt 1000000) { throw "APK trop petit : build suspect" }
& gh auth status 1>$null 2>$null
if ($LASTEXITCODE -ne 0) { throw "Authentification GitHub requise" }
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $root
try {
  if (git status --porcelain) { throw "Dépôt non propre : validez ou rangez les modifications d'abord" }
  git pull --ff-only origin main
  if ($LASTEXITCODE -ne 0) { throw "git pull a échoué" }
  $release = & gh release view android-latest --repo $Repository --json tagName 2>$null
  if ($LASTEXITCODE -ne 0) {
    & gh release create android-latest --repo $Repository --title "PrivateGateKey Android - latest" --notes "Dernière version Android uniquement." --latest=false
    if ($LASTEXITCODE -ne 0) { throw "Création release échouée" }
  }
  $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("PrivateGateKey-" + [guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Path $tmp | Out-Null
  try {
    $target = Join-Path $tmp "PrivateGateKey-Android.apk"
    Copy-Item -LiteralPath $apk -Destination $target
    & gh release upload android-latest $target --repo $Repository --clobber
    if ($LASTEXITCODE -ne 0) { throw "Envoi de l'APK échoué" }
  } finally { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
  $digest = (Get-FileHash -LiteralPath $apk -Algorithm SHA256).Hash.ToLowerInvariant()
  $metadata = [ordered]@{
    version = $Version
    filename = "PrivateGateKey-Android.apk"
    url = "https://github.com/$Repository/releases/download/android-latest/PrivateGateKey-Android.apk"
    sha256 = $digest
    publishedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  }
  $json = $metadata | ConvertTo-Json
  [System.IO.File]::WriteAllText((Join-Path $root "android\latest.json"), $json + "`n", [System.Text.UTF8Encoding]::new($false))
  git add android/latest.json
  git commit -m "Android: publish $Version as latest APK"
  if ($LASTEXITCODE -ne 0) { throw "Commit métadonnées échoué" }
  git push origin main
  if ($LASTEXITCODE -ne 0) { throw "Push métadonnées échoué" }
  Write-Output "Publié: PrivateGateKey Android $Version"
} finally { Pop-Location }
