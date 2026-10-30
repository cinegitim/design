/* Brandstudio: administrator-initiated Instagram publication check only.
   The browser never receives a Meta token, refresh credential, or scheduled task. */
(function () {
"use strict";
if (location.hostname !== "studio.asyadaegitim.com") return;
const section = document.getElementById("publication-check");
const button = document.getElementById("publication-check-button");
const status = document.getElementById("publication-check-status");
if (!section || !button || !status) return;
const messageKey = "brandstudio:publication-check:result";
const format = value => {
  if (!value) return "Henüz denetim yapılmadı";
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? "Bilinmiyor" :
    date.toLocaleString("tr-TR",{timeZone:"Europe/Istanbul",dateStyle:"medium",timeStyle:"short"});
};
async function readStatus() {
  const response = await fetch("/admin/publications/status", {
    credentials:"same-origin",cache:"no-store",headers:{Accept:"application/json"}
  });
  if (!response.ok) throw Error("Yönetici bağlantısı kurulamadı");
  return response.json();
}
async function init() {
  try {
    const result = await readStatus();
    section.hidden = false;
    const notice = sessionStorage.getItem(messageKey);
    if (notice) {
      sessionStorage.removeItem(messageKey);
      status.textContent = notice;
    } else {
      status.textContent = "Son denetim: " + format(result.lastScan?.finishedAt||result.lastScan?.startedAt) +
       (result.lastScan?.state==="error" ? " · Son işlem başarısız" : "");
    }
  } catch (_) {
    // On Pages previews or unauthenticated sessions there is no admin action.
    section.hidden = true;
  }
}
button.addEventListener("click", async function () {
  if (button.disabled) return;
  button.disabled = true;
  status.textContent = "Instagram yayınları denetleniyor…";
  try {
    const response = await fetch("/admin/publications/refresh",{
      method:"POST",credentials:"same-origin",cache:"no-store",
      headers:{"Content-Type":"application/json",Accept:"application/json"},
      body:JSON.stringify({platforms:["instagram"]})
    });
    const result = await response.json();
    if (!response.ok || result.platforms?.instagram?.state!=="ok")
      throw Error(result.details||result.error||"Instagram denetimi başarısız");
    const scan = result.platforms.instagram;
    sessionStorage.setItem(messageKey,"Denetim tamamlandı · "+Number(scan.fetched||0)+
      " gönderi kontrol edildi · "+Number(scan.needsReview||0)+
      " gönderi inceleme bekliyor · "+format(result.completedAt));
    // Reload all design cards; merged() reads the new stored proofs without another Meta request.
    location.reload();
  } catch (error) {
    status.textContent = "Denetim tamamlanamadı: "+String(error?.message||error).slice(0,160);
    button.disabled = false;
  }
});
init();
})();
