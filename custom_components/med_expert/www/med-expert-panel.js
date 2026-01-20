var $e = Object.defineProperty;
var we = (r, e, t) => e in r ? $e(r, e, { enumerable: !0, configurable: !0, writable: !0, value: t }) : r[e] = t;
var v = (r, e, t) => we(r, typeof e != "symbol" ? e + "" : e, t);
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const j = globalThis, Z = j.ShadowRoot && (j.ShadyCSS === void 0 || j.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, G = Symbol(), ee = /* @__PURE__ */ new WeakMap();
let ve = class {
  constructor(e, t, i) {
    if (this._$cssResult$ = !0, i !== G) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = e, this.t = t;
  }
  get styleSheet() {
    let e = this.o;
    const t = this.t;
    if (Z && e === void 0) {
      const i = t !== void 0 && t.length === 1;
      i && (e = ee.get(t)), e === void 0 && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), i && ee.set(t, e));
    }
    return e;
  }
  toString() {
    return this.cssText;
  }
};
const Se = (r) => new ve(typeof r == "string" ? r : r + "", void 0, G), $ = (r, ...e) => {
  const t = r.length === 1 ? r[0] : e.reduce((i, a, s) => i + ((o) => {
    if (o._$cssResult$ === !0) return o.cssText;
    if (typeof o == "number") return o;
    throw Error("Value passed to 'css' function must be a 'css' function result: " + o + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
  })(a) + r[s + 1], r[0]);
  return new ve(t, r, G);
}, ke = (r, e) => {
  if (Z) r.adoptedStyleSheets = e.map((t) => t instanceof CSSStyleSheet ? t : t.styleSheet);
  else for (const t of e) {
    const i = document.createElement("style"), a = j.litNonce;
    a !== void 0 && i.setAttribute("nonce", a), i.textContent = t.cssText, r.appendChild(i);
  }
}, te = Z ? (r) => r : (r) => r instanceof CSSStyleSheet ? ((e) => {
  let t = "";
  for (const i of e.cssRules) t += i.cssText;
  return Se(t);
})(r) : r;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const { is: ze, defineProperty: Ae, getOwnPropertyDescriptor: Ee, getOwnPropertyNames: Te, getOwnPropertySymbols: Ce, getPrototypeOf: Pe } = Object, x = globalThis, ie = x.trustedTypes, De = ie ? ie.emptyScript : "", q = x.reactiveElementPolyfillSupport, P = (r, e) => r, W = { toAttribute(r, e) {
  switch (e) {
    case Boolean:
      r = r ? De : null;
      break;
    case Object:
    case Array:
      r = r == null ? r : JSON.stringify(r);
  }
  return r;
}, fromAttribute(r, e) {
  let t = r;
  switch (e) {
    case Boolean:
      t = r !== null;
      break;
    case Number:
      t = r === null ? null : Number(r);
      break;
    case Object:
    case Array:
      try {
        t = JSON.parse(r);
      } catch {
        t = null;
      }
  }
  return t;
} }, J = (r, e) => !ze(r, e), re = { attribute: !0, type: String, converter: W, reflect: !1, useDefault: !1, hasChanged: J };
Symbol.metadata ?? (Symbol.metadata = Symbol("metadata")), x.litPropertyMetadata ?? (x.litPropertyMetadata = /* @__PURE__ */ new WeakMap());
let A = class extends HTMLElement {
  static addInitializer(e) {
    this._$Ei(), (this.l ?? (this.l = [])).push(e);
  }
  static get observedAttributes() {
    return this.finalize(), this._$Eh && [...this._$Eh.keys()];
  }
  static createProperty(e, t = re) {
    if (t.state && (t.attribute = !1), this._$Ei(), this.prototype.hasOwnProperty(e) && ((t = Object.create(t)).wrapped = !0), this.elementProperties.set(e, t), !t.noAccessor) {
      const i = Symbol(), a = this.getPropertyDescriptor(e, i, t);
      a !== void 0 && Ae(this.prototype, e, a);
    }
  }
  static getPropertyDescriptor(e, t, i) {
    const { get: a, set: s } = Ee(this.prototype, e) ?? { get() {
      return this[t];
    }, set(o) {
      this[t] = o;
    } };
    return { get: a, set(o) {
      const d = a == null ? void 0 : a.call(this);
      s == null || s.call(this, o), this.requestUpdate(e, d, i);
    }, configurable: !0, enumerable: !0 };
  }
  static getPropertyOptions(e) {
    return this.elementProperties.get(e) ?? re;
  }
  static _$Ei() {
    if (this.hasOwnProperty(P("elementProperties"))) return;
    const e = Pe(this);
    e.finalize(), e.l !== void 0 && (this.l = [...e.l]), this.elementProperties = new Map(e.elementProperties);
  }
  static finalize() {
    if (this.hasOwnProperty(P("finalized"))) return;
    if (this.finalized = !0, this._$Ei(), this.hasOwnProperty(P("properties"))) {
      const t = this.properties, i = [...Te(t), ...Ce(t)];
      for (const a of i) this.createProperty(a, t[a]);
    }
    const e = this[Symbol.metadata];
    if (e !== null) {
      const t = litPropertyMetadata.get(e);
      if (t !== void 0) for (const [i, a] of t) this.elementProperties.set(i, a);
    }
    this._$Eh = /* @__PURE__ */ new Map();
    for (const [t, i] of this.elementProperties) {
      const a = this._$Eu(t, i);
      a !== void 0 && this._$Eh.set(a, t);
    }
    this.elementStyles = this.finalizeStyles(this.styles);
  }
  static finalizeStyles(e) {
    const t = [];
    if (Array.isArray(e)) {
      const i = new Set(e.flat(1 / 0).reverse());
      for (const a of i) t.unshift(te(a));
    } else e !== void 0 && t.push(te(e));
    return t;
  }
  static _$Eu(e, t) {
    const i = t.attribute;
    return i === !1 ? void 0 : typeof i == "string" ? i : typeof e == "string" ? e.toLowerCase() : void 0;
  }
  constructor() {
    super(), this._$Ep = void 0, this.isUpdatePending = !1, this.hasUpdated = !1, this._$Em = null, this._$Ev();
  }
  _$Ev() {
    var e;
    this._$ES = new Promise((t) => this.enableUpdating = t), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), (e = this.constructor.l) == null || e.forEach((t) => t(this));
  }
  addController(e) {
    var t;
    (this._$EO ?? (this._$EO = /* @__PURE__ */ new Set())).add(e), this.renderRoot !== void 0 && this.isConnected && ((t = e.hostConnected) == null || t.call(e));
  }
  removeController(e) {
    var t;
    (t = this._$EO) == null || t.delete(e);
  }
  _$E_() {
    const e = /* @__PURE__ */ new Map(), t = this.constructor.elementProperties;
    for (const i of t.keys()) this.hasOwnProperty(i) && (e.set(i, this[i]), delete this[i]);
    e.size > 0 && (this._$Ep = e);
  }
  createRenderRoot() {
    const e = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
    return ke(e, this.constructor.elementStyles), e;
  }
  connectedCallback() {
    var e;
    this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this.enableUpdating(!0), (e = this._$EO) == null || e.forEach((t) => {
      var i;
      return (i = t.hostConnected) == null ? void 0 : i.call(t);
    });
  }
  enableUpdating(e) {
  }
  disconnectedCallback() {
    var e;
    (e = this._$EO) == null || e.forEach((t) => {
      var i;
      return (i = t.hostDisconnected) == null ? void 0 : i.call(t);
    });
  }
  attributeChangedCallback(e, t, i) {
    this._$AK(e, i);
  }
  _$ET(e, t) {
    var s;
    const i = this.constructor.elementProperties.get(e), a = this.constructor._$Eu(e, i);
    if (a !== void 0 && i.reflect === !0) {
      const o = (((s = i.converter) == null ? void 0 : s.toAttribute) !== void 0 ? i.converter : W).toAttribute(t, i.type);
      this._$Em = e, o == null ? this.removeAttribute(a) : this.setAttribute(a, o), this._$Em = null;
    }
  }
  _$AK(e, t) {
    var s, o;
    const i = this.constructor, a = i._$Eh.get(e);
    if (a !== void 0 && this._$Em !== a) {
      const d = i.getPropertyOptions(a), l = typeof d.converter == "function" ? { fromAttribute: d.converter } : ((s = d.converter) == null ? void 0 : s.fromAttribute) !== void 0 ? d.converter : W;
      this._$Em = a;
      const p = l.fromAttribute(t, d.type);
      this[a] = p ?? ((o = this._$Ej) == null ? void 0 : o.get(a)) ?? p, this._$Em = null;
    }
  }
  requestUpdate(e, t, i, a = !1, s) {
    var o;
    if (e !== void 0) {
      const d = this.constructor;
      if (a === !1 && (s = this[e]), i ?? (i = d.getPropertyOptions(e)), !((i.hasChanged ?? J)(s, t) || i.useDefault && i.reflect && s === ((o = this._$Ej) == null ? void 0 : o.get(e)) && !this.hasAttribute(d._$Eu(e, i)))) return;
      this.C(e, t, i);
    }
    this.isUpdatePending === !1 && (this._$ES = this._$EP());
  }
  C(e, t, { useDefault: i, reflect: a, wrapped: s }, o) {
    i && !(this._$Ej ?? (this._$Ej = /* @__PURE__ */ new Map())).has(e) && (this._$Ej.set(e, o ?? t ?? this[e]), s !== !0 || o !== void 0) || (this._$AL.has(e) || (this.hasUpdated || i || (t = void 0), this._$AL.set(e, t)), a === !0 && this._$Em !== e && (this._$Eq ?? (this._$Eq = /* @__PURE__ */ new Set())).add(e));
  }
  async _$EP() {
    this.isUpdatePending = !0;
    try {
      await this._$ES;
    } catch (t) {
      Promise.reject(t);
    }
    const e = this.scheduleUpdate();
    return e != null && await e, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    var i;
    if (!this.isUpdatePending) return;
    if (!this.hasUpdated) {
      if (this.renderRoot ?? (this.renderRoot = this.createRenderRoot()), this._$Ep) {
        for (const [s, o] of this._$Ep) this[s] = o;
        this._$Ep = void 0;
      }
      const a = this.constructor.elementProperties;
      if (a.size > 0) for (const [s, o] of a) {
        const { wrapped: d } = o, l = this[s];
        d !== !0 || this._$AL.has(s) || l === void 0 || this.C(s, void 0, o, l);
      }
    }
    let e = !1;
    const t = this._$AL;
    try {
      e = this.shouldUpdate(t), e ? (this.willUpdate(t), (i = this._$EO) == null || i.forEach((a) => {
        var s;
        return (s = a.hostUpdate) == null ? void 0 : s.call(a);
      }), this.update(t)) : this._$EM();
    } catch (a) {
      throw e = !1, this._$EM(), a;
    }
    e && this._$AE(t);
  }
  willUpdate(e) {
  }
  _$AE(e) {
    var t;
    (t = this._$EO) == null || t.forEach((i) => {
      var a;
      return (a = i.hostUpdated) == null ? void 0 : a.call(i);
    }), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(e)), this.updated(e);
  }
  _$EM() {
    this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = !1;
  }
  get updateComplete() {
    return this.getUpdateComplete();
  }
  getUpdateComplete() {
    return this._$ES;
  }
  shouldUpdate(e) {
    return !0;
  }
  update(e) {
    this._$Eq && (this._$Eq = this._$Eq.forEach((t) => this._$ET(t, this[t]))), this._$EM();
  }
  updated(e) {
  }
  firstUpdated(e) {
  }
};
A.elementStyles = [], A.shadowRootOptions = { mode: "open" }, A[P("elementProperties")] = /* @__PURE__ */ new Map(), A[P("finalized")] = /* @__PURE__ */ new Map(), q == null || q({ ReactiveElement: A }), (x.reactiveElementVersions ?? (x.reactiveElementVersions = [])).push("2.1.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const D = globalThis, ae = (r) => r, L = D.trustedTypes, se = L ? L.createPolicy("lit-html", { createHTML: (r) => r }) : void 0, fe = "$lit$", _ = `lit$${Math.random().toFixed(9).slice(2)}$`, ge = "?" + _, Ne = `<${ge}>`, z = document, M = () => z.createComment(""), O = (r) => r === null || typeof r != "object" && typeof r != "function", X = Array.isArray, Me = (r) => X(r) || typeof (r == null ? void 0 : r[Symbol.iterator]) == "function", B = `[ 	
\f\r]`, C = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, oe = /-->/g, ne = />/g, w = RegExp(`>|${B}(?:([^\\s"'>=/]+)(${B}*=${B}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g"), de = /'/g, le = /"/g, be = /^(?:script|style|textarea|title)$/i, Oe = (r) => (e, ...t) => ({ _$litType$: r, strings: e, values: t }), n = Oe(1), E = Symbol.for("lit-noChange"), h = Symbol.for("lit-nothing"), ce = /* @__PURE__ */ new WeakMap(), S = z.createTreeWalker(z, 129);
function ye(r, e) {
  if (!X(r) || !r.hasOwnProperty("raw")) throw Error("invalid template strings array");
  return se !== void 0 ? se.createHTML(e) : e;
}
const Ue = (r, e) => {
  const t = r.length - 1, i = [];
  let a, s = e === 2 ? "<svg>" : e === 3 ? "<math>" : "", o = C;
  for (let d = 0; d < t; d++) {
    const l = r[d];
    let p, m, c = -1, b = 0;
    for (; b < l.length && (o.lastIndex = b, m = o.exec(l), m !== null); ) b = o.lastIndex, o === C ? m[1] === "!--" ? o = oe : m[1] !== void 0 ? o = ne : m[2] !== void 0 ? (be.test(m[2]) && (a = RegExp("</" + m[2], "g")), o = w) : m[3] !== void 0 && (o = w) : o === w ? m[0] === ">" ? (o = a ?? C, c = -1) : m[1] === void 0 ? c = -2 : (c = o.lastIndex - m[2].length, p = m[1], o = m[3] === void 0 ? w : m[3] === '"' ? le : de) : o === le || o === de ? o = w : o === oe || o === ne ? o = C : (o = w, a = void 0);
    const y = o === w && r[d + 1].startsWith("/>") ? " " : "";
    s += o === C ? l + Ne : c >= 0 ? (i.push(p), l.slice(0, c) + fe + l.slice(c) + _ + y) : l + _ + (c === -2 ? d : y);
  }
  return [ye(r, s + (r[t] || "<?>") + (e === 2 ? "</svg>" : e === 3 ? "</math>" : "")), i];
};
class U {
  constructor({ strings: e, _$litType$: t }, i) {
    let a;
    this.parts = [];
    let s = 0, o = 0;
    const d = e.length - 1, l = this.parts, [p, m] = Ue(e, t);
    if (this.el = U.createElement(p, i), S.currentNode = this.el.content, t === 2 || t === 3) {
      const c = this.el.content.firstChild;
      c.replaceWith(...c.childNodes);
    }
    for (; (a = S.nextNode()) !== null && l.length < d; ) {
      if (a.nodeType === 1) {
        if (a.hasAttributes()) for (const c of a.getAttributeNames()) if (c.endsWith(fe)) {
          const b = m[o++], y = a.getAttribute(c).split(_), H = /([.?@])?(.*)/.exec(b);
          l.push({ type: 1, index: s, name: H[2], strings: y, ctor: H[1] === "." ? Ie : H[1] === "?" ? He : H[1] === "@" ? je : K }), a.removeAttribute(c);
        } else c.startsWith(_) && (l.push({ type: 6, index: s }), a.removeAttribute(c));
        if (be.test(a.tagName)) {
          const c = a.textContent.split(_), b = c.length - 1;
          if (b > 0) {
            a.textContent = L ? L.emptyScript : "";
            for (let y = 0; y < b; y++) a.append(c[y], M()), S.nextNode(), l.push({ type: 2, index: ++s });
            a.append(c[b], M());
          }
        }
      } else if (a.nodeType === 8) if (a.data === ge) l.push({ type: 2, index: s });
      else {
        let c = -1;
        for (; (c = a.data.indexOf(_, c + 1)) !== -1; ) l.push({ type: 7, index: s }), c += _.length - 1;
      }
      s++;
    }
  }
  static createElement(e, t) {
    const i = z.createElement("template");
    return i.innerHTML = e, i;
  }
}
function T(r, e, t = r, i) {
  var o, d;
  if (e === E) return e;
  let a = i !== void 0 ? (o = t._$Co) == null ? void 0 : o[i] : t._$Cl;
  const s = O(e) ? void 0 : e._$litDirective$;
  return (a == null ? void 0 : a.constructor) !== s && ((d = a == null ? void 0 : a._$AO) == null || d.call(a, !1), s === void 0 ? a = void 0 : (a = new s(r), a._$AT(r, t, i)), i !== void 0 ? (t._$Co ?? (t._$Co = []))[i] = a : t._$Cl = a), a !== void 0 && (e = T(r, a._$AS(r, e.values), a, i)), e;
}
class Re {
  constructor(e, t) {
    this._$AV = [], this._$AN = void 0, this._$AD = e, this._$AM = t;
  }
  get parentNode() {
    return this._$AM.parentNode;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  u(e) {
    const { el: { content: t }, parts: i } = this._$AD, a = ((e == null ? void 0 : e.creationScope) ?? z).importNode(t, !0);
    S.currentNode = a;
    let s = S.nextNode(), o = 0, d = 0, l = i[0];
    for (; l !== void 0; ) {
      if (o === l.index) {
        let p;
        l.type === 2 ? p = new R(s, s.nextSibling, this, e) : l.type === 1 ? p = new l.ctor(s, l.name, l.strings, this, e) : l.type === 6 && (p = new We(s, this, e)), this._$AV.push(p), l = i[++d];
      }
      o !== (l == null ? void 0 : l.index) && (s = S.nextNode(), o++);
    }
    return S.currentNode = z, a;
  }
  p(e) {
    let t = 0;
    for (const i of this._$AV) i !== void 0 && (i.strings !== void 0 ? (i._$AI(e, i, t), t += i.strings.length - 2) : i._$AI(e[t])), t++;
  }
}
class R {
  get _$AU() {
    var e;
    return ((e = this._$AM) == null ? void 0 : e._$AU) ?? this._$Cv;
  }
  constructor(e, t, i, a) {
    this.type = 2, this._$AH = h, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = i, this.options = a, this._$Cv = (a == null ? void 0 : a.isConnected) ?? !0;
  }
  get parentNode() {
    let e = this._$AA.parentNode;
    const t = this._$AM;
    return t !== void 0 && (e == null ? void 0 : e.nodeType) === 11 && (e = t.parentNode), e;
  }
  get startNode() {
    return this._$AA;
  }
  get endNode() {
    return this._$AB;
  }
  _$AI(e, t = this) {
    e = T(this, e, t), O(e) ? e === h || e == null || e === "" ? (this._$AH !== h && this._$AR(), this._$AH = h) : e !== this._$AH && e !== E && this._(e) : e._$litType$ !== void 0 ? this.$(e) : e.nodeType !== void 0 ? this.T(e) : Me(e) ? this.k(e) : this._(e);
  }
  O(e) {
    return this._$AA.parentNode.insertBefore(e, this._$AB);
  }
  T(e) {
    this._$AH !== e && (this._$AR(), this._$AH = this.O(e));
  }
  _(e) {
    this._$AH !== h && O(this._$AH) ? this._$AA.nextSibling.data = e : this.T(z.createTextNode(e)), this._$AH = e;
  }
  $(e) {
    var s;
    const { values: t, _$litType$: i } = e, a = typeof i == "number" ? this._$AC(e) : (i.el === void 0 && (i.el = U.createElement(ye(i.h, i.h[0]), this.options)), i);
    if (((s = this._$AH) == null ? void 0 : s._$AD) === a) this._$AH.p(t);
    else {
      const o = new Re(a, this), d = o.u(this.options);
      o.p(t), this.T(d), this._$AH = o;
    }
  }
  _$AC(e) {
    let t = ce.get(e.strings);
    return t === void 0 && ce.set(e.strings, t = new U(e)), t;
  }
  k(e) {
    X(this._$AH) || (this._$AH = [], this._$AR());
    const t = this._$AH;
    let i, a = 0;
    for (const s of e) a === t.length ? t.push(i = new R(this.O(M()), this.O(M()), this, this.options)) : i = t[a], i._$AI(s), a++;
    a < t.length && (this._$AR(i && i._$AB.nextSibling, a), t.length = a);
  }
  _$AR(e = this._$AA.nextSibling, t) {
    var i;
    for ((i = this._$AP) == null ? void 0 : i.call(this, !1, !0, t); e !== this._$AB; ) {
      const a = ae(e).nextSibling;
      ae(e).remove(), e = a;
    }
  }
  setConnected(e) {
    var t;
    this._$AM === void 0 && (this._$Cv = e, (t = this._$AP) == null || t.call(this, e));
  }
}
class K {
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  constructor(e, t, i, a, s) {
    this.type = 1, this._$AH = h, this._$AN = void 0, this.element = e, this.name = t, this._$AM = a, this.options = s, i.length > 2 || i[0] !== "" || i[1] !== "" ? (this._$AH = Array(i.length - 1).fill(new String()), this.strings = i) : this._$AH = h;
  }
  _$AI(e, t = this, i, a) {
    const s = this.strings;
    let o = !1;
    if (s === void 0) e = T(this, e, t, 0), o = !O(e) || e !== this._$AH && e !== E, o && (this._$AH = e);
    else {
      const d = e;
      let l, p;
      for (e = s[0], l = 0; l < s.length - 1; l++) p = T(this, d[i + l], t, l), p === E && (p = this._$AH[l]), o || (o = !O(p) || p !== this._$AH[l]), p === h ? e = h : e !== h && (e += (p ?? "") + s[l + 1]), this._$AH[l] = p;
    }
    o && !a && this.j(e);
  }
  j(e) {
    e === h ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, e ?? "");
  }
}
class Ie extends K {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(e) {
    this.element[this.name] = e === h ? void 0 : e;
  }
}
class He extends K {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(e) {
    this.element.toggleAttribute(this.name, !!e && e !== h);
  }
}
class je extends K {
  constructor(e, t, i, a, s) {
    super(e, t, i, a, s), this.type = 5;
  }
  _$AI(e, t = this) {
    if ((e = T(this, e, t, 0) ?? h) === E) return;
    const i = this._$AH, a = e === h && i !== h || e.capture !== i.capture || e.once !== i.once || e.passive !== i.passive, s = e !== h && (i === h || a);
    a && this.element.removeEventListener(this.name, this, i), s && this.element.addEventListener(this.name, this, e), this._$AH = e;
  }
  handleEvent(e) {
    var t;
    typeof this._$AH == "function" ? this._$AH.call(((t = this.options) == null ? void 0 : t.host) ?? this.element, e) : this._$AH.handleEvent(e);
  }
}
class We {
  constructor(e, t, i) {
    this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = i;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(e) {
    T(this, e);
  }
}
const Y = D.litHtmlPolyfillSupport;
Y == null || Y(U, R), (D.litHtmlVersions ?? (D.litHtmlVersions = [])).push("3.3.2");
const Le = (r, e, t) => {
  const i = (t == null ? void 0 : t.renderBefore) ?? e;
  let a = i._$litPart$;
  if (a === void 0) {
    const s = (t == null ? void 0 : t.renderBefore) ?? null;
    i._$litPart$ = a = new R(e.insertBefore(M(), s), s, void 0, t ?? {});
  }
  return a._$AI(r), a;
};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const k = globalThis;
class N extends A {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    var t;
    const e = super.createRenderRoot();
    return (t = this.renderOptions).renderBefore ?? (t.renderBefore = e.firstChild), e;
  }
  update(e) {
    const t = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = Le(t, this.renderRoot, this.renderOptions);
  }
  connectedCallback() {
    var e;
    super.connectedCallback(), (e = this._$Do) == null || e.setConnected(!0);
  }
  disconnectedCallback() {
    var e;
    super.disconnectedCallback(), (e = this._$Do) == null || e.setConnected(!1);
  }
  render() {
    return E;
  }
}
var me;
N._$litElement$ = !0, N.finalized = !0, (me = k.litElementHydrateSupport) == null || me.call(k, { LitElement: N });
const F = k.litElementPolyfillSupport;
F == null || F({ LitElement: N });
(k.litElementVersions ?? (k.litElementVersions = [])).push("4.2.2");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const Ke = (r) => (e, t) => {
  t !== void 0 ? t.addInitializer(() => {
    customElements.define(r, e);
  }) : customElements.define(r, e);
};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const qe = { attribute: !0, type: String, converter: W, reflect: !1, hasChanged: J }, Be = (r = qe, e, t) => {
  const { kind: i, metadata: a } = t;
  let s = globalThis.litPropertyMetadata.get(a);
  if (s === void 0 && globalThis.litPropertyMetadata.set(a, s = /* @__PURE__ */ new Map()), i === "setter" && ((r = Object.create(r)).wrapped = !0), s.set(t.name, r), i === "accessor") {
    const { name: o } = t;
    return { set(d) {
      const l = e.get.call(this);
      e.set.call(this, d), this.requestUpdate(o, l, r, !0, d);
    }, init(d) {
      return d !== void 0 && this.C(o, void 0, r, d), d;
    } };
  }
  if (i === "setter") {
    const { name: o } = t;
    return function(d) {
      const l = this[o];
      e.call(this, d), this.requestUpdate(o, l, r, !0, d);
    };
  }
  throw Error("Unsupported decorator location: " + i);
};
function I(r) {
  return (e, t) => typeof t == "object" ? Be(r, e, t) : ((i, a, s) => {
    const o = a.hasOwnProperty(s);
    return a.constructor.createProperty(s, i), o ? Object.getOwnPropertyDescriptor(a, s) : void 0;
  })(r, e, t);
}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
function g(r) {
  return I({ ...r, state: !0, attribute: !1 });
}
const Ye = {
  due: "#ff9800",
  missed: "#f44336",
  snoozed: "#2196f3",
  ok: "#4caf50",
  prn: "#9c27b0"
}, Fe = {
  due: "mdi:bell-ring",
  missed: "mdi:alert-circle",
  snoozed: "mdi:clock-outline",
  ok: "mdi:check-circle",
  prn: "mdi:hand-extended",
  taken: "mdi:check-circle",
  skipped: "mdi:close-circle"
}, Ve = {
  tablet: "mdi:pill",
  capsule: "mdi:capsule",
  injection: "mdi:needle",
  inhaler: "mdi:air-filter",
  drops: "mdi:eyedropper",
  liquid: "mdi:cup-water",
  cream: "mdi:lotion",
  patch: "mdi:bandage",
  nasal_spray: "mdi:spray",
  suppository: "mdi:medication",
  powder: "mdi:grain",
  other: "mdi:medication"
}, Qe = [
  { id: "medications", label: "Medications", icon: "mdi:pill" },
  { id: "adherence", label: "Adherence", icon: "mdi:chart-line" },
  { id: "inventory", label: "Inventory", icon: "mdi:package-variant" },
  { id: "history", label: "History", icon: "mdi:history" },
  { id: "settings", label: "Settings", icon: "mdi:cog" }
], Ze = [
  { id: "tablet", name: "Tablet", icon: "mdi:pill" },
  { id: "capsule", name: "Capsule", icon: "mdi:capsule" },
  { id: "injection", name: "Injection", icon: "mdi:needle" },
  { id: "inhaler", name: "Inhaler", icon: "mdi:lungs" },
  { id: "drops", name: "Drops", icon: "mdi:eyedropper" },
  { id: "liquid", name: "Liquid", icon: "mdi:cup-water" },
  { id: "cream", name: "Cream", icon: "mdi:lotion" },
  { id: "patch", name: "Patch", icon: "mdi:bandage" }
], Ge = [
  { id: "times_per_day", name: "Times per Day", icon: "mdi:clock-outline" },
  { id: "interval", name: "Interval", icon: "mdi:timer-outline" },
  { id: "weekly", name: "Weekly", icon: "mdi:calendar-week" },
  { id: "as_needed", name: "As Needed (PRN)", icon: "mdi:hand-extended" }
], V = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], zt = [
  "tablet",
  "capsule",
  "ml",
  "mg",
  "puff",
  "spray",
  "drop",
  "IU",
  "mcg",
  "g"
], Je = 6e4, pe = 36e5, Xe = 864e5;
function At(r) {
  const e = (r || "ok").toLowerCase();
  return Ye[e] || "#757575";
}
function he(r) {
  const e = (r || "ok").toLowerCase();
  return Fe[e] || "mdi:pill";
}
function et(r) {
  return r && Ve[r.toLowerCase()] || "mdi:medication";
}
function tt(r) {
  if (!r) return "No schedule";
  const e = new Date(r), t = /* @__PURE__ */ new Date(), i = e.getTime() - t.getTime();
  return i < 0 ? "Overdue" : i < pe ? `${Math.floor(i / Je)}min` : i < Xe ? `${Math.floor(i / pe)}h` : e.toLocaleDateString();
}
function Et(r, e, t) {
  return e === 1 ? `${r} ${t}` : `${r}/${e} ${t}`;
}
function it(r) {
  const e = { due: [], missed: [], upcoming: [], prn: [] };
  return r.forEach((t) => {
    const i = (t.status || t.state || "ok").toLowerCase();
    i === "due" ? e.due.push(t) : i === "missed" ? e.missed.push(t) : i === "prn" ? e.prn.push(t) : e.upcoming.push(t);
  }), e;
}
function rt(r) {
  return Object.keys(r.states).filter((e) => e.startsWith("sensor.") && e.includes("_medication_")).map((e) => {
    const t = r.states[e];
    return {
      entityId: e,
      ...t.attributes,
      state: t.state,
      status: t.state || "ok"
    };
  });
}
function ue(r) {
  return Object.keys(r.states).filter((e) => e.startsWith("sensor.") && e.includes("adherence_rate")).map((e) => ({
    id: e,
    name: e.replace("sensor.", "").replace("_adherence_rate", "").split("_").map((t) => t.charAt(0).toUpperCase() + t.slice(1)).join(" ")
  }));
}
function Q(r) {
  return {
    step: 0,
    displayName: (r == null ? void 0 : r.display_name) || "",
    form: (r == null ? void 0 : r.form) || "tablet",
    scheduleKind: (r == null ? void 0 : r.schedule_kind) || "times_per_day",
    times: (r == null ? void 0 : r.times) || ["08:00"],
    weekdays: (r == null ? void 0 : r.weekdays) || [1, 2, 3, 4, 5],
    intervalMinutes: (r == null ? void 0 : r.interval_minutes) || 480,
    doseNumerator: 1,
    doseDenominator: 1,
    doseUnit: "tablet",
    inventoryEnabled: !1,
    currentQuantity: null,
    refillThreshold: null,
    notes: (r == null ? void 0 : r.notes) || "",
    errors: {}
  };
}
function at(r) {
  const e = {};
  return r.displayName.trim() || (e.displayName = "Name is required"), (r.scheduleKind === "times_per_day" || r.scheduleKind === "weekly") && r.times.length === 0 && (e.times = "At least one time is required"), r.scheduleKind === "weekly" && r.weekdays.length === 0 && (e.weekdays = "At least one weekday is required"), r.scheduleKind === "interval" && r.intervalMinutes <= 0 && (e.intervalMinutes = "Interval must be positive"), r.doseNumerator <= 0 && (e.doseNumerator = "Dose must be positive"), r.doseDenominator <= 0 && (e.doseDenominator = "Dose denominator must be positive"), e;
}
function st(r, e) {
  const t = {
    entry_id: e,
    display_name: r.displayName,
    form: r.form,
    schedule_kind: r.scheduleKind,
    default_dose: {
      numerator: r.doseNumerator,
      denominator: r.doseDenominator,
      unit: r.doseUnit
    }
  };
  return (r.scheduleKind === "times_per_day" || r.scheduleKind === "weekly") && (t.times = r.times), r.scheduleKind === "weekly" && (t.weekdays = r.weekdays), r.scheduleKind === "interval" && (t.interval_minutes = r.intervalMinutes), r.inventoryEnabled && r.currentQuantity !== null && (t.inventory = {
    current_quantity: r.currentQuantity,
    refill_threshold: r.refillThreshold
  }), r.notes && (t.notes = r.notes), t;
}
function ot(r, e) {
  const t = new Date(r, e, 1).getDay(), i = new Date(r, e + 1, 0).getDate(), a = [], s = t === 0 ? 6 : t - 1;
  for (let o = 0; o < s; o++)
    a.push({ day: 0, isEmpty: !0 });
  for (let o = 1; o <= i; o++)
    a.push({ day: o, isEmpty: !1 });
  return a;
}
function nt(r, e) {
  const t = e.filter(
    (s) => s.schedule_kind !== "as_needed"
  ).length, i = Math.floor(Math.random() * (t + 1));
  let a = "";
  if (t > 0) {
    const s = i / t;
    s === 1 ? a = "perfect" : s >= 0.8 ? a = "good" : s > 0 ? a = "partial" : a = "missed";
  }
  return { taken: i, total: t, class: a };
}
function dt(r) {
  return [
    {
      time: "08:00",
      medication: "Aspirin 100mg",
      dose: "1 tablet",
      status: "taken",
      statusText: "Taken on time"
    },
    {
      time: "12:00",
      medication: "Vitamin D",
      dose: "1 capsule",
      status: "taken",
      statusText: "Taken on time"
    },
    {
      time: "20:00",
      medication: "Blood Pressure Med",
      dose: "1/2 tablet",
      status: "snoozed",
      statusText: "Snoozed 30min"
    }
  ];
}
function lt(r, e = "long") {
  return e === "short" ? r.toLocaleDateString() : r.toLocaleDateString("en", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric"
  });
}
function ct(r, e) {
  return new Date(r, e).toLocaleDateString("en", {
    month: "long",
    year: "numeric"
  });
}
function _e(r, e) {
  return r.toDateString() === e.toDateString();
}
function pt(r) {
  return _e(r, /* @__PURE__ */ new Date());
}
const ht = $`
  :host {
    display: block;
    height: 100vh;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-family: var(--paper-font-body1_-_font-family);
  }

  .panel-container {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  /* Buttons */
  button {
    font-family: inherit;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: var(--primary-color);
    color: white;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
  }

  .btn-primary:hover {
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }

  .btn-secondary {
    padding: 8px 16px;
    background: var(--secondary-background-color);
    color: var(--primary-text-color);
    border-radius: 8px;
    font-size: 14px;
  }

  .btn-secondary:hover {
    background: var(--divider-color);
  }

  .btn-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    padding: 0;
    background: transparent;
    color: var(--secondary-text-color);
    border-radius: 50%;
  }

  .btn-icon:hover {
    background: var(--secondary-background-color);
  }

  /* Form elements */
  .form-field {
    margin-bottom: 24px;
  }

  .form-field label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: var(--primary-text-color);
  }

  .form-input {
    width: 100%;
    padding: 12px;
    border: 1px solid var(--divider-color);
    border-radius: 8px;
    background: var(--card-background-color);
    color: var(--primary-text-color);
    font-size: 14px;
    box-sizing: border-box;
  }

  .form-input:focus {
    outline: none;
    border-color: var(--primary-color);
  }

  .form-textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid var(--divider-color);
    border-radius: 8px;
    background: var(--card-background-color);
    color: var(--primary-text-color);
    font-size: 14px;
    font-family: inherit;
    resize: vertical;
    box-sizing: border-box;
  }

  .error {
    color: var(--error-color);
    font-size: 12px;
    margin-top: 4px;
  }

  /* Alerts */
  .alert {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
  }

  .alert-warning {
    background: #fff3e0;
    color: #e65100;
    border-left: 4px solid #ff9800;
  }

  /* Info box */
  .info-box {
    display: flex;
    gap: 12px;
    padding: 16px;
    background: rgba(var(--rgb-primary-color), 0.1);
    border-radius: 8px;
    color: var(--primary-text-color);
  }

  .info-box ha-icon {
    flex-shrink: 0;
    color: var(--primary-color);
  }
`, ut = $`
  .header {
    background: var(--card-background-color);
    border-bottom: 1px solid var(--divider-color);
    padding: 16px 24px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .header-content {
    display: flex;
    align-items: center;
    gap: 24px;
    max-width: 1400px;
    margin: 0 auto;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .logo ha-icon {
    --mdc-icon-size: 32px;
    color: var(--primary-color);
  }

  .logo h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 500;
  }

  .profile-select {
    padding: 8px 12px;
    border: 1px solid var(--divider-color);
    border-radius: 8px;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-size: 14px;
  }

  .header-stats {
    display: flex;
    gap: 24px;
    margin-left: auto;
  }

  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--primary-color);
  }

  .stat-label {
    font-size: 12px;
    color: var(--secondary-text-color);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
`, mt = $`
  .tabs {
    display: flex;
    background: var(--card-background-color);
    border-bottom: 1px solid var(--divider-color);
    padding: 0 24px;
    overflow-x: auto;
  }

  .tab {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 16px 20px;
    border: none;
    background: none;
    color: var(--secondary-text-color);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.2s;
  }

  .tab:hover {
    color: var(--primary-text-color);
    background: var(--secondary-background-color);
  }

  .tab.active {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
  }

  .tab ha-icon {
    --mdc-icon-size: 20px;
  }
`, vt = $`
  .med-card {
    background: var(--card-background-color);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-left: 4px solid var(--divider-color);
    transition: all 0.2s;
  }

  .med-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }

  .med-card[data-status='due'] {
    border-left-color: #ff9800;
  }

  .med-card[data-status='missed'] {
    border-left-color: #f44336;
  }

  .med-card[data-status='prn'] {
    border-left-color: #9c27b0;
  }

  .med-card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .med-card-header ha-icon {
    --mdc-icon-size: 24px;
    color: var(--primary-color);
  }

  .med-info {
    flex: 1;
  }

  .med-info h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 500;
  }

  .med-dose {
    font-size: 13px;
    color: var(--secondary-text-color);
  }

  .med-card-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
  }

  .med-detail {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--secondary-text-color);
  }

  .med-detail ha-icon {
    --mdc-icon-size: 16px;
  }

  .med-detail.inventory .warning {
    color: #ff9800;
    margin-left: auto;
  }

  .med-card-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
  }

  .action-btn.take {
    background: #4caf50;
    color: white;
    flex: 1;
  }

  .action-btn.snooze {
    background: #2196f3;
    color: white;
  }

  .action-btn.skip {
    background: #f44336;
    color: white;
  }

  .action-btn ha-icon {
    --mdc-icon-size: 16px;
  }

  .status-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    background: var(--secondary-background-color);
  }

  .status-badge.status-ok {
    color: #4caf50;
  }
`, ft = $`
  .wizard-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 24px;
  }

  .wizard {
    background: var(--card-background-color);
    border-radius: 16px;
    width: 100%;
    max-width: 600px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }

  .wizard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid var(--divider-color);
  }

  .wizard-header h2 {
    margin: 0;
    font-size: 20px;
  }

  .wizard-content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
  }

  .wizard-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 20px 24px;
    border-top: 1px solid var(--divider-color);
  }

  .wizard-stepper {
    display: flex;
    align-items: center;
    padding: 24px;
    border-bottom: 1px solid var(--divider-color);
    overflow-x: auto;
  }

  .wizard-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    min-width: 80px;
  }

  .step-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--card-background-color);
    border: 2px solid var(--divider-color);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: var(--secondary-text-color);
  }

  .wizard-step.active .step-circle {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
  }

  .wizard-step.completed .step-circle {
    background: var(--success-color);
    border-color: var(--success-color);
    color: white;
  }

  .step-label {
    font-size: 12px;
    color: var(--secondary-text-color);
  }

  .wizard-step.active .step-label {
    color: var(--primary-text-color);
    font-weight: 600;
  }

  .step-line {
    flex: 1;
    height: 2px;
    background: var(--divider-color);
    margin: 0 8px;
    min-width: 20px;
  }

  .wizard-section {
    max-width: 600px;
    margin: 0 auto;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
  }

  .form-option {
    padding: 16px;
    border: 2px solid var(--divider-color);
    border-radius: 8px;
    background: var(--card-background-color);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    transition: all 0.2s;
  }

  .form-option:hover {
    border-color: var(--primary-color);
  }

  .form-option.selected {
    border-color: var(--primary-color);
    background: rgba(var(--rgb-primary-color), 0.1);
  }

  .schedule-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
  }

  .schedule-option {
    padding: 16px;
    border: 2px solid var(--divider-color);
    border-radius: 8px;
    background: var(--card-background-color);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    transition: all 0.2s;
  }

  .schedule-option:hover {
    border-color: var(--primary-color);
  }

  .schedule-option.selected {
    border-color: var(--primary-color);
    background: rgba(var(--rgb-primary-color), 0.1);
  }

  .time-row {
    display: flex;
    gap: 12px;
    margin-bottom: 8px;
  }

  .time-row .form-input {
    flex: 1;
  }

  .weekday-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
  }

  .weekday-btn {
    padding: 12px 8px;
    border: 2px solid var(--divider-color);
    border-radius: 8px;
    background: var(--card-background-color);
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
  }

  .weekday-btn:hover {
    border-color: var(--primary-color);
  }

  .weekday-btn.selected {
    border-color: var(--primary-color);
    background: var(--primary-color);
    color: white;
  }

  .dose-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .dose-input {
    width: 80px;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
  }

  .checkbox-label input[type='checkbox'] {
    width: 20px;
    height: 20px;
    cursor: pointer;
  }

  .review {
    background: var(--card-background-color);
    border-radius: 12px;
    padding: 24px;
  }

  .review h3 {
    margin: 0 0 24px 0;
  }

  .review-item {
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid var(--divider-color);
  }

  .review-item:last-child {
    border-bottom: none;
  }

  .review-label {
    font-weight: 500;
    color: var(--secondary-text-color);
  }

  .review-value {
    color: var(--primary-text-color);
    text-align: right;
  }
`, gt = $`
  .calendar-nav {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .calendar-nav span {
    font-weight: 600;
    font-size: 18px;
  }

  .calendar {
    margin-top: 24px;
  }

  .calendar-header {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
    margin-bottom: 8px;
  }

  .calendar-weekday {
    text-align: center;
    font-weight: 600;
    font-size: 12px;
    color: var(--secondary-text-color);
    padding: 16px;
  }

  .calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
  }

  .calendar-day {
    aspect-ratio: 1;
    padding: 8px;
    border-radius: 8px;
    background: var(--card-background-color);
    border: 2px solid var(--divider-color);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    transition: all 0.2s;
  }

  .calendar-day:hover {
    border-color: var(--primary-color);
    transform: scale(1.05);
  }

  .calendar-day.empty {
    background: transparent;
    border: none;
    cursor: default;
  }

  .calendar-day.empty:hover {
    transform: none;
  }

  .calendar-day.today {
    border-color: var(--primary-color);
    font-weight: 700;
  }

  .calendar-day.selected {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
  }

  .calendar-day.perfect {
    background: var(--success-color);
    border-color: var(--success-color);
    color: white;
  }

  .calendar-day.good {
    background: rgba(var(--rgb-success-color, 76, 175, 80), 0.5);
    border-color: var(--success-color);
  }

  .calendar-day.partial {
    background: rgba(var(--rgb-warning-color, 255, 152, 0), 0.5);
    border-color: var(--warning-color);
  }

  .calendar-day.missed {
    background: rgba(var(--rgb-error-color, 244, 67, 54), 0.5);
    border-color: var(--error-color);
  }

  .day-number {
    font-size: 16px;
    font-weight: 600;
  }

  .day-doses {
    font-size: 11px;
    opacity: 0.8;
  }

  .calendar-legend {
    display: flex;
    gap: 24px;
    margin-top: 16px;
    justify-content: center;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .legend-color {
    width: 20px;
    height: 20px;
    border-radius: 4px;
  }

  .legend-color.perfect {
    background: var(--success-color);
  }

  .legend-color.good {
    background: rgba(var(--rgb-success-color, 76, 175, 80), 0.5);
  }

  .legend-color.partial {
    background: rgba(var(--rgb-warning-color, 255, 152, 0), 0.5);
  }

  .legend-color.missed {
    background: rgba(var(--rgb-error-color, 244, 67, 54), 0.5);
  }

  .day-details {
    margin-top: 32px;
    padding: 24px;
    background: var(--card-background-color);
    border-radius: 12px;
  }

  .day-details h3 {
    margin: 0 0 16px 0;
  }

  .no-data {
    text-align: center;
    color: var(--secondary-text-color);
    padding: 32px;
  }

  .events-timeline {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .event-item {
    display: flex;
    gap: 16px;
    padding: 12px;
    border-radius: 8px;
    border-left: 4px solid var(--divider-color);
    background: var(--primary-background-color);
  }

  .event-item.taken {
    border-left-color: var(--success-color);
  }

  .event-item.snoozed {
    border-left-color: var(--warning-color);
  }

  .event-item.skipped,
  .event-item.missed {
    border-left-color: var(--error-color);
  }

  .event-time {
    font-weight: 600;
    font-size: 16px;
    min-width: 60px;
  }

  .event-content {
    flex: 1;
  }

  .event-medication {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .event-dose {
    font-size: 14px;
    color: var(--secondary-text-color);
    margin-bottom: 8px;
  }

  .event-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }
`, bt = $`
  .content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
    box-sizing: border-box;
  }

  .content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .content-header h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 500;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .med-section {
    margin-bottom: 32px;
  }

  .med-section h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 500;
    color: var(--secondary-text-color);
  }

  .med-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
  }

  .inventory-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .inventory-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: var(--card-background-color);
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  }

  .item-info h4 {
    margin: 0 0 4px 0;
    font-size: 16px;
  }

  .item-info span {
    font-size: 14px;
    color: var(--secondary-text-color);
  }
`, yt = $`
  @media (max-width: 768px) {
    .header-stats {
      display: none;
    }

    .med-list {
      grid-template-columns: 1fr;
    }

    .tab span {
      display: none;
    }

    .calendar-grid {
      gap: 4px;
    }

    .calendar-day {
      padding: 4px;
    }

    .day-number {
      font-size: 14px;
    }

    .day-doses {
      font-size: 10px;
    }

    .wizard-stepper {
      overflow-x: auto;
    }

    .step-label {
      display: none;
    }
  }
`;
var xe = Object.defineProperty, _t = Object.getOwnPropertyDescriptor, xt = (r, e, t) => e in r ? xe(r, e, { enumerable: !0, configurable: !0, writable: !0, value: t }) : r[e] = t, f = (r, e, t, i) => {
  for (var a = i > 1 ? void 0 : i ? _t(e, t) : e, s = r.length - 1, o; s >= 0; s--)
    (o = r[s]) && (a = (i ? o(e, t, a) : o(a)) || a);
  return i && a && xe(e, t, a), a;
}, $t = (r, e, t) => xt(r, e + "", t);
let u = class extends N {
  constructor() {
    super(...arguments);
    v(this, "hass");
    v(this, "narrow", !1);
    v(this, "route");
    v(this, "panel");
    v(this, "_activeTab", "medications");
    v(this, "_selectedProfile", null);
    v(this, "_medications", []);
    v(this, "_wizardOpen", !1);
    v(this, "_editingMed", null);
    v(this, "_loading", !1);
    v(this, "_wizardState", null);
    v(this, "_historyMonth", (/* @__PURE__ */ new Date()).getMonth());
    v(this, "_historyYear", (/* @__PURE__ */ new Date()).getFullYear());
    v(this, "_selectedDate", null);
  }
  connectedCallback() {
    super.connectedCallback(), this._loadProfiles();
  }
  updated(e) {
    e.has("hass") && this.hass && this._updateMedications();
  }
  _loadProfiles() {
    if (!this.hass) return;
    const e = ue(this.hass);
    e.length > 0 && !this._selectedProfile && (this._selectedProfile = e[0].id);
  }
  _updateMedications() {
    this.hass && (this._medications = rt(this.hass));
  }
  async _callService(e, t) {
    if (this.hass) {
      this._loading = !0;
      try {
        await this.hass.callService("med_expert", e, t), this._showToast(`${e} successful`, "success");
      } catch (i) {
        console.error("Service call failed:", i), this._showToast(
          `Failed: ${i instanceof Error ? i.message : "Unknown error"}`,
          "error"
        );
      } finally {
        this._loading = !1;
      }
    }
  }
  _showToast(e, t = "info") {
    const i = new CustomEvent("hass-notification", {
      detail: { message: e, duration: 3e3 },
      bubbles: !0,
      composed: !0
    });
    this.dispatchEvent(i);
  }
  _getProfiles() {
    return this.hass ? ue(this.hass) : [];
  }
  _getProfileId() {
    return this._selectedProfile;
  }
  async _handleAction(e, t) {
    const i = this._getProfileId();
    if (i)
      switch (e) {
        case "take":
        case "prn-take":
          await this._callService(e === "prn-take" ? "prn_take" : "take", {
            entry_id: i,
            medication_id: t
          });
          break;
        case "snooze":
          await this._callService("snooze", {
            entry_id: i,
            medication_id: t,
            minutes: 15
          });
          break;
        case "skip":
          await this._callService("skip", {
            entry_id: i,
            medication_id: t
          });
          break;
      }
  }
  _editMedication(e) {
    this._editingMed = e, this._wizardState = Q(e), this._wizardOpen = !0;
  }
  _openWizard() {
    this._wizardState = Q(), this._wizardOpen = !0;
  }
  _closeWizard() {
    this._wizardOpen = !1, this._editingMed = null, this._wizardState = null;
  }
  async _submitWizard() {
    if (!this._wizardState) return;
    const e = at(this._wizardState);
    if (Object.keys(e).length > 0) {
      this._wizardState = { ...this._wizardState, errors: e };
      return;
    }
    const t = this._getProfileId();
    if (!t) return;
    const i = st(this._wizardState, t);
    await this._callService("add_medication", i), this._closeWizard();
  }
  _changeMonth(e) {
    const t = new Date(this._historyYear, this._historyMonth + e, 1);
    this._historyMonth = t.getMonth(), this._historyYear = t.getFullYear();
  }
  _selectDay(e) {
    this._selectedDate = e;
  }
  async _refillMedication(e) {
    const t = prompt("Enter quantity to add:", "30");
    t && await this._callService("refill", {
      entry_id: this._getProfileId(),
      medication_id: e.medication_id,
      quantity: parseInt(t)
    });
  }
  render() {
    return this._loading ? n`
        <div class="panel-container loading">
          <ha-icon icon="mdi:loading" class="spin"></ha-icon>
          <span>Loading...</span>
        </div>
      ` : n`
      <div class="panel-container">
        ${this._renderHeader()} ${this._renderTabs()} ${this._renderContent()}
        ${this._wizardOpen ? this._renderWizard() : ""}
      </div>
    `;
  }
  _renderHeader() {
    var a, s, o;
    const e = this._getProfiles(), t = (s = (a = this.hass) == null ? void 0 : a.states) == null ? void 0 : s[this._selectedProfile || ""], i = (t == null ? void 0 : t.state) || "N/A";
    return n`
      <header class="header">
        <div class="header-content">
          <div class="logo">
            <ha-icon icon="mdi:pill"></ha-icon>
            <h1>Med Expert</h1>
          </div>

          ${e.length > 1 ? n`
                <select
                  class="profile-select"
                  @change=${(d) => this._selectedProfile = d.target.value}
                >
                  ${e.map(
      (d) => n`
                      <option
                        value="${d.id}"
                        ?selected=${d.id === this._selectedProfile}
                      >
                        ${d.name}
                      </option>
                    `
    )}
                </select>
              ` : n`<h2>${(o = e[0]) == null ? void 0 : o.name}</h2>`}

          <div class="header-stats">
            <div class="stat">
              <span class="stat-value">${this._medications.length}</span>
              <span class="stat-label">Medications</span>
            </div>
            <div class="stat">
              <span class="stat-value">${i}%</span>
              <span class="stat-label">Adherence</span>
            </div>
          </div>
        </div>
      </header>
    `;
  }
  _renderTabs() {
    return n`
      <nav class="tabs">
        ${Qe.map(
      (e) => n`
            <button
              class="tab ${this._activeTab === e.id ? "active" : ""}"
              @click=${() => this._activeTab = e.id}
            >
              <ha-icon icon="${e.icon}"></ha-icon>
              ${this.narrow ? "" : n`<span>${e.label}</span>`}
            </button>
          `
    )}
      </nav>
    `;
  }
  _renderContent() {
    switch (this._activeTab) {
      case "medications":
        return this._renderMedicationsTab();
      case "adherence":
        return this._renderAdherenceTab();
      case "inventory":
        return this._renderInventoryTab();
      case "history":
        return this._renderHistoryTab();
      case "settings":
        return this._renderSettingsTab();
      default:
        return n`<div>Unknown tab</div>`;
    }
  }
  _renderMedicationsTab() {
    const e = it(this._medications);
    return n`
      <div class="content medications-content">
        <div class="content-header">
          <h2>Your Medications</h2>
          <button class="btn-primary" @click=${this._openWizard}>
            <ha-icon icon="mdi:plus"></ha-icon>
            Add Medication
          </button>
        </div>

        ${e.due.length > 0 ? n`
              <section class="med-section">
                <h3><ha-icon icon="mdi:bell-ring"></ha-icon> Due Now</h3>
                <div class="med-list">
                  ${e.due.map((t) => this._renderMedicationCard(t))}
                </div>
              </section>
            ` : ""}
        ${e.missed.length > 0 ? n`
              <section class="med-section">
                <h3><ha-icon icon="mdi:alert-circle"></ha-icon> Missed</h3>
                <div class="med-list">
                  ${e.missed.map((t) => this._renderMedicationCard(t))}
                </div>
              </section>
            ` : ""}
        ${e.upcoming.length > 0 ? n`
              <section class="med-section">
                <h3><ha-icon icon="mdi:clock-outline"></ha-icon> Upcoming</h3>
                <div class="med-list">
                  ${e.upcoming.map((t) => this._renderMedicationCard(t))}
                </div>
              </section>
            ` : ""}
        ${e.prn.length > 0 ? n`
              <section class="med-section">
                <h3><ha-icon icon="mdi:hand-extended"></ha-icon> As Needed</h3>
                <div class="med-list">
                  ${e.prn.map((t) => this._renderMedicationCard(t))}
                </div>
              </section>
            ` : ""}
      </div>
    `;
  }
  _renderMedicationCard(e) {
    const t = (e.status || e.state || "ok").toLowerCase(), i = t === "prn", a = t === "due" || t === "missed";
    return n`
      <div class="med-card" data-status="${t}">
        <div class="med-card-header">
          <ha-icon icon="${et(e.form)}"></ha-icon>
          <div class="med-info">
            <h4>${e.display_name || e.medication_name || "Unknown"}</h4>
            <span class="med-dose">${e.default_dose || "Dose not specified"}</span>
          </div>
          <button class="btn-icon" @click=${() => this._editMedication(e)}>
            <ha-icon icon="mdi:pencil"></ha-icon>
          </button>
        </div>

        <div class="med-card-body">
          <div class="med-detail">
            <ha-icon icon="mdi:clock-outline"></ha-icon>
            <span>${tt(e.next_dose_at)}</span>
          </div>

          ${e.inventory ? n`
                <div class="med-detail inventory">
                  <ha-icon icon="mdi:package-variant"></ha-icon>
                  <span
                    >${e.inventory.current_quantity || 0}
                    ${e.inventory.unit || "units"}</span
                  >
                  ${e.inventory.low_stock ? n` <ha-icon class="warning" icon="mdi:alert"></ha-icon> ` : ""}
                </div>
              ` : ""}
        </div>

        <div class="med-card-actions">
          ${i ? n`
                <button
                  class="action-btn take"
                  @click=${() => this._handleAction("prn-take", e.medication_id)}
                >
                  <ha-icon icon="mdi:check"></ha-icon>
                  Take as needed
                </button>
              ` : a ? n`
                  <button
                    class="action-btn take"
                    @click=${() => this._handleAction("take", e.medication_id)}
                  >
                    <ha-icon icon="mdi:check"></ha-icon>
                    Taken
                  </button>
                  <button
                    class="action-btn snooze"
                    @click=${() => this._handleAction("snooze", e.medication_id)}
                  >
                    <ha-icon icon="mdi:clock-outline"></ha-icon>
                    Snooze
                  </button>
                  <button
                    class="action-btn skip"
                    @click=${() => this._handleAction("skip", e.medication_id)}
                  >
                    <ha-icon icon="mdi:close"></ha-icon>
                    Skip
                  </button>
                ` : n`
                  <span class="status-badge status-${t}">
                    <ha-icon icon="${he(t)}"></ha-icon>
                    ${t.toUpperCase()}
                  </span>
                `}
        </div>
      </div>
    `;
  }
  _renderAdherenceTab() {
    return n`
      <div class="content">
        <h2>Adherence Statistics</h2>
        <p>Coming soon: Charts and adherence tracking</p>
      </div>
    `;
  }
  _renderInventoryTab() {
    const e = this._medications.filter((t) => {
      var i;
      return (i = t.inventory) == null ? void 0 : i.low_stock;
    });
    return n`
      <div class="content">
        <h2>Inventory Management</h2>

        ${e.length > 0 ? n`
              <div class="alert alert-warning">
                <ha-icon icon="mdi:alert"></ha-icon>
                <span>${e.length} medication(s) running low</span>
              </div>
            ` : ""}

        <div class="inventory-list">
          ${this._medications.filter((t) => t.inventory).map(
      (t) => {
        var i, a;
        return n`
                <div class="inventory-item">
                  <div class="item-info">
                    <h4>${t.display_name}</h4>
                    <span
                      >${((i = t.inventory) == null ? void 0 : i.current_quantity) || 0}
                      ${((a = t.inventory) == null ? void 0 : a.unit) || "units"}</span
                    >
                  </div>
                  <button
                    class="btn-secondary"
                    @click=${() => this._refillMedication(t)}
                  >
                    <ha-icon icon="mdi:plus"></ha-icon>
                    Refill
                  </button>
                </div>
              `;
      }
    )}
        </div>
      </div>
    `;
  }
  _renderHistoryTab() {
    const e = /* @__PURE__ */ new Date();
    return n`
      <div class="content">
        <div class="section-header">
          <h2>Calendar View</h2>
          <div class="calendar-nav">
            <button class="btn-icon" @click=${() => this._changeMonth(-1)}>
              <ha-icon icon="mdi:chevron-left"></ha-icon>
            </button>
            <span>${ct(this._historyYear, this._historyMonth)}</span>
            <button class="btn-icon" @click=${() => this._changeMonth(1)}>
              <ha-icon icon="mdi:chevron-right"></ha-icon>
            </button>
            <button
              class="btn-secondary"
              @click=${() => {
      this._historyMonth = e.getMonth(), this._historyYear = e.getFullYear();
    }}
            >
              Today
            </button>
          </div>
        </div>

        ${this._renderCalendar()} ${this._renderDayDetails()}
      </div>
    `;
  }
  _renderCalendar() {
    const e = ot(this._historyYear, this._historyMonth);
    return n`
      <div class="calendar">
        <div class="calendar-header">
          ${V.map(
      (t) => n` <div class="calendar-weekday">${t}</div> `
    )}
        </div>
        <div class="calendar-grid">
          ${e.map((t) => {
      if (t.isEmpty)
        return n`<div class="calendar-day empty"></div>`;
      const i = new Date(
        this._historyYear,
        this._historyMonth,
        t.day
      ), a = nt(i, this._medications), s = this._selectedDate && _e(i, this._selectedDate);
      return n`
              <div
                class="calendar-day ${pt(i) ? "today" : ""} ${s ? "selected" : ""} ${a.class}"
                @click=${() => this._selectDay(i)}
              >
                <span class="day-number">${t.day}</span>
                ${a.taken > 0 || a.total > 0 ? n`
                      <span class="day-doses"
                        >${a.taken}/${a.total}</span
                      >
                    ` : ""}
              </div>
            `;
    })}
        </div>
        <div class="calendar-legend">
          <div class="legend-item">
            <div class="legend-color perfect"></div>
            <span>Perfect</span>
          </div>
          <div class="legend-item">
            <div class="legend-color good"></div>
            <span>Good</span>
          </div>
          <div class="legend-item">
            <div class="legend-color partial"></div>
            <span>Partial</span>
          </div>
          <div class="legend-item">
            <div class="legend-color missed"></div>
            <span>Missed</span>
          </div>
        </div>
      </div>
    `;
  }
  _renderDayDetails() {
    if (!this._selectedDate) return "";
    const e = dt(this._selectedDate);
    return n`
      <div class="day-details">
        <h3>${lt(this._selectedDate)}</h3>
        ${e.length === 0 ? n` <p class="no-data">No medication events on this day</p> ` : n`
              <div class="events-timeline">
                ${e.map(
      (t) => n`
                    <div class="event-item ${t.status}">
                      <div class="event-time">${t.time}</div>
                      <div class="event-content">
                        <div class="event-medication">${t.medication}</div>
                        <div class="event-dose">${t.dose}</div>
                        <div class="event-status">
                          <ha-icon icon="${he(t.status)}"></ha-icon>
                          ${t.statusText}
                        </div>
                      </div>
                    </div>
                  `
    )}
              </div>
            `}
      </div>
    `;
  }
  _renderSettingsTab() {
    return n`
      <div class="content">
        <h2>Profile Settings</h2>
        <p>Coming soon: Notification settings, quiet hours, etc.</p>
      </div>
    `;
  }
  _renderWizard() {
    this._wizardState || (this._wizardState = Q(
      this._editingMed || void 0
    ));
    const e = ["Basics", "Schedule", "Dosage", "Options", "Review"], t = this._wizardState;
    return n`
      <div
        class="wizard-overlay"
        @click=${(i) => i.target === i.currentTarget && this._closeWizard()}
      >
        <div class="wizard">
          <div class="wizard-header">
            <h2>${this._editingMed ? "Edit" : "Add"} Medication</h2>
            <button class="btn-icon" @click=${this._closeWizard}>
              <ha-icon icon="mdi:close"></ha-icon>
            </button>
          </div>

          <div class="wizard-stepper">
            ${e.map(
      (i, a) => n`
                <div
                  class="wizard-step ${a === t.step ? "active" : ""} ${a < t.step ? "completed" : ""}"
                >
                  <div class="step-circle">${a < t.step ? "✓" : a + 1}</div>
                  <span class="step-label">${i}</span>
                </div>
                ${a < e.length - 1 ? n`<div class="step-line"></div>` : ""}
              `
    )}
          </div>

          <div class="wizard-content">
            ${t.step === 0 ? this._renderWizardBasics() : ""}
            ${t.step === 1 ? this._renderWizardSchedule() : ""}
            ${t.step === 2 ? this._renderWizardDosage() : ""}
            ${t.step === 3 ? this._renderWizardOptions() : ""}
            ${t.step === 4 ? this._renderWizardReview() : ""}
          </div>

          <div class="wizard-footer">
            <button class="btn-secondary" @click=${this._closeWizard}>
              Cancel
            </button>
            ${t.step > 0 ? n`
                  <button
                    class="btn-secondary"
                    @click=${() => {
      this._wizardState && (this._wizardState = { ...this._wizardState, step: t.step - 1 });
    }}
                  >
                    Back
                  </button>
                ` : ""}
            ${t.step < 4 ? n`
                  <button
                    class="btn-primary"
                    @click=${() => {
      this._wizardState && (this._wizardState = { ...this._wizardState, step: t.step + 1 });
    }}
                  >
                    Next
                  </button>
                ` : n`
                  <button class="btn-primary" @click=${this._submitWizard}>
                    ${this._editingMed ? "Save Changes" : "Add Medication"}
                  </button>
                `}
          </div>
        </div>
      </div>
    `;
  }
  _renderWizardBasics() {
    const e = this._wizardState;
    return n`
      <div class="wizard-section">
        <div class="form-field">
          <label>Medication Name *</label>
          <input
            type="text"
            .value=${e.displayName}
            @input=${(t) => {
      this._wizardState && (this._wizardState = {
        ...this._wizardState,
        displayName: t.target.value
      });
    }}
            placeholder="e.g., Aspirin, Metformin"
            class="form-input"
          />
          ${e.errors.displayName ? n`<span class="error">${e.errors.displayName}</span>` : ""}
        </div>

        <div class="form-field">
          <label>Dosage Form</label>
          <div class="form-grid">
            ${Ze.map(
      (t) => n`
                <button
                  class="form-option ${e.form === t.id ? "selected" : ""}"
                  @click=${() => {
        this._wizardState && (this._wizardState = { ...this._wizardState, form: t.id });
      }}
                >
                  <ha-icon icon="${t.icon}"></ha-icon>
                  <span>${t.name}</span>
                </button>
              `
    )}
          </div>
        </div>
      </div>
    `;
  }
  _renderWizardSchedule() {
    const e = this._wizardState;
    return n`
      <div class="wizard-section">
        <div class="form-field">
          <label>Schedule Type</label>
          <div class="schedule-grid">
            ${Ge.map(
      (t) => n`
                <button
                  class="schedule-option ${e.scheduleKind === t.id ? "selected" : ""}"
                  @click=${() => {
        this._wizardState && (this._wizardState = {
          ...this._wizardState,
          scheduleKind: t.id
        });
      }}
                >
                  <ha-icon icon="${t.icon}"></ha-icon>
                  <span>${t.name}</span>
                </button>
              `
    )}
          </div>
        </div>

        ${e.scheduleKind === "times_per_day" || e.scheduleKind === "weekly" ? n`
              <div class="form-field">
                <label>Times</label>
                ${e.times.map(
      (t, i) => n`
                    <div class="time-row">
                      <input
                        type="time"
                        .value=${t}
                        @change=${(a) => {
        if (this._wizardState) {
          const s = [...this._wizardState.times];
          s[i] = a.target.value, this._wizardState = {
            ...this._wizardState,
            times: s
          };
        }
      }}
                        class="form-input"
                      />
                      ${e.times.length > 1 ? n`
                            <button
                              class="btn-icon"
                              @click=${() => {
        if (this._wizardState) {
          const a = this._wizardState.times.filter(
            (s, o) => o !== i
          );
          this._wizardState = {
            ...this._wizardState,
            times: a
          };
        }
      }}
                            >
                              <ha-icon icon="mdi:delete"></ha-icon>
                            </button>
                          ` : ""}
                    </div>
                  `
    )}
                <button
                  class="btn-secondary"
                  @click=${() => {
      this._wizardState && (this._wizardState = {
        ...this._wizardState,
        times: [...this._wizardState.times, "12:00"]
      });
    }}
                >
                  <ha-icon icon="mdi:plus"></ha-icon>
                  Add Time
                </button>
              </div>
            ` : ""}
        ${e.scheduleKind === "weekly" ? n`
              <div class="form-field">
                <label>Weekdays</label>
                <div class="weekday-grid">
                  ${V.map(
      (t, i) => n`
                      <button
                        class="weekday-btn ${e.weekdays.includes(i + 1) ? "selected" : ""}"
                        @click=${() => {
        if (this._wizardState) {
          const a = i + 1, s = e.weekdays.includes(a) ? e.weekdays.filter((o) => o !== a) : [...e.weekdays, a];
          this._wizardState = {
            ...this._wizardState,
            weekdays: s
          };
        }
      }}
                      >
                        ${t}
                      </button>
                    `
    )}
                </div>
              </div>
            ` : ""}
        ${e.scheduleKind === "interval" ? n`
              <div class="form-field">
                <label>Interval (hours)</label>
                <input
                  type="number"
                  .value=${(e.intervalMinutes / 60).toString()}
                  @input=${(t) => {
      this._wizardState && (this._wizardState = {
        ...this._wizardState,
        intervalMinutes: parseInt(t.target.value) * 60
      });
    }}
                  min="1"
                  max="24"
                  class="form-input"
                />
              </div>
            ` : ""}
        ${e.scheduleKind === "as_needed" ? n`
              <div class="info-box">
                <ha-icon icon="mdi:information"></ha-icon>
                <p>
                  This medication can be taken as needed (PRN). No fixed schedule
                  will be set.
                </p>
              </div>
            ` : ""}
      </div>
    `;
  }
  _renderWizardDosage() {
    const e = this._wizardState;
    return n`
      <div class="wizard-section">
        <div class="form-field">
          <label>Default Dose</label>
          <div class="dose-row">
            <input
              type="number"
              .value=${e.doseNumerator.toString()}
              @input=${(t) => {
      this._wizardState && (this._wizardState = {
        ...this._wizardState,
        doseNumerator: parseInt(t.target.value)
      });
    }}
              min="1"
              class="form-input dose-input"
              placeholder="1"
            />
            <span>/</span>
            <input
              type="number"
              .value=${e.doseDenominator.toString()}
              @input=${(t) => {
      this._wizardState && (this._wizardState = {
        ...this._wizardState,
        doseDenominator: parseInt(t.target.value)
      });
    }}
              min="1"
              class="form-input dose-input"
              placeholder="1"
            />
            <input
              type="text"
              .value=${e.doseUnit}
              @input=${(t) => {
      this._wizardState && (this._wizardState = {
        ...this._wizardState,
        doseUnit: t.target.value
      });
    }}
              class="form-input"
              placeholder="tablet"
              list="units-list"
            />
            <datalist id="units-list">
              <option>tablet</option>
              <option>capsule</option>
              <option>ml</option>
              <option>mg</option>
              <option>puff</option>
              <option>spray</option>
              <option>drop</option>
            </datalist>
          </div>
          <small>e.g., 1/2 tablet or 2/1 ml</small>
        </div>
      </div>
    `;
  }
  _renderWizardOptions() {
    var t, i;
    const e = this._wizardState;
    return n`
      <div class="wizard-section">
        <div class="form-field">
          <label class="checkbox-label">
            <input
              type="checkbox"
              .checked=${e.inventoryEnabled}
              @change=${(a) => {
      this._wizardState && (this._wizardState = {
        ...this._wizardState,
        inventoryEnabled: a.target.checked
      });
    }}
            />
            <span>Track Inventory</span>
          </label>
        </div>

        ${e.inventoryEnabled ? n`
              <div class="form-field">
                <label>Current Quantity</label>
                <input
                  type="number"
                  .value=${((t = e.currentQuantity) == null ? void 0 : t.toString()) || ""}
                  @input=${(a) => {
      this._wizardState && (this._wizardState = {
        ...this._wizardState,
        currentQuantity: parseInt(a.target.value) || null
      });
    }}
                  min="0"
                  class="form-input"
                  placeholder="e.g., 30"
                />
              </div>

              <div class="form-field">
                <label>Refill Threshold</label>
                <input
                  type="number"
                  .value=${((i = e.refillThreshold) == null ? void 0 : i.toString()) || ""}
                  @input=${(a) => {
      this._wizardState && (this._wizardState = {
        ...this._wizardState,
        refillThreshold: parseInt(a.target.value) || null
      });
    }}
                  min="0"
                  class="form-input"
                  placeholder="e.g., 5"
                />
                <small>Get notified when inventory drops below this amount</small>
              </div>
            ` : ""}

        <div class="form-field">
          <label>Notes (optional)</label>
          <textarea
            .value=${e.notes}
            @input=${(a) => {
      this._wizardState && (this._wizardState = {
        ...this._wizardState,
        notes: a.target.value
      });
    }}
            class="form-textarea"
            placeholder="Additional information..."
            rows="3"
          ></textarea>
        </div>
      </div>
    `;
  }
  _renderWizardReview() {
    const e = this._wizardState;
    return n`
      <div class="wizard-section review">
        <h3>Review Medication</h3>

        <div class="review-item">
          <span class="review-label">Name:</span>
          <span class="review-value">${e.displayName}</span>
        </div>

        <div class="review-item">
          <span class="review-label">Form:</span>
          <span class="review-value">${e.form}</span>
        </div>

        <div class="review-item">
          <span class="review-label">Schedule:</span>
          <span class="review-value">
            ${e.scheduleKind === "times_per_day" ? `${e.times.length}x daily at ${e.times.join(", ")}` : ""}
            ${e.scheduleKind === "interval" ? `Every ${e.intervalMinutes / 60} hours` : ""}
            ${e.scheduleKind === "weekly" ? `Weekly on ${e.weekdays.map((t) => V[t - 1]).join(", ")}` : ""}
            ${e.scheduleKind === "as_needed" ? "As needed (PRN)" : ""}
          </span>
        </div>

        <div class="review-item">
          <span class="review-label">Dose:</span>
          <span class="review-value"
            >${e.doseNumerator}/${e.doseDenominator} ${e.doseUnit}</span
          >
        </div>

        ${e.inventoryEnabled ? n`
              <div class="review-item">
                <span class="review-label">Inventory:</span>
                <span class="review-value">
                  ${e.currentQuantity || 0} units (refill at
                  ${e.refillThreshold || 0})
                </span>
              </div>
            ` : ""}
        ${e.notes ? n`
              <div class="review-item">
                <span class="review-label">Notes:</span>
                <span class="review-value">${e.notes}</span>
              </div>
            ` : ""}
      </div>
    `;
  }
};
$t(u, "styles", [
  ht,
  ut,
  mt,
  vt,
  ft,
  gt,
  bt,
  yt
]);
f([
  I({ type: Object })
], u.prototype, "hass", 2);
f([
  I({ type: Boolean })
], u.prototype, "narrow", 2);
f([
  I({ type: Object })
], u.prototype, "route", 2);
f([
  I({ type: Object })
], u.prototype, "panel", 2);
f([
  g()
], u.prototype, "_activeTab", 2);
f([
  g()
], u.prototype, "_selectedProfile", 2);
f([
  g()
], u.prototype, "_medications", 2);
f([
  g()
], u.prototype, "_wizardOpen", 2);
f([
  g()
], u.prototype, "_editingMed", 2);
f([
  g()
], u.prototype, "_loading", 2);
f([
  g()
], u.prototype, "_wizardState", 2);
f([
  g()
], u.prototype, "_historyMonth", 2);
f([
  g()
], u.prototype, "_historyYear", 2);
f([
  g()
], u.prototype, "_selectedDate", 2);
u = f([
  Ke("med-expert-panel")
], u);
export {
  zt as DOSE_UNITS,
  Ve as FORM_ICONS,
  Ze as FORM_OPTIONS,
  Xe as MS_PER_DAY,
  pe as MS_PER_HOUR,
  Je as MS_PER_MINUTE,
  u as MedExpertPanel,
  Ge as SCHEDULE_OPTIONS,
  Ye as STATUS_COLORS,
  Fe as STATUS_ICONS,
  Qe as TABS,
  V as WEEKDAY_LABELS,
  st as buildServiceData,
  Q as createDefaultWizardState,
  rt as extractMedications,
  ue as extractProfiles,
  lt as formatDate,
  Et as formatDose,
  ct as formatMonthYear,
  tt as formatNextDose,
  nt as getAdherenceForDay,
  ot as getCalendarDays,
  dt as getEventsForDay,
  et as getFormIcon,
  At as getStatusColor,
  he as getStatusIcon,
  it as groupMedicationsByStatus,
  _e as isSameDay,
  pt as isToday,
  at as validateWizardState
};
