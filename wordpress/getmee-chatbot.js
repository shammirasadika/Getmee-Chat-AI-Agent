(function(){(function(){const i={mode:"floating",position:"bottom-right",targetId:"",chatUrl:""};function c(){const e=document.currentScript,t=window.ChatWidgetConfig||{},o=e?.getAttribute("data-chat-url")||t.chatUrl||i.chatUrl||new URL("/",e?.src||window.location.href).origin;return{mode:e?.getAttribute("data-mode")||t.mode||i.mode,position:e?.getAttribute("data-position")||t.position||i.position,targetId:e?.getAttribute("data-target-id")||t.targetId||i.targetId,chatUrl:o}}function d(e){const t=document.createElement("iframe");return t.src=e,t.style.width="100%",t.style.height="100%",t.style.border="none",t.style.display="block",t.allow="clipboard-write",t.title="GetMee AI Chatbot",t}function h(e){const t=document.getElementById(e.targetId);if(!t){console.error(`[GetMeeChat] Target element #${e.targetId} not found.`);return}t.style.position="relative",t.style.overflow="hidden",t.style.height||(t.style.height="600px"),t.appendChild(d(e.chatUrl))}function p(e){const t=e.position==="bottom-right",o=document.createElement("button");o.id="getmee-chat-fab",o.setAttribute("aria-label","Open chat"),Object.assign(o.style,{position:"fixed",bottom:"24px",[t?"right":"left"]:"24px",[t?"left":"right"]:"auto",width:"60px",height:"60px",borderRadius:"50%",background:"#2a9d8f",color:"#fff",border:"none",cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center",boxShadow:"0 4px 20px rgba(0,0,0,0.2)",zIndex:"99998",transition:"transform 0.2s",fontSize:"2rem",fontWeight:"bold"}),o.textContent="";const n=document.createElement("div");n.id="getmee-chat-panel",Object.assign(n.style,{position:"fixed",bottom:"96px",[t?"right":"left"]:"24px",[t?"left":"right"]:"auto",width:"400px",maxWidth:"calc(100vw - 32px)",height:"600px",maxHeight:"calc(100vh - 120px)",borderRadius:"16px",overflow:"hidden",boxShadow:"0 8px 40px rgba(0,0,0,0.15)",zIndex:"99999",display:"none",border:"1px solid #e2e8f0"}),n.appendChild(d(e.chatUrl));let a=!1;o.addEventListener("click",()=>{a=!a,n.style.display=a?"block":"none",o.textContent=a?"✖":""});const l=document.createElement("style");l.textContent=`
      @media (max-width: 480px) {
        #getmee-chat-panel {
          width: 100vw !important;
          height: 100vh !important;
          max-width: 100vw !important;
          max-height: 100vh !important;
          bottom: 0 !important;
          left: 0 !important;
          right: 0 !important;
          border-radius: 0 !important;
          border: none !important;
        }
        #getmee-chat-fab {
          bottom: 16px !important;
          ${t?"right: 16px !important;":"left: 16px !important;"}
        }
      }
    `,document.head.appendChild(l),document.body.appendChild(n),document.body.appendChild(o)}function r(e){e&&(window.ChatWidgetConfig={...window.ChatWidgetConfig||{},...e});const t=c();t.mode==="inline"&&t.targetId?h(t):p(t)}window.GetMeeChat={init:r};const s=document.currentScript;(window.ChatWidgetConfig||s?.hasAttribute("data-chat-url"))&&(document.readyState==="loading"?document.addEventListener("DOMContentLoaded",()=>r()):r())})()})();
