import{w as s}from"./index.CZPF9jM2.js";const g=s([]),w=s(!0),I=s(null),d=s(""),i=s(""),l=s(""),p=s("");function n(){const t=window.location.hash,a=t?t.slice(1).split("/"):[],c=a[0]||"";d.set(c);const e=a[1]||"",o=e.startsWith("r:")?e.slice(2):"",r=e.startsWith("c:")?e.slice(2):"",h=e.startsWith("search:")?e.slice(7):"";return i.set(o),l.set(r),p.set(h),{projectId:c,runId:o,challengeId:r,search:h}}function j(){const t=n();return window.addEventListener("hashchange",n),{...t,cleanup:()=>window.removeEventListener("hashchange",n)}}export{I as a,g as b,d as c,j as d,l as e,i as f,w as p,p as s};
