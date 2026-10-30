import {suggestFamily,validPermalink} from "./match.mjs";
const PLATFORMS=["instagram","facebook","linkedin","x"];
const REGISTRY="https://cinegitim.github.io/design/visual-editor/browser/product-groups.json";
const REGISTRY_FALLBACK="https://raw.githubusercontent.com/cinegitim/design/main/docs/visual-editor/browser/product-groups.json";
const NOW=()=>new Date().toISOString();
function json(body,status=200,origin=""){
  const headers={"Content-Type":"application/json; charset=utf-8","Cache-Control":"no-store","X-Content-Type-Options":"nosniff"};
  if(origin==="https://studio.asyadaegitim.com"){headers["Access-Control-Allow-Origin"]=origin;headers["Vary"]="Origin";headers["Access-Control-Allow-Headers"]="Authorization,Content-Type";headers["Access-Control-Allow-Methods"]="GET,POST,OPTIONS";}
  return new Response(JSON.stringify(body),{status,headers});
}
function enabled(env,platform){
  if(platform==="instagram")return Boolean(env.META_IG_ID&&(env.META_IG_TOKEN||env.META_PAGE_TOKEN));
  if(platform==="facebook")return Boolean(env.META_PAGE_ID&&env.META_PAGE_TOKEN);
  if(platform==="linkedin")return Boolean(env.LINKEDIN_ORG_ID&&env.LINKEDIN_TOKEN);
  if(platform==="x")return Boolean(env.X_RSS_URL);
  return false;
}
async function fetchJSON(url,headers={}){
  const res=await fetch(url,{headers:{Accept:"application/json",...headers},signal:AbortSignal.timeout(12000)});
  if(!res.ok)throw Error("Source HTTP "+res.status);
  return res.json();
}
async function readMeta(env,platform){
  const ig=platform==="instagram";
  const id=ig?env.META_IG_ID:env.META_PAGE_ID;
  const url=new URL("https://graph.facebook.com/v26.0/"+encodeURIComponent(id)+"/"+(ig?"media":"posts"));
  url.searchParams.set("fields",ig?"id,caption,permalink,timestamp,media_type":"id,message,permalink_url,created_time");
  url.searchParams.set("limit","50");
  const token=ig?(env.META_IG_TOKEN||env.META_PAGE_TOKEN):env.META_PAGE_TOKEN;
  const response=await fetchJSON(url.toString(),{"Authorization":"Bearer "+token});
  return (response.data||[]).map(p=>({
    platform,id:String(p.id),url:ig?p.permalink:p.permalink_url,
    caption:ig?(p.caption||""):(p.message||""),date:ig?p.timestamp:p.created_time,
    evidence:"official_meta_api"
  }));
}
async function readLinkedIn(env){
  const u=new URL("https://api.linkedin.com/rest/posts");
  u.searchParams.set("q","author");u.searchParams.set("author","urn:li:organization:"+env.LINKEDIN_ORG_ID);u.searchParams.set("count","50");
  const data=await fetchJSON(u.toString(),{
    "Authorization":"Bearer "+env.LINKEDIN_TOKEN,
    "Linkedin-Version":env.LINKEDIN_VERSION||"202609",
    "X-Restli-Protocol-Version":"2.0.0"
  });
  return (data.elements||[]).filter(p=>p.lifecycleState==="PUBLISHED").map(p=>({
    platform:"linkedin",id:String(p.id),
    // This is the URN-based update route, not a post-specific vanity URL.
    url:"https://www.linkedin.com/feed/update/"+String(p.id)+"/",
    caption:p.commentary||"",date:p.publishedAt?new Date(p.publishedAt).toISOString():null,
    evidence:"official_linkedin_api"
  }));
}
function plainXml(s){return s.replace(/<!\[CDATA\[|\]\]>/g,"").replace(/<[^>]+>/g," ").replace(/&amp;/g,"&").replace(/&lt;/g,"<").replace(/&gt;/g,">").replace(/&quot;/g,'"').replace(/\s+/g," ").trim();}
async function readXFeed(env){
  const feed=new URL(env.X_RSS_URL);
  if(feed.protocol!=="https:"||!["nitter.mie.foundation","nitter.mizuki.st"].includes(feed.hostname))throw Error("X feed host not allowlisted");
  const res=await fetch(feed,{signal:AbortSignal.timeout(12000),headers:{Accept:"application/rss+xml,application/xml,text/xml"}});
  if(!res.ok)throw Error("X RSS mirror HTTP "+res.status);
  const xml=(await res.text()).slice(0,250000);
  const items=[...xml.matchAll(/<item[\s>][\s\S]*?<\/item>/gi)].slice(0,40);
  const records=[];
  for(const item of items){
    const x=item[0],raw=(x.match(/<link>([\s\S]*?)<\/link>/i)||[])[1]||"";
    const path=plainXml(raw).match(/\/([^\s/]+)\/status\/(\d+)/);
    if(!path)continue;
    records.push({platform:"x",id:path[2],url:"https://x.com/"+path[1]+"/status/"+path[2],
      caption:plainXml((x.match(/<description>([\s\S]*?)<\/description>/i)||[])[1]||""),
      date:null,evidence:"unofficial_rss_unverified"});
  }
  return records;
}
async function register(db,post,match){
  const t=NOW();
  await db.prepare(`INSERT INTO publication_posts
  (platform,source_id,permalink,caption,published_at,group_id,product_id,match_status,match_score,evidence,first_seen_at,last_seen_at)
  VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
  ON CONFLICT(platform,source_id) DO UPDATE SET
  permalink=excluded.permalink,caption=excluded.caption,last_seen_at=excluded.last_seen_at,
  group_id=CASE WHEN publication_posts.match_status IN ('revision_verified','family_verified') THEN publication_posts.group_id ELSE excluded.group_id END,
  match_status=CASE WHEN publication_posts.match_status IN ('revision_verified','family_verified') THEN publication_posts.match_status ELSE excluded.match_status END,
  match_score=CASE WHEN publication_posts.match_status IN ('revision_verified','family_verified') THEN publication_posts.match_score ELSE excluded.match_score END`)
  .bind(post.platform,post.id,post.url,post.caption||"",post.date||null,match.groupId,null,match.status,match.confidence,post.evidence,t,t).run();
}
async function refresh(env,platforms){
  const summary={startedAt:NOW(),platforms:{},completedAt:null};
  let groups=[];
  try{
    let data;
    try { data=await fetchJSON(REGISTRY); if(!Array.isArray(data.groups)) throw Error("Catalog groups missing"); }
    catch (_primaryError) { data=await fetchJSON(REGISTRY_FALLBACK); if(!Array.isArray(data.groups)) throw Error("Fallback catalog groups missing"); }
    groups=data.groups;
  }catch(e){summary.catalogError=String(e.message||e);}
  for(const p of platforms){
    if(!enabled(env,p)){summary.platforms[p]={state:"not_connected"};continue;}
    try{
      const posts=p==="instagram"||p==="facebook"?await readMeta(env,p):p==="linkedin"?await readLinkedIn(env):await readXFeed(env);
      let saved=0,review=0,invalid=0;
      for(const post of posts){
        if(!post.id||!validPermalink(post.platform,post.url)){invalid++;continue;}
        const match=suggestFamily(post,groups);
        // A discovered family does not establish the exact exported revision.
        await register(env.DB,post,match);
        saved++;if(match.status==="needs_review")review++;
      }
      summary.platforms[p]={state:"ok",fetched:posts.length,saved,needsReview:review,invalid};
    }catch(e){summary.platforms[p]={state:"error",message:String(e.message||e)};}
  }
  summary.completedAt=NOW();
  await env.DB.prepare("INSERT INTO publication_runs(id,started_at,finished_at,summary_json) VALUES(?,?,?,?)")
    .bind(crypto.randomUUID(),summary.startedAt,summary.completedAt,JSON.stringify(summary)).run();
  return summary;
}
function authorize(req,env){
  const supplied=req.headers.get("Authorization")||"";
  return Boolean((env.PUBLICATION_REFRESH_TOKEN&&supplied==="Bearer "+env.PUBLICATION_REFRESH_TOKEN) || (env.BRANDSTUDIO_PUBLICATION_BRIDGE_TOKEN&&supplied==="Bearer "+env.BRANDSTUDIO_PUBLICATION_BRIDGE_TOKEN));
}
export default {
  async fetch(request,env){
    const origin=request.headers.get("Origin")||"";
    const url=new URL(request.url);
    if(request.method==="OPTIONS")return new Response(null,{status:204,headers:origin==="https://studio.asyadaegitim.com"?{"Access-Control-Allow-Origin":origin,"Access-Control-Allow-Methods":"GET,POST,OPTIONS","Access-Control-Allow-Headers":"Authorization,Content-Type","Vary":"Origin"}:{}});
    if(url.pathname==="/health")return json({service:"brandstudio-publications",state:"alive",timestamp:NOW()},200,origin);
    if(url.pathname==="/api/status"&&request.method==="GET"){
      let lastScan=null;
      if(env.DB){
        try{
          const row=await env.DB.prepare("SELECT started_at,finished_at,summary_json FROM publication_runs ORDER BY started_at DESC LIMIT 1").first();
          if(row){
            const info=JSON.parse(row.summary_json||"{}");
            const ig=info.platforms?.instagram||{};
            lastScan={startedAt:row.started_at,finishedAt:row.finished_at,state:ig.state||"unknown",saved:ig.saved??null,needsReview:ig.needsReview??null};
          }
        }catch(_){/* Status remains available even if the runs table is temporarily unavailable. */}
      }
      return json({platforms:Object.fromEntries(PLATFORMS.map(p=>[p,{configured:enabled(env,p)}])),mode:"on_demand_only",storage:!!env.DB,lastScan},200,origin);
    }
    // Public, bounded proof feed: caption/text candidates and credentials never leave D1.
    // A caption anchor confirms an Instagram design FAMILY only, never a specific revision.
    if(url.pathname==="/api/proofs"&&request.method==="GET"){
      if(!env.DB)return json({error:"database_not_bound"},503,origin);
      try{
        const {results}=await env.DB.prepare("SELECT platform,source_id,permalink,published_at,group_id,product_id,match_status FROM publication_posts WHERE platform='instagram' AND match_status='family_verified' AND evidence='official_meta_api' AND group_id IS NOT NULL ORDER BY published_at DESC LIMIT 100").all();
        return json({posts:results,rule:"verified Meta post + unique caption anchor; family only"},200,origin);
      }catch(e){return json({error:"database_not_initialized"},503,origin)}
    }
    if(url.pathname==="/api/posts"&&request.method==="GET"){
      if(!env.DB)return json({error:"database_not_bound"},503,origin);
      const groupId=url.searchParams.get("groupId");
      if(groupId&&groupId.length>150)return json({error:"invalid_group"},400,origin);
      try {
        const stmt=groupId?env.DB.prepare("SELECT * FROM publication_posts WHERE group_id=? ORDER BY published_at DESC LIMIT 100").bind(groupId):
          env.DB.prepare("SELECT * FROM publication_posts ORDER BY first_seen_at DESC LIMIT 100");
        const {results}=await stmt.all();
        return json({posts:results,verifiedRevisionRule:"product_id can only be populated after explicit verification"},200,origin);
      }catch(e){return json({error:"database_not_initialized"},503,origin)}
    }
    if(url.pathname==="/api/refresh"&&request.method==="POST"){
      if(!authorize(request,env))return json({error:"unauthorized"},401,origin);
      if(!env.DB)return json({error:"database_not_bound"},503,origin);
      const body=await request.json().catch(()=>({}));
      const requested=Array.isArray(body.platforms)?body.platforms:PLATFORMS;
      if(!requested.length||requested.some(p=>!PLATFORMS.includes(p)))return json({error:"invalid_platforms"},400,origin);
      try{return json(await refresh(env,[...new Set(requested)]),200,origin)}
      catch(e){return json({error:"refresh_failed",detail:String(e.message||e)},503,origin)}
    }
    return json({error:"not_found"},404,origin);
  }
};
