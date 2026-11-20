(async function () {
  const badge = document.querySelector(".version strong");
  const button = document.querySelector("a.download");
  const artVersion = document.querySelector(".art .bar span:last-child");
  const previewButton = document.querySelector("#try-android");
  const previewStatus = document.querySelector("#emulator-status");
  let latestVersion = null;

  try {
    const response = await fetch("/android/latest.json", { cache: "no-store" });
    if (!response.ok) throw new Error("Metadata unavailable");
    const latest = await response.json();
    if (!/^\d+\.\d+\.\d+([-.][a-z0-9.-]+)?$/i.test(latest.version)) throw new Error("Invalid version");
    if (typeof latest.url !== "string" ||
        !latest.url.startsWith("https://github.com/zmehanna/gatekey-info/releases/download/android-latest/")) {
      throw new Error("Invalid download");
    }
    latestVersion = latest.version;
    if (badge) badge.textContent = "Android " + latestVersion + " Bêta";
    if (artVersion) artVersion.textContent = "Version " + latestVersion;
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
