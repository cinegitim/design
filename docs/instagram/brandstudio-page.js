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
    "body.bs-dark-gallery .bs-product-trail{color:#e8e0d5}",
    "body.bs-dark-gallery .bs-product-trail a{border-color:#a79a89}",
    "body.bs-dark-gallery .bs-product-trail .bs-separator{color:#b8aa99}",
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
  var background=getComputedStyle(document.body).backgroundColor.match(/\d+(?:\.\d+)?/g);
  if(background&&background.length>=3){
    var rgb=background.slice(0,3).map(Number),lum=0.2126*rgb[0]+0.7152*rgb[1]+0.0722*rgb[2];
    if(lum<132)document.body.classList.add("bs-dark-gallery");
  }
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
  }).then(async function(reg){
    var group=(reg.groups||[]).find(function(g){return (g.versions||[]).some(function(v){return v.id===versionId})});
    if(!group)return;
    workspaceUrl=new URL(group.brand==="cin-egitim"?"workspaces/cin-egitim/":"workspaces/asyada-egitim/",root);
    back.href=workspaceUrl.href;back.textContent=group.brand==="cin-egitim"?"Çin Eğitim":"Asya'da Eğitim";
    (group.categoryPath||[]).forEach(function(part){crumb(trail,part)});
    crumb(trail,group.title);
    var edition=(group.versions||[]).find(function(v){return v.id===versionId});
    if(edition)crumb(trail,edition.label);
    // Shared proof filtering works on all versioned gallery pages; offline keeps manual records.
    try{await import(new URL("publication-bridge.js",script.src).href)}catch(_){}
    var verifiedPosts=window.BrandstudioPublicationBridge?await window.BrandstudioPublicationBridge.merged(reg):
      (reg.socialPublication&&reg.socialPublication.posts||[]);
    var posts=verifiedPosts.filter(function(p){
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

  /* All secondary production materials live below the artwork in four
   * accessible native-details panels. Original links and content nodes are moved,
   * not duplicated or rewritten; legacy deep links and downloads remain intact. */
  function resourceType(label,href) {
    var text=(label+" "+href).toLocaleLowerCase("tr")
      .replace(/ı/g,"i").normalize("NFD").replace(/[\u0300-\u036f]/g,"");
    if(/mobile-324|324.contact|mobile.\d+.contact|375.469|paket|download|indir|\.zip(?:$|[?#])|source\/|\/editable\/|\.svg(?:$|[?#])/.test(text))
      return "sources";
    if(/v1.v2|v[1-9].v[1-9]|revision.comparison|revizyon karsilastirmasi|surum gecmisi|\bversiyon\b|v[1-9].galeri|\bv1\b|eski surum|onceki surum/.test(text))
      return "history";
    if(/factual|kaynak raporu|kaynak ve dogrulama|quality.review|quality.review|gorsel qa|kalite incele|caption|atif|credit|fotoraf kaynak|fotograf kaynak|photography|visual.qa|manifest|geometry.audit|exact.copy|\.(?:md|json)(?:$|[?#])|teknik dogrulama|uretim ve sanat yonetimi|platform.adaptation/.test(text))
      return "audit";
    if(/mobile|mobil|contact.sheet|temas sayfa|iletisim sayfa|feed.cover|mockup|onizleme|preview|profil izgarasi|karsilastirma.seridi/.test(text))
      return "preview";
    return null;
  }
  function organizeResources() {
    if(document.querySelector(".bs-support"))return;
    var types={
      preview:{label:"Önizlemeler",description:"Mobil akış, temas sayfası ve kapak yerleşimi"},
      history:{label:"Sürüm geçmişi",description:"Önceki sürümler ve karşılaştırmalar"},
      audit:{label:"Üretim belgeleri",description:"Kaynak doğrulama, QA, caption ve görsel atıfları"},
      sources:{label:"Kaynaklar ve indirmeler",description:"Düzenlenebilir dosyalar, teknik kontroller ve ZIP paketleri"},
      extra:{label:"Diğer materyaller",description:"Önceki üretimden kalan ek bağlantılar"}
    };
    var items={preview:[],history:[],audit:[],sources:[],extra:[]};
    var moved=new Set();
    function add(type,node) {
      if(!types[type]||moved.has(node))return;
      moved.add(node);items[type].push(node);
    }
    // Resource links in the original header are production utilities, not
    // primary nav. Preserve any unclassified link under "Diğer materyaller".
    document.querySelectorAll("header nav.links, header .links").forEach(function(nav){
      var links=Array.from(nav.querySelectorAll("a[href]"));
      if(links.length<3||!links.some(function(a){return resourceType(a.textContent,a.getAttribute("href")||"")}))
        return;
      links.forEach(function(a){
        var kind=resourceType(a.textContent,a.getAttribute("href")||"")||"extra";
        var li=document.createElement("li");li.appendChild(a);add(kind,li);
      });
      if(!nav.querySelector("a,button,input,select"))nav.remove();
    });
    // A standalone primary-header download is a source asset, not a CTA
    // comparable to "Instagram gönderisini gör" or "Visual Editor".
    document.querySelectorAll("header a.download[href]").forEach(function(a){
      if(!/\.zip(?:$|[?#])/.test(a.getAttribute("href")||""))return;
      var li=document.createElement("li");li.appendChild(a);add("sources",li);
    });
    // QA/mobility sections are appended without reconstructing their DOM;
    // this preserves any existing live gallery handlers / element references.
    document.querySelectorAll("main section.section,main section.tech,main section.review").forEach(function(sec){
      var head=sec.querySelector("h2,h3");
      if(!head)return;
      var label=head.textContent.trim();
      var plain=label.toLocaleLowerCase("tr").replace(/ı/g,"i")
        .normalize("NFD").replace(/[\u0300-\u036f]/g,"");
      var kind=null;
      if(/^(mobil okunabilirlik|mobil akis|mobil kontrol|mobil onizleme)/.test(plain))kind="preview";
      else if(/^(revizyon karsilastirmasi|surum karsilastirmasi)/.test(plain))kind="history";
      else if(/^(kaynak,? dogrulama ve atif|teknik dogrulama ozeti|uretim ve sanat yonetimi ilkeleri|kalite kontrol|gorsel qa)/.test(plain))kind="audit";
      else if(/^(slayt kaynaklari|kaynak dosyalari)/.test(plain))kind="sources";
      if(kind)add(kind,sec);
    });
    // Revision pages may expose a flat JSON/ZIP evidence bar rather than
    // structured sections; preserve those same links inside the drawers.
    document.querySelectorAll("main > .files,main > .resources").forEach(function(block){
      var links=Array.from(block.querySelectorAll("a[href]"));
      if(links.length<2||!links.every(function(a){
        return !!resourceType(a.textContent,a.getAttribute("href")||"");
      }))return;
      links.forEach(function(a){
        var kind=resourceType(a.textContent,a.getAttribute("href")||"");
        var li=document.createElement("li");li.appendChild(a);add(kind,li);
      });
      if(!block.querySelector("a,button,input,select"))block.remove();
    });
    // Slide galleries use different markup (article.card, div.slide, panels),
    // so scan actual technical links rather than requiring a specific template.
    // Keep artwork links around thumbnail images in their original place.
    document.querySelectorAll("main a[href]").forEach(function(a){
      if(moved.has(a)||a.querySelector("img,picture,svg,canvas"))return;
      var href=a.getAttribute("href")||"";
      var kind=resourceType(a.textContent,href);
      var technical=/(?:^|\/)(?:source|editable)\/|\.svg(?:$|[?#])|\.zip(?:$|[?#])|\.(?:md|json)(?:$|[?#])/.test(href);
      if(!technical||!kind)return;
      var card=a.closest("article.card,.slide-card,.slide-item,.slide,section.section,article");
      var title=card&&card.querySelector("h2,h3,h4");
      var li=document.createElement("li");
      if(title){var prefix=document.createElement("span");prefix.className="bs-resource-prefix";
        prefix.textContent=title.textContent.trim()+" — ";li.appendChild(prefix)}
      li.appendChild(a);add(kind,li);
    });
    // No need for an empty category or a third navigation interface.
    if(!Object.keys(items).some(function(k){return items[k].length}))return;
    var section=document.createElement("section");section.className="bs-support";
    section.setAttribute("aria-label","Tasarımın yardımcı üretim materyalleri");
    var heading=document.createElement("h2");heading.textContent="Tasarım materyalleri";
    var description=document.createElement("p");description.className="bs-support-lead";
    description.textContent="Önizleme ve üretim belgeleri gerektiğinde açılabilir. Tasarımın kendisi yukarıda.";
    section.append(heading,description);
    Object.keys(types).forEach(function(key){
      var nodes=items[key];if(!nodes.length)return;
      var detail=document.createElement("details");detail.className="bs-drawer";
      detail.dataset.group=key;if(key==="preview")detail.open=true;
      var summary=document.createElement("summary");
      var title=document.createElement("strong");title.textContent=types[key].label;
      var count=document.createElement("span");count.className="bs-drawer-count";
      count.textContent=String(nodes.length);
      var sub=document.createElement("small");sub.textContent=types[key].description;
      summary.append(title,count,sub);detail.append(summary);
      var body=document.createElement("div");body.className="bs-drawer-body";
      var list=document.createElement("ul");list.className="bs-resource-links";
      nodes.forEach(function(node){
        if(node.tagName==="LI")list.appendChild(node);
        else {var wrap=document.createElement("div");wrap.className="bs-resource-section";wrap.appendChild(node);body.appendChild(wrap)}
      });
      if(list.children.length)body.insertBefore(list,body.firstChild);
      detail.append(body);section.append(detail);
    });
    var main=document.querySelector("main");
    if(main)main.insertAdjacentElement("afterend",section);
    else{var footer=document.querySelector("footer");if(footer)footer.before(section);else document.body.append(section)}
    document.documentElement.dataset.bsResourceOrganized="true";
  }
  var supportStyle=document.createElement("style");
  supportStyle.textContent=[
    ".bs-support{max-width:1180px;margin:24px auto 50px;padding:0 24px;color:#1d2027;font:14px/1.5 system-ui,-apple-system,sans-serif}",
    ".bs-support *{box-sizing:border-box}",
    ".bs-support h2{font:600 clamp(25px,3vw,34px)/1.12 Georgia,serif;letter-spacing:-.025em;margin:0 0 5px;color:inherit}",
    ".bs-support-lead{font-size:13px;color:#5e5a54;margin:0 0 20px}",
    ".bs-drawer{border:1px solid #c5bfb3;border-radius:10px;margin-top:9px;background:#f7f3e9;overflow:hidden;color:#1d2027}",
    ".bs-drawer summary{display:flex;align-items:center;gap:10px;flex-wrap:wrap;cursor:pointer;padding:14px 18px;font:14px/1.3 system-ui,-apple-system,sans-serif;list-style:none}",
    ".bs-drawer summary::-webkit-details-marker{display:none}",
    ".bs-drawer summary:focus-visible{outline:3px solid #bd2120;outline-offset:-3px}",
    ".bs-drawer summary::after{content:'⌄';font-size:20px;margin-left:auto;color:#bd2120;line-height:1}",
    ".bs-drawer[open] summary::after{content:'⌃'}",
    ".bs-drawer-count{font:12px/1 system-ui,sans-serif;color:#6b6459;background:#e8e2d6;padding:5px 7px;border-radius:20px}",
    ".bs-drawer summary small{width:100%;color:#655e55;font-size:11px;margin-top:-4px}",
    ".bs-drawer-body{border-top:1px solid #d9d2c5;padding:13px 18px}",
    ".bs-resource-links{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 18px;padding:0;list-style:none;margin:0}",
    ".bs-resource-links li{min-width:0;overflow-wrap:anywhere}",
    ".bs-resource-links a,.bs-resource-section a{color:#9c2225!important;text-decoration:underline;text-underline-offset:3px}",
    ".bs-resource-prefix{color:#625e58;font-size:12px}",
    ".bs-resource-section{min-width:0;max-width:100%;margin-bottom:12px}",
    ".bs-resource-section:last-child{margin-bottom:0}",
    ".bs-resource-section img{max-width:100%;height:auto}",
    ".bs-resource-section h2,.bs-resource-section h3{font-size:20px;line-height:1.25;letter-spacing:0}",
    "body.bs-dark-gallery .bs-support{color:#f7f3e9}",
    "body.bs-dark-gallery .bs-support-lead{color:#c8beb3}",
    "@media(max-width:680px){.bs-support{padding:0 15px}.bs-resource-links{grid-template-columns:1fr}.bs-drawer summary{padding:12px 14px}.bs-drawer-body{padding:12px 14px}}"
  ].join("\n");
  document.head.append(supportStyle);
  organizeResources();

})();