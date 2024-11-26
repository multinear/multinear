import{a as j,n as N,d as F}from"./disclose-version.DJKRdGjo.js";import{i as W}from"./legacy.RfLVu9Ez.js";import{p as P,t as b,a as R,c as z,f as A,s as I,r as B,g as $,N as G}from"./index-client.CTjIiTiR.js";import{e as O,d as U,k as D,i as J,f as x}from"./projects.B4n7Uloc.js";import{l as v,p as a}from"./props.hsVcazBB.js";/**
 * @license lucide-svelte v0.456.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const L={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor","stroke-width":2,"stroke-linecap":"round","stroke-linejoin":"round"};var M=N("<svg><!><!></svg>");function Y(e,t){const s=v(t,["children","$$slots","$$events","$$legacy"]),o=v(s,["name","color","size","strokeWidth","absoluteStrokeWidth","iconNode"]);P(t,!1);let n=a(t,"name",8,void 0),T=a(t,"color",8,"currentColor"),l=a(t,"size",8,24),m=a(t,"strokeWidth",8,2),_=a(t,"absoluteStrokeWidth",8,!1),y=a(t,"iconNode",24,()=>[]);const E=(...u)=>u.filter((i,d,f)=>!!i&&f.indexOf(i)===d).join(" ");W();var c=M();let p;var w=z(c);O(w,1,y,J,(u,i)=>{let d=()=>$(i)[0],f=()=>$(i)[1];var k=F(),C=A(k);D(C,d,!0,(h,V)=>{let g;b(()=>g=x(h,g,{...f()},void 0,h.namespaceURI===G,h.nodeName.includes("-")))}),j(u,k)});var S=I(w);U(S,t,"default",{},null),B(c),b(()=>p=x(c,p,{...L,...o,width:l(),height:l(),stroke:T(),"stroke-width":_()?Number(m())*24/Number(l()):m(),class:E("lucide-icon","lucide",n()?`lucide-${n()}`:"",s.class)},void 0,!0)),j(e,c),R()}const r="http://localhost:8000/api";async function Z(){const e=await fetch(`${r}/projects`);if(!e.ok)throw new Error(`Failed to fetch projects: ${e.statusText}`);return e.json()}async function tt(e){const t=await fetch(`${r}/jobs/${e}`,{method:"POST",headers:{"Content-Type":"application/json"}});if(!t.ok)throw new Error(`Failed to start experiment: ${t.statusText}`);return t.json()}async function et(e,t){const s=await fetch(`${r}/jobs/${e}/${t}/status`,{method:"GET",headers:{"Content-Type":"application/json"}});if(!s.ok)throw new Error(`Failed to fetch job status: ${s.statusText}`);return s.json()}async function st(e,t=5,s=0){const o=await fetch(`${r}/runs/${e}?limit=${t}&offset=${s}`,{headers:{"Content-Type":"application/json"}});if(!o.ok)throw new Error(`Failed to fetch recent runs: ${o.statusText}`);return o.json()}async function ot(e){const t=await fetch(`${r}/run-details/${e}`);if(!t.ok)throw new Error(`Failed to fetch run details: ${t.statusText}`);return t.json()}async function nt(e,t,s=10,o=0){const n=await fetch(`${r}/same-tasks/${e}/${t}?limit=${s}&offset=${o}`);if(!n.ok)throw new Error(`Failed to fetch same tasks: ${n.statusText}`);return n.json()}export{Y as I,ot as a,Z as b,et as c,nt as d,st as g,tt as s};