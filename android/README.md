# Android cloud preview / iPhone Safari

The site displays **Tester Android depuis Safari** only when an Appetize.io
offline demo is ready and matches the exact version in android/latest.json.
The control is disabled (rather than redirecting to an unverified live app)
until an offline preview is published.

## One-time setup

1. Create an Appetize.io account and get an API token. Configure the token
   server-side as APPETIZE_API_TOKEN. Never put it in the HTML or JSON.
2. Build BOTH APKs at the same commit/version from the Android repository:
   gradle :app:assembleDebug :app:assemblePreview
3. Publish the APKs together using the site repository's existing publisher:
   ./scripts/publish_android.ps1 -ApkPath <path-to-app-debug.apk> -Version 1.0.6 -DemoApkPath <path-to-app-preview.apk>

The script detects an adjacent preview/app-preview.apk automatically if
-DemoApkPath was omitted. Before uploading, it verifies the different
package name (com.klmehanna.privategatekey.demo), matching versionName
and absence of INTERNET permission via Android SDK aapt.exe.

If APPETIZE_PUBLIC_KEY is configured, the upload updates that Appetize app.
Otherwise the first upload creates one. Its publicKey is retained in
android/emulator.json for subsequent version updates. The app remains
unavailable if the latest public APK and emulator demo versions differ.

Without the API token, publishing the regular APK remains possible and the
emulator stays disabled. Appetize usage is subject to the provider's plan.

## Safety

The preview APK is isolated: it starts in offline demo, has no INTERNET
permission and a network call guard. Physical gate operations, biometric
enrollment and invitations are never tested in a hosted emulator.
