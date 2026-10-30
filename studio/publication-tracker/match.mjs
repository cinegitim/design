// Brandstudio publication matching: conservative, source-only evidence.
// A text match NEVER proves a particular rendered revision was published.
const STOP = new Set(["icin","ve","ile","bir","bu","mu","mi","mı","de","da","the","of","in","egitim","universitesi","universite","2027","2026","at","our","as","your"]);
export function normalizeText(s="") {
  return String(s).toLocaleLowerCase("tr").replace(/ı/g,"i").replace(/İ/g,"i")
    .normalize("NFD").replace(/[\u0300-\u036f]/g,"")
    .replace(/[^a-z0-9\s]/g," ").replace(/\s+/g," ").trim();
}
export function tokens(s) {
  return new Set(normalizeText(s).split(" ").filter(w => w.length>=3 && !STOP.has(w)));
}
export function groupScore(post,group) {
  const cap=tokens(post.caption||""), title=tokens(group.title||"");
  if(!title.size || !cap.size) return 0;
  let common=0;for(const w of title)if(cap.has(w))common++;
  const exact=normalizeText(post.caption||"").includes(normalizeText(group.title||""));
  const recall=common/title.size;
  const precision=common/Math.min(cap.size, Math.max(title.size,6));
  return Math.min(1, (exact?0.40:0)+recall*0.52+precision*0.08);
}
// A verified Meta post and a unique, deliberately recorded caption anchor
// justify a FAMILY-level link; no caption can prove a particular artwork revision.
export function exactCaptionFamily(post,groups) {
  if(post.platform && !["instagram","facebook","linkedin","x"].includes(post.platform))return null;
  const caption=normalizeText(post.caption||"");
  if(!caption)return null;
  const matches=[];
  for(const group of groups||[]) {
    if(group.brand!=="asyada-egitim"||!group.id?.startsWith("instagram-"))continue;
    const anchors=Array.isArray(group.publicationAnchors)?group.publicationAnchors:[];
    // Explicit editorial anchors may be 16 characters (e.g. "Tokyo mu, Seul mu?").
    // A title-only match requires a longer distinctive phrase.
    const exact=anchors.some(text=>{
      const phrase=normalizeText(text);
      return phrase.length>=16 && caption.includes(phrase);
    }) || (normalizeText(group.title||"").length>=25 &&
          caption.includes(normalizeText(group.title||"")));
    if(exact)matches.push(group);
  }
  // More than one eligible family means not safe to automatically link.
  return matches.length===1?matches[0].id:null;
}
export function suggestFamily(post,groups) {
  const exact=exactCaptionFamily(post,groups);
  if(exact)return {groupId:exact,productId:null,confidence:1,status:"family_verified",candidates:[]};
  const scored=(groups||[]).filter(g=>g.brand==="asyada-egitim"&&g.categoryPath?.includes("Karuseller") || (g.brand==="asyada-egitim"&&g.id?.startsWith("instagram-")))
    .map(g=>({id:g.id,title:g.title,score:groupScore(post,g)}))
    .sort((a,b)=>b.score-a.score);
  const best=scored[0],second=scored[1];
  // Insufficient text may produce false positives; ambiguous candidates stay unassigned.
  if(!best || best.score<0.74 || (second && best.score-second.score<0.12))
    return {groupId:null,productId:null,confidence:best?.score||0,status:"needs_review",candidates:scored.slice(0,3)};
  return {groupId:best.id,productId:null,confidence:best.score,status:"family_candidate",candidates:scored.slice(0,3)};
}
export function validPermalink(platform,url) {
  if(typeof url!=="string")return false;
  try {
    const u=new URL(url);
    if(u.protocol!=="https:"||u.username||u.password)return false;
    const h=u.hostname.toLowerCase().replace(/^www\./,"");
    switch(platform){
      case "instagram":return h==="instagram.com" && /^\/(p|reel|tv)\/[a-z0-9_-]+\/?$/i.test(u.pathname);
      case "facebook":return (h==="facebook.com"||h==="m.facebook.com") && (/\/posts\//.test(u.pathname)||/\/permalink\//.test(u.pathname)||/\/photo/.test(u.pathname)||/story\.php/.test(u.pathname));
      case "linkedin":return h==="linkedin.com" && (/\/feed\/update\//.test(u.pathname)||/\/posts\//.test(u.pathname));
      case "x":return (h==="x.com"||h==="twitter.com") && /^\/[^/]+\/status\/\d+\/?$/.test(u.pathname);
      default:return false;
    }
  }catch{return false}
}
