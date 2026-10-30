import test from "node:test";
import assert from "node:assert/strict";
import worker from "./worker.mjs";
import {webcrypto} from "node:crypto";
const originalFetch=globalThis.fetch;
if(!globalThis.crypto)globalThis.crypto=webcrypto;
const group={id:"instagram-utokyo-design-2027-001",brand:"asyada-egitim",
 title:"Tokyo Üniversitesi · Yeni Tasarım Okulu 2027",publicationAnchors:["UTokyo College of Design"]};
const release={
 facebook:"https://www.facebook.com/122117876091502048/posts/122117876079502048",
 linkedin:"https://www.linkedin.com/feed/update/urn:li:share:7521972429041168384",
 x:"https://x.com/asyadaegitim/status/1234567890"
};
const posts=[
 {id:"fb1",state:"PUBLISHED",releaseURL:release.facebook,publishDate:"2026-10-30T16:31:00Z",content:"<p>UTokyo College of Design başvuruları başladı</p>",channel:{id:"cmvuxyj5q006itb9fkk72abu1",platform:"facebook"}},
 {id:"li1",state:"PUBLISHED",releaseURL:release.linkedin,publishDate:"2026-10-30T16:31:00Z",content:"<p>UTokyo College of Design applications</p>",channel:{id:"cmvutsyvy0bu7ny9q2x71gl4c",platform:"linkedin-page"}},
 {id:"x1",state:"PUBLISHED",releaseURL:release.x,publishDate:"2026-10-30T16:31:00Z",content:"UTokyo College of Design",channel:{id:"cmvuy1soj006ktb9fwpia7wga",platform:"x"}},
 {id:"fake",state:"PUBLISHED",releaseURL:release.facebook,publishDate:"2026-10-30T16:31:00Z",content:"UTokyo College of Design",channel:{id:"OTHER_ORGANIZATION",platform:"facebook"}},
 {id:"draft",state:"DRAFT",releaseURL:release.facebook,publishDate:"2026-10-30T16:31:00Z",content:"UTokyo College of Design",channel:{id:"cmvuxyj5q006itb9fkk72abu1",platform:"facebook"}},
 {id:"error",state:"PUBLISHED",releaseURL:"https://bad.example/posts/a",publishDate:"2026-10-30T16:31:00Z",content:"UTokyo College of Design",channel:{id:"cmvuxyj5q006itb9fkk72abu1",platform:"facebook"}}
];
function fakeDB(){
 const writes=[];
 return {
  writes,
  prepare(sql){
   return {
    bind(...values){
     return {run:async()=>{if(sql.includes("publication_posts"))writes.push(values);return {success:true}}};
    }
   };
  }
 };
}
test("one Voholabs API request imports only explicitly selected connected channels with real published links",async()=>{
 const db=fakeDB(),calls=[];
 globalThis.fetch=async(url,options)=>{
  calls.push({url:String(url),headers:options?.headers||{}});
  if(String(url).includes("product-groups.json"))return Response.json({groups:[group]});
  if(String(url).includes("studio.voholabs.com/api/public/v1/posts"))return Response.json({posts});
  throw Error("Unexpected network request: "+String(url));
 };
 try{
  const request=new Request("https://brandstudio-publications.test/api/refresh",{
   method:"POST",headers:{"Authorization":"Bearer test-admin-secret"},
   body:JSON.stringify({platforms:["facebook","linkedin","x"]})
  });
  const env={DB:db,VOHOLABS_API_KEY:"test-provider-secret",BRANDSTUDIO_PUBLICATION_BRIDGE_TOKEN:"test-admin-secret"};
  const response=await worker.fetch(request,env);
  const data=await response.json();
  assert.equal(response.status,200);
  for(const p of ["facebook","linkedin","x"]){assert.equal(data.platforms[p].saved,1);assert.equal(data.platforms[p].source,"voholabs_api")}
  assert.equal(db.writes.length,3);
  assert.ok(db.writes.every(x=>x[7]==="family_verified" && x[5]===group.id));
  assert.equal(calls.filter(x=>x.url.includes("studio.voholabs.com")).length,1);
  assert.equal(calls.some(x=>x.url.includes("graph.facebook.com")),false);
  assert.equal(calls.find(x=>x.url.includes("studio.voholabs.com")).headers.Authorization,"test-provider-secret");
 }finally{globalThis.fetch=originalFetch}
});
test("without a Voholabs key the source is disabled and no request is made",async()=>{
 let requests=0;globalThis.fetch=()=>{requests++;throw Error("must not fetch")};
 try{
  const env={DB:fakeDB()};
  const response=await worker.fetch(new Request("https://brandstudio-publications.test/api/status"),env);
  const data=await response.json();
  assert.equal(data.platforms.facebook.configured,false);
  assert.equal(data.platforms.linkedin.configured,false);
  assert.equal(data.platforms.x.configured,false);
  assert.equal(requests,0);
 }finally{globalThis.fetch=originalFetch}
});

test("the X-only check reads Buffer sent posts and rejects other channels",async()=>{
 const db=fakeDB(),calls=[];
 globalThis.fetch=async(url,options)=>{
  calls.push(String(url));
  if(String(url).includes("product-groups.json"))return Response.json({groups:[{
   ...group,publicationAnchors:["Tokyo Üniversitesi’nin yeni tasarım okulu"]
  }]});
  if(String(url)==="https://api.buffer.com")return Response.json({data:{posts:{edges:[
   {node:{id:"buffer-1",status:"sent",channelId:"6ae497ec2f1f5ed6481ff706",text:"Tokyo Üniversitesi’nin yeni tasarım okulu Eylül 2027’de açılıyor!",externalLink:"https://x.com/2108217886128910336/status/2116206749296230468",sentAt:"2026-10-30T16:33:01Z"}},
   {node:{id:"wrong-channel",status:"sent",channelId:"OTHER",text:"Tokyo Üniversitesi’nin yeni tasarım okulu",externalLink:"https://x.com/other/status/123",sentAt:"2026-10-30T16:33:01Z"}},
   {node:{id:"fake-url",status:"sent",channelId:"6ae497ec2f1f5ed6481ff706",text:"Tokyo Üniversitesi’nin yeni tasarım okulu",externalLink:"https://evil.example/status/123",sentAt:"2026-10-30T16:33:01Z"}}
  ]}}});
  throw Error("Unexpected fetch: "+url);
 };
 try{
  const env={DB:db,BUFFER_API_KEY:"test-buffer-token",BRANDSTUDIO_PUBLICATION_BRIDGE_TOKEN:"test-admin-secret"};
  const req=new Request("https://brandstudio-publications.test/api/refresh",{
   method:"POST",headers:{"Authorization":"Bearer test-admin-secret"},body:JSON.stringify({platforms:["x"]})
  });
  const res=await worker.fetch(req,env);
  const result=await res.json();
  assert.equal(res.status,200);
  assert.equal(result.platforms.x.fetched,1);
  assert.equal(result.platforms.x.saved,1);
  assert.equal(result.platforms.x.source,"buffer_api");
  assert.equal(db.writes.length,1);
  assert.equal(db.writes[0][7],"family_verified");
  assert.equal(calls.filter(u=>u==="https://api.buffer.com").length,1);
  assert.equal(calls.some(u=>u.includes("voholabs.com")),false);
 }finally{globalThis.fetch=originalFetch}
});
