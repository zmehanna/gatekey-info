(async function () {
  const badge = document.querySelector(".version strong");
  const button = document.querySelector("a.download");
  const artVersion = document.querySelector(".art .bar span:last-child");
  if (!badge || !button) return;
  try {
    const response = await fetch("/android/latest.json", {cache:"no-store"});
    if (!response.ok) throw new Error("Metadata unavailable");
    const latest = await response.json();
    if (!/^\d+\.\d+\.\d+([-.][a-z0-9.-]+)?$/i.test(latest.version)) throw new Error("Invalid version");
    if (typeof latest.url !== "string" || !latest.url.startsWith("https://github.com/zmehanna/gatekey-info/releases/download/android-latest/")) throw new Error("Invalid download");
    badge.textContent = "Android " + latest.version + " Bêta";
    artVersion.textContent = "Version " + latest.version;
    button.href = latest.url;
    button.setAttribute("download", latest.filename || "PrivateGateKey-Android.apk");
  } catch (error) {
    console.warn("Latest Android metadata not available", error);
  }
})();