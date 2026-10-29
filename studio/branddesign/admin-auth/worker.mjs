// Branddesign trusted-device sessions. Private Durable Object; no public Worker routes.
// Stores only SHA-256 hashes of cryptographically random session tokens.
const DAY=86400000, YEAR=365*DAY, RENEW=30*DAY, LOCK=15*60000;
const json=(body,status=200)=>new Response(JSON.stringify(body),{status,headers:{"content-type":"application/json","cache-control":"no-store"}});
export class BrandstudioAuthObject {
 constructor(ctx){this.ctx=ctx}
 async fetch(request){
  if(request.method!=="POST")return json({error:"method"},405);
  let input;try{input=await request.json()}catch{return json({error:"payload"},400)}
  const now=Date.now(),id=String(input.id||"");
  const action=input.action;
  if(action==="attempt"){
   const key="attempt:"+id;
   if(!/^[0-9a-f]{64}$/.test(id))return json({ok:false},400);
   const state=await this.ctx.storage.get(key)||{count:0,until:0};
   if(state.until<=now){state.count=0;state.until=now+LOCK}
   if(input.op==="probe")return json({ok:state.count<6,retryAfter:Math.max(0,state.until-now)});
   if(input.op==="failed"){state.count+=1;await this.ctx.storage.put(key,state);return json({ok:state.count<6,retryAfter:Math.max(0,state.until-now)})}
   if(input.op==="success"){await this.ctx.storage.delete(key);return json({ok:true})}
   return json({ok:false},400)
  }
  if(action==="challenge"||action==="consume"){
   if(!/^[0-9a-f]{64}$/.test(id))return json({ok:false},400);
   const key="challenge:"+id;
   if(action==="challenge"){
    const nonce=Array.from(crypto.getRandomValues(new Uint8Array(32)),b=>b.toString(16).padStart(2,"0")).join("");
    await this.ctx.storage.put(key,{nonce,expiresAt:now+120000});
    return json({ok:true,challenge:nonce})
   }
   const record=await this.ctx.storage.get(key);
   if(record)await this.ctx.storage.delete(key);
   if(!record||record.expiresAt<now||record.nonce!==input.challenge)return json({ok:false});
   return json({ok:true})
  }
  if(!/^[0-9a-f]{64}$/.test(id))return json({ok:false},400);
  const key="session:"+id;
  if(action==="issue"){
   // The token never enters storage; the session hash is its only identifier.
   await this.ctx.storage.put(key,{createdAt:now,expiresAt:now+YEAR});
   return json({ok:true,expiresAt:now+YEAR})
  }
  if(action==="check"){
   const old=await this.ctx.storage.get(key);
   if(!old)return json({ok:false});
   if(old.expiresAt<=now){await this.ctx.storage.delete(key);return json({ok:false})}
   if(old.expiresAt-now<RENEW){
    const next={...old,expiresAt:now+YEAR};
    await this.ctx.storage.put(key,next);
    return json({ok:true,renewed:true,expiresAt:next.expiresAt})
   }
   return json({ok:true,expiresAt:old.expiresAt})
  }
  if(action==="revoke"){await this.ctx.storage.delete(key);return json({ok:true})}
  return json({error:"action"},400)
 }
}
export default {fetch(){return new Response("Not Found",{status:404})}};
