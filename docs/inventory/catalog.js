/* Exhaustive Brandstudio inventory. Every committed blob belongs to one review unit. */
(function(root){
"use strict";
function title(s){return String(s||"").replace(/[-_]+/g," ").replace(/\b\w/g,c=>c.toUpperCase())}
function normalize(f){return Array.isArray(f)?{path:f[0],sha:f[1],size:f[2]}:{path:f.path,sha:f.sha,size:f.size}}
function role(p){
 const x=p.toLowerCase(),base=x.split("/").at(-1);
 if(/(?:^|\/)(?:manifest[^/]*\.json|[^/]*-manifest\.json)$/.test(x))return"manifest";
 if(/\/(?:source|editable|source-originals)\//.test(x))return"editable-source";
 if(/\/(?:history|originals?|v\d+)\//.test(x))return"version";
 if(/\/(?:final|export|renders?|composited|png|mobile|mobile-preview)\//.test(x))return"render";
 if(/\/(?:assets|photos?|reference|fonts?)\//.test(x))return"dependency";
 if(/\/(?:review|qa|previews?|consistency)\//.test(x))return"review";
 if(/\.(?:png|jpe?g|webp|svg|pdf|zip)$/i.test(base))return"artwork";
 if(/\.html$/i.test(base))return"html";
 if(/\.json$/i.test(base))return"metadata";
 if(/\.md$/i.test(base))return"documentation";
 return"other";
}
function classify(p){
 const a=p.split("/"),top=a[0],second=a[1]||"",third=a[2]||"";
 const asya="asyada-egitim",chin="cin-egitim";
 let brand="system",category="infrastructure",key=top,review="protected",basis="Runtime/configuration, not a standalone creative output.";
 if(top==="docs"){
  if(second==="instagram"){
   brand=asya;category="social";review="review";
   if(/^phase-2[bc]$/.test(third)&&/^[a-d]-/.test(a[3]||""))key=a.slice(0,4).join("/");
   else key=a.slice(0,3).join("/");
   if(/^phase-|^carousel-01(?:-v\d+)?$|^discovery-01$/.test(third)){review="candidate";basis="Early campaign phase or earlier creative iteration; compare against later revisions."}
   else basis="Published review artifact; publication/approval remains unverified.";
  }else if(second==="asyada-seal"){
   brand=asya;category="identity-exploration";key=a.slice(0,3).join("/");review="candidate";basis="Historical seal/wordmark review galleries, not canonical identity source.";
   if(["canonical-lockups","final-lockups","unified"].includes(third)){review="verify";basis="May contain approved or referenced lockup presentations; check manifest and shared links."}
  }else if(second==="cin-egitim"){
   brand=chin;category=third==="rollup"?"print":"identity-exploration";key=a.slice(0,3).join("/");review="verify";basis="Review/public presentation or print output; retain if linked or approved.";
   if(["typography-round-01","social-avatars-01","social-avatars-02"].includes(third)){review="candidate";basis="Earlier experimental series; compare against newer and approved sources."}
  }else if(second==="asya-egitim"){
   brand="asya-egitim-legacy";category="identity-exploration";key=a.slice(0,3).join("/");review="candidate";basis="Separate historic Asya Eğitim visual exploration, not current Asya’da Eğitim canonical brand.";
  }else if(second==="asyada-egitim"){
   brand=asya;category="brand-application";review="verify";key=a.slice(0,3).join("/");
   if(third==="assets"){
    let f=a.at(-1);
    if(/^visual-round-|^high-aesthetic-|^seal-v-\d+/.test(f)){key="docs/asyada-egitim/assets/visual-explorations";category="identity-exploration";review="candidate";basis="Old exploratory visual rounds, not canonical source."}
    else if(/^ieft-/.test(f)){key="docs/asyada-egitim/assets/ieft";category="campaign";basis="IEFT fair collateral; verify preservation and cross-references."}
    else if(/^app-/.test(f)){key="docs/asyada-egitim/assets/applications";category="brand-application"}
    else if(/^web/.test(f)){key="docs/asyada-egitim/assets/web";category="web"}
    else {key="docs/asyada-egitim/assets/other";review="verify"}
   }
  }else if(second==="social-covers"){
   brand="cross-brand";category="social";key="docs/social-covers";review="verify";basis="Social profile/cover design variants; check current chosen versions.";
  }else if(second==="review"){
   brand="cross-brand";category="review";key=a.slice(0,3).join("/");review="candidate";basis="Comparisons and demonstrations, not approved production.";
  }else if(second==="workspaces"||second==="visual-editor"||second==="productions"||second==="cloud"){
   brand="system";category="infrastructure";key="docs/"+second;review="protected";basis="Active site/editor routing and hosting infrastructure.";
  }else if(second==="archive"){
   brand="system";category="archive-interface";key="docs/archive";review="protected";basis="Existing archive index/routing pages; not a detached preservation repository.";
  }else{
   brand="cross-brand";category="infrastructure";key="docs/"+second;review="protected";
  }
 }else if(top==="brands"){
  brand=second||"cross-brand";
  if(["applications","explorations","share-seal","boards"].includes(third)){
   key=a.slice(0,4).join("/");
   if(a.length<4)key=a.slice(0,3).join("/");
   category=third==="applications"?"brand-application":third==="boards"?"review":"identity-exploration";
   review=third==="applications"?"verify":"candidate";
   basis=third==="applications"?"Authored application source or collateral; evaluate version and dependencies.":"Historic creative explorations/boards; requires human retirement decision.";
  }else if(third==="enhancements"||third==="reconstruction-direction-3"){
   category="identity-exploration";key=a.slice(0,3).join("/");review="candidate";basis="Historical enhancement or reconstruction trial.";
  }else if(third==="reference"){
   category="brand-reference";key=a.slice(0,3).join("/");review="protected";basis="Locked or provenance-bearing reference assets.";
  }else if(third==="assets"||third==="decisions"||third==="styles"){
   category="brand-foundation";key=a.slice(0,3).join("/");review="protected";basis="Shared identity source, approvals, recorded decisions and dependent assets.";
  }else{
   category="brand-foundation";key=a.slice(0,3).join("/");review="protected";basis="Brand governance/status and production constraints.";
  }
 }else if(top==="figma"){
  brand="cross-brand";category="integration";key="figma";review="protected";
 }else if(top==="studio"||top===".agents"||top===".opencode"||top===".github"){
  key=top+"/"+(second||"root");review="protected";category="infrastructure";
 }else{
  key="repository-root";review="protected";category="infrastructure";
 }
 // Synthetic group keys may aggregate filenames with a shared campaign prefix.
 return{key,brand,category,review,basis}
}
function build(list,meta){
 if(!Array.isArray(list))throw Error("File tree missing");
 const seen=new Set(),groups=new Map(),files=[],dupes=new Map();
 list.forEach(f=>{
  const item=normalize(f);
  if(!item.path||seen.has(item.path)||!(/^[0-9a-f]{40}$/.test(item.sha))||!Number.isFinite(item.size)||item.size<0)throw Error("Duplicate or invalid file "+item.path);
  seen.add(item.path);
  const cl=classify(item.path),r=role(item.path);
  let g=groups.get(cl.key);
  if(!g){g={id:cl.key,title:title(cl.key.split("/").at(-1)),brand:cl.brand,category:cl.category,review:cl.review,basis:cl.basis,files:[],bytes:0,formats:{},roles:{},versions:[]};groups.set(cl.key,g)}
  const ext=item.path.split(".").at(-1).toLowerCase();
  g.files.push({...item,role:r});g.bytes+=item.size;g.formats[ext]=(g.formats[ext]||0)+1;g.roles[r]=(g.roles[r]||0)+1;
  const versions=item.path.match(/\/(v\d+|history|originals?|final|editable|source|export)\//ig)||[];
  for(const v of versions){let t=v.slice(1,-1);if(!g.versions.includes(t))g.versions.push(t)}
  files.push(item);
  const same=dupes.get(item.sha)||[];same.push(item.path);dupes.set(item.sha,same)
 });
 const rows=Array.from(groups.values()).sort((a,b)=>a.brand.localeCompare(b.brand)||a.category.localeCompare(b.category)||a.id.localeCompare(b.id));
 const covered=rows.reduce((n,g)=>n+g.files.length,0);
 if(covered!==seen.size)throw Error("Classification incomplete "+covered+"/"+seen.size);
 const count=(f)=>rows.filter(f).length;
 return{meta:meta||{},filesCount:seen.size,groupsCount:rows.length,bytes:rows.reduce((n,g)=>n+g.bytes,0),groups:rows,
  summary:{byBrand:Object.fromEntries([...new Set(rows.map(g=>g.brand))].map(x=>[x,rows.filter(g=>g.brand===x).reduce((n,g)=>n+g.files.length,0)])),
   byCategory:Object.fromEntries([...new Set(rows.map(g=>g.category))].map(x=>[x,rows.filter(g=>g.category===x).reduce((n,g)=>n+g.files.length,0)])),
   byReview:Object.fromEntries([...new Set(rows.map(g=>g.review))].map(x=>[x,{groups:count(g=>g.review===x),files:rows.filter(g=>g.review===x).reduce((n,g)=>n+g.files.length,0)}])),
   exactDuplicateBlobs:[...dupes.values()].filter(arr=>arr.length>1).length}
 }
}
function snapshotToTree(s){if(!s||s.schema!==1||!Array.isArray(s.files)||s.files.length!==s.file_count)throw Error("Pinned snapshot incomplete");return s.files}
async function load(){
 const pinned=await fetch("snapshot.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("Snapshot unavailable");return r.json()});
 let files=snapshotToTree(pinned),meta={source:"pinned",sha:pinned.tree_sha,scan:pinned.captured_on,coverage:pinned.file_count};
 try{
  const response=await fetch("https://api.github.com/repos/cinegitim/design/git/trees/main?recursive=1",{cache:"no-store",headers:{Accept:"application/vnd.github+json"}});
  if(response.ok){
   const remote=await response.json();
   if(!remote.truncated&&Array.isArray(remote.tree)&&remote.tree.some(x=>x.type==="blob")){
    files=remote.tree.filter(x=>x.type==="blob").map(x=>[x.path,x.sha,x.size]);meta={source:"live-main",sha:remote.sha,scan:new Date().toISOString(),coverage:files.length};
   }
  }
 }catch(_){}
 return build(files,meta)
}
root.BrandstudioInventory={build,classify,role,snapshotToTree,load};
})(typeof globalThis!=="undefined"?globalThis:this);
