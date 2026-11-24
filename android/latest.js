(async function () {
  const badge = document.getElementById("android-latest-version");
  const button = document.querySelector("a.download");
  const artVersion = document.getElementById("android-card-version");
  const releaseMeta = document.getElementById("android-release-meta");
  const previewButton = document.querySelector("#try-android");
  const previewStatus = document.querySelector("#emulator-status");
  let latestVersion = null;

  try {
    // Bust both browser and CDN caches; the published manifest is the
    // authoritative source of the visible version and release timestamp.
    const response = await fetch("/android/latest.json?_v=" + Date.now(),
      { cache: "no-store", credentials: "same-origin" });
    if (!response.ok) throw new Error("Metadata unavailable");
    const latest = await response.json();
    if (!/^\d+\.\d+\.\d+([-.][a-z0-9.-]+)?$/i.test(latest.version)) throw new Error("Invalid version");
    if (typeof latest.url !== "string" ||
        !latest.url.startsWith("https://github.com/zmehanna/gatekey-info/releases/download/android-latest/")) {
      throw new Error("Invalid download");
    }
    latestVersion = latest.version;
    if (badge) badge.textContent = "Android " + latestVersion + " bêta";
    if (artVersion) artVersion.textContent = "Version " + latestVersion;
    if (releaseMeta && typeof latest.publishedAt === "string") {
      const published = new Date(latest.publishedAt);
      if (!Number.isNaN(published.getTime())) {
        const date = new Intl.DateTimeFormat("fr-FR", {
          day: "numeric", month: "long", year: "numeric", timeZone: "Europe/Paris"
        }).format(published);
        releaseMeta.textContent =
          "Dernière publication : " + date + " · Version vérifiée automatiquement.";
      }
    }
    if (button) {
      button.href = latest.url;
      button.setAttribute("download", latest.filename || "PrivateGateKey-Android.apk");
    }
  } catch (error) {
    console.warn("Latest Android metadata not available", error);
  }

  // The online emulator is an independently built, network-disabled demo APK.
  // Never open an emulator pointing to the live, portal-capable APK.
  if (!previewButton || !previewStatus) return;
  try {
    const response = await fetch("/android/emulator.json", { cache: "no-store" });
    if (!response.ok) throw new Error("Emulator metadata unavailable");
    const config = await response.json();
    if (config.provider !== "appetize" || config.mode !== "offline-demo" ||
        config.status !== "ready" || !latestVersion ||
        config.version !== latestVersion ||
        typeof config.publicKey !== "string" ||
        !/^[A-Za-z0-9_-]{8,128}$/.test(config.publicKey)) {
      throw new Error("No verified emulator demo for the latest APK");
    }
    previewButton.href = "https://appetize.io/app/" + encodeURIComponent(config.publicKey);
    previewButton.target = "_blank";
    previewButton.rel = "noopener noreferrer";
    previewButton.removeAttribute("aria-disabled");
    previewButton.removeAttribute("tabindex");
    previewStatus.textContent = "Démo hors ligne · Version " + latestVersion + " · Aucun accès réel";
  } catch (error) {
    previewButton.removeAttribute("href");
    previewButton.setAttribute("aria-disabled", "true");
    previewButton.setAttribute("tabindex", "-1");
    previewStatus.textContent = "Démo cloud indisponible : publication Appetize en attente";
  }
})();

/*
 * Keep the Android download page current while it remains open.
 * Check the deployed script and APK metadata without using cached responses.
 * A changed deployment reloads the page; an unchanged one never does.
 */
(function watchAndroidPageUpdates() {
  const intervalMs = 60000;
  const scriptPath = "/android/latest.js";
  const metadataPath = "/android/latest.json";
  let baselineScript = null;
  let baselineVersion = null;
  let checking = false;
  let reloading = false;

  async function readText(path) {
    const url = path + "?_check=" + Date.now();
    const response = await fetch(url, { cache: "no-store", credentials: "same-origin" });
    if (!response.ok) throw new Error("Update check unavailable");
    return response.text();
  }

  async function check() {
    if (checking || reloading || !navigator.onLine) return;
    checking = true;
    try {
      const [script, metadata] = await Promise.all([
        readText(scriptPath),
        readText(metadataPath)
      ]);
      const version = JSON.parse(metadata).version;
      if (baselineScript === null || baselineVersion === null) {
        baselineScript = script;
        baselineVersion = version;
      } else if (script !== baselineScript || version !== baselineVersion) {
        reloading = true;
        // Bypass a stale cached HTML document on the next navigation.
        const url = new URL(window.location.href);
        url.searchParams.set("_updated", Date.now().toString());
        window.location.replace(url.href);
      }
    } catch (error) {
      // Keep the existing page usable when offline or during deployment.
      console.debug("Android page update check deferred", error);
    } finally {
      checking = false;
    }
  }

  check();
  setInterval(() => {
    if (document.visibilityState === "visible") check();
  }, intervalMs);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") check();
  });
  window.addEventListener("online", check);
})();
