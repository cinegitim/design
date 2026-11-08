import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {test} from 'node:test';

const root=path.resolve(import.meta.dirname,'../../..');
const base=path.join(root,'docs/visual-editor/browser');
const moduleSource=fs.readFileSync(path.join(base,'provenance.js'),'utf8');
const index=JSON.parse(fs.readFileSync(path.join(base,'provenance.json'),'utf8'));
const html=fs.readFileSync(path.join(base,'index.html'),'utf8');
const scope={};
vm.runInNewContext(moduleSource,scope);
const P=scope.BrandstudioProvenance;

class Element {
 constructor(tag='div'){this.tag=tag;this.children=[];this.textContent='';this.hidden=false;this.open=false;this.href='';this.target='';this.rel='';}
 append(...children){this.children.push(...children);}
 replaceChildren(...children){this.children=[...children];}
}
function nodes(){
 const credit=new Element('span'),events=new Element('ol'),disclosure=new Element('details');
 return {credit,events,disclosure,root:{querySelector(sel){return ({'#production-agent':credit,'#production-events':events,'#production-timeline':disclosure})[sel]}}};
}
const document={createElement:(tag)=>new Element(tag)};

test('historical KAIST V2 agent remains unrecorded while its actual GitHub PR is visible',()=>{
 const r=P.entry(index,'instagram-kaist-tech-track-2027-001-v2');
 assert.equal(r.executor,'unknown');
 assert.equal(r.agentVerified,false);
 assert.equal(r.events.length,1);
 assert.equal(r.events[0].proofUrl,'https://github.com/cinegitim/design/pull/190');
 assert.equal(r.events[0].stage,'github-merge');
});
test('unknown products and adjacent KAIST v1 do not inherit v2 author or timeline',()=>{
 for(const id of ['instagram-kaist-tech-track-2027-001','new-other-design']){
  const r=P.entry(index,id);
  assert.equal(r.executor,'unknown');
  assert.equal(r.events.length,0);
 }
});
test('chronology is ordered by actual observed UTC timestamp, never by input order',()=>{
 const record={schema_version:1,products:{'instagram-pilot-v2':{
  producer:{executor:'opencode',verification:'verified',host_evidence:'github:commit:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'},
  events:[
   {stage:'render',executor:'opencode',at:'2026-11-02T10:00:00Z',verification:'reported',proof:{kind:'pr',number:123}},
   {stage:'code',executor:'opencode',at:'2026-11-02T08:00:00Z',verification:'verified',proof:{kind:'pr',number:124}}
  ]
 }}};
 const result=P.entry(record,'instagram-pilot-v2');
 assert.deepEqual(Array.from(result.events,x=>x.stage),['code','render']);
});
test('untrusted proof URLs and malicious labels are not made into live HTML or links',()=>{
 const data={schema_version:1,products:{'instagram-pilot-v2':{
  producer:{executor:'unknown',verification:'unrecorded'},
  events:[{stage:'code',executor:'unknown',at:'2026-11-02T08:00:00Z',verification:'reported',proof:{kind:'url',url:'javascript:alert(1)'},note:'<img src=x onerror=alert(1)>'}]
 }}};
 const n=nodes();
 const r=P.entry(data,'instagram-pilot-v2');
 P.render(n.root,r,document);
 assert.equal(n.credit.textContent.includes('<img'),false);
 assert.equal(n.events.children.length,1);
 assert.equal(n.events.children[0].children.filter(c=>c.tag==='a').length,0);
 assert.equal(n.disclosure.open,false);
});
test('renderer updates existing version and resets disclosure on product change',()=>{
 const n=nodes();
 n.disclosure.open=true;
 P.render(n.root,P.entry(index,'instagram-kaist-tech-track-2027-001-v2'),document);
 assert.equal(n.disclosure.open,false);
 assert.equal(n.events.children.length,1);
 P.render(n.root,P.entry(index,'instagram-kaist-tech-track-2027-001'),document);
 assert.equal(n.events.children.length,1);
 assert.match(n.credit.textContent,/belgelenmedi/i);
});
test('footer is outside editable workspace and JS has no polling, innerHTML, or Cloudflare writer',()=>{
 assert.match(html,/<footer[^>]*id="production-credit"/);
 const footerAt=html.indexOf('id="production-credit"');
 const workspaceEnd=html.indexOf('id="context-menu"');
 assert.ok(footerAt>0 && footerAt<workspaceEnd);
 assert.match(html,/src="provenance\.js"/);
 assert.match(html,/fetch\('provenance\.json'/);
 assert.match(html,/BrandstudioProvenance\.entry\(provenanceIndex,selected\.id\)/);
 assert.doesNotMatch(moduleSource,/innerHTML|setInterval|fetch\(|XMLHttpRequest/);
});
