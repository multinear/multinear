import{s as W,e as Y,a as u,t as j,b as J,c as y,d as K}from"../chunks/disclose-version.BjBLbfIf.js";import{L as Q,R as V,O as X,e as Z,aj as ee,h as ae,Y as te,p as B,l as se,b as re,c as t,g as $,n as w,t as A,r as s,a as F,d as oe,u as ne,q as le,m as ce,f as S,o as ie,s as _,A as pe}from"../chunks/index-client.BoCi2Vgn.js";import{B as C,a as T,s as de,e as ve,i as fe}from"../chunks/index.DxvZjEHL.js";import{i as he}from"../chunks/legacy.b-VaXUeO.js";import{p as E,l as ue,s as ge}from"../chunks/props.Cy3ILhV4.js";import{p as z}from"../chunks/stores.BfidqmOg.js";import{I as me,d as _e}from"../chunks/index.Dvh8W8ZQ.js";import{d as M,a as R,b as $e,p as be,c as xe,e as ye}from"../chunks/projects.C_-bKb6m.js";import{a as we}from"../chunks/entry.C16cB7Ci.js";function je(f,r,...c){var i=f,e=Z,a;Q(()=>{e!==(e=r())&&(a&&(ee(a),a=null),a=X(()=>e(i,...c)))},V),ae&&(i=te)}const Pe=!0,ke="always",qe=Object.freeze(Object.defineProperty({__proto__:null,prerender:Pe,trailingSlash:ke},Symbol.toStringTag,{value:"Module"})),Ce=""+new URL("../assets/logo.o9F5wtRW.png",import.meta.url).href;var Ie=j('<a class="block"><!></a>');function He(f,r){B(r,!1);const c=W(),i=()=>y(z,"$page",c),e=ce();let a=E(r,"href",8),h=E(r,"label",8);function g(p,d){return p===d||p.split("#")[0].startsWith(`${d}`)||`${p.split("#")[0]}/`.startsWith(`${d}`)||p==="/"&&d.startsWith("/dashboard")}se(()=>(ne(a()),i()),()=>{oe(e,g(a(),i().url.pathname))}),re(),he();var v=Ie(),m=t(v),b=le(()=>`hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full ${($(e)?"active-nav":"")??""}`);C(m,{variant:"ghost",get class(){return $(b)},children:(p,d)=>{w();var x=Y();A(()=>J(x,h())),u(p,x)},$$slots:{default:!0}}),s(v),A(()=>T(v,"href",a())),u(f,v),F()}function Le(f,r){const c=ue(r,["children","$$slots","$$events","$$legacy"]);me(f,ge({name:"book"},()=>c,{iconNode:[["path",{d:"M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"}]],children:(e,a)=>{var h=K(),g=S(h);de(g,r,"default",{},null),u(e,h)},$$slots:{default:!0}}))}var Ne=j("<!> <span>Documentation</span>",1),Ae=j('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-6 w-6"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.11.82-.26.82-.577v-2.17c-3.338.726-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.73.083-.73 1.205.084 1.84 1.237 1.84 1.237 1.07 1.835 2.807 1.305 3.492.997.108-.775.42-1.305.763-1.605-2.665-.3-5.467-1.332-5.467-5.93 0-1.31.467-2.38 1.235-3.22-.123-.303-.535-1.523.117-3.176 0 0 1.007-.322 3.3 1.23.957-.266 1.983-.398 3.003-.403 1.02.005 2.046.137 3.003.403 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.24 2.873.118 3.176.77.84 1.233 1.91 1.233 3.22 0 4.61-2.807 5.625-5.48 5.92.43.37.823 1.102.823 2.222v3.293c0 .32.22.694.825.576C20.565 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z"></path></svg> <span>GitHub</span>',1),Ee=j('<div class="min-h-screen flex flex-col"><nav class="bg-gray-800 p-4"><div class="container mx-auto flex justify-between items-center"><div class="flex items-center"><a href="/" class="flex items-center"><img alt="Logo" class="h-8 w-10 mr-4"> <div class="text-lg text-white font-bold pr-8">Multinear</div></a> <!></div></div></nav> <main class="flex-1 flex"><!></main> <footer class="bg-gray-800 p-4"><div class="container mx-auto flex justify-between items-center text-gray-300"><div><a href="https://multinear.com" target="_blank" rel="noopener noreferrer">&copy; 2025 Multinear.</a></div> <div class="flex items-center"><a href="https://multinear.com" target="_blank" rel="noopener noreferrer"><!></a> <a href="https://github.com/multinear" target="_blank" rel="noopener noreferrer"><!></a></div></div></footer></div>');function De(f,r){B(r,!0);const c=W(),i=()=>y(z,"$page",c),e=()=>y(xe,"$selectedProjectId",c),a=()=>y(ye,"$selectedChallengeId",c),h=[{href:"/",label:"Home"}],g=pe(()=>{const o=i().url.pathname;let l=[...h];return e()&&l.push({href:`/experiments#${e()}`,label:"Experiments"}),o.startsWith("/run")&&l.push({href:o+i().url.hash,label:"Run"}),(o.startsWith("/compare")||a())&&l.push({href:`/compare#${e()}/c:${a()}`,label:"Compare"}),l});ie(()=>{const{cleanup:o}=M();return we(()=>{M()}),(async()=>{try{const n=await _e();if(!n){R.set("Invalid response from server");return}$e.set(n)}catch(n){R.set(n instanceof Error?n.message:"Failed to load projects"),console.error(n)}finally{be.set(!1)}})(),()=>{o()}});var v=Ee(),m=t(v),b=t(m),p=t(b),d=t(p),x=t(d);T(x,"src",Ce),w(2),s(d);var O=_(d,2);ve(O,17,()=>$(g),fe,(o,l)=>{He(o,{get href(){return $(l).href},get label(){return $(l).label}})}),s(p),s(b),s(m);var P=_(m,2),q=t(P);je(q,()=>r.children),s(P);var I=_(P,2),H=t(I),L=_(t(H),2),k=t(L),D=t(k);C(D,{variant:"ghost",class:"hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full flex items-center space-x-2",children:(o,l)=>{var n=Ne(),U=S(n);Le(U,{class:"h-6 w-6"}),w(2),u(o,n)},$$slots:{default:!0}}),s(k);var N=_(k,2),G=t(N);C(G,{variant:"ghost",class:"hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full flex items-center space-x-2",children:(o,l)=>{var n=Ae();w(2),u(o,n)},$$slots:{default:!0}}),s(N),s(L),s(H),s(I),s(v),u(f,v),F()}export{De as component,qe as universal};
