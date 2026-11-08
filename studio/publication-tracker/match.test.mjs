import test from "node:test";
import assert from "node:assert/strict";
import {normalizeText,validPermalink,suggestFamily,exactCaptionFamily} from "./match.mjs";
const groups=[
 {id:"instagram-tsinghua-atlas-2027",brand:"asyada-egitim",title:"Tsinghua Atlas 2027",versions:[{id:"tsinghua-v1"},{id:"tsinghua-v2"}]},
 {id:"instagram-rotani-sec-tokyo-seoul-001",brand:"asyada-egitim",title:"Rotanı Seç · Tokyo mu, Seul mü?",versions:[{id:"tokyo-v3"}]},
 {id:"instagram-test-other",brand:"cin-egitim",title:"Tsinghua Atlas 2027"}
];
test("Turkish and combining characters normalize consistently",()=>{
 assert.equal(normalizeText("İstanbul'ın ÇİN'İ"),"istanbul in cin i");
});
test("clear family wording never establishes a specific revision",()=>{
 const x=suggestFamily({caption:"Tsinghua Atlas 2027: Apply now. An introduction to Tsinghua."},groups);
 assert.equal(x.groupId,"instagram-tsinghua-atlas-2027");
 assert.equal(x.productId,null);
 assert.equal(x.status,"family_candidate");
});
test("insufficient source content is left for human review",()=>{
 const x=suggestFamily({caption:"New opportunities in Asia!"},groups);
 assert.equal(x.groupId,null);assert.equal(x.status,"needs_review");
});
test("URL validation rejects unrelated hosts and arbitrary links",()=>{
 assert.equal(validPermalink("x","https://x.com/asyadaegitim/status/123456789"),true);
 assert.equal(validPermalink("x","https://evil.example/status/123456789"),false);
 assert.equal(validPermalink("instagram","https://www.instagram.com/p/DePgrvQDdeB/"),true);
 assert.equal(validPermalink("instagram","javascript:alert(1)"),false);
 assert.equal(validPermalink("linkedin","https://www.linkedin.com/feed/update/urn:li:share:123456/"),true);
});

test("unique declared caption anchor establishes only the family",()=>{
 const gs=[...groups,{id:"instagram-ieft",title:"IEFT Sonrası · Fırsatlar Bitmedi",brand:"asyada-egitim",publicationAnchors:["IEFT bitti. Eğitim fırsatları bitmedi!"]}];
 const p={platform:"instagram",caption:"IEFT bitti. Eğitim fırsatları bitmedi! Daha fazla fırsat için yazın."};
 assert.equal(exactCaptionFamily(p,gs),"instagram-ieft");
 assert.deepEqual(Object.fromEntries(Object.entries(suggestFamily(p,gs)).filter(([k])=>["groupId","productId","status"].includes(k))),{groupId:"instagram-ieft",productId:null,status:"family_verified"});
});
test("a generic or ambiguous anchor cannot auto-publish",()=>{
 const gs=[{id:"instagram-a",title:"Birinci",brand:"asyada-egitim",publicationAnchors:["Çok özel bir üniversite fırsatı"]},{id:"instagram-b",title:"İkinci",brand:"asyada-egitim",publicationAnchors:["Çok özel bir üniversite fırsatı"]}];
 assert.equal(exactCaptionFamily({platform:"instagram",caption:"Çok özel bir üniversite fırsatı"},gs),null);
 assert.equal(suggestFamily({caption:"Yeni fırsatlar"},gs).status,"needs_review");
});
test("recognized platform records can use unique anchors, unknown platforms cannot",()=>{
 assert.equal(exactCaptionFamily({platform:"facebook",caption:"IEFT bitti. Eğitim fırsatları bitmedi!"},[{id:"instagram-ieft",brand:"asyada-egitim",publicationAnchors:["IEFT bitti. Eğitim fırsatları bitmedi!"]}]),"instagram-ieft");
 assert.equal(exactCaptionFamily({platform:"evil",caption:"IEFT bitti. Eğitim fırsatları bitmedi!"},[{id:"instagram-ieft",brand:"asyada-egitim",publicationAnchors:["IEFT bitti. Eğitim fırsatları bitmedi!"]}]),null);
});

test("short unique editorial anchor is valid while short generic title alone is not",()=>{
 const gs=[{id:"instagram-tokyo-seoul",brand:"asyada-egitim",title:"Tokyo ve Seul",publicationAnchors:["Tokyo mu, Seul mu?"]}];
 assert.equal(exactCaptionFamily({platform:"instagram",caption:"Tokyo mu, Seul mu? Şehri seç, nedenini yaz."},gs),"instagram-tokyo-seoul");
 assert.equal(exactCaptionFamily({platform:"instagram",caption:"Tokyo ve Seul"},[{id:"instagram-tokyo-seoul",brand:"asyada-egitim",title:"Tokyo ve Seul"}]),null);
});
