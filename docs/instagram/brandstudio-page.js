/* Brandstudio: shared, read-only metadata and compact actions for published design pages.
 * Do not infer Instagram publication from repository existence. No API keys or backend writes.
 */
(function () {
  "use strict";
  var script=document.currentScript;
  if(!script)return;
  var versionId=script.dataset.productId;
  if(!versionId)return;
  var root=new URL("../",script.src);
  var registryUrl=new URL("visual-editor/browser/product-groups.json",root);
  var editorUrl=new URL("visual-editor/browser/?product="+encodeURIComponent(versionId),root);
  var workspaceUrl=new URL("workspaces/asyada-egitim/",root);
  var stylesheet=document.createElement("style");
  stylesheet.textContent=[
    ".bs-product-bar{max-width:1180px;margin:0 auto;padding:22px 24px 0;display:flex;gap:14px;align-items:center;justify-content:space-between;flex-wrap:wrap;color:#1d2027;font:13px/1.45 system-ui,-apple-system,sans-serif}",
    ".bs-product-bar *{box-sizing:border-box}",
    ".bs-product-trail{display:flex;align-items:center;gap:6px;flex-wrap:wrap;min-width:0;color:#55504b;font-size:12px}",
    ".bs-product-trail a{color:inherit;text-decoration:none;border-bottom:1px solid #b7ad9b}",
    ".bs-product-trail a:hover{text-decoration:underline}",
    ".bs-product-trail .bs-separator{color:#a89e90}",
    ".bs-actions{display:flex;align-items:center;flex-wrap:wrap;gap:9px}",
    ".bs-action{display:inline-flex;justify-content:center;align-items:center;gap:9px;padding:11px 17px;min-height:45px;text-decoration:none!important;border-radius:9px;border:1px solid #bd2120;color:#fff!important;background:#bd2120;font-size:13px;font-weight:720;white-space:nowrap;transition:filter .16s}",
    ".bs-action:hover{filter:brightness(.9)}",
    ".bs-action:focus-visible{outline:3px solid #1d2027;outline-offset:3px}",
    ".bs-action.instagram{background:#fffaf0;border-color:#d7ccc1;color:#1d2027!important}",
    ".bs-action svg{width:17px;height:17px;flex-shrink:0;display:block}",
    ".bs-product-provenance{width:100%;font-size:11px;color:#686156;margin-top:-3px}",
    "@media(max-width:680px){.bs-product-bar{padding:14px 15px 0;display:block}.bs-actions{margin-top:13px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.bs-actions .bs-action{white-space:normal;text-align:center;padding:11px 9px;font-size:12px}.bs-actions .bs-action:only-child{grid-column:1/-1}}"
  ].join("\n");
  document.head.appendChild(stylesheet);
  var bar=document.createElement("nav");bar.className="bs-product-bar";bar.setAttribute("aria-label","Tasarım künyesi ve işlemler");
  var trail=document.createElement("div");trail.className="bs-product-trail";
  var back=document.createElement("a");back.href=workspaceUrl.href;back.textContent="Asya'da Eğitim";trail.append(back);
  var actions=document.createElement("div");actions.className="bs-actions";
  function icon(kind) {
    if(kind==="instagram")return '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5"/><circle cx="12" cy="12" r="4.1"/><circle cx="17.8" cy="6.5" r="1.15" fill="currentColor" stroke="none"/></svg>';
    return '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M13.5 4.5H20v6.5M20 4.5l-9.2 9.2"/><path d="M18 13v6.5H4.5V6H11"/></svg>';
  }
  function action(href,label,kind) {
    var link=document.createElement("a");link.href=href;link.className="bs-action "+kind;
    link.innerHTML=icon(kind)+"<span></span>";link.lastElementChild.textContent=label;
    if(kind==="instagram"){link.target="_blank";link.rel="noopener noreferrer"}
    return link;
  }
  actions.append(action(editorUrl.href,"Visual Editor ile düzenle","editor"));
  bar.append(trail,actions);
  document.body.insertBefore(bar,document.body.firstChild);
  function verified(p){
    return p&&p.verified===true&&typeof p.publishedAt==="string"&&
      /^https:\/\/(?:www\.)?instagram\.com\/(?:asyadaegitim\/)?(?:p|reel|tv)\/[A-Za-z0-9_-]+\/?(?:\?.*)?$/.test(p.url||"");
  }
  function crumb(parent,part){
    var sep=document.createElement("span");sep.className="bs-separator";sep.textContent="›";
    var piece=document.createElement("span");piece.textContent=part;parent.append(sep,piece);
  }
  fetch(registryUrl.href,{cache:"no-store"}).then(function(r){
    if(!r.ok)throw Error("Registry HTTP "+r.status);return r.json()
  }).then(function(reg){
    var group=(reg.groups||[]).find(function(g){return (g.versions||[]).some(function(v){return v.id===versionId})});
    if(!group)return;
    workspaceUrl=new URL(group.brand==="cin-egitim"?"workspaces/cin-egitim/":"workspaces/asyada-egitim/",root);
    back.href=workspaceUrl.href;back.textContent=group.brand==="cin-egitim"?"Çin Eğitim":"Asya'da Eğitim";
    (group.categoryPath||[]).forEach(function(part){crumb(trail,part)});
    crumb(trail,group.title);
    var edition=(group.versions||[]).find(function(v){return v.id===versionId});
    if(edition)crumb(trail,edition.label);
    var posts=(reg.socialPublication&&reg.socialPublication.posts||[]).filter(function(p){
      return verified(p)&&(p.productId===versionId||p.groupId===group.id);
    });
    if(posts.length){
      var exact=posts.some(function(p){return p.productId===versionId});
      var publishedEdition=(group.versions||[]).find(function(v){return v.id===group.publishedVersionId});
      var label=exact?"Instagram gönderisini gör":(publishedEdition?
        "Instagram'da yayımlanan "+publishedEdition.label+" sürümünü gör":"Ailenin Instagram gönderisini gör");
      var instagram=action(posts[0].url,label,"instagram");
      instagram.title=exact?"Bu sürüm Instagram'da yayımlandı.":(publishedEdition?
        "Bu sayfa "+versionId+" taslağına ait; yayımlanan sürüm "+publishedEdition.label+".":"Tasarım ailesinin Instagram gönderisi; yayımlanan kesin sürüm henüz doğrulanmadı.");
      actions.insertBefore(instagram,actions.firstChild);
    }
  }).catch(function(){/* Static page and Visual Editor access are still usable without metadata network. */});
})();