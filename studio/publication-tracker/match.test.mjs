import test from "node:test";
import assert from "node:assert/strict";
import {normalizeText,validPermalink,suggestFamily} from "./match.mjs";
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
