param(
  [Parameter(Mandatory=$true)][string]$ApkPath,
  [Parameter(Mandatory=$true)][string]$Version,
  [string]$DemoApkPath = "",
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
  # When available, update the browser emulator with the separate, offline-only APK.
  # This is never the production APK and failure must not block normal downloads.
  if ([string]::IsNullOrWhiteSpace($DemoApkPath)) {
    $sameFolder = Join-Path (Split-Path -Parent $apk) "app-preview.apk"
    $apkVariants = Split-Path -Parent (Split-Path -Parent $apk)
    $siblingPreview = Join-Path $apkVariants "preview\app-preview.apk"
    if (Test-Path -LiteralPath $sameFolder -PathType Leaf) { $DemoApkPath = $sameFolder }
    elseif (Test-Path -LiteralPath $siblingPreview -PathType Leaf) { $DemoApkPath = $siblingPreview }
  }
  if (![string]::IsNullOrWhiteSpace($DemoApkPath)) {
    if ($env:APPETIZE_API_TOKEN) {
      try {
        & (Join-Path $root "scripts\publish_emulator.ps1") -DemoApkPath $DemoApkPath -Version $Version -MetadataPath (Join-Path $root "android\emulator.json")
        Write-Output "Demonstration Android Appetize synchronisee."
      } catch {
        Write-Warning "Emulateur non actualise : $($_.Exception.Message). La version classique reste publiee."
      }
    } else {
      Write-Warning "APPETIZE_API_TOKEN absent : la demonstration cloud est indisponible."
    }
  }
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
  git add android/latest.json android/emulator.json
  git commit -m "Android: publish $Version as latest APK"
  if ($LASTEXITCODE -ne 0) { throw "Commit métadonnées échoué" }
  git push origin main
  if ($LASTEXITCODE -ne 0) { throw "Push métadonnées échoué" }
  Write-Output "Publié: PrivateGateKey Android $Version"
} finally { Pop-Location }
