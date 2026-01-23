/*! For license information please see med-expert-panel.js.LICENSE.txt */
(()=>{"use strict";const t=globalThis,e=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,i=Symbol(),r=new WeakMap;class s{constructor(t,e,r){if(this._$cssResult$=!0,r!==i)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const i=this.t;if(e&&void 0===t){const e=void 0!==i&&1===i.length;e&&(t=r.get(i)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),e&&r.set(i,t))}return t}toString(){return this.cssText}}const o=(t,...e)=>{const r=1===t.length?t[0]:e.reduce((e,i,r)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[r+1],t[0]);return new s(r,t,i)},a=(i,r)=>{if(e)i.adoptedStyleSheets=r.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const e of r){const r=document.createElement("style"),s=t.litNonce;void 0!==s&&r.setAttribute("nonce",s),r.textContent=e.cssText,i.appendChild(r)}},n=e?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new s("string"==typeof t?t:t+"",void 0,i))(e)})(t):t,{is:l,defineProperty:d,getOwnPropertyDescriptor:c,getOwnPropertyNames:p,getOwnPropertySymbols:h,getPrototypeOf:u}=Object,m=globalThis,_=m.trustedTypes,v=_?_.emptyScript:"",f=m.reactiveElementPolyfillSupport,g=(t,e)=>t,b={toAttribute(t,e){switch(e){case Boolean:t=t?v:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},y=(t,e)=>!l(t,e),x={attribute:!0,type:String,converter:b,reflect:!1,useDefault:!1,hasChanged:y};Symbol.metadata??=Symbol("metadata"),m.litPropertyMetadata??=new WeakMap;class $ extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=x){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),r=this.getPropertyDescriptor(t,i,e);void 0!==r&&d(this.prototype,t,r)}}static getPropertyDescriptor(t,e,i){const{get:r,set:s}=c(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:r,set(e){const o=r?.call(this);s?.call(this,e),this.requestUpdate(t,o,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??x}static _$Ei(){if(this.hasOwnProperty(g("elementProperties")))return;const t=u(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(g("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(g("properties"))){const t=this.properties,e=[...p(t),...h(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return a(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,i);if(void 0!==r&&!0===i.reflect){const s=(void 0!==i.converter?.toAttribute?i.converter:b).toAttribute(e,i.type);this._$Em=t,null==s?this.removeAttribute(r):this.setAttribute(r,s),this._$Em=null}}_$AK(t,e){const i=this.constructor,r=i._$Eh.get(t);if(void 0!==r&&this._$Em!==r){const t=i.getPropertyOptions(r),s="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:b;this._$Em=r;const o=s.fromAttribute(e,t.type);this[r]=o??this._$Ej?.get(r)??o,this._$Em=null}}requestUpdate(t,e,i,r=!1,s){if(void 0!==t){const o=this.constructor;if(!1===r&&(s=this[t]),i??=o.getPropertyOptions(t),!((i.hasChanged??y)(s,e)||i.useDefault&&i.reflect&&s===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:r,wrapped:s},o){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??e??this[t]),!0!==s||void 0!==o)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===r&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,r=this[e];!0!==t||this._$AL.has(e)||void 0===r||this.C(e,void 0,i,r)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}}$.elementStyles=[],$.shadowRootOptions={mode:"open"},$[g("elementProperties")]=new Map,$[g("finalized")]=new Map,f?.({ReactiveElement:$}),(m.reactiveElementVersions??=[]).push("2.1.2");const k=globalThis,w=t=>t,A=k.trustedTypes,z=A?A.createPolicy("lit-html",{createHTML:t=>t}):void 0,S="$lit$",D=`lit$${Math.random().toFixed(9).slice(2)}$`,E="?"+D,P=`<${E}>`,T=document,M=()=>T.createComment(""),C=t=>null===t||"object"!=typeof t&&"function"!=typeof t,O=Array.isArray,U="[ \t\n\f\r]",I=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,j=/-->/g,H=/>/g,N=RegExp(`>|${U}(?:([^\\s"'>=/]+)(${U}*=${U}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),F=/'/g,R=/"/g,W=/^(?:script|style|textarea|title)$/i,B=t=>(e,...i)=>({_$litType$:t,strings:e,values:i}),q=B(1),L=(B(2),B(3),Symbol.for("lit-noChange")),K=Symbol.for("lit-nothing"),G=new WeakMap,V=T.createTreeWalker(T,129);function Z(t,e){if(!O(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==z?z.createHTML(e):e}const J=(t,e)=>{const i=t.length-1,r=[];let s,o=2===e?"<svg>":3===e?"<math>":"",a=I;for(let e=0;e<i;e++){const i=t[e];let n,l,d=-1,c=0;for(;c<i.length&&(a.lastIndex=c,l=a.exec(i),null!==l);)c=a.lastIndex,a===I?"!--"===l[1]?a=j:void 0!==l[1]?a=H:void 0!==l[2]?(W.test(l[2])&&(s=RegExp("</"+l[2],"g")),a=N):void 0!==l[3]&&(a=N):a===N?">"===l[0]?(a=s??I,d=-1):void 0===l[1]?d=-2:(d=a.lastIndex-l[2].length,n=l[1],a=void 0===l[3]?N:'"'===l[3]?R:F):a===R||a===F?a=N:a===j||a===H?a=I:(a=N,s=void 0);const p=a===N&&t[e+1].startsWith("/>")?" ":"";o+=a===I?i+P:d>=0?(r.push(n),i.slice(0,d)+S+i.slice(d)+D+p):i+D+(-2===d?e:p)}return[Z(t,o+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),r]};class X{constructor({strings:t,_$litType$:e},i){let r;this.parts=[];let s=0,o=0;const a=t.length-1,n=this.parts,[l,d]=J(t,e);if(this.el=X.createElement(l,i),V.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(r=V.nextNode())&&n.length<a;){if(1===r.nodeType){if(r.hasAttributes())for(const t of r.getAttributeNames())if(t.endsWith(S)){const e=d[o++],i=r.getAttribute(t).split(D),a=/([.?@])?(.*)/.exec(e);n.push({type:1,index:s,name:a[2],strings:i,ctor:"."===a[1]?it:"?"===a[1]?rt:"@"===a[1]?st:et}),r.removeAttribute(t)}else t.startsWith(D)&&(n.push({type:6,index:s}),r.removeAttribute(t));if(W.test(r.tagName)){const t=r.textContent.split(D),e=t.length-1;if(e>0){r.textContent=A?A.emptyScript:"";for(let i=0;i<e;i++)r.append(t[i],M()),V.nextNode(),n.push({type:2,index:++s});r.append(t[e],M())}}}else if(8===r.nodeType)if(r.data===E)n.push({type:2,index:s});else{let t=-1;for(;-1!==(t=r.data.indexOf(D,t+1));)n.push({type:7,index:s}),t+=D.length-1}s++}}static createElement(t,e){const i=T.createElement("template");return i.innerHTML=t,i}}function Q(t,e,i=t,r){if(e===L)return e;let s=void 0!==r?i._$Co?.[r]:i._$Cl;const o=C(e)?void 0:e._$litDirective$;return s?.constructor!==o&&(s?._$AO?.(!1),void 0===o?s=void 0:(s=new o(t),s._$AT(t,i,r)),void 0!==r?(i._$Co??=[])[r]=s:i._$Cl=s),void 0!==s&&(e=Q(t,s._$AS(t,e.values),s,r)),e}class Y{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,r=(t?.creationScope??T).importNode(e,!0);V.currentNode=r;let s=V.nextNode(),o=0,a=0,n=i[0];for(;void 0!==n;){if(o===n.index){let e;2===n.type?e=new tt(s,s.nextSibling,this,t):1===n.type?e=new n.ctor(s,n.name,n.strings,this,t):6===n.type&&(e=new ot(s,this,t)),this._$AV.push(e),n=i[++a]}o!==n?.index&&(s=V.nextNode(),o++)}return V.currentNode=T,r}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class tt{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,r){this.type=2,this._$AH=K,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Q(this,t,e),C(t)?t===K||null==t||""===t?(this._$AH!==K&&this._$AR(),this._$AH=K):t!==this._$AH&&t!==L&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>O(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==K&&C(this._$AH)?this._$AA.nextSibling.data=t:this.T(T.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,r="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=X.createElement(Z(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===r)this._$AH.p(e);else{const t=new Y(r,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=G.get(t.strings);return void 0===e&&G.set(t.strings,e=new X(t)),e}k(t){O(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,r=0;for(const s of t)r===e.length?e.push(i=new tt(this.O(M()),this.O(M()),this,this.options)):i=e[r],i._$AI(s),r++;r<e.length&&(this._$AR(i&&i._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=w(t).nextSibling;w(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class et{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,r,s){this.type=1,this._$AH=K,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=s,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=K}_$AI(t,e=this,i,r){const s=this.strings;let o=!1;if(void 0===s)t=Q(this,t,e,0),o=!C(t)||t!==this._$AH&&t!==L,o&&(this._$AH=t);else{const r=t;let a,n;for(t=s[0],a=0;a<s.length-1;a++)n=Q(this,r[i+a],e,a),n===L&&(n=this._$AH[a]),o||=!C(n)||n!==this._$AH[a],n===K?t=K:t!==K&&(t+=(n??"")+s[a+1]),this._$AH[a]=n}o&&!r&&this.j(t)}j(t){t===K?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class it extends et{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===K?void 0:t}}class rt extends et{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==K)}}class st extends et{constructor(t,e,i,r,s){super(t,e,i,r,s),this.type=5}_$AI(t,e=this){if((t=Q(this,t,e,0)??K)===L)return;const i=this._$AH,r=t===K&&i!==K||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,s=t!==K&&(i===K||r);r&&this.element.removeEventListener(this.name,this,i),s&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class ot{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){Q(this,t)}}const at=k.litHtmlPolyfillSupport;at?.(X,tt),(k.litHtmlVersions??=[]).push("3.3.2");const nt=globalThis;class lt extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const r=i?.renderBefore??e;let s=r._$litPart$;if(void 0===s){const t=i?.renderBefore??null;r._$litPart$=s=new tt(e.insertBefore(M(),t),t,void 0,i??{})}return s._$AI(t),s})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return L}}lt._$litElement$=!0,lt.finalized=!0,nt.litElementHydrateSupport?.({LitElement:lt});const dt=nt.litElementPolyfillSupport;dt?.({LitElement:lt}),(nt.litElementVersions??=[]).push("4.2.2");const ct=t=>(e,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)},pt={attribute:!0,type:String,converter:b,reflect:!1,hasChanged:y},ht=(t=pt,e,i)=>{const{kind:r,metadata:s}=i;let o=globalThis.litPropertyMetadata.get(s);if(void 0===o&&globalThis.litPropertyMetadata.set(s,o=new Map),"setter"===r&&((t=Object.create(t)).wrapped=!0),o.set(i.name,t),"accessor"===r){const{name:r}=i;return{set(i){const s=e.get.call(this);e.set.call(this,i),this.requestUpdate(r,s,t,!0,i)},init(e){return void 0!==e&&this.C(r,void 0,t,e),e}}}if("setter"===r){const{name:r}=i;return function(i){const s=this[r];e.call(this,i),this.requestUpdate(r,s,t,!0,i)}}throw Error("Unsupported decorator location: "+r)};function ut(t){return(e,i)=>"object"==typeof i?ht(t,e,i):((t,e,i)=>{const r=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),r?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}function mt(t){return ut({...t,state:!0,attribute:!1})}const _t={tablet:{icon:"💊",label:"Tablette",units:["tablet","mg","g"]},capsule:{icon:"💊",label:"Kapsel",units:["capsule","mg","g"]},injection:{icon:"💉",label:"Spritze",units:["ml","IU","mg","unit"]},nasal_spray:{icon:"👃",label:"Nasenspray",units:["spray","puff"]},inhaler:{icon:"🫁",label:"Inhalator",units:["puff","mcg"]},drops:{icon:"💧",label:"Tropfen",units:["drop","ml"]},cream:{icon:"🧴",label:"Creme/Salbe",units:["application","g"]},patch:{icon:"🩹",label:"Pflaster",units:["patch"]},suppository:{icon:"💊",label:"Zäpfchen",units:["suppository"]},liquid:{icon:"🧪",label:"Saft/Lösung",units:["ml","teaspoon","tablespoon"]},powder:{icon:"📦",label:"Pulver",units:["sachet","scoop","g"]},other:{icon:"📦",label:"Sonstige",units:["unit","dose","application"]}},vt={times_per_day:{icon:"🕐",label:"Täglich zu festen Zeiten",description:"z.B. 8:00, 12:00, 18:00"},interval:{icon:"⏱️",label:"Alle X Stunden",description:"z.B. alle 8 Stunden"},weekly:{icon:"📅",label:"Bestimmte Wochentage",description:"z.B. Mo, Mi, Fr"},as_needed:{icon:"🆘",label:"Bei Bedarf (PRN)",description:"Nur wenn nötig"},depot:{icon:"💉",label:"Depot-Injektion",description:"Termin-basiert (z.B. monatlich)"}},ft=[{value:0,short:"Mo",long:"Montag"},{value:1,short:"Di",long:"Dienstag"},{value:2,short:"Mi",long:"Mittwoch"},{value:3,short:"Do",long:"Donnerstag"},{value:4,short:"Fr",long:"Freitag"},{value:5,short:"Sa",long:"Samstag"},{value:6,short:"So",long:"Sonntag"}],gt=[{label:"¼",numerator:1,denominator:4},{label:"½",numerator:1,denominator:2},{label:"1",numerator:1,denominator:1},{label:"1½",numerator:3,denominator:2},{label:"2",numerator:2,denominator:1}];var bt=function(t,e,i,r){var s,o=arguments.length,a=o<3?e:null===r?r=Object.getOwnPropertyDescriptor(e,i):r;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)a=Reflect.decorate(t,e,i,r);else for(var n=t.length-1;n>=0;n--)(s=t[n])&&(a=(o<3?s(a):o>3?s(e,i,a):s(e,i))||a);return o>3&&a&&Object.defineProperty(e,i,a),a};let yt=class extends lt{constructor(){super(...arguments),this._step=1,this._saving=!1,this._error=null,this._formData={form:"tablet",display_name:"",dose_numerator:1,dose_denominator:1,dose_unit:"tablet",schedule_kind:"times_per_day",times:["08:00"],weekdays:[0,1,2,3,4],interval_minutes:480,track_inventory:!1,current_quantity:30,refill_threshold:7,grace_minutes:30,snooze_minutes:10}}render(){return q`
      <div class="wizard-container">
        <div class="wizard-header">
          <h2>Medikament hinzufügen</h2>
          <span class="step-indicator">${this._step}/4</span>
        </div>

        <div class="wizard-content">
          ${this._error?q`<div class="error">${this._error}</div>`:""}
          
          ${1===this._step?this._renderStep1():""}
          ${2===this._step?this._renderStep2():""}
          ${3===this._step?this._renderStep3():""}
          ${4===this._step?this._renderStep4():""}
          ${5===this._step?this._renderSuccess():""}
        </div>

        ${this._step<5?q`
          <div class="wizard-footer">
            ${this._step>1?q`<button class="btn btn-secondary" @click=${this._prevStep}>← Zurück</button>`:q`<button class="btn btn-text" @click=${this._close}>Abbrechen</button>`}
            
            ${this._step<4?q`<button class="btn btn-primary" @click=${this._nextStep} ?disabled=${!this._canProceed()}>Weiter →</button>`:q`<button class="btn btn-primary" @click=${this._save} ?disabled=${this._saving}>
                  ${this._saving?"Speichern...":"💊 Medikament speichern"}
                </button>`}
          </div>
        `:""}
      </div>
    `}_renderStep1(){const t=Object.entries(_t);return q`
      <div class="step-title">Was möchtest du hinzufügen?</div>
      <div class="form-grid">
        ${t.map(([t,e])=>q`
          <div 
            class="form-type-card ${this._formData.form===t?"selected":""}"
            @click=${()=>this._selectForm(t)}
          >
            <span class="form-type-icon">${e.icon}</span>
            <span class="form-type-label">${e.label}</span>
          </div>
        `)}
      </div>
    `}_renderStep2(){const t=_t[this._formData.form];return q`
      <div class="step-title">${t.icon} ${t.label} - Details</div>
      
      <div class="field">
        <label>Name *</label>
        <input 
          type="text" 
          placeholder="z.B. Metformin"
          .value=${this._formData.display_name}
          @input=${t=>this._updateField("display_name",t.target.value)}
        />
      </div>

      <div class="field-row">
        <div class="field">
          <label>Stärke (optional)</label>
          <input 
            type="text" 
            placeholder="z.B. 500"
            .value=${this._formData.strength||""}
            @input=${t=>this._updateField("strength",t.target.value)}
          />
        </div>
        <div class="field">
          <label>Einheit</label>
          <select 
            .value=${this._formData.strength_unit||"mg"}
            @change=${t=>this._updateField("strength_unit",t.target.value)}
          >
            <option value="mg">mg</option>
            <option value="g">g</option>
            <option value="mcg">mcg</option>
            <option value="ml">ml</option>
            <option value="IU">IU</option>
          </select>
        </div>
      </div>

      <div class="field">
        <label>Dosis pro Einnahme</label>
        <div class="dose-presets">
          ${gt.map(t=>q`
            <div 
              class="dose-preset ${this._formData.dose_numerator===t.numerator&&this._formData.dose_denominator===t.denominator?"selected":""}"
              @click=${()=>this._selectDose(t.numerator,t.denominator)}
            >
              ${t.label}
            </div>
          `)}
        </div>
      </div>

      <div class="field">
        <label>Einheit</label>
        <select 
          .value=${this._formData.dose_unit}
          @change=${t=>this._updateField("dose_unit",t.target.value)}
        >
          ${t.units.map(t=>q`
            <option value=${t}>${t}</option>
          `)}
        </select>
      </div>

      <div class="field">
        <label>Notizen (optional)</label>
        <input 
          type="text" 
          placeholder="z.B. Mit dem Essen einnehmen"
          .value=${this._formData.notes||""}
          @input=${t=>this._updateField("notes",t.target.value)}
        />
      </div>
    `}_renderStep3(){return q`
      <div class="step-title">Wann nimmst du ${this._formData.display_name||"dieses Medikament"}?</div>
      
      ${Object.entries(vt).map(([t,e])=>q`
        <div 
          class="schedule-option ${this._formData.schedule_kind===t?"selected":""}"
          @click=${()=>this._updateField("schedule_kind",t)}
        >
          <span class="schedule-option-icon">${e.icon}</span>
          <div class="schedule-option-content">
            <div class="schedule-option-label">${e.label}</div>
            <div class="schedule-option-desc">${e.description}</div>
          </div>
        </div>
      `)}

      ${"times_per_day"===this._formData.schedule_kind?this._renderTimesInput():""}
      ${"weekly"===this._formData.schedule_kind?this._renderWeeklyInput():""}
      ${"interval"===this._formData.schedule_kind?this._renderIntervalInput():""}
    `}_renderTimesInput(){return q`
      <div class="field" style="margin-top: 16px;">
        <label>Um welche Uhrzeit(en)?</label>
        <div class="time-inputs">
          ${(this._formData.times||[]).map((t,e)=>q`
            <div class="time-input-wrapper">
              <input 
                type="time" 
                class="time-input"
                .value=${t}
                @change=${t=>this._updateTime(e,t.target.value)}
              />
              ${(this._formData.times?.length||0)>1?q`
                <button class="remove-time" @click=${()=>this._removeTime(e)}>×</button>
              `:""}
            </div>
          `)}
          <button class="add-time-btn" @click=${this._addTime}>+ Zeit</button>
        </div>
      </div>
    `}_renderWeeklyInput(){return q`
      <div class="field" style="margin-top: 16px;">
        <label>An welchen Tagen?</label>
        <div class="weekday-toggles">
          ${ft.map(t=>q`
            <div 
              class="weekday-toggle ${(this._formData.weekdays||[]).includes(t.value)?"selected":""}"
              @click=${()=>this._toggleWeekday(t.value)}
            >
              ${t.short}
            </div>
          `)}
        </div>
      </div>
      ${this._renderTimesInput()}
    `}_renderIntervalInput(){return q`
      <div class="field" style="margin-top: 16px;">
        <label>Alle wie viele Stunden?</label>
        <div class="dose-presets">
          ${[4,6,8,12,24].map(t=>q`
            <div 
              class="dose-preset ${this._formData.interval_minutes===60*t?"selected":""}"
              @click=${()=>this._updateField("interval_minutes",60*t)}
            >
              ${t}h
            </div>
          `)}
        </div>
      </div>
    `}_renderStep4(){return q`
      <div class="step-title">Bestand & Erinnerungen</div>
      
      <label class="checkbox-field" @click=${()=>this._updateField("track_inventory",!this._formData.track_inventory)}>
        <input type="checkbox" .checked=${this._formData.track_inventory} />
        <span>Bestand verwalten</span>
      </label>

      ${this._formData.track_inventory?q`
        <div class="field-row">
          <div class="field">
            <label>Aktueller Bestand</label>
            <input 
              type="number" 
              min="0"
              .value=${String(this._formData.current_quantity||0)}
              @input=${t=>this._updateField("current_quantity",parseInt(t.target.value)||0)}
            />
          </div>
          <div class="field">
            <label>Warnen unter</label>
            <input 
              type="number" 
              min="1"
              .value=${String(this._formData.refill_threshold||7)}
              @input=${t=>this._updateField("refill_threshold",parseInt(t.target.value)||7)}
            />
          </div>
        </div>
      `:""}

      <div class="field">
        <label>Gnadenfrist (Minuten)</label>
        <div class="dose-presets">
          ${[10,15,30,60].map(t=>q`
            <div 
              class="dose-preset ${this._formData.grace_minutes===t?"selected":""}"
              @click=${()=>this._updateField("grace_minutes",t)}
            >
              ${t} min
            </div>
          `)}
        </div>
        <small style="color: var(--secondary-text-color); font-size: 11px; margin-top: 4px; display: block;">
          Zeit nach Fälligkeit bevor als "verpasst" markiert
        </small>
      </div>

      <div class="field">
        <label>Snooze-Dauer (Minuten)</label>
        <div class="dose-presets">
          ${[5,10,15,30].map(t=>q`
            <div 
              class="dose-preset ${this._formData.snooze_minutes===t?"selected":""}"
              @click=${()=>this._updateField("snooze_minutes",t)}
            >
              ${t} min
            </div>
          `)}
        </div>
      </div>
    `}_renderSuccess(){return q`
      <div class="success-message">
        <div class="success-icon">✅</div>
        <h3>${this._formData.display_name} hinzugefügt!</h3>
        <p>Das Medikament wurde erfolgreich angelegt.</p>
        <button class="btn btn-primary" @click=${this._addAnother}>+ Weiteres hinzufügen</button>
        <button class="btn btn-text" @click=${this._close}>Fertig</button>
      </div>
    `}_selectForm(t){const e=_t[t];this._formData={...this._formData,form:t,dose_unit:e.units[0]},this.requestUpdate()}_selectDose(t,e){this._formData={...this._formData,dose_numerator:t,dose_denominator:e},this.requestUpdate()}_updateField(t,e){this._formData={...this._formData,[t]:e},this.requestUpdate()}_addTime(){const t=[...this._formData.times||[],"12:00"];this._updateField("times",t)}_removeTime(t){const e=[...this._formData.times||[]];e.splice(t,1),this._updateField("times",e)}_updateTime(t,e){const i=[...this._formData.times||[]];i[t]=e,this._updateField("times",i)}_toggleWeekday(t){const e=[...this._formData.weekdays||[]],i=e.indexOf(t);i>=0?e.splice(i,1):(e.push(t),e.sort()),this._updateField("weekdays",e)}_canProceed(){switch(this._step){case 1:return!!this._formData.form;case 2:return!!this._formData.display_name.trim();case 3:return"as_needed"===this._formData.schedule_kind||("times_per_day"===this._formData.schedule_kind?(this._formData.times?.length||0)>0:"weekly"===this._formData.schedule_kind?(this._formData.weekdays?.length||0)>0&&(this._formData.times?.length||0)>0:"interval"!==this._formData.schedule_kind||(this._formData.interval_minutes||0)>0);default:return!0}}_nextStep(){this._canProceed()&&(this._step++,this._error=null)}_prevStep(){this._step>1&&(this._step--,this._error=null)}async _save(){this._saving=!0,this._error=null;try{const t=this._formData.strength?`${this._formData.display_name} ${this._formData.strength}${this._formData.strength_unit||"mg"}`:this._formData.display_name,e={entry_id:this.entryId,display_name:t,schedule_kind:this._formData.schedule_kind,form:this._formData.form,default_dose:{numerator:this._formData.dose_numerator,denominator:this._formData.dose_denominator,unit:this._formData.dose_unit},policy:{grace_minutes:this._formData.grace_minutes,snooze_minutes:this._formData.snooze_minutes}};"times_per_day"!==this._formData.schedule_kind&&"weekly"!==this._formData.schedule_kind||(e.times=this._formData.times),"weekly"===this._formData.schedule_kind&&(e.weekdays=this._formData.weekdays),"interval"!==this._formData.schedule_kind&&"depot"!==this._formData.schedule_kind||(e.interval_minutes=this._formData.interval_minutes),this._formData.track_inventory&&(e.inventory={current_quantity:this._formData.current_quantity,refill_threshold:this._formData.refill_threshold,auto_decrement:!0}),this._formData.notes&&(e.notes=this._formData.notes),await this.hass.callService("med_expert","add_medication",e),this._step=5}catch(t){this._error=`Fehler beim Speichern: ${t}`}finally{this._saving=!1}}_addAnother(){this._formData={form:"tablet",display_name:"",dose_numerator:1,dose_denominator:1,dose_unit:"tablet",schedule_kind:"times_per_day",times:["08:00"],weekdays:[0,1,2,3,4],interval_minutes:480,track_inventory:!1,current_quantity:30,refill_threshold:7,grace_minutes:30,snooze_minutes:10},this._step=1,this._error=null}_close(){this.dispatchEvent(new CustomEvent("close"))}};yt.styles=o`
    :host {
      display: block;
    }

    .wizard-container {
      background: var(--card-background-color);
      border-radius: 12px;
      overflow: hidden;
      max-width: 500px;
      margin: 0 auto;
    }

    .wizard-header {
      background: var(--primary-color);
      color: var(--text-primary-color);
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .wizard-header h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 500;
    }

    .step-indicator {
      font-size: 14px;
      opacity: 0.9;
    }

    .wizard-content {
      padding: 24px;
      min-height: 300px;
    }

    .wizard-footer {
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      border-top: 1px solid var(--divider-color);
    }

    .step-title {
      font-size: 16px;
      font-weight: 500;
      margin-bottom: 20px;
      color: var(--primary-text-color);
    }

    /* Form Grid */
    .form-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }

    .form-grid-2 {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }

    /* Form Type Cards */
    .form-type-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px 8px;
      border: 2px solid var(--divider-color);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      background: var(--card-background-color);
    }

    .form-type-card:hover {
      border-color: var(--primary-color);
      background: var(--secondary-background-color);
    }

    .form-type-card.selected {
      border-color: var(--primary-color);
      background: rgba(var(--rgb-primary-color), 0.1);
    }

    .form-type-icon {
      font-size: 32px;
      margin-bottom: 8px;
    }

    .form-type-label {
      font-size: 12px;
      text-align: center;
      color: var(--primary-text-color);
    }

    /* Input Fields */
    .field {
      margin-bottom: 16px;
    }

    .field label {
      display: block;
      font-size: 12px;
      font-weight: 500;
      color: var(--secondary-text-color);
      margin-bottom: 6px;
      text-transform: uppercase;
    }

    .field input, .field select {
      width: 100%;
      padding: 12px;
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      font-size: 16px;
      background: var(--card-background-color);
      color: var(--primary-text-color);
      box-sizing: border-box;
    }

    .field input:focus, .field select:focus {
      outline: none;
      border-color: var(--primary-color);
    }

    .field-row {
      display: flex;
      gap: 12px;
    }

    .field-row .field {
      flex: 1;
    }

    /* Dose Presets */
    .dose-presets {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .dose-preset {
      padding: 10px 16px;
      border: 2px solid var(--divider-color);
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      font-weight: 500;
      background: var(--card-background-color);
      color: var(--primary-text-color);
      transition: all 0.2s;
    }

    .dose-preset:hover {
      border-color: var(--primary-color);
    }

    .dose-preset.selected {
      border-color: var(--primary-color);
      background: var(--primary-color);
      color: var(--text-primary-color);
    }

    /* Schedule Type Options */
    .schedule-option {
      display: flex;
      align-items: flex-start;
      padding: 12px;
      border: 2px solid var(--divider-color);
      border-radius: 8px;
      cursor: pointer;
      margin-bottom: 8px;
      transition: all 0.2s;
    }

    .schedule-option:hover {
      border-color: var(--primary-color);
    }

    .schedule-option.selected {
      border-color: var(--primary-color);
      background: rgba(var(--rgb-primary-color), 0.1);
    }

    .schedule-option-icon {
      font-size: 24px;
      margin-right: 12px;
    }

    .schedule-option-content {
      flex: 1;
    }

    .schedule-option-label {
      font-weight: 500;
      color: var(--primary-text-color);
    }

    .schedule-option-desc {
      font-size: 12px;
      color: var(--secondary-text-color);
      margin-top: 2px;
    }

    /* Weekday Toggles */
    .weekday-toggles {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .weekday-toggle {
      width: 44px;
      height: 44px;
      border: 2px solid var(--divider-color);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-weight: 500;
      font-size: 14px;
      background: var(--card-background-color);
      color: var(--primary-text-color);
      transition: all 0.2s;
    }

    .weekday-toggle:hover {
      border-color: var(--primary-color);
    }

    .weekday-toggle.selected {
      border-color: var(--primary-color);
      background: var(--primary-color);
      color: var(--text-primary-color);
    }

    /* Time Inputs */
    .time-inputs {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }

    .time-input-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }

    .time-input {
      width: 100px;
      padding: 10px 12px;
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      font-size: 16px;
      background: var(--card-background-color);
      color: var(--primary-text-color);
    }

    .remove-time {
      position: absolute;
      right: -8px;
      top: -8px;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--error-color);
      color: white;
      border: none;
      cursor: pointer;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .add-time-btn {
      padding: 10px 16px;
      border: 2px dashed var(--divider-color);
      border-radius: 8px;
      background: transparent;
      color: var(--primary-color);
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s;
    }

    .add-time-btn:hover {
      border-color: var(--primary-color);
      background: rgba(var(--rgb-primary-color), 0.1);
    }

    /* Checkbox */
    .checkbox-field {
      display: flex;
      align-items: center;
      padding: 12px;
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      cursor: pointer;
      margin-bottom: 16px;
    }

    .checkbox-field input {
      width: 20px;
      height: 20px;
      margin-right: 12px;
    }

    .checkbox-field span {
      color: var(--primary-text-color);
    }

    /* Buttons */
    .btn {
      padding: 12px 24px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-primary {
      background: var(--primary-color);
      color: var(--text-primary-color);
    }

    .btn-primary:hover {
      filter: brightness(1.1);
    }

    .btn-primary:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-secondary {
      background: var(--secondary-background-color);
      color: var(--primary-text-color);
    }

    .btn-secondary:hover {
      background: var(--divider-color);
    }

    .btn-text {
      background: transparent;
      color: var(--primary-color);
      padding: 12px 16px;
    }

    /* Error */
    .error {
      background: var(--error-color);
      color: white;
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 16px;
    }

    /* Success */
    .success-message {
      text-align: center;
      padding: 40px 20px;
    }

    .success-icon {
      font-size: 64px;
      margin-bottom: 16px;
    }

    .success-message h3 {
      margin: 0 0 8px;
      color: var(--primary-text-color);
    }

    .success-message p {
      color: var(--secondary-text-color);
      margin: 0 0 24px;
    }
  `,bt([ut({attribute:!1})],yt.prototype,"hass",void 0),bt([ut({type:String})],yt.prototype,"entryId",void 0),bt([mt()],yt.prototype,"_step",void 0),bt([mt()],yt.prototype,"_saving",void 0),bt([mt()],yt.prototype,"_error",void 0),bt([mt()],yt.prototype,"_formData",void 0),yt=bt([ct("add-medication-wizard")],yt);var xt=function(t,e,i,r){var s,o=arguments.length,a=o<3?e:null===r?r=Object.getOwnPropertyDescriptor(e,i):r;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)a=Reflect.decorate(t,e,i,r);else for(var n=t.length-1;n>=0;n--)(s=t[n])&&(a=(o<3?s(a):o>3?s(e,i,a):s(e,i))||a);return o>3&&a&&Object.defineProperty(e,i,a),a};let $t=class extends lt{constructor(){super(...arguments),this.narrow=!1,this._medications=[],this._loading=!0,this._error=null,this._activeTab="today",this._showWizard=!1,this._entryId=null,this._profiles=[],this._currentProfile=null}connectedCallback(){super.connectedCallback(),this._loadData(),this._refreshInterval=setInterval(()=>this._loadData(),3e4)}disconnectedCallback(){super.disconnectedCallback(),this._refreshInterval&&clearInterval(this._refreshInterval)}async _loadData(){try{this._loading=0===this._medications.length&&0===this._profiles.length,this._error=null,await this._loadProfiles(),!this._currentProfile&&this._profiles.length>0&&(this._currentProfile=this._profiles[0],this._entryId=this._currentProfile.entry_id);const t=Object.keys(this.hass.states).filter(t=>{if(!t.startsWith("sensor.")||!t.endsWith("_status"))return!1;const e=this.hass.states[t];return void 0!==e?.attributes?.medication_id});this._medications=t.map(t=>{const e=this.hass.states[t],i=t.replace("sensor.","").replace("_status",""),r=this.hass.states[`sensor.${i}_next_due`],s=this.hass.states[`sensor.${i}_next_dose`];!this._entryId&&e.attributes.entry_id&&(this._entryId=e.attributes.entry_id);let o=null;r?.state&&"unknown"!==r.state&&(o=new Date(r.state));const a=e.attributes.form||"tablet",n=_t[a]||_t.tablet;return{entity_id:t,medication_id:e.attributes.medication_id||"",entry_id:e.attributes.entry_id||"",name:e.attributes.friendly_name?.replace(" Status","")||e.attributes.display_name||i,status:e.state,next_due:o,next_dose:s?.state||e.attributes.next_dose||"",form:a,icon:n.icon,inventory:e.attributes.inventory?{current:e.attributes.inventory.current_quantity||0,threshold:e.attributes.inventory.refill_threshold||7,low:(e.attributes.inventory.current_quantity||0)<=(e.attributes.inventory.refill_threshold||7)}:void 0,attributes:e.attributes}}).filter(t=>!this._currentProfile||t.entry_id===this._currentProfile.entry_id),this._loading=!1}catch(t){this._error=`Failed to load medications: ${t}`,this._loading=!1}}async _loadProfiles(){try{const t=await this.hass.callWS({type:"config_entries/get"});this._profiles=t.filter(t=>"med_expert"===t.domain).map(t=>({entry_id:t.entry_id,title:t.title,state:t.state}))}catch(t){console.error("Failed to load profiles:",t),this._profiles=[]}}_selectProfile(t){this._currentProfile=t,this._entryId=t.entry_id,this._loadData()}get _dueMedications(){return this._medications.filter(t=>"due"===t.status||"missed"===t.status||"snoozed"===t.status)}get _upcomingMedications(){const t=new Date,e=new Date(t);return e.setHours(23,59,59,999),this._medications.filter(t=>!("ok"!==t.status||!t.next_due)&&t.next_due<=e).sort((t,e)=>(t.next_due?.getTime()||0)-(e.next_due?.getTime()||0))}get _completedToday(){return[]}get _stats(){return{total:this._medications.length,due:this._dueMedications.length,upcoming:this._upcomingMedications.length}}async _takeMedication(t){try{await this.hass.callService("med_expert","take",{medication_id:t.medication_id,entry_id:t.entry_id}),await this._loadData()}catch(t){this._error=`Failed to take medication: ${t}`}}async _snoozeMedication(t){try{await this.hass.callService("med_expert","snooze",{medication_id:t.medication_id,entry_id:t.entry_id}),await this._loadData()}catch(t){this._error=`Failed to snooze medication: ${t}`}}async _skipMedication(t){try{await this.hass.callService("med_expert","skip",{medication_id:t.medication_id,entry_id:t.entry_id}),await this._loadData()}catch(t){this._error=`Failed to skip medication: ${t}`}}_formatTime(t){return t?t.toLocaleTimeString("de-DE",{hour:"2-digit",minute:"2-digit"}):"--:--"}_formatTimeAgo(t){if(!t)return{value:"--:--",label:"",overdue:!1};const e=new Date,i=t.getTime()-e.getTime(),r=Math.abs(i),s=i<0;return r<6e4?{value:"Jetzt",label:"",overdue:s}:r<36e5?{value:`${s?"-":""}${Math.round(r/6e4)}`,label:"Min",overdue:s}:{value:this._formatTime(t),label:s?"Überfällig":"Uhr",overdue:s}}render(){return this._loading?q`
        <div class="loading">
          <div class="loading-spinner">💊</div>
          <p>Medikamente laden...</p>
        </div>
      `:q`
      <div class="app-container">
        ${this._renderHeader()}
        ${this._renderTabs()}
        
        <div class="content">
          ${this._error?q`<div class="error">${this._error}</div>`:""}
          
          ${"today"===this._activeTab?this._renderTodayTab():""}
          ${"calendar"===this._activeTab?this._renderCalendarTab():""}
          ${"profile"===this._activeTab?this._renderProfileTab():""}
          ${"meds"===this._activeTab?this._renderMedsTab():""}
        </div>
      </div>

      ${this._showWizard?q`
        <div class="wizard-overlay" @click=${t=>t.target===t.currentTarget&&this._closeWizard()}>
          <add-medication-wizard
            .hass=${this.hass}
            .entryId=${this._entryId||""}
            @close=${this._closeWizard}
          ></add-medication-wizard>
        </div>
      `:""}
    `}_renderHeader(){const t=this._stats,e=this._getGreeting(),i=this._currentProfile?.title||"Kein Profil";return q`
      <div class="header">
        <div class="header-top">
          <div>
            <h1>${e}</h1>
            <div class="header-subtitle">
              ${this._profiles.length>1?q`
                <select 
                  class="profile-select"
                  .value=${this._currentProfile?.entry_id||""}
                  @change=${t=>{const e=t.target,i=this._profiles.find(t=>t.entry_id===e.value);i&&this._selectProfile(i)}}
                >
                  ${this._profiles.map(t=>q`
                    <option value=${t.entry_id} ?selected=${t.entry_id===this._currentProfile?.entry_id}>
                      ${t.title}
                    </option>
                  `)}
                </select>
                <span style="margin: 0 6px;">•</span>
              `:1===this._profiles.length?q`
                <span class="profile-badge">👤 ${i}</span>
                <span style="margin: 0 6px;">•</span>
              `:""}
              ${t.due>0?`${t.due} Medikament${t.due>1?"e":""} jetzt fällig`:t.upcoming>0?`${t.upcoming} noch heute`:"Alles erledigt 🎉"}
            </div>
          </div>
          <button class="add-btn" @click=${this._openWizard} title="Medikament hinzufügen">
            ➕
          </button>
        </div>
        
        <div class="stats-bar">
          <div class="stat">
            <div class="stat-value">${t.due}</div>
            <div class="stat-label">Fällig</div>
          </div>
          <div class="stat">
            <div class="stat-value">${t.upcoming}</div>
            <div class="stat-label">Heute noch</div>
          </div>
          <div class="stat">
            <div class="stat-value">${t.total}</div>
            <div class="stat-label">Gesamt</div>
          </div>
        </div>
      </div>
    `}_getGreeting(){const t=(new Date).getHours();return t<12?"☀️ Guten Morgen":t<18?"🌤️ Guten Tag":"🌙 Guten Abend"}_renderTabs(){return q`
      <nav class="tab-nav">
        ${[{id:"today",icon:"📅",label:"Heute"},{id:"calendar",icon:"🗓️",label:"Kalender"},{id:"profile",icon:"👤",label:"Profil"},{id:"meds",icon:"💊",label:"Meds"}].map(t=>q`
          <button 
            class="tab ${this._activeTab===t.id?"active":""}"
            @click=${()=>this._activeTab=t.id}
          >
            <span class="tab-icon">${t.icon}</span>
            ${t.label}
          </button>
        `)}
      </nav>
    `}_renderTodayTab(){if(0===this._medications.length)return this._renderEmptyState();const t=this._dueMedications,e=this._upcomingMedications;return q`
      ${t.length>0?q`
        <div class="section">
          <div class="section-header">
            <span class="section-title">🔴 Jetzt fällig</span>
            <span class="section-badge">${t.length}</span>
          </div>
          ${t.map(t=>this._renderMedCard(t,!0))}
        </div>
      `:""}

      ${e.length>0?q`
        <div class="section">
          <div class="section-header">
            <span class="section-title">⏳ Heute noch</span>
          </div>
          ${e.map(t=>this._renderMedCard(t,!1))}
        </div>
      `:""}

      ${0===t.length&&0===e.length?q`
        <div class="empty-state">
          <div class="empty-icon">✅</div>
          <div class="empty-title">Alles erledigt!</div>
          <div class="empty-text">Keine Medikamente mehr für heute.</div>
        </div>
      `:""}
    `}_renderMedCard(t,e){const i=this._formatTimeAgo(t.next_due),r="missed"===t.status,s="due"===t.status||"snoozed"===t.status;return q`
      <div class="med-card ${r?"urgent":s?"due":""}">
        <div class="med-icon">${t.icon}</div>
        <div class="med-info">
          <div class="med-name">${t.name}</div>
          <div class="med-dose">${t.next_dose}</div>
          ${t.inventory?.low?q`
            <div class="inventory-warning">⚠️ Nur noch ${t.inventory.current} übrig</div>
          `:""}
        </div>
        <div class="med-time">
          <div class="med-time-value ${i.overdue?"med-time-overdue":""}">${i.value}</div>
          <div class="med-time-label">${i.label}</div>
        </div>
      </div>
      
      ${e?q`
        <div class="med-actions" style="margin-top: -4px; margin-bottom: 12px;">
          <button class="action-btn take" @click=${()=>this._takeMedication(t)}>
            ✓ Genommen
          </button>
          <button class="action-btn snooze" @click=${()=>this._snoozeMedication(t)}>
            ⏰ Später
          </button>
          <button class="action-btn skip" @click=${()=>this._skipMedication(t)}>
            ✕
          </button>
        </div>
      `:""}
    `}_renderEmptyState(){return q`
      <div class="empty-state">
        <div class="empty-icon">💊</div>
        <div class="empty-title">Keine Medikamente</div>
        <div class="empty-text">Füge dein erstes Medikament hinzu, um loszulegen.</div>
        <button class="empty-btn" @click=${this._openWizard}>
          ➕ Medikament hinzufügen
        </button>
      </div>
    `}_renderCalendarTab(){return q`
      <div class="calendar-placeholder">
        <div style="font-size: 48px; margin-bottom: 16px;">🗓️</div>
        <p>Kalenderansicht kommt bald...</p>
      </div>
    `}_renderProfileTab(){return q`
      <div class="section">
        <div class="section-header">
          <span class="section-title">Aktuelles Profil</span>
        </div>
        
        ${this._currentProfile?q`
          <div class="profile-card">
            <div class="profile-avatar">👤</div>
            <div class="profile-info">
              <div class="profile-name">${this._currentProfile.title}</div>
              <div class="profile-status">
                ${"loaded"===this._currentProfile.state?"🟢 Aktiv":"🔴 "+this._currentProfile.state}
              </div>
            </div>
          </div>
          
          <div class="profile-stats">
            <div class="profile-stat">
              <span class="stat-icon">💊</span>
              <span>${this._medications.length} Medikamente</span>
            </div>
          </div>
        `:q`
          <div class="no-profile">
            <p>Kein Profil ausgewählt</p>
          </div>
        `}
      </div>
      
      ${this._profiles.length>0?q`
        <div class="section">
          <div class="section-header">
            <span class="section-title">Alle Profile (${this._profiles.length})</span>
          </div>
          
          ${this._profiles.map(t=>q`
            <div 
              class="profile-list-item ${t.entry_id===this._currentProfile?.entry_id?"active":""}"
              @click=${()=>this._selectProfile(t)}
            >
              <div class="profile-avatar-small">👤</div>
              <div class="profile-item-info">
                <div class="profile-item-name">${t.title}</div>
                <div class="profile-item-status">
                  ${"loaded"===t.state?"Aktiv":t.state}
                </div>
              </div>
              ${t.entry_id===this._currentProfile?.entry_id?q`
                <span class="check-mark">✓</span>
              `:""}
            </div>
          `)}
        </div>
      `:""}
      
      <div class="section">
        <button class="profile-action-btn" @click=${this._openAddProfile}>
          ➕ Neues Profil erstellen
        </button>
      </div>
    `}_openAddProfile(){window.location.href="/config/integrations/integration/med_expert"}_renderMedsTab(){return 0===this._medications.length?this._renderEmptyState():q`
      <div class="section">
        <div class="section-header">
          <span class="section-title">Alle Medikamente</span>
        </div>
        ${this._medications.map(t=>q`
          <div class="meds-list-item">
            <div class="med-icon">${t.icon}</div>
            <div class="med-info">
              <div class="med-name">${t.name}</div>
              <div class="med-dose">${t.next_dose}</div>
              ${t.inventory?q`
                <div style="font-size: 11px; color: var(--secondary-text-color);">
                  📦 ${t.inventory.current} auf Lager
                </div>
              `:""}
            </div>
          </div>
        `)}
      </div>
    `}async _openWizard(){if(!this._entryId&&this._medications.length>0&&(this._entryId=this._medications[0].entry_id),!this._entryId){const t=Object.keys(this.hass.states).filter(t=>t.includes("med_expert")).map(t=>this.hass.states[t]?.attributes?.entry_id).filter(Boolean);t.length>0&&(this._entryId=t[0])}if(!this._entryId)try{const t=(await this.hass.callWS({type:"config_entries/get"})).find(t=>"med_expert"===t.domain);t&&(this._entryId=t.entry_id)}catch(t){console.error("Failed to fetch config entries:",t)}this._entryId?this._showWizard=!0:this._error="Kein Med Expert Profil gefunden. Bitte erstelle zuerst ein Profil in den Einstellungen."}_closeWizard(){this._showWizard=!1,setTimeout(()=>this._loadData(),500)}};$t.styles=o`
    :host {
      display: block;
      min-height: 100vh;
      background-color: var(--primary-background-color);
      color: var(--primary-text-color);
    }

    /* App Container */
    .app-container {
      max-width: 600px;
      margin: 0 auto;
      padding-bottom: 80px;
    }

    /* Header */
    .header {
      background: linear-gradient(135deg, var(--primary-color), var(--accent-color, var(--primary-color)));
      color: var(--text-primary-color);
      padding: 20px;
      padding-top: max(20px, env(safe-area-inset-top));
    }

    .header-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .header h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
    }

    .header-subtitle {
      opacity: 0.9;
      margin-top: 4px;
      font-size: 14px;
    }

    .add-btn {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: rgba(255,255,255,0.2);
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
    }

    .add-btn:hover {
      background: rgba(255,255,255,0.3);
      transform: scale(1.05);
    }

    /* Stats Bar */
    .stats-bar {
      display: flex;
      justify-content: space-around;
      padding: 16px;
      margin-top: 12px;
      background: rgba(255,255,255,0.1);
      border-radius: 12px;
    }

    .stat {
      text-align: center;
    }

    .stat-value {
      font-size: 24px;
      font-weight: 700;
    }

    .stat-label {
      font-size: 11px;
      opacity: 0.9;
      text-transform: uppercase;
    }

    /* Tab Navigation */
    .tab-nav {
      display: flex;
      background: var(--card-background-color);
      border-bottom: 1px solid var(--divider-color);
      position: sticky;
      top: 0;
      z-index: 10;
    }

    .tab {
      flex: 1;
      padding: 14px 8px;
      text-align: center;
      cursor: pointer;
      border: none;
      background: none;
      color: var(--secondary-text-color);
      font-size: 12px;
      font-weight: 500;
      transition: all 0.2s;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
    }

    .tab.active {
      color: var(--primary-color);
      border-bottom: 2px solid var(--primary-color);
    }

    .tab-icon {
      font-size: 20px;
    }

    /* Content */
    .content {
      padding: 16px;
    }

    /* Section */
    .section {
      margin-bottom: 24px;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    .section-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--secondary-text-color);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .section-badge {
      background: var(--error-color);
      color: white;
      font-size: 11px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 10px;
    }

    /* Medication Cards */
    .med-card {
      background: var(--card-background-color);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;
      box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
      display: flex;
      align-items: center;
      gap: 12px;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .med-card:active {
      transform: scale(0.98);
    }

    .med-card.urgent {
      border-left: 4px solid var(--error-color);
    }

    .med-card.due {
      border-left: 4px solid var(--warning-color);
    }

    .med-card.done {
      opacity: 0.6;
    }

    .med-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: var(--secondary-background-color);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      flex-shrink: 0;
    }

    .med-info {
      flex: 1;
      min-width: 0;
    }

    .med-name {
      font-weight: 600;
      font-size: 16px;
      margin-bottom: 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .med-dose {
      color: var(--secondary-text-color);
      font-size: 13px;
    }

    .med-time {
      text-align: right;
      flex-shrink: 0;
    }

    .med-time-value {
      font-weight: 600;
      font-size: 15px;
      color: var(--primary-text-color);
    }

    .med-time-label {
      font-size: 11px;
      color: var(--secondary-text-color);
    }

    .med-time-overdue {
      color: var(--error-color);
    }

    /* Action Buttons */
    .med-actions {
      display: flex;
      gap: 8px;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--divider-color);
    }

    .action-btn {
      flex: 1;
      padding: 10px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.2s;
    }

    .action-btn.take {
      background: var(--success-color, #4CAF50);
      color: white;
    }

    .action-btn.snooze {
      background: var(--secondary-background-color);
      color: var(--primary-text-color);
    }

    .action-btn.skip {
      background: var(--secondary-background-color);
      color: var(--secondary-text-color);
    }

    .action-btn:hover {
      filter: brightness(1.1);
    }

    /* Empty State */
    .empty-state {
      text-align: center;
      padding: 60px 20px;
    }

    .empty-icon {
      font-size: 72px;
      margin-bottom: 16px;
      opacity: 0.5;
    }

    .empty-title {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 8px;
    }

    .empty-text {
      color: var(--secondary-text-color);
      margin-bottom: 24px;
    }

    .empty-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 12px 24px;
      background: var(--primary-color);
      color: var(--text-primary-color);
      border: none;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
    }

    /* Loading */
    .loading {
      text-align: center;
      padding: 60px 20px;
      color: var(--secondary-text-color);
    }

    .loading-spinner {
      font-size: 48px;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      100% { transform: rotate(360deg); }
    }

    /* Error */
    .error {
      background: var(--error-color);
      color: white;
      padding: 12px 16px;
      border-radius: 8px;
      margin: 16px;
    }

    /* Wizard Overlay */
    .wizard-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
      z-index: 100;
    }

    /* Medications List Tab */
    .meds-list-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      background: var(--card-background-color);
      border-radius: 8px;
      margin-bottom: 8px;
      cursor: pointer;
    }

    .meds-list-item:hover {
      background: var(--secondary-background-color);
    }

    .inventory-warning {
      font-size: 11px;
      color: var(--warning-color);
      display: flex;
      align-items: center;
      gap: 4px;
      margin-top: 2px;
    }

    /* Calendar placeholder */
    .calendar-placeholder, .stats-placeholder {
      text-align: center;
      padding: 40px;
      color: var(--secondary-text-color);
    }

    /* Profile selector in header */
    .profile-select {
      background: rgba(255,255,255,0.2);
      border: none;
      color: inherit;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 14px;
      cursor: pointer;
    }

    .profile-select option {
      color: var(--primary-text-color);
      background: var(--card-background-color);
    }

    .profile-badge {
      opacity: 0.9;
    }

    /* Profile Tab Styles */
    .profile-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 20px;
      background: var(--card-background-color);
      border-radius: 12px;
      margin-bottom: 16px;
    }

    .profile-avatar {
      font-size: 48px;
      width: 64px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--primary-color);
      border-radius: 50%;
    }

    .profile-info {
      flex: 1;
    }

    .profile-name {
      font-size: 20px;
      font-weight: 600;
    }

    .profile-status {
      font-size: 14px;
      color: var(--secondary-text-color);
      margin-top: 4px;
    }

    .profile-stats {
      display: flex;
      gap: 16px;
      padding: 12px 16px;
      background: var(--card-background-color);
      border-radius: 8px;
      margin-bottom: 16px;
    }

    .profile-stat {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
    }

    .stat-icon {
      font-size: 18px;
    }

    .profile-list-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      background: var(--card-background-color);
      border-radius: 8px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .profile-list-item:hover {
      background: var(--secondary-background-color);
    }

    .profile-list-item.active {
      border: 2px solid var(--primary-color);
    }

    .profile-avatar-small {
      font-size: 24px;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--secondary-background-color);
      border-radius: 50%;
    }

    .profile-item-info {
      flex: 1;
    }

    .profile-item-name {
      font-weight: 500;
    }

    .profile-item-status {
      font-size: 12px;
      color: var(--secondary-text-color);
    }

    .check-mark {
      color: var(--primary-color);
      font-size: 20px;
      font-weight: bold;
    }

    .profile-action-btn {
      width: 100%;
      padding: 14px;
      background: var(--primary-color);
      color: var(--text-primary-color);
      border: none;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }

    .profile-action-btn:hover {
      opacity: 0.9;
    }

    .no-profile {
      text-align: center;
      padding: 40px;
      color: var(--secondary-text-color);
    }
  `,xt([ut({attribute:!1})],$t.prototype,"hass",void 0),xt([ut({type:Boolean})],$t.prototype,"narrow",void 0),xt([mt()],$t.prototype,"_medications",void 0),xt([mt()],$t.prototype,"_loading",void 0),xt([mt()],$t.prototype,"_error",void 0),xt([mt()],$t.prototype,"_activeTab",void 0),xt([mt()],$t.prototype,"_showWizard",void 0),xt([mt()],$t.prototype,"_entryId",void 0),xt([mt()],$t.prototype,"_profiles",void 0),xt([mt()],$t.prototype,"_currentProfile",void 0),$t=xt([ct("med-expert-panel")],$t)})();
//# sourceMappingURL=med-expert-panel.js.map