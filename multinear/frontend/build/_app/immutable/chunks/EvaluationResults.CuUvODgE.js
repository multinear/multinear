import{a as w,t as k,b as F}from"./disclose-version.DitXKBiM.js";import{i as G}from"./legacy.DmYQQF0A.js";import{p as H,l as I,b as J,c as s,t as S,r as t,s as R,a as K,d as N,q as M,g as i,m as O,u as T}from"./index-client.IJhfC0Az.js";import{e as A,i as B}from"./index.DJ6cfu9r.js";import{s as z}from"./class.CFHkN7I5.js";import{p as f,i as Q}from"./props.C-C6UnW2.js";function D(a,e=!1){const u=e?" print:bg-green-50":"";return a>=1?{color:`status-completed status-completed-border${u}`,border:"status-completed-border",text:"text-green-600"}:a>=.5?{color:`status-default status-default-border${e?" print:bg-yellow-50":""}`,border:"status-default-border",text:"text-yellow-500"}:{color:`status-failed status-failed-border${e?" print:bg-red-50":""}`,border:"status-failed-border",text:"text-red-600"}}function se(a,e=500){return a.length<=e?a:a.slice(0,e)+"..."}var U=k('<div class="mt-1 -mr-2.5"><span> </span></div>'),V=k('<div class="flex flex-col" style="min-height: 40px"><div class="h-9"><div><span class="text-xs font-medium leading-none"> </span></div></div> <!></div>');function W(a,e){H(e,!1);const u=O();let l=f(e,"score",8),n=f(e,"minScore",8,void 0),y=f(e,"includePrintStyles",8,!1),x=f(e,"showMinScore",8,!0);I(()=>(M(n()),M(l())),()=>{N(u,n()?l()/n():l())}),J(),G();var b=V(),m=s(b),r=s(m);const d=T(()=>`flex-none flex items-center justify-center w-9 h-9 rounded-full border
            ${D(i(u),y()).color??""}`);var o=s(r),p=s(o);S(()=>F(p,`${(l()*100).toFixed(0)??""}%`)),t(o),t(r),t(m);var c=R(m,2);Q(c,()=>n()&&x(),v=>{var h=U(),_=s(h);const P=T(()=>`text-[10px] font-medium ${D(l(),y()).text??""}`);var C=s(_);S(()=>F(C,`min: ${(n()*100).toFixed(0)??""}%`)),t(_),t(h),S(()=>z(_,i(P))),w(v,h)}),t(b),S(()=>z(r,i(d))),w(a,b),K()}var X=k("<div> </div>"),Y=k('<div><div class="flex gap-3 items-start"><div class="flex-none pt-[2px]"><!></div> <div></div></div> <div class="mt-1 text-sm text-gray-600"> </div></div>'),Z=k('<div class="space-y-5 divide-y divide-gray-100"></div>');function ae(a,e){H(e,!1);const u=O();let l=f(e,"evaluations",8),n=f(e,"evalSpec",8),y=f(e,"includePrintStyles",8,!1),x=f(e,"filter",8,"");function b(r){var o,p,c;const d=(c=(p=(o=n())==null?void 0:o.checklist)==null?void 0:p.find(v=>typeof v=="object"&&v.text===r.criterion))==null?void 0:c.min_score;return d?r.score>=d:r.score>=1}I(()=>(M(l()),M(x())),()=>{N(u,l().filter(r=>x()===""||x()==="passed"&&b(r)||x()==="failed"&&!b(r)))}),J(),G();var m=Z();A(m,5,()=>i(u),B,(r,d)=>{var o=Y();const p=T(()=>{var j,E,g;return(g=(E=(j=n())==null?void 0:j.checklist)==null?void 0:E.find(q=>typeof q=="object"&&q.text===i(d).criterion))==null?void 0:g.min_score});var c=s(o),v=s(c),h=s(v);W(h,{get score(){return i(d).score},get minScore(){return i(p)},get includePrintStyles(){return y()}}),t(v);var _=R(v,2);A(_,5,()=>i(d).criterion.replace(/\\n/g,`
`).replace(/\\(\s{1,2})\\ /g," ").split(`
`),B,(j,E)=>{var g=X(),q=s(g,!0);t(g),S(()=>F(q,i(E))),w(j,g)}),t(_),t(c);var P=R(c,2),C=s(P,!0);t(P),t(o),S(()=>{z(o,`pt-4 first:pt-0 ${(y()?"print:break-inside-avoid":"")??""}`),z(_,`text-sm font-medium flex-1 ${(i(p)?"pb-7":"pb-1")??""}`),F(C,i(d).rationale)}),w(r,o)}),t(m),w(a,m),K()}export{ae as E,W as S,se as t};
