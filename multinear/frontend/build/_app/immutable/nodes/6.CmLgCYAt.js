import{a as v,t as _,b as o,h as Pt,d as ht,f as Ft,e as $t}from"../chunks/disclose-version.BjBLbfIf.js";import{i as kt}from"../chunks/legacy.b-VaXUeO.js";import{p as Et,t as n,a as Rt,c as e,r as t,s as a,f as at,o as It,l as Jt,b as Tt,g as r,d as A,m as rt,q as Dt}from"../chunks/index-client.BoCi2Vgn.js";import{p as jt,i as u}from"../chunks/props.Cy3ILhV4.js";import{a as yt,e as lt,i as ct}from"../chunks/index.DxvZjEHL.js";import{s as z}from"../chunks/class.CemJQFJe.js";import{a as At}from"../chunks/index.Dvh8W8ZQ.js";import{S as Lt}from"../chunks/StatusBadge.D8Nlu6NL.js";import{L as Ct}from"../chunks/Loading.Cp3YBOHz.js";import{E as Ht}from"../chunks/ErrorDisplay.B1ftezSC.js";import{f as Mt,i as qt}from"../chunks/intervalToDuration.BpIG60gY.js";var zt=_('<div><div class="text-2xl font-bold mb-1"><span> </span></div> <div>Tasks Passed</div> <div class="text-sm text-gray-500 mt-1"> </div></div>'),Bt=_('<div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-gray-300"></div> <span> </span></div>'),Gt=_('<div class="flex gap-1 h-2 rounded-full overflow-hidden bg-gray-100 w-full"><div class="bg-green-500"></div> <div class="bg-red-500"></div> <div class="bg-gray-300"></div></div> <div class="flex gap-6 text-sm mt-2"><div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-green-500"></div> <span> </span></div> <div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-red-500"></div> <span> </span></div> <!></div>',1),Kt=_('<div class="p-8 border-b"><div class="flex justify-between items-start mb-6"><div><h1 class="text-4xl font-bold mb-2"> </h1> <div class="text-gray-600"> </div></div> <!></div> <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6"><div><h3 class="text-sm font-medium text-gray-500">Project</h3> <p class="mt-1 text-lg"> </p></div> <div><h3 class="text-sm font-medium text-gray-500">Status</h3> <p class="mt-1"><!></p></div> <div><h3 class="text-sm font-medium text-gray-500">Created</h3> <p class="mt-1 text-lg"> </p></div> <div><h3 class="text-sm font-medium text-gray-500">Model</h3> <p class="mt-1 text-lg"> </p></div></div> <!></div>');function Qt(pt,B){Et(B,!1);let $=jt(B,"runDetails",8),i=jt(B,"taskStats",8);kt();var P=Kt(),D=e(P),F=e(D),I=e(F),dt=e(I);n(()=>o(dt,`Run Report: ${$().id.slice(-8)??""}`)),t(I);var G=a(I,2),K=e(G);n(()=>o(K,`Generated on ${new Date().toLocaleString()??""}`)),t(G),t(F);var _t=a(F,2);u(_t,i,d=>{var b=zt(),m=e(b),w=e(m),k=e(w);t(w),t(m);var H=a(m,2),E=a(H,2),R=e(E);n(()=>o(R,`Avg Score: ${(i().avgScore*100).toFixed(0)??""}%`)),t(E),t(b),n(()=>{z(b,`text-center px-6 py-4 rounded-lg ${i().failed===0?"bg-green-50 border-2 border-green-200":"bg-red-50 border-2 border-red-200"}`),z(w,i().failed===0?"text-green-600":"text-red-600"),o(k,`${i().completed??""}/${i().total??""}`),z(H,`text-sm ${i().failed===0?"text-green-600":"text-red-600"}`)}),v(d,b)}),t(D);var p=a(D,2),l=e(p),S=a(e(l),2),Q=e(S,!0);t(S),t(l);var C=a(l,2),it=a(e(C),2),U=e(it);Lt(U,{get status(){return $().status}}),t(it),t(C);var j=a(C,2),V=a(e(j),2),W=e(V,!0);n(()=>o(W,new Date($().date).toLocaleString())),t(V),t(j);var st=a(j,2),X=a(e(st),2),gt=e(X,!0);t(X),t(st),t(p);var ut=a(p,2);u(ut,i,d=>{var b=Gt(),m=at(b),w=e(m),k=a(w,2),H=a(k,2);t(m);var E=a(m,2),R=e(E),Y=a(e(R),2),mt=e(Y);t(Y),t(R);var M=a(R,2),Z=a(e(M),2),ft=e(Z);t(Z),t(M);var ot=a(M,2);u(ot,()=>i().inProgress>0,vt=>{var J=Bt(),tt=a(e(J),2),nt=e(tt);t(tt),t(J),n(()=>o(nt,`${i().inProgress??""} in progress`)),v(vt,J)}),t(E),n(()=>{yt(w,"style",`width: ${i().completed/i().total*100}%`),yt(k,"style",`width: ${i().failed/i().total*100}%`),yt(H,"style",`width: ${i().inProgress/i().total*100}%`),o(mt,`${i().completed??""} completed`),o(ft,`${i().failed??""} failed`)}),v(d,b)}),t(P),n(()=>{o(Q,$().project.name),o(gt,$().details.model||"N/A")}),v(pt,P),Rt()}var Ut=_(`<style>@media screen {
            body {
                background: white;
                margin: 0;
                padding: 0;
            }
        }
        @media print {
            @page {
                margin: 1.5cm;
                size: A4;
            }
            body {
                margin: 0;
                padding: 0;
                color: black;
                background: white;
                font-size: 11pt;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            .no-print {
                display: none !important;
            }
            /* Ensure backgrounds and colors are printed */
            * {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            /* Enhance borders for better print visibility */
            .border {
                border-width: 1.5px !important;
            }
            .border-b {
                border-bottom-width: 1.5px !important;
            }
            /* Enhance text contrast for print */
            .text-gray-500 {
                color: #4a5568 !important;
            }
            .text-gray-600 {
                color: #2d3748 !important;
            }
        }
        /* Hide header and footer */
        nav, footer, header {
            display: none !important;
        }</style>`),Vt=_('<div><span class="text-xs font-medium leading-none"> </span></div>'),Wt=_('<div><h4 class="text-sm font-semibold mb-2">Input</h4> <div class="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs"> </div></div>'),Xt=_('<div><h4 class="text-sm font-semibold mb-2">Output</h4> <div class="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs"> </div></div>'),Yt=_('<div><div class="text-sm font-medium text-gray-600 mb-1"> </div> <div class="bg-gray-50 p-3 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs"> </div></div>'),Zt=_('<div><h4 class="text-sm font-semibold mb-2">Details</h4> <div class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div></div>'),te=_('<div class="print:break-inside-avoid pt-4 first:pt-0"><div class="flex items-center gap-3"><div><span class="text-xs font-medium leading-none"> </span></div> <div class="text-sm font-medium flex-1"> </div></div> <div class="mt-1 text-sm text-gray-600"> </div></div>'),ee=_('<div><h4 class="text-sm font-semibold mb-3">Evaluation Results</h4> <div class="space-y-4 divide-y divide-gray-100"></div></div>'),re=_('<div><div class="text-sm font-medium text-gray-600 mb-1"> </div> <div class="bg-gray-50 p-3 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs"> </div></div>'),ae=_('<div><h4 class="text-sm font-semibold mb-2">Evaluation Details</h4> <div class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div></div>'),de=_('<div class="task-card mb-8 border rounded-lg overflow-hidden"><div><div><h3 class="text-lg font-bold"> </h3> <div class="text-sm text-gray-500 mt-1"> <!> <!></div></div> <div class="flex items-center gap-4"><!> <!></div></div> <div class="p-6"><div class="grid grid-cols-1 lg:grid-cols-2 gap-8"><div class="space-y-6"><!> <!> <!></div> <div class="space-y-6 lg:border-l lg:pl-8"><!> <!></div></div></div></div>'),ie=_('<!> <div class="p-8"><h2 class="text-2xl font-bold mb-6">Tasks</h2> <!></div> <div class="fixed bottom-4 right-4 no-print"><button class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded shadow">Print Report</button></div>',1),se=_('<div class="text-center text-gray-500 p-8">No run found</div>'),oe=_('<div class="min-h-screen bg-white"><!></div>');function be(pt,B){Et(B,!1);const $=rt();let i=rt(null),P=rt(!0),D=rt(null),F=rt(null);function I(){const p=window.location.hash.slice(1);if(p){const[l,S]=p.split("/");l&&S&&(A(F,S),dt(r(F)))}}It(()=>(I(),window.addEventListener("hashchange",I),()=>{window.removeEventListener("hashchange",I)}));async function dt(p){A(P,!0),A(D,null);try{A(i,await At(p))}catch(l){A(D,l instanceof Error?l.message:"Failed to load run details"),console.error(l)}finally{A(P,!1)}}function G(p){return p>=.9?"status-completed status-completed-border print:bg-green-50":p>0?"status-default status-default-border print:bg-yellow-50":"status-failed status-failed-border print:bg-red-50"}Jt(()=>r(i),()=>{var p;A($,(p=r(i))!=null&&p.tasks?{total:r(i).tasks.length,completed:r(i).tasks.filter(l=>l.status==="completed").length,failed:r(i).tasks.filter(l=>l.status==="failed").length,inProgress:r(i).tasks.filter(l=>!["completed","failed"].includes(l.status)).length,avgScore:r(i).tasks.reduce((l,S)=>l+(S.eval_score||0),0)/r(i).tasks.length}:null)}),Tt(),kt();var K=oe();Pt(p=>{var l=Ut();v(p,l)});var _t=e(K);u(_t,()=>r(P),p=>{Ct(p,{message:"Loading run details..."})},p=>{var l=ht(),S=at(l);u(S,()=>r(D),Q=>{Ht(Q,{get errorMessage(){return r(D)},onRetry:()=>dt(r(F))})},Q=>{var C=ht(),it=at(C);u(it,()=>r(i),U=>{var j=ie(),V=at(j);Qt(V,{get runDetails(){return r(i)},get taskStats(){return r($)}});var W=a(V,2),st=a(e(W),2);lt(st,1,()=>r(i).tasks,ct,(ut,d)=>{var b=de(),m=e(b),w=e(m),k=e(w),H=e(k);n(()=>o(H,`Task ${r(d).id.slice(-8)??""}`)),t(k);var E=a(k,2),R=e(E);n(()=>o(R,`${new Date(r(d).created_at).toLocaleString()??""} `));var Y=a(R);u(Y,()=>r(d).finished_at,c=>{var s=$t();n(()=>o(s,`· ${Mt(qt({start:new Date(r(d).created_at),end:new Date(r(d).finished_at)}),{format:["minutes","seconds"]})??""}`)),v(c,s)});var mt=a(Y,2);u(mt,()=>{var c;return(c=r(d).task_details)==null?void 0:c.model},c=>{var s=$t();n(()=>o(s,`· ${r(d).task_details.model??""}`)),v(c,s)}),t(E),t(w);var M=a(w,2),Z=e(M);Lt(Z,{get status(){return r(d).status},className:"px-3 py-1"});var ft=a(Z,2);u(ft,()=>r(d).eval_score!==null,c=>{var s=Vt();const g=Dt(()=>`flex-none flex items-center justify-center w-9 h-9 rounded-full border
                                    ${G(r(d).eval_score)??""}`);var f=e(s),x=e(f);n(()=>o(x,`${(r(d).eval_score*100).toFixed(0)??""}%`)),t(f),t(s),n(()=>z(s,r(g))),v(c,s)}),t(M),t(m);var ot=a(m,2),vt=e(ot),J=e(vt),tt=e(J);u(tt,()=>r(d).task_input,c=>{var s=Wt(),g=a(e(s),2),f=e(g,!0);n(()=>o(f,typeof r(d).task_input=="object"&&"str"in r(d).task_input?r(d).task_input.str:JSON.stringify(r(d).task_input,null,2))),t(g),t(s),v(c,s)});var nt=a(tt,2);u(nt,()=>r(d).task_output,c=>{var s=Xt(),g=a(e(s),2),f=e(g,!0);n(()=>o(f,typeof r(d).task_output=="object"&&"str"in r(d).task_output?r(d).task_output.str:JSON.stringify(r(d).task_output,null,2))),t(g),t(s),v(c,s)});var Nt=a(nt,2);u(Nt,()=>r(d).task_details,c=>{var s=Zt(),g=a(e(s),2);lt(g,5,()=>Object.entries(r(d).task_details),ct,(f,x)=>{let L=()=>r(x)[0],h=()=>r(x)[1];var y=Yt(),T=e(y),q=e(T,!0);t(T);var N=a(T,2),O=e(N,!0);n(()=>o(O,typeof h()=="string"?h():JSON.stringify(h(),null,2))),t(N),t(y),n(()=>o(q,L())),v(f,y)}),t(g),t(s),v(c,s)}),t(J);var wt=a(J,2),St=e(wt);u(St,()=>{var c;return(c=r(d).eval_details)==null?void 0:c.evaluations},c=>{var s=ee(),g=a(e(s),2);lt(g,5,()=>r(d).eval_details.evaluations,ct,(f,x)=>{var L=te(),h=e(L),y=e(h);const T=Dt(()=>`flex-none flex items-center justify-center w-9 h-9 rounded-full border
                                                            ${G(r(x).score)??""}`);var q=e(y),N=e(q);n(()=>o(N,`${(r(x).score*100).toFixed(0)??""}%`)),t(q),t(y);var O=a(y,2),xt=e(O,!0);t(O),t(h);var et=a(h,2),bt=e(et,!0);t(et),t(L),n(()=>{z(y,r(T)),o(xt,r(x).criterion),o(bt,r(x).rationale)}),v(f,L)}),t(g),t(s),v(c,s)});var Ot=a(St,2);u(Ot,()=>r(d).eval_details,c=>{var s=ae(),g=a(e(s),2);lt(g,5,()=>Object.entries(r(d).eval_details),ct,(f,x)=>{let L=()=>r(x)[0],h=()=>r(x)[1];var y=ht(),T=at(y);u(T,()=>L()!=="evaluations",q=>{var N=re(),O=e(N),xt=e(O,!0);t(O);var et=a(O,2),bt=e(et,!0);n(()=>o(bt,typeof h()=="string"?h():JSON.stringify(h(),null,2))),t(et),t(N),n(()=>o(xt,L())),v(q,N)}),v(f,y)}),t(g),t(s),v(c,s)}),t(wt),t(vt),t(ot),t(b),n(()=>z(m,`p-4 flex justify-between items-center
                        ${r(d).status==="completed"?"bg-green-50 border-b-2 border-green-200 print:border-green-300":r(d).status==="failed"?"bg-red-50 border-b-2 border-red-200 print:border-red-300":"bg-gray-50 border-b-2 border-gray-200 print:border-gray-300"}`)),v(ut,b)}),t(W);var X=a(W,2),gt=e(X);t(X),Ft("click",gt,()=>window.print()),v(U,j)},U=>{var j=se();v(U,j)},!0),v(Q,C)},!0),v(p,l)}),t(K),v(pt,K),Rt()}export{be as component};
