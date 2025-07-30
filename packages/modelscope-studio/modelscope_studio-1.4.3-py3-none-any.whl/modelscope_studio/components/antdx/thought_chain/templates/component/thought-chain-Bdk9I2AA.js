import { i as on, a as gt, r as an, w as Ae, g as sn, c as G } from "./Index-uTOgrcLB.js";
const M = window.ms_globals.React, x = window.ms_globals.React, Jr = window.ms_globals.React.isValidElement, Zr = window.ms_globals.React.version, ee = window.ms_globals.React.useRef, en = window.ms_globals.React.useLayoutEffect, ge = window.ms_globals.React.useEffect, tn = window.ms_globals.React.forwardRef, rn = window.ms_globals.React.useState, nn = window.ms_globals.React.useMemo, jt = window.ms_globals.ReactDOM, pt = window.ms_globals.ReactDOM.createPortal, cn = window.ms_globals.internalContext.useContextPropsContext, zt = window.ms_globals.internalContext.ContextPropsProvider, ln = window.ms_globals.createItemsContext.createItemsContext, un = window.ms_globals.antd.ConfigProvider, vt = window.ms_globals.antd.theme, fn = window.ms_globals.antd.Avatar, Dt = window.ms_globals.antd.Typography, ze = window.ms_globals.antdCssinjs.unit, rt = window.ms_globals.antdCssinjs.token2CSSVar, kt = window.ms_globals.antdCssinjs.useStyleRegister, dn = window.ms_globals.antdCssinjs.useCSSVarRegister, mn = window.ms_globals.antdCssinjs.createTheme, hn = window.ms_globals.antdCssinjs.useCacheToken, pn = window.ms_globals.antdIcons.LeftOutlined, gn = window.ms_globals.antdIcons.RightOutlined;
var vn = /\s/;
function yn(e) {
  for (var t = e.length; t-- && vn.test(e.charAt(t)); )
    ;
  return t;
}
var bn = /^\s+/;
function Sn(e) {
  return e && e.slice(0, yn(e) + 1).replace(bn, "");
}
var Nt = NaN, xn = /^[-+]0x[0-9a-f]+$/i, Cn = /^0b[01]+$/i, En = /^0o[0-7]+$/i, _n = parseInt;
function Ft(e) {
  if (typeof e == "number")
    return e;
  if (on(e))
    return Nt;
  if (gt(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = gt(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Sn(e);
  var r = Cn.test(e);
  return r || En.test(e) ? _n(e.slice(2), r ? 2 : 8) : xn.test(e) ? Nt : +e;
}
var nt = function() {
  return an.Date.now();
}, wn = "Expected a function", Tn = Math.max, Pn = Math.min;
function Mn(e, t, r) {
  var o, n, i, a, s, c, l = 0, f = !1, u = !1, d = !0;
  if (typeof e != "function")
    throw new TypeError(wn);
  t = Ft(t) || 0, gt(r) && (f = !!r.leading, u = "maxWait" in r, i = u ? Tn(Ft(r.maxWait) || 0, t) : i, d = "trailing" in r ? !!r.trailing : d);
  function m(p) {
    var P = o, T = n;
    return o = n = void 0, l = p, a = e.apply(T, P), a;
  }
  function v(p) {
    return l = p, s = setTimeout(S, t), f ? m(p) : a;
  }
  function g(p) {
    var P = p - c, T = p - l, R = t - P;
    return u ? Pn(R, i - T) : R;
  }
  function h(p) {
    var P = p - c, T = p - l;
    return c === void 0 || P >= t || P < 0 || u && T >= i;
  }
  function S() {
    var p = nt();
    if (h(p))
      return y(p);
    s = setTimeout(S, g(p));
  }
  function y(p) {
    return s = void 0, d && o ? m(p) : (o = n = void 0, a);
  }
  function _() {
    s !== void 0 && clearTimeout(s), l = 0, o = c = n = s = void 0;
  }
  function b() {
    return s === void 0 ? a : y(nt());
  }
  function w() {
    var p = nt(), P = h(p);
    if (o = arguments, n = this, c = p, P) {
      if (s === void 0)
        return v(c);
      if (u)
        return clearTimeout(s), s = setTimeout(S, t), m(c);
    }
    return s === void 0 && (s = setTimeout(S, t)), a;
  }
  return w.cancel = _, w.flush = b, w;
}
var br = {
  exports: {}
}, Ne = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var On = x, Rn = Symbol.for("react.element"), Ln = Symbol.for("react.fragment"), $n = Object.prototype.hasOwnProperty, An = On.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, In = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Sr(e, t, r) {
  var o, n = {}, i = null, a = null;
  r !== void 0 && (i = "" + r), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (a = t.ref);
  for (o in t) $n.call(t, o) && !In.hasOwnProperty(o) && (n[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) n[o] === void 0 && (n[o] = t[o]);
  return {
    $$typeof: Rn,
    type: e,
    key: i,
    ref: a,
    props: n,
    _owner: An.current
  };
}
Ne.Fragment = Ln;
Ne.jsx = Sr;
Ne.jsxs = Sr;
br.exports = Ne;
var q = br.exports;
const {
  SvelteComponent: jn,
  assign: Ht,
  binding_callbacks: Vt,
  check_outros: zn,
  children: xr,
  claim_element: Cr,
  claim_space: Dn,
  component_subscribe: Bt,
  compute_slots: kn,
  create_slot: Nn,
  detach: ce,
  element: Er,
  empty: Gt,
  exclude_internal_props: Xt,
  get_all_dirty_from_scope: Fn,
  get_slot_changes: Hn,
  group_outros: Vn,
  init: Bn,
  insert_hydration: Ie,
  safe_not_equal: Gn,
  set_custom_element_data: _r,
  space: Xn,
  transition_in: je,
  transition_out: yt,
  update_slot_base: Un
} = window.__gradio__svelte__internal, {
  beforeUpdate: Wn,
  getContext: Kn,
  onDestroy: qn,
  setContext: Qn
} = window.__gradio__svelte__internal;
function Ut(e) {
  let t, r;
  const o = (
    /*#slots*/
    e[7].default
  ), n = Nn(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Er("svelte-slot"), n && n.c(), this.h();
    },
    l(i) {
      t = Cr(i, "SVELTE-SLOT", {
        class: !0
      });
      var a = xr(t);
      n && n.l(a), a.forEach(ce), this.h();
    },
    h() {
      _r(t, "class", "svelte-1rt0kpf");
    },
    m(i, a) {
      Ie(i, t, a), n && n.m(t, null), e[9](t), r = !0;
    },
    p(i, a) {
      n && n.p && (!r || a & /*$$scope*/
      64) && Un(
        n,
        o,
        i,
        /*$$scope*/
        i[6],
        r ? Hn(
          o,
          /*$$scope*/
          i[6],
          a,
          null
        ) : Fn(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      r || (je(n, i), r = !0);
    },
    o(i) {
      yt(n, i), r = !1;
    },
    d(i) {
      i && ce(t), n && n.d(i), e[9](null);
    }
  };
}
function Yn(e) {
  let t, r, o, n, i = (
    /*$$slots*/
    e[4].default && Ut(e)
  );
  return {
    c() {
      t = Er("react-portal-target"), r = Xn(), i && i.c(), o = Gt(), this.h();
    },
    l(a) {
      t = Cr(a, "REACT-PORTAL-TARGET", {
        class: !0
      }), xr(t).forEach(ce), r = Dn(a), i && i.l(a), o = Gt(), this.h();
    },
    h() {
      _r(t, "class", "svelte-1rt0kpf");
    },
    m(a, s) {
      Ie(a, t, s), e[8](t), Ie(a, r, s), i && i.m(a, s), Ie(a, o, s), n = !0;
    },
    p(a, [s]) {
      /*$$slots*/
      a[4].default ? i ? (i.p(a, s), s & /*$$slots*/
      16 && je(i, 1)) : (i = Ut(a), i.c(), je(i, 1), i.m(o.parentNode, o)) : i && (Vn(), yt(i, 1, 1, () => {
        i = null;
      }), zn());
    },
    i(a) {
      n || (je(i), n = !0);
    },
    o(a) {
      yt(i), n = !1;
    },
    d(a) {
      a && (ce(t), ce(r), ce(o)), e[8](null), i && i.d(a);
    }
  };
}
function Wt(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function Jn(e, t, r) {
  let o, n, {
    $$slots: i = {},
    $$scope: a
  } = t;
  const s = kn(i);
  let {
    svelteInit: c
  } = t;
  const l = Ae(Wt(t)), f = Ae();
  Bt(e, f, (b) => r(0, o = b));
  const u = Ae();
  Bt(e, u, (b) => r(1, n = b));
  const d = [], m = Kn("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: g,
    subSlotIndex: h
  } = sn() || {}, S = c({
    parent: m,
    props: l,
    target: f,
    slot: u,
    slotKey: v,
    slotIndex: g,
    subSlotIndex: h,
    onDestroy(b) {
      d.push(b);
    }
  });
  Qn("$$ms-gr-react-wrapper", S), Wn(() => {
    l.set(Wt(t));
  }), qn(() => {
    d.forEach((b) => b());
  });
  function y(b) {
    Vt[b ? "unshift" : "push"](() => {
      o = b, f.set(o);
    });
  }
  function _(b) {
    Vt[b ? "unshift" : "push"](() => {
      n = b, u.set(n);
    });
  }
  return e.$$set = (b) => {
    r(17, t = Ht(Ht({}, t), Xt(b))), "svelteInit" in b && r(5, c = b.svelteInit), "$$scope" in b && r(6, a = b.$$scope);
  }, t = Xt(t), [o, n, f, u, s, c, a, i, y, _];
}
class Zn extends jn {
  constructor(t) {
    super(), Bn(this, t, Jn, Yn, Gn, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: qi
} = window.__gradio__svelte__internal, Kt = window.ms_globals.rerender, ot = window.ms_globals.tree;
function eo(e, t = {}) {
  function r(o) {
    const n = Ae(), i = new Zn({
      ...o,
      props: {
        svelteInit(a) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: e,
            props: a.props,
            slot: a.slot,
            target: a.target,
            slotIndex: a.slotIndex,
            subSlotIndex: a.subSlotIndex,
            ignore: t.ignore,
            slotKey: a.slotKey,
            nodes: []
          }, c = a.parent ?? ot;
          return c.nodes = [...c.nodes, s], Kt({
            createPortal: pt,
            node: ot
          }), a.onDestroy(() => {
            c.nodes = c.nodes.filter((l) => l.svelteInstance !== n), Kt({
              createPortal: pt,
              node: ot
            });
          }), s;
        },
        ...o.props
      }
    });
    return n.set(i), i;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(r);
    });
  });
}
const to = "1.4.0";
function fe() {
  return fe = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var r = arguments[t];
      for (var o in r) ({}).hasOwnProperty.call(r, o) && (e[o] = r[o]);
    }
    return e;
  }, fe.apply(null, arguments);
}
const ro = /* @__PURE__ */ x.createContext({}), no = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, oo = (e) => {
  const t = x.useContext(ro);
  return x.useMemo(() => ({
    ...no,
    ...t[e]
  }), [t[e]]);
}, io = "ant";
function bt() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: o,
    theme: n
  } = x.useContext(un.ConfigContext);
  return {
    theme: n,
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: o
  };
}
function F(e) {
  "@babel/helpers - typeof";
  return F = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, F(e);
}
function ao(e) {
  if (Array.isArray(e)) return e;
}
function so(e, t) {
  var r = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (r != null) {
    var o, n, i, a, s = [], c = !0, l = !1;
    try {
      if (i = (r = r.call(e)).next, t === 0) {
        if (Object(r) !== r) return;
        c = !1;
      } else for (; !(c = (o = i.call(r)).done) && (s.push(o.value), s.length !== t); c = !0) ;
    } catch (f) {
      l = !0, n = f;
    } finally {
      try {
        if (!c && r.return != null && (a = r.return(), Object(a) !== a)) return;
      } finally {
        if (l) throw n;
      }
    }
    return s;
  }
}
function qt(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var r = 0, o = Array(t); r < t; r++) o[r] = e[r];
  return o;
}
function co(e, t) {
  if (e) {
    if (typeof e == "string") return qt(e, t);
    var r = {}.toString.call(e).slice(8, -1);
    return r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set" ? Array.from(e) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? qt(e, t) : void 0;
  }
}
function lo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function X(e, t) {
  return ao(e) || so(e, t) || co(e, t) || lo();
}
function uo(e, t) {
  if (F(e) != "object" || !e) return e;
  var r = e[Symbol.toPrimitive];
  if (r !== void 0) {
    var o = r.call(e, t);
    if (F(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function wr(e) {
  var t = uo(e, "string");
  return F(t) == "symbol" ? t : t + "";
}
function E(e, t, r) {
  return (t = wr(t)) in e ? Object.defineProperty(e, t, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = r, e;
}
function Qt(e, t) {
  var r = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(e);
    t && (o = o.filter(function(n) {
      return Object.getOwnPropertyDescriptor(e, n).enumerable;
    })), r.push.apply(r, o);
  }
  return r;
}
function C(e) {
  for (var t = 1; t < arguments.length; t++) {
    var r = arguments[t] != null ? arguments[t] : {};
    t % 2 ? Qt(Object(r), !0).forEach(function(o) {
      E(e, o, r[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r)) : Qt(Object(r)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(r, o));
    });
  }
  return e;
}
function de(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function Yt(e, t) {
  for (var r = 0; r < t.length; r++) {
    var o = t[r];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, wr(o.key), o);
  }
}
function me(e, t, r) {
  return t && Yt(e.prototype, t), r && Yt(e, r), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function se(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function St(e, t) {
  return St = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, o) {
    return r.__proto__ = o, r;
  }, St(e, t);
}
function Fe(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && St(e, t);
}
function De(e) {
  return De = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, De(e);
}
function Tr() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Tr = function() {
    return !!e;
  })();
}
function fo(e, t) {
  if (t && (F(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return se(e);
}
function He(e) {
  var t = Tr();
  return function() {
    var r, o = De(e);
    if (t) {
      var n = De(this).constructor;
      r = Reflect.construct(o, arguments, n);
    } else r = o.apply(this, arguments);
    return fo(this, r);
  };
}
var Pr = /* @__PURE__ */ me(function e() {
  de(this, e);
}), Mr = "CALC_UNIT", mo = new RegExp(Mr, "g");
function it(e) {
  return typeof e == "number" ? "".concat(e).concat(Mr) : e;
}
var ho = /* @__PURE__ */ function(e) {
  Fe(r, e);
  var t = He(r);
  function r(o, n) {
    var i;
    de(this, r), i = t.call(this), E(se(i), "result", ""), E(se(i), "unitlessCssVar", void 0), E(se(i), "lowPriority", void 0);
    var a = F(o);
    return i.unitlessCssVar = n, o instanceof r ? i.result = "(".concat(o.result, ")") : a === "number" ? i.result = it(o) : a === "string" && (i.result = o), i;
  }
  return me(r, [{
    key: "add",
    value: function(n) {
      return n instanceof r ? this.result = "".concat(this.result, " + ").concat(n.getResult()) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " + ").concat(it(n))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(n) {
      return n instanceof r ? this.result = "".concat(this.result, " - ").concat(n.getResult()) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " - ").concat(it(n))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(n) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), n instanceof r ? this.result = "".concat(this.result, " * ").concat(n.getResult(!0)) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " * ").concat(n)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(n) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), n instanceof r ? this.result = "".concat(this.result, " / ").concat(n.getResult(!0)) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " / ").concat(n)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(n) {
      return this.lowPriority || n ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(n) {
      var i = this, a = n || {}, s = a.unit, c = !0;
      return typeof s == "boolean" ? c = s : Array.from(this.unitlessCssVar).some(function(l) {
        return i.result.includes(l);
      }) && (c = !1), this.result = this.result.replace(mo, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), r;
}(Pr), po = /* @__PURE__ */ function(e) {
  Fe(r, e);
  var t = He(r);
  function r(o) {
    var n;
    return de(this, r), n = t.call(this), E(se(n), "result", 0), o instanceof r ? n.result = o.result : typeof o == "number" && (n.result = o), n;
  }
  return me(r, [{
    key: "add",
    value: function(n) {
      return n instanceof r ? this.result += n.result : typeof n == "number" && (this.result += n), this;
    }
  }, {
    key: "sub",
    value: function(n) {
      return n instanceof r ? this.result -= n.result : typeof n == "number" && (this.result -= n), this;
    }
  }, {
    key: "mul",
    value: function(n) {
      return n instanceof r ? this.result *= n.result : typeof n == "number" && (this.result *= n), this;
    }
  }, {
    key: "div",
    value: function(n) {
      return n instanceof r ? this.result /= n.result : typeof n == "number" && (this.result /= n), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), r;
}(Pr), go = function(t, r) {
  var o = t === "css" ? ho : po;
  return function(n) {
    return new o(n, r);
  };
}, Jt = function(t, r) {
  return "".concat([r, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function ve(e) {
  var t = M.useRef();
  t.current = e;
  var r = M.useCallback(function() {
    for (var o, n = arguments.length, i = new Array(n), a = 0; a < n; a++)
      i[a] = arguments[a];
    return (o = t.current) === null || o === void 0 ? void 0 : o.call.apply(o, [t].concat(i));
  }, []);
  return r;
}
function vo(e) {
  if (Array.isArray(e)) return e;
}
function yo(e, t) {
  var r = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (r != null) {
    var o, n, i, a, s = [], c = !0, l = !1;
    try {
      if (i = (r = r.call(e)).next, t !== 0) for (; !(c = (o = i.call(r)).done) && (s.push(o.value), s.length !== t); c = !0) ;
    } catch (f) {
      l = !0, n = f;
    } finally {
      try {
        if (!c && r.return != null && (a = r.return(), Object(a) !== a)) return;
      } finally {
        if (l) throw n;
      }
    }
    return s;
  }
}
function Zt(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var r = 0, o = Array(t); r < t; r++) o[r] = e[r];
  return o;
}
function bo(e, t) {
  if (e) {
    if (typeof e == "string") return Zt(e, t);
    var r = {}.toString.call(e).slice(8, -1);
    return r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set" ? Array.from(e) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? Zt(e, t) : void 0;
  }
}
function So() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function ke(e, t) {
  return vo(e) || yo(e, t) || bo(e, t) || So();
}
function Ve() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var er = Ve() ? M.useLayoutEffect : M.useEffect, xo = function(t, r) {
  var o = M.useRef(!0);
  er(function() {
    return t(o.current);
  }, r), er(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, tr = function(t, r) {
  xo(function(o) {
    if (!o)
      return t();
  }, r);
};
function ye(e) {
  var t = M.useRef(!1), r = M.useState(e), o = ke(r, 2), n = o[0], i = o[1];
  M.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function a(s, c) {
    c && t.current || i(s);
  }
  return [n, a];
}
function at(e) {
  return e !== void 0;
}
function Co(e, t) {
  var r = t || {}, o = r.defaultValue, n = r.value, i = r.onChange, a = r.postState, s = ye(function() {
    return at(n) ? n : at(o) ? typeof o == "function" ? o() : o : typeof e == "function" ? e() : e;
  }), c = ke(s, 2), l = c[0], f = c[1], u = n !== void 0 ? n : l, d = a ? a(u) : u, m = ve(i), v = ye([u]), g = ke(v, 2), h = g[0], S = g[1];
  tr(function() {
    var _ = h[0];
    l !== _ && m(l, _);
  }, [h]), tr(function() {
    at(n) || f(n);
  }, [n]);
  var y = ve(function(_, b) {
    f(_, b), S([u], b);
  });
  return [d, y];
}
function te(e) {
  "@babel/helpers - typeof";
  return te = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, te(e);
}
var Or = {
  exports: {}
}, O = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Mt = Symbol.for("react.element"), Ot = Symbol.for("react.portal"), Be = Symbol.for("react.fragment"), Ge = Symbol.for("react.strict_mode"), Xe = Symbol.for("react.profiler"), Ue = Symbol.for("react.provider"), We = Symbol.for("react.context"), Eo = Symbol.for("react.server_context"), Ke = Symbol.for("react.forward_ref"), qe = Symbol.for("react.suspense"), Qe = Symbol.for("react.suspense_list"), Ye = Symbol.for("react.memo"), Je = Symbol.for("react.lazy"), _o = Symbol.for("react.offscreen"), Rr;
Rr = Symbol.for("react.module.reference");
function U(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Mt:
        switch (e = e.type, e) {
          case Be:
          case Xe:
          case Ge:
          case qe:
          case Qe:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case Eo:
              case We:
              case Ke:
              case Je:
              case Ye:
              case Ue:
                return e;
              default:
                return t;
            }
        }
      case Ot:
        return t;
    }
  }
}
O.ContextConsumer = We;
O.ContextProvider = Ue;
O.Element = Mt;
O.ForwardRef = Ke;
O.Fragment = Be;
O.Lazy = Je;
O.Memo = Ye;
O.Portal = Ot;
O.Profiler = Xe;
O.StrictMode = Ge;
O.Suspense = qe;
O.SuspenseList = Qe;
O.isAsyncMode = function() {
  return !1;
};
O.isConcurrentMode = function() {
  return !1;
};
O.isContextConsumer = function(e) {
  return U(e) === We;
};
O.isContextProvider = function(e) {
  return U(e) === Ue;
};
O.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Mt;
};
O.isForwardRef = function(e) {
  return U(e) === Ke;
};
O.isFragment = function(e) {
  return U(e) === Be;
};
O.isLazy = function(e) {
  return U(e) === Je;
};
O.isMemo = function(e) {
  return U(e) === Ye;
};
O.isPortal = function(e) {
  return U(e) === Ot;
};
O.isProfiler = function(e) {
  return U(e) === Xe;
};
O.isStrictMode = function(e) {
  return U(e) === Ge;
};
O.isSuspense = function(e) {
  return U(e) === qe;
};
O.isSuspenseList = function(e) {
  return U(e) === Qe;
};
O.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === Be || e === Xe || e === Ge || e === qe || e === Qe || e === _o || typeof e == "object" && e !== null && (e.$$typeof === Je || e.$$typeof === Ye || e.$$typeof === Ue || e.$$typeof === We || e.$$typeof === Ke || e.$$typeof === Rr || e.getModuleId !== void 0);
};
O.typeOf = U;
Or.exports = O;
var st = Or.exports, wo = Symbol.for("react.element"), To = Symbol.for("react.transitional.element"), Po = Symbol.for("react.fragment");
function Mo(e) {
  return (
    // Base object type
    e && te(e) === "object" && // React Element type
    (e.$$typeof === wo || e.$$typeof === To) && // React Fragment type
    e.type === Po
  );
}
var Oo = Number(Zr.split(".")[0]), Ro = function(t, r) {
  typeof t == "function" ? t(r) : te(t) === "object" && t && "current" in t && (t.current = r);
}, Lo = function(t) {
  var r, o;
  if (!t)
    return !1;
  if (Lr(t) && Oo >= 19)
    return !0;
  var n = st.isMemo(t) ? t.type.type : t.type;
  return !(typeof n == "function" && !((r = n.prototype) !== null && r !== void 0 && r.render) && n.$$typeof !== st.ForwardRef || typeof t == "function" && !((o = t.prototype) !== null && o !== void 0 && o.render) && t.$$typeof !== st.ForwardRef);
};
function Lr(e) {
  return /* @__PURE__ */ Jr(e) && !Mo(e);
}
var $o = function(t) {
  if (t && Lr(t)) {
    var r = t;
    return r.props.propertyIsEnumerable("ref") ? r.props.ref : r.ref;
  }
  return null;
};
function Ao(e, t) {
  if (te(e) != "object" || !e) return e;
  var r = e[Symbol.toPrimitive];
  if (r !== void 0) {
    var o = r.call(e, t);
    if (te(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function Io(e) {
  var t = Ao(e, "string");
  return te(t) == "symbol" ? t : t + "";
}
function jo(e, t, r) {
  return (t = Io(t)) in e ? Object.defineProperty(e, t, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = r, e;
}
function rr(e, t) {
  var r = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(e);
    t && (o = o.filter(function(n) {
      return Object.getOwnPropertyDescriptor(e, n).enumerable;
    })), r.push.apply(r, o);
  }
  return r;
}
function zo(e) {
  for (var t = 1; t < arguments.length; t++) {
    var r = arguments[t] != null ? arguments[t] : {};
    t % 2 ? rr(Object(r), !0).forEach(function(o) {
      jo(e, o, r[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r)) : rr(Object(r)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(r, o));
    });
  }
  return e;
}
function nr(e, t, r, o) {
  var n = C({}, t[e]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(s) {
      var c = X(s, 2), l = c[0], f = c[1];
      if (n != null && n[l] || n != null && n[f]) {
        var u;
        (u = n[f]) !== null && u !== void 0 || (n[f] = n == null ? void 0 : n[l]);
      }
    });
  }
  var a = C(C({}, r), n);
  return Object.keys(a).forEach(function(s) {
    a[s] === t[s] && delete a[s];
  }), a;
}
var $r = typeof CSSINJS_STATISTIC < "u", xt = !0;
function Rt() {
  for (var e = arguments.length, t = new Array(e), r = 0; r < e; r++)
    t[r] = arguments[r];
  if (!$r)
    return Object.assign.apply(Object, [{}].concat(t));
  xt = !1;
  var o = {};
  return t.forEach(function(n) {
    if (F(n) === "object") {
      var i = Object.keys(n);
      i.forEach(function(a) {
        Object.defineProperty(o, a, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return n[a];
          }
        });
      });
    }
  }), xt = !0, o;
}
var or = {};
function Do() {
}
var ko = function(t) {
  var r, o = t, n = Do;
  return $r && typeof Proxy < "u" && (r = /* @__PURE__ */ new Set(), o = new Proxy(t, {
    get: function(a, s) {
      if (xt) {
        var c;
        (c = r) === null || c === void 0 || c.add(s);
      }
      return a[s];
    }
  }), n = function(a, s) {
    var c;
    or[a] = {
      global: Array.from(r),
      component: C(C({}, (c = or[a]) === null || c === void 0 ? void 0 : c.component), s)
    };
  }), {
    token: o,
    keys: r,
    flush: n
  };
};
function ir(e, t, r) {
  if (typeof r == "function") {
    var o;
    return r(Rt(t, (o = t[e]) !== null && o !== void 0 ? o : {}));
  }
  return r ?? {};
}
function No(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var r = arguments.length, o = new Array(r), n = 0; n < r; n++)
        o[n] = arguments[n];
      return "max(".concat(o.map(function(i) {
        return ze(i);
      }).join(","), ")");
    },
    min: function() {
      for (var r = arguments.length, o = new Array(r), n = 0; n < r; n++)
        o[n] = arguments[n];
      return "min(".concat(o.map(function(i) {
        return ze(i);
      }).join(","), ")");
    }
  };
}
var Fo = 1e3 * 60 * 10, Ho = /* @__PURE__ */ function() {
  function e() {
    de(this, e), E(this, "map", /* @__PURE__ */ new Map()), E(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), E(this, "nextID", 0), E(this, "lastAccessBeat", /* @__PURE__ */ new Map()), E(this, "accessBeat", 0);
  }
  return me(e, [{
    key: "set",
    value: function(r, o) {
      this.clear();
      var n = this.getCompositeKey(r);
      this.map.set(n, o), this.lastAccessBeat.set(n, Date.now());
    }
  }, {
    key: "get",
    value: function(r) {
      var o = this.getCompositeKey(r), n = this.map.get(o);
      return this.lastAccessBeat.set(o, Date.now()), this.accessBeat += 1, n;
    }
  }, {
    key: "getCompositeKey",
    value: function(r) {
      var o = this, n = r.map(function(i) {
        return i && F(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(F(i), "_").concat(i);
      });
      return n.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(r) {
      if (this.objectIDMap.has(r))
        return this.objectIDMap.get(r);
      var o = this.nextID;
      return this.objectIDMap.set(r, o), this.nextID += 1, o;
    }
  }, {
    key: "clear",
    value: function() {
      var r = this;
      if (this.accessBeat > 1e4) {
        var o = Date.now();
        this.lastAccessBeat.forEach(function(n, i) {
          o - n > Fo && (r.map.delete(i), r.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), ar = new Ho();
function Vo(e, t) {
  return x.useMemo(function() {
    var r = ar.get(t);
    if (r)
      return r;
    var o = e();
    return ar.set(t, o), o;
  }, t);
}
var Bo = function() {
  return {};
};
function Go(e) {
  var t = e.useCSP, r = t === void 0 ? Bo : t, o = e.useToken, n = e.usePrefix, i = e.getResetStyles, a = e.getCommonStyle, s = e.getCompUnitless;
  function c(d, m, v, g) {
    var h = Array.isArray(d) ? d[0] : d;
    function S(T) {
      return "".concat(String(h)).concat(T.slice(0, 1).toUpperCase()).concat(T.slice(1));
    }
    var y = (g == null ? void 0 : g.unitless) || {}, _ = typeof s == "function" ? s(d) : {}, b = C(C({}, _), {}, E({}, S("zIndexPopup"), !0));
    Object.keys(y).forEach(function(T) {
      b[S(T)] = y[T];
    });
    var w = C(C({}, g), {}, {
      unitless: b,
      prefixToken: S
    }), p = f(d, m, v, w), P = l(h, v, w);
    return function(T) {
      var R = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : T, L = p(T, R), $ = X(L, 2), A = $[1], I = P(R), j = X(I, 2), z = j[0], H = j[1];
      return [z, A, H];
    };
  }
  function l(d, m, v) {
    var g = v.unitless, h = v.injectStyle, S = h === void 0 ? !0 : h, y = v.prefixToken, _ = v.ignore, b = function(P) {
      var T = P.rootCls, R = P.cssVar, L = R === void 0 ? {} : R, $ = o(), A = $.realToken;
      return dn({
        path: [d],
        prefix: L.prefix,
        key: L.key,
        unitless: g,
        ignore: _,
        token: A,
        scope: T
      }, function() {
        var I = ir(d, A, m), j = nr(d, A, I, {
          deprecatedTokens: v == null ? void 0 : v.deprecatedTokens
        });
        return Object.keys(I).forEach(function(z) {
          j[y(z)] = j[z], delete j[z];
        }), j;
      }), null;
    }, w = function(P) {
      var T = o(), R = T.cssVar;
      return [function(L) {
        return S && R ? /* @__PURE__ */ x.createElement(x.Fragment, null, /* @__PURE__ */ x.createElement(b, {
          rootCls: P,
          cssVar: R,
          component: d
        }), L) : L;
      }, R == null ? void 0 : R.key];
    };
    return w;
  }
  function f(d, m, v) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = Array.isArray(d) ? d : [d, d], S = X(h, 1), y = S[0], _ = h.join("-"), b = e.layer || {
      name: "antd"
    };
    return function(w) {
      var p = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : w, P = o(), T = P.theme, R = P.realToken, L = P.hashId, $ = P.token, A = P.cssVar, I = n(), j = I.rootPrefixCls, z = I.iconPrefixCls, H = r(), re = A ? "css" : "js", J = Vo(function() {
        var B = /* @__PURE__ */ new Set();
        return A && Object.keys(g.unitless || {}).forEach(function(oe) {
          B.add(rt(oe, A.prefix)), B.add(rt(oe, Jt(y, A.prefix)));
        }), go(re, B);
      }, [re, y, A == null ? void 0 : A.prefix]), be = No(re), Se = be.max, V = be.min, ne = {
        theme: T,
        token: $,
        hashId: L,
        nonce: function() {
          return H.nonce;
        },
        clientOnly: g.clientOnly,
        layer: b,
        // antd is always at top of styles
        order: g.order || -999
      };
      typeof i == "function" && kt(C(C({}, ne), {}, {
        clientOnly: !1,
        path: ["Shared", j]
      }), function() {
        return i($, {
          prefix: {
            rootPrefixCls: j,
            iconPrefixCls: z
          },
          csp: H
        });
      });
      var he = kt(C(C({}, ne), {}, {
        path: [_, w, z]
      }), function() {
        if (g.injectStyle === !1)
          return [];
        var B = ko($), oe = B.token, xe = B.flush, Q = ir(y, R, v), Ze = ".".concat(w), Ce = nr(y, R, Q, {
          deprecatedTokens: g.deprecatedTokens
        });
        A && Q && F(Q) === "object" && Object.keys(Q).forEach(function(we) {
          Q[we] = "var(".concat(rt(we, Jt(y, A.prefix)), ")");
        });
        var Ee = Rt(oe, {
          componentCls: Ze,
          prefixCls: w,
          iconCls: ".".concat(z),
          antCls: ".".concat(j),
          calc: J,
          // @ts-ignore
          max: Se,
          // @ts-ignore
          min: V
        }, A ? Q : Ce), _e = m(Ee, {
          hashId: L,
          prefixCls: w,
          rootPrefixCls: j,
          iconPrefixCls: z
        });
        xe(y, Ce);
        var ie = typeof a == "function" ? a(Ee, w, p, g.resetFont) : null;
        return [g.resetStyle === !1 ? null : ie, _e];
      });
      return [he, L];
    };
  }
  function u(d, m, v) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = f(d, m, v, C({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, g)), S = function(_) {
      var b = _.prefixCls, w = _.rootCls, p = w === void 0 ? b : w;
      return h(b, p), null;
    };
    return S;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: u,
    genComponentStyleHook: f
  };
}
const Xo = {
  blue: "#1677FF",
  purple: "#722ED1",
  cyan: "#13C2C2",
  green: "#52C41A",
  magenta: "#EB2F96",
  /**
   * @deprecated Use magenta instead
   */
  pink: "#EB2F96",
  red: "#F5222D",
  orange: "#FA8C16",
  yellow: "#FADB14",
  volcano: "#FA541C",
  geekblue: "#2F54EB",
  gold: "#FAAD14",
  lime: "#A0D911"
}, Uo = Object.assign(Object.assign({}, Xo), {
  // Color
  colorPrimary: "#1677ff",
  colorSuccess: "#52c41a",
  colorWarning: "#faad14",
  colorError: "#ff4d4f",
  colorInfo: "#1677ff",
  colorLink: "",
  colorTextBase: "",
  colorBgBase: "",
  // Font
  fontFamily: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
'Noto Color Emoji'`,
  fontFamilyCode: "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace",
  fontSize: 14,
  // Line
  lineWidth: 1,
  lineType: "solid",
  // Motion
  motionUnit: 0.1,
  motionBase: 0,
  motionEaseOutCirc: "cubic-bezier(0.08, 0.82, 0.17, 1)",
  motionEaseInOutCirc: "cubic-bezier(0.78, 0.14, 0.15, 0.86)",
  motionEaseOut: "cubic-bezier(0.215, 0.61, 0.355, 1)",
  motionEaseInOut: "cubic-bezier(0.645, 0.045, 0.355, 1)",
  motionEaseOutBack: "cubic-bezier(0.12, 0.4, 0.29, 1.46)",
  motionEaseInBack: "cubic-bezier(0.71, -0.46, 0.88, 0.6)",
  motionEaseInQuint: "cubic-bezier(0.755, 0.05, 0.855, 0.06)",
  motionEaseOutQuint: "cubic-bezier(0.23, 1, 0.32, 1)",
  // Radius
  borderRadius: 6,
  // Size
  sizeUnit: 4,
  sizeStep: 4,
  sizePopupArrow: 16,
  // Control Base
  controlHeight: 32,
  // zIndex
  zIndexBase: 0,
  zIndexPopupBase: 1e3,
  // Image
  opacityImage: 1,
  // Wireframe
  wireframe: !1,
  // Motion
  motion: !0
}), D = Math.round;
function ct(e, t) {
  const r = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = r.map((n) => parseFloat(n));
  for (let n = 0; n < 3; n += 1)
    o[n] = t(o[n] || 0, r[n] || "", n);
  return r[3] ? o[3] = r[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const sr = (e, t, r) => r === 0 ? e : e / 100;
function pe(e, t) {
  const r = t || 255;
  return e > r ? r : e < 0 ? 0 : e;
}
class Y {
  constructor(t) {
    E(this, "isValid", !0), E(this, "r", 0), E(this, "g", 0), E(this, "b", 0), E(this, "a", 1), E(this, "_h", void 0), E(this, "_s", void 0), E(this, "_l", void 0), E(this, "_v", void 0), E(this, "_max", void 0), E(this, "_min", void 0), E(this, "_brightness", void 0);
    function r(o) {
      return o[0] in t && o[1] in t && o[2] in t;
    }
    if (t) if (typeof t == "string") {
      let n = function(i) {
        return o.startsWith(i);
      };
      const o = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : n("rgb") ? this.fromRgbString(o) : n("hsl") ? this.fromHslString(o) : (n("hsv") || n("hsb")) && this.fromHsvString(o);
    } else if (t instanceof Y)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (r("rgb"))
      this.r = pe(t.r), this.g = pe(t.g), this.b = pe(t.b), this.a = typeof t.a == "number" ? pe(t.a, 1) : 1;
    else if (r("hsl"))
      this.fromHsl(t);
    else if (r("hsv"))
      this.fromHsv(t);
    else
      throw new Error("@ant-design/fast-color: unsupported input " + JSON.stringify(t));
  }
  // ======================= Setter =======================
  setR(t) {
    return this._sc("r", t);
  }
  setG(t) {
    return this._sc("g", t);
  }
  setB(t) {
    return this._sc("b", t);
  }
  setA(t) {
    return this._sc("a", t, 1);
  }
  setHue(t) {
    const r = this.toHsv();
    return r.h = t, this._c(r);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function t(i) {
      const a = i / 255;
      return a <= 0.03928 ? a / 12.92 : Math.pow((a + 0.055) / 1.055, 2.4);
    }
    const r = t(this.r), o = t(this.g), n = t(this.b);
    return 0.2126 * r + 0.7152 * o + 0.0722 * n;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = D(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
    }
    return this._h;
  }
  getSaturation() {
    if (typeof this._s > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._s = 0 : this._s = t / this.getMax();
    }
    return this._s;
  }
  getLightness() {
    return typeof this._l > "u" && (this._l = (this.getMax() + this.getMin()) / 510), this._l;
  }
  getValue() {
    return typeof this._v > "u" && (this._v = this.getMax() / 255), this._v;
  }
  /**
   * Returns the perceived brightness of the color, from 0-255.
   * Note: this is not the b of HSB
   * @see http://www.w3.org/TR/AERT#color-contrast
   */
  getBrightness() {
    return typeof this._brightness > "u" && (this._brightness = (this.r * 299 + this.g * 587 + this.b * 114) / 1e3), this._brightness;
  }
  // ======================== Func ========================
  darken(t = 10) {
    const r = this.getHue(), o = this.getSaturation();
    let n = this.getLightness() - t / 100;
    return n < 0 && (n = 0), this._c({
      h: r,
      s: o,
      l: n,
      a: this.a
    });
  }
  lighten(t = 10) {
    const r = this.getHue(), o = this.getSaturation();
    let n = this.getLightness() + t / 100;
    return n > 1 && (n = 1), this._c({
      h: r,
      s: o,
      l: n,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(t, r = 50) {
    const o = this._c(t), n = r / 100, i = (s) => (o[s] - this[s]) * n + this[s], a = {
      r: D(i("r")),
      g: D(i("g")),
      b: D(i("b")),
      a: D(i("a") * 100) / 100
    };
    return this._c(a);
  }
  /**
   * Mix the color with pure white, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return white.
   */
  tint(t = 10) {
    return this.mix({
      r: 255,
      g: 255,
      b: 255,
      a: 1
    }, t);
  }
  /**
   * Mix the color with pure black, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return black.
   */
  shade(t = 10) {
    return this.mix({
      r: 0,
      g: 0,
      b: 0,
      a: 1
    }, t);
  }
  onBackground(t) {
    const r = this._c(t), o = this.a + r.a * (1 - this.a), n = (i) => D((this[i] * this.a + r[i] * r.a * (1 - this.a)) / o);
    return this._c({
      r: n("r"),
      g: n("g"),
      b: n("b"),
      a: o
    });
  }
  // ======================= Status =======================
  isDark() {
    return this.getBrightness() < 128;
  }
  isLight() {
    return this.getBrightness() >= 128;
  }
  // ======================== MISC ========================
  equals(t) {
    return this.r === t.r && this.g === t.g && this.b === t.b && this.a === t.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let t = "#";
    const r = (this.r || 0).toString(16);
    t += r.length === 2 ? r : "0" + r;
    const o = (this.g || 0).toString(16);
    t += o.length === 2 ? o : "0" + o;
    const n = (this.b || 0).toString(16);
    if (t += n.length === 2 ? n : "0" + n, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = D(this.a * 255).toString(16);
      t += i.length === 2 ? i : "0" + i;
    }
    return t;
  }
  /** CSS support color pattern */
  toHsl() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      l: this.getLightness(),
      a: this.a
    };
  }
  /** CSS support color pattern */
  toHslString() {
    const t = this.getHue(), r = D(this.getSaturation() * 100), o = D(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${r}%,${o}%,${this.a})` : `hsl(${t},${r}%,${o}%)`;
  }
  /** Same as toHsb */
  toHsv() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      v: this.getValue(),
      a: this.a
    };
  }
  toRgb() {
    return {
      r: this.r,
      g: this.g,
      b: this.b,
      a: this.a
    };
  }
  toRgbString() {
    return this.a !== 1 ? `rgba(${this.r},${this.g},${this.b},${this.a})` : `rgb(${this.r},${this.g},${this.b})`;
  }
  toString() {
    return this.toRgbString();
  }
  // ====================== Privates ======================
  /** Return a new FastColor object with one channel changed */
  _sc(t, r, o) {
    const n = this.clone();
    return n[t] = pe(r, o), n;
  }
  _c(t) {
    return new this.constructor(t);
  }
  getMax() {
    return typeof this._max > "u" && (this._max = Math.max(this.r, this.g, this.b)), this._max;
  }
  getMin() {
    return typeof this._min > "u" && (this._min = Math.min(this.r, this.g, this.b)), this._min;
  }
  fromHexString(t) {
    const r = t.replace("#", "");
    function o(n, i) {
      return parseInt(r[n] + r[i || n], 16);
    }
    r.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = r[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = r[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: r,
    l: o,
    a: n
  }) {
    if (this._h = t % 360, this._s = r, this._l = o, this.a = typeof n == "number" ? n : 1, r <= 0) {
      const d = D(o * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let i = 0, a = 0, s = 0;
    const c = t / 60, l = (1 - Math.abs(2 * o - 1)) * r, f = l * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (i = l, a = f) : c >= 1 && c < 2 ? (i = f, a = l) : c >= 2 && c < 3 ? (a = l, s = f) : c >= 3 && c < 4 ? (a = f, s = l) : c >= 4 && c < 5 ? (i = f, s = l) : c >= 5 && c < 6 && (i = l, s = f);
    const u = o - l / 2;
    this.r = D((i + u) * 255), this.g = D((a + u) * 255), this.b = D((s + u) * 255);
  }
  fromHsv({
    h: t,
    s: r,
    v: o,
    a: n
  }) {
    this._h = t % 360, this._s = r, this._v = o, this.a = typeof n == "number" ? n : 1;
    const i = D(o * 255);
    if (this.r = i, this.g = i, this.b = i, r <= 0)
      return;
    const a = t / 60, s = Math.floor(a), c = a - s, l = D(o * (1 - r) * 255), f = D(o * (1 - r * c) * 255), u = D(o * (1 - r * (1 - c)) * 255);
    switch (s) {
      case 0:
        this.g = u, this.b = l;
        break;
      case 1:
        this.r = f, this.b = l;
        break;
      case 2:
        this.r = l, this.b = u;
        break;
      case 3:
        this.r = l, this.g = f;
        break;
      case 4:
        this.r = u, this.g = l;
        break;
      case 5:
      default:
        this.g = l, this.b = f;
        break;
    }
  }
  fromHsvString(t) {
    const r = ct(t, sr);
    this.fromHsv({
      h: r[0],
      s: r[1],
      v: r[2],
      a: r[3]
    });
  }
  fromHslString(t) {
    const r = ct(t, sr);
    this.fromHsl({
      h: r[0],
      s: r[1],
      l: r[2],
      a: r[3]
    });
  }
  fromRgbString(t) {
    const r = ct(t, (o, n) => (
      // Convert percentage to number. e.g. 50% -> 128
      n.includes("%") ? D(o / 100 * 255) : o
    ));
    this.r = r[0], this.g = r[1], this.b = r[2], this.a = r[3];
  }
}
function lt(e) {
  return e >= 0 && e <= 255;
}
function Me(e, t) {
  const {
    r,
    g: o,
    b: n,
    a: i
  } = new Y(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: a,
    g: s,
    b: c
  } = new Y(t).toRgb();
  for (let l = 0.01; l <= 1; l += 0.01) {
    const f = Math.round((r - a * (1 - l)) / l), u = Math.round((o - s * (1 - l)) / l), d = Math.round((n - c * (1 - l)) / l);
    if (lt(f) && lt(u) && lt(d))
      return new Y({
        r: f,
        g: u,
        b: d,
        a: Math.round(l * 100) / 100
      }).toRgbString();
  }
  return new Y({
    r,
    g: o,
    b: n,
    a: 1
  }).toRgbString();
}
var Wo = function(e, t) {
  var r = {};
  for (var o in e) Object.prototype.hasOwnProperty.call(e, o) && t.indexOf(o) < 0 && (r[o] = e[o]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var n = 0, o = Object.getOwnPropertySymbols(e); n < o.length; n++)
    t.indexOf(o[n]) < 0 && Object.prototype.propertyIsEnumerable.call(e, o[n]) && (r[o[n]] = e[o[n]]);
  return r;
};
function Ko(e) {
  const {
    override: t
  } = e, r = Wo(e, ["override"]), o = Object.assign({}, t);
  Object.keys(Uo).forEach((d) => {
    delete o[d];
  });
  const n = Object.assign(Object.assign({}, r), o), i = 480, a = 576, s = 768, c = 992, l = 1200, f = 1600;
  if (n.motion === !1) {
    const d = "0s";
    n.motionDurationFast = d, n.motionDurationMid = d, n.motionDurationSlow = d;
  }
  return Object.assign(Object.assign(Object.assign({}, n), {
    // ============== Background ============== //
    colorFillContent: n.colorFillSecondary,
    colorFillContentHover: n.colorFill,
    colorFillAlter: n.colorFillQuaternary,
    colorBgContainerDisabled: n.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: n.colorBgContainer,
    colorSplit: Me(n.colorBorderSecondary, n.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: n.colorTextQuaternary,
    colorTextDisabled: n.colorTextQuaternary,
    colorTextHeading: n.colorText,
    colorTextLabel: n.colorTextSecondary,
    colorTextDescription: n.colorTextTertiary,
    colorTextLightSolid: n.colorWhite,
    colorHighlight: n.colorError,
    colorBgTextHover: n.colorFillSecondary,
    colorBgTextActive: n.colorFill,
    colorIcon: n.colorTextTertiary,
    colorIconHover: n.colorText,
    colorErrorOutline: Me(n.colorErrorBg, n.colorBgContainer),
    colorWarningOutline: Me(n.colorWarningBg, n.colorBgContainer),
    // Font
    fontSizeIcon: n.fontSizeSM,
    // Line
    lineWidthFocus: n.lineWidth * 3,
    // Control
    lineWidth: n.lineWidth,
    controlOutlineWidth: n.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: n.controlHeight / 2,
    controlItemBgHover: n.colorFillTertiary,
    controlItemBgActive: n.colorPrimaryBg,
    controlItemBgActiveHover: n.colorPrimaryBgHover,
    controlItemBgActiveDisabled: n.colorFill,
    controlTmpOutline: n.colorFillQuaternary,
    controlOutline: Me(n.colorPrimaryBg, n.colorBgContainer),
    lineType: n.lineType,
    borderRadius: n.borderRadius,
    borderRadiusXS: n.borderRadiusXS,
    borderRadiusSM: n.borderRadiusSM,
    borderRadiusLG: n.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: n.sizeXXS,
    paddingXS: n.sizeXS,
    paddingSM: n.sizeSM,
    padding: n.size,
    paddingMD: n.sizeMD,
    paddingLG: n.sizeLG,
    paddingXL: n.sizeXL,
    paddingContentHorizontalLG: n.sizeLG,
    paddingContentVerticalLG: n.sizeMS,
    paddingContentHorizontal: n.sizeMS,
    paddingContentVertical: n.sizeSM,
    paddingContentHorizontalSM: n.size,
    paddingContentVerticalSM: n.sizeXS,
    marginXXS: n.sizeXXS,
    marginXS: n.sizeXS,
    marginSM: n.sizeSM,
    margin: n.size,
    marginMD: n.sizeMD,
    marginLG: n.sizeLG,
    marginXL: n.sizeXL,
    marginXXL: n.sizeXXL,
    boxShadow: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowSecondary: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTertiary: `
      0 1px 2px 0 rgba(0, 0, 0, 0.03),
      0 1px 6px -1px rgba(0, 0, 0, 0.02),
      0 2px 4px 0 rgba(0, 0, 0, 0.02)
    `,
    screenXS: i,
    screenXSMin: i,
    screenXSMax: a - 1,
    screenSM: a,
    screenSMMin: a,
    screenSMMax: s - 1,
    screenMD: s,
    screenMDMin: s,
    screenMDMax: c - 1,
    screenLG: c,
    screenLGMin: c,
    screenLGMax: l - 1,
    screenXL: l,
    screenXLMin: l,
    screenXLMax: f - 1,
    screenXXL: f,
    screenXXLMin: f,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new Y("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new Y("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new Y("rgba(0, 0, 0, 0.09)").toRgbString()}
    `,
    boxShadowDrawerRight: `
      -6px 0 16px 0 rgba(0, 0, 0, 0.08),
      -3px 0 6px -4px rgba(0, 0, 0, 0.12),
      -9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerLeft: `
      6px 0 16px 0 rgba(0, 0, 0, 0.08),
      3px 0 6px -4px rgba(0, 0, 0, 0.12),
      9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerUp: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerDown: `
      0 -6px 16px 0 rgba(0, 0, 0, 0.08),
      0 -3px 6px -4px rgba(0, 0, 0, 0.12),
      0 -9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTabsOverflowLeft: "inset 10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowRight: "inset -10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowTop: "inset 0 10px 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowBottom: "inset 0 -10px 8px -8px rgba(0, 0, 0, 0.08)"
  }), o);
}
const qo = {
  lineHeight: !0,
  lineHeightSM: !0,
  lineHeightLG: !0,
  lineHeightHeading1: !0,
  lineHeightHeading2: !0,
  lineHeightHeading3: !0,
  lineHeightHeading4: !0,
  lineHeightHeading5: !0,
  opacityLoading: !0,
  fontWeightStrong: !0,
  zIndexPopupBase: !0,
  zIndexBase: !0,
  opacityImage: !0
}, Qo = {
  size: !0,
  sizeSM: !0,
  sizeLG: !0,
  sizeMD: !0,
  sizeXS: !0,
  sizeXXS: !0,
  sizeMS: !0,
  sizeXL: !0,
  sizeXXL: !0,
  sizeUnit: !0,
  sizeStep: !0,
  motionBase: !0,
  motionUnit: !0
}, Yo = mn(vt.defaultAlgorithm), Jo = {
  screenXS: !0,
  screenXSMin: !0,
  screenXSMax: !0,
  screenSM: !0,
  screenSMMin: !0,
  screenSMMax: !0,
  screenMD: !0,
  screenMDMin: !0,
  screenMDMax: !0,
  screenLG: !0,
  screenLGMin: !0,
  screenLGMax: !0,
  screenXL: !0,
  screenXLMin: !0,
  screenXLMax: !0,
  screenXXL: !0,
  screenXXLMin: !0
}, Ar = (e, t, r) => {
  const o = r.getDerivativeToken(e), {
    override: n,
    ...i
  } = t;
  let a = {
    ...o,
    override: n
  };
  return a = Ko(a), i && Object.entries(i).forEach(([s, c]) => {
    const {
      theme: l,
      ...f
    } = c;
    let u = f;
    l && (u = Ar({
      ...a,
      ...f
    }, {
      override: f
    }, l)), a[s] = u;
  }), a;
};
function Zo() {
  const {
    token: e,
    hashed: t,
    theme: r = Yo,
    override: o,
    cssVar: n
  } = x.useContext(vt._internalContext), [i, a, s] = hn(r, [vt.defaultSeed, e], {
    salt: `${to}-${t || ""}`,
    override: o,
    getComputedToken: Ar,
    cssVar: n && {
      prefix: n.prefix,
      key: n.key,
      unitless: qo,
      ignore: Qo,
      preserve: Jo
    }
  });
  return [r, s, t ? a : "", i, n];
}
const {
  genStyleHooks: ei
} = Go({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = bt();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, r, o, n] = Zo();
    return {
      theme: e,
      realToken: t,
      hashId: r,
      token: o,
      cssVar: n
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = bt();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
});
function cr(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function ti(e) {
  return e && te(e) === "object" && cr(e.nativeElement) ? e.nativeElement : cr(e) ? e : null;
}
function ri(e) {
  var t = ti(e);
  if (t)
    return t;
  if (e instanceof x.Component) {
    var r;
    return (r = jt.findDOMNode) === null || r === void 0 ? void 0 : r.call(jt, e);
  }
  return null;
}
function ni(e, t) {
  if (e == null) return {};
  var r = {};
  for (var o in e) if ({}.hasOwnProperty.call(e, o)) {
    if (t.indexOf(o) !== -1) continue;
    r[o] = e[o];
  }
  return r;
}
function lr(e, t) {
  if (e == null) return {};
  var r, o, n = ni(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (o = 0; o < i.length; o++) r = i[o], t.indexOf(r) === -1 && {}.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
  }
  return n;
}
var oi = /* @__PURE__ */ M.createContext({}), ii = /* @__PURE__ */ function(e) {
  Fe(r, e);
  var t = He(r);
  function r() {
    return de(this, r), t.apply(this, arguments);
  }
  return me(r, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), r;
}(M.Component);
function ai(e) {
  var t = M.useReducer(function(s) {
    return s + 1;
  }, 0), r = ke(t, 2), o = r[1], n = M.useRef(e), i = ve(function() {
    return n.current;
  }), a = ve(function(s) {
    n.current = typeof s == "function" ? s(n.current) : s, o();
  });
  return [i, a];
}
var Z = "none", Oe = "appear", Re = "enter", Le = "leave", ur = "none", W = "prepare", le = "start", ue = "active", Lt = "end", Ir = "prepared";
function fr(e, t) {
  var r = {};
  return r[e.toLowerCase()] = t.toLowerCase(), r["Webkit".concat(e)] = "webkit".concat(t), r["Moz".concat(e)] = "moz".concat(t), r["ms".concat(e)] = "MS".concat(t), r["O".concat(e)] = "o".concat(t.toLowerCase()), r;
}
function si(e, t) {
  var r = {
    animationend: fr("Animation", "AnimationEnd"),
    transitionend: fr("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete r.animationend.animation, "TransitionEvent" in t || delete r.transitionend.transition), r;
}
var ci = si(Ve(), typeof window < "u" ? window : {}), jr = {};
if (Ve()) {
  var li = document.createElement("div");
  jr = li.style;
}
var $e = {};
function zr(e) {
  if ($e[e])
    return $e[e];
  var t = ci[e];
  if (t)
    for (var r = Object.keys(t), o = r.length, n = 0; n < o; n += 1) {
      var i = r[n];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in jr)
        return $e[e] = t[i], $e[e];
    }
  return "";
}
var Dr = zr("animationend"), kr = zr("transitionend"), Nr = !!(Dr && kr), dr = Dr || "animationend", mr = kr || "transitionend";
function hr(e, t) {
  if (!e) return null;
  if (F(e) === "object") {
    var r = t.replace(/-\w/g, function(o) {
      return o[1].toUpperCase();
    });
    return e[r];
  }
  return "".concat(e, "-").concat(t);
}
const ui = function(e) {
  var t = ee();
  function r(n) {
    n && (n.removeEventListener(mr, e), n.removeEventListener(dr, e));
  }
  function o(n) {
    t.current && t.current !== n && r(t.current), n && n !== t.current && (n.addEventListener(mr, e), n.addEventListener(dr, e), t.current = n);
  }
  return M.useEffect(function() {
    return function() {
      r(t.current);
    };
  }, []), [o, r];
};
var Fr = Ve() ? en : ge, Hr = function(t) {
  return +setTimeout(t, 16);
}, Vr = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (Hr = function(t) {
  return window.requestAnimationFrame(t);
}, Vr = function(t) {
  return window.cancelAnimationFrame(t);
});
var pr = 0, $t = /* @__PURE__ */ new Map();
function Br(e) {
  $t.delete(e);
}
var Ct = function(t) {
  var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  pr += 1;
  var o = pr;
  function n(i) {
    if (i === 0)
      Br(o), t();
    else {
      var a = Hr(function() {
        n(i - 1);
      });
      $t.set(o, a);
    }
  }
  return n(r), o;
};
Ct.cancel = function(e) {
  var t = $t.get(e);
  return Br(e), Vr(t);
};
const fi = function() {
  var e = M.useRef(null);
  function t() {
    Ct.cancel(e.current);
  }
  function r(o) {
    var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = Ct(function() {
      n <= 1 ? o({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : r(o, n - 1);
    });
    e.current = i;
  }
  return M.useEffect(function() {
    return function() {
      t();
    };
  }, []), [r, t];
};
var di = [W, le, ue, Lt], mi = [W, Ir], Gr = !1, hi = !0;
function Xr(e) {
  return e === ue || e === Lt;
}
const pi = function(e, t, r) {
  var o = ye(ur), n = X(o, 2), i = n[0], a = n[1], s = fi(), c = X(s, 2), l = c[0], f = c[1];
  function u() {
    a(W, !0);
  }
  var d = t ? mi : di;
  return Fr(function() {
    if (i !== ur && i !== Lt) {
      var m = d.indexOf(i), v = d[m + 1], g = r(i);
      g === Gr ? a(v, !0) : v && l(function(h) {
        function S() {
          h.isCanceled() || a(v, !0);
        }
        g === !0 ? S() : Promise.resolve(g).then(S);
      });
    }
  }, [e, i]), M.useEffect(function() {
    return function() {
      f();
    };
  }, []), [u, i];
};
function gi(e, t, r, o) {
  var n = o.motionEnter, i = n === void 0 ? !0 : n, a = o.motionAppear, s = a === void 0 ? !0 : a, c = o.motionLeave, l = c === void 0 ? !0 : c, f = o.motionDeadline, u = o.motionLeaveImmediately, d = o.onAppearPrepare, m = o.onEnterPrepare, v = o.onLeavePrepare, g = o.onAppearStart, h = o.onEnterStart, S = o.onLeaveStart, y = o.onAppearActive, _ = o.onEnterActive, b = o.onLeaveActive, w = o.onAppearEnd, p = o.onEnterEnd, P = o.onLeaveEnd, T = o.onVisibleChanged, R = ye(), L = X(R, 2), $ = L[0], A = L[1], I = ai(Z), j = X(I, 2), z = j[0], H = j[1], re = ye(null), J = X(re, 2), be = J[0], Se = J[1], V = z(), ne = ee(!1), he = ee(null);
  function B() {
    return r();
  }
  var oe = ee(!1);
  function xe() {
    H(Z), Se(null, !0);
  }
  var Q = ve(function(N) {
    var k = z();
    if (k !== Z) {
      var K = B();
      if (!(N && !N.deadline && N.target !== K)) {
        var Te = oe.current, Pe;
        k === Oe && Te ? Pe = w == null ? void 0 : w(K, N) : k === Re && Te ? Pe = p == null ? void 0 : p(K, N) : k === Le && Te && (Pe = P == null ? void 0 : P(K, N)), Te && Pe !== !1 && xe();
      }
    }
  }), Ze = ui(Q), Ce = X(Ze, 1), Ee = Ce[0], _e = function(k) {
    switch (k) {
      case Oe:
        return E(E(E({}, W, d), le, g), ue, y);
      case Re:
        return E(E(E({}, W, m), le, h), ue, _);
      case Le:
        return E(E(E({}, W, v), le, S), ue, b);
      default:
        return {};
    }
  }, ie = M.useMemo(function() {
    return _e(V);
  }, [V]), we = pi(V, !e, function(N) {
    if (N === W) {
      var k = ie[W];
      return k ? k(B()) : Gr;
    }
    if (ae in ie) {
      var K;
      Se(((K = ie[ae]) === null || K === void 0 ? void 0 : K.call(ie, B(), null)) || null);
    }
    return ae === ue && V !== Z && (Ee(B()), f > 0 && (clearTimeout(he.current), he.current = setTimeout(function() {
      Q({
        deadline: !0
      });
    }, f))), ae === Ir && xe(), hi;
  }), At = X(we, 2), Qr = At[0], ae = At[1], Yr = Xr(ae);
  oe.current = Yr;
  var It = ee(null);
  Fr(function() {
    if (!(ne.current && It.current === t)) {
      A(t);
      var N = ne.current;
      ne.current = !0;
      var k;
      !N && t && s && (k = Oe), N && t && i && (k = Re), (N && !t && l || !N && u && !t && l) && (k = Le);
      var K = _e(k);
      k && (e || K[W]) ? (H(k), Qr()) : H(Z), It.current = t;
    }
  }, [t]), ge(function() {
    // Cancel appear
    (V === Oe && !s || // Cancel enter
    V === Re && !i || // Cancel leave
    V === Le && !l) && H(Z);
  }, [s, i, l]), ge(function() {
    return function() {
      ne.current = !1, clearTimeout(he.current);
    };
  }, []);
  var et = M.useRef(!1);
  ge(function() {
    $ && (et.current = !0), $ !== void 0 && V === Z && ((et.current || $) && (T == null || T($)), et.current = !0);
  }, [$, V]);
  var tt = be;
  return ie[W] && ae === le && (tt = C({
    transition: "none"
  }, tt)), [V, ae, tt, $ ?? t];
}
function vi(e) {
  var t = e;
  F(e) === "object" && (t = e.transitionSupport);
  function r(n, i) {
    return !!(n.motionName && t && i !== !1);
  }
  var o = /* @__PURE__ */ M.forwardRef(function(n, i) {
    var a = n.visible, s = a === void 0 ? !0 : a, c = n.removeOnLeave, l = c === void 0 ? !0 : c, f = n.forceRender, u = n.children, d = n.motionName, m = n.leavedClassName, v = n.eventProps, g = M.useContext(oi), h = g.motion, S = r(n, h), y = ee(), _ = ee();
    function b() {
      try {
        return y.current instanceof HTMLElement ? y.current : ri(_.current);
      } catch {
        return null;
      }
    }
    var w = gi(S, s, b, n), p = X(w, 4), P = p[0], T = p[1], R = p[2], L = p[3], $ = M.useRef(L);
    L && ($.current = !0);
    var A = M.useCallback(function(J) {
      y.current = J, Ro(i, J);
    }, [i]), I, j = C(C({}, v), {}, {
      visible: s
    });
    if (!u)
      I = null;
    else if (P === Z)
      L ? I = u(C({}, j), A) : !l && $.current && m ? I = u(C(C({}, j), {}, {
        className: m
      }), A) : f || !l && !m ? I = u(C(C({}, j), {}, {
        style: {
          display: "none"
        }
      }), A) : I = null;
    else {
      var z;
      T === W ? z = "prepare" : Xr(T) ? z = "active" : T === le && (z = "start");
      var H = hr(d, "".concat(P, "-").concat(z));
      I = u(C(C({}, j), {}, {
        className: G(hr(d, P), E(E({}, H, H && z), d, typeof d == "string")),
        style: R
      }), A);
    }
    if (/* @__PURE__ */ M.isValidElement(I) && Lo(I)) {
      var re = $o(I);
      re || (I = /* @__PURE__ */ M.cloneElement(I, {
        ref: A
      }));
    }
    return /* @__PURE__ */ M.createElement(ii, {
      ref: _
    }, I);
  });
  return o.displayName = "CSSMotion", o;
}
const Ur = vi(Nr);
var Et = "add", _t = "keep", wt = "remove", ut = "removed";
function yi(e) {
  var t;
  return e && F(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, C(C({}, t), {}, {
    key: String(t.key)
  });
}
function Tt() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(yi);
}
function bi() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], r = [], o = 0, n = t.length, i = Tt(e), a = Tt(t);
  i.forEach(function(l) {
    for (var f = !1, u = o; u < n; u += 1) {
      var d = a[u];
      if (d.key === l.key) {
        o < u && (r = r.concat(a.slice(o, u).map(function(m) {
          return C(C({}, m), {}, {
            status: Et
          });
        })), o = u), r.push(C(C({}, d), {}, {
          status: _t
        })), o += 1, f = !0;
        break;
      }
    }
    f || r.push(C(C({}, l), {}, {
      status: wt
    }));
  }), o < n && (r = r.concat(a.slice(o).map(function(l) {
    return C(C({}, l), {}, {
      status: Et
    });
  })));
  var s = {};
  r.forEach(function(l) {
    var f = l.key;
    s[f] = (s[f] || 0) + 1;
  });
  var c = Object.keys(s).filter(function(l) {
    return s[l] > 1;
  });
  return c.forEach(function(l) {
    r = r.filter(function(f) {
      var u = f.key, d = f.status;
      return u !== l || d !== wt;
    }), r.forEach(function(f) {
      f.key === l && (f.status = _t);
    });
  }), r;
}
var Si = ["component", "children", "onVisibleChanged", "onAllRemoved"], xi = ["status"], Ci = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function Ei(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Ur, r = /* @__PURE__ */ function(o) {
    Fe(i, o);
    var n = He(i);
    function i() {
      var a;
      de(this, i);
      for (var s = arguments.length, c = new Array(s), l = 0; l < s; l++)
        c[l] = arguments[l];
      return a = n.call.apply(n, [this].concat(c)), E(se(a), "state", {
        keyEntities: []
      }), E(se(a), "removeKey", function(f) {
        a.setState(function(u) {
          var d = u.keyEntities.map(function(m) {
            return m.key !== f ? m : C(C({}, m), {}, {
              status: ut
            });
          });
          return {
            keyEntities: d
          };
        }, function() {
          var u = a.state.keyEntities, d = u.filter(function(m) {
            var v = m.status;
            return v !== ut;
          }).length;
          d === 0 && a.props.onAllRemoved && a.props.onAllRemoved();
        });
      }), a;
    }
    return me(i, [{
      key: "render",
      value: function() {
        var s = this, c = this.state.keyEntities, l = this.props, f = l.component, u = l.children, d = l.onVisibleChanged;
        l.onAllRemoved;
        var m = lr(l, Si), v = f || M.Fragment, g = {};
        return Ci.forEach(function(h) {
          g[h] = m[h], delete m[h];
        }), delete m.keys, /* @__PURE__ */ M.createElement(v, m, c.map(function(h, S) {
          var y = h.status, _ = lr(h, xi), b = y === Et || y === _t;
          return /* @__PURE__ */ M.createElement(t, fe({}, g, {
            key: _.key,
            visible: b,
            eventProps: _,
            onVisibleChanged: function(p) {
              d == null || d(p, {
                key: _.key
              }), p || s.removeKey(_.key);
            }
          }), function(w, p) {
            return u(C(C({}, w), {}, {
              index: S
            }), p);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(s, c) {
        var l = s.keys, f = c.keyEntities, u = Tt(l), d = bi(f, u);
        return {
          keyEntities: d.filter(function(m) {
            var v = f.find(function(g) {
              var h = g.key;
              return m.key === h;
            });
            return !(v && v.status === ut && m.status === wt);
          })
        };
      }
    }]), i;
  }(M.Component);
  return E(r, "defaultProps", {
    component: "div"
  }), r;
}
Ei(Nr);
var _i = `accept acceptCharset accessKey action allowFullScreen allowTransparency
    alt async autoComplete autoFocus autoPlay capture cellPadding cellSpacing challenge
    charSet checked classID className colSpan cols content contentEditable contextMenu
    controls coords crossOrigin data dateTime default defer dir disabled download draggable
    encType form formAction formEncType formMethod formNoValidate formTarget frameBorder
    headers height hidden high href hrefLang htmlFor httpEquiv icon id inputMode integrity
    is keyParams keyType kind label lang list loop low manifest marginHeight marginWidth max maxLength media
    mediaGroup method min minLength multiple muted name noValidate nonce open
    optimum pattern placeholder poster preload radioGroup readOnly rel required
    reversed role rowSpan rows sandbox scope scoped scrolling seamless selected
    shape size sizes span spellCheck src srcDoc srcLang srcSet start step style
    summary tabIndex target title type useMap value width wmode wrap`, wi = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Ti = "".concat(_i, " ").concat(wi).split(/[\s\n]+/), Pi = "aria-", Mi = "data-";
function gr(e, t) {
  return e.indexOf(t) === 0;
}
function Wr(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, r;
  t === !1 ? r = {
    aria: !0,
    data: !0,
    attr: !0
  } : t === !0 ? r = {
    aria: !0
  } : r = zo({}, t);
  var o = {};
  return Object.keys(e).forEach(function(n) {
    // Aria
    (r.aria && (n === "role" || gr(n, Pi)) || // Data
    r.data && gr(n, Mi) || // Attr
    r.attr && Ti.includes(n)) && (o[n] = e[n]);
  }), o;
}
const ft = () => ({
  height: 0,
  opacity: 0
}), vr = (e) => {
  const {
    scrollHeight: t
  } = e;
  return {
    height: t,
    opacity: 1
  };
}, Oi = (e) => ({
  height: e ? e.offsetHeight : 0
}), dt = (e, t) => (t == null ? void 0 : t.deadline) === !0 || t.propertyName === "height", Ri = (e = io) => ({
  motionName: `${e}-motion-collapse`,
  onAppearStart: ft,
  onEnterStart: ft,
  onAppearActive: vr,
  onEnterActive: vr,
  onLeaveStart: Oi,
  onLeaveActive: ft,
  onAppearEnd: dt,
  onEnterEnd: dt,
  onLeaveEnd: dt,
  motionDeadline: 500
}), Li = (e, t, r) => {
  const o = typeof e == "boolean" || (e == null ? void 0 : e.expandedKeys) === void 0, [n, i, a] = x.useMemo(() => {
    let u = {
      expandedKeys: [],
      onExpand: () => {
      }
    };
    return e ? (typeof e == "object" && (u = {
      ...u,
      ...e
    }), [!0, u.expandedKeys, u.onExpand]) : [!1, u.expandedKeys, u.onExpand];
  }, [e]), [s, c] = Co(i, {
    value: o ? void 0 : i,
    onChange: a
  }), l = (u) => {
    c((d) => {
      const m = o ? d : i, v = m.includes(u) ? m.filter((g) => g !== u) : [...m, u];
      return a == null || a(v), v;
    });
  }, f = x.useMemo(() => n ? {
    ...Ri(r),
    motionAppear: !1,
    leavedClassName: `${t}-content-hidden`
  } : {}, [r, t, n]);
  return [n, s, n ? l : void 0, f];
}, $i = (e) => ({
  [e.componentCls]: {
    // For common/openAnimation
    [`${e.antCls}-motion-collapse-legacy`]: {
      overflow: "hidden",
      "&-active": {
        transition: `height ${e.motionDurationMid} ${e.motionEaseInOut},
        opacity ${e.motionDurationMid} ${e.motionEaseInOut} !important`
      }
    },
    [`${e.antCls}-motion-collapse`]: {
      overflow: "hidden",
      transition: `height ${e.motionDurationMid} ${e.motionEaseInOut},
        opacity ${e.motionDurationMid} ${e.motionEaseInOut} !important`
    }
  }
});
let mt = /* @__PURE__ */ function(e) {
  return e.PENDING = "pending", e.SUCCESS = "success", e.ERROR = "error", e;
}({});
const Kr = /* @__PURE__ */ x.createContext(null), Ai = (e) => {
  const {
    info: t = {},
    nextStatus: r,
    onClick: o,
    ...n
  } = e, i = Wr(n, {
    attr: !0,
    aria: !0,
    data: !0
  }), {
    prefixCls: a,
    collapseMotion: s,
    enableCollapse: c,
    expandedKeys: l,
    direction: f,
    classNames: u = {},
    styles: d = {}
  } = x.useContext(Kr), m = x.useId(), {
    key: v = m,
    icon: g,
    title: h,
    extra: S,
    content: y,
    footer: _,
    status: b,
    description: w
  } = t, p = `${a}-item`, P = () => o == null ? void 0 : o(v), T = l == null ? void 0 : l.includes(v);
  return /* @__PURE__ */ x.createElement("div", fe({}, i, {
    className: G(p, {
      [`${p}-${b}${r ? `-${r}` : ""}`]: b
    }, e.className),
    style: e.style
  }), /* @__PURE__ */ x.createElement("div", {
    className: G(`${p}-header`, u.itemHeader),
    style: d.itemHeader,
    onClick: P
  }, /* @__PURE__ */ x.createElement(fn, {
    icon: g,
    className: `${p}-icon`
  }), /* @__PURE__ */ x.createElement("div", {
    className: G(`${p}-header-box`, {
      [`${p}-collapsible`]: c && y
    })
  }, /* @__PURE__ */ x.createElement(Dt.Text, {
    strong: !0,
    ellipsis: {
      tooltip: {
        placement: f === "rtl" ? "topRight" : "topLeft",
        title: h
      }
    },
    className: `${p}-title`
  }, c && y && (f === "rtl" ? /* @__PURE__ */ x.createElement(pn, {
    className: `${p}-collapse-icon`,
    rotate: T ? -90 : 0
  }) : /* @__PURE__ */ x.createElement(gn, {
    className: `${p}-collapse-icon`,
    rotate: T ? 90 : 0
  })), h), w && /* @__PURE__ */ x.createElement(Dt.Text, {
    className: `${p}-desc`,
    ellipsis: {
      tooltip: {
        placement: f === "rtl" ? "topRight" : "topLeft",
        title: w
      }
    },
    type: "secondary"
  }, w)), S && /* @__PURE__ */ x.createElement("div", {
    className: `${p}-extra`
  }, S)), y && /* @__PURE__ */ x.createElement(Ur, fe({}, s, {
    visible: c ? T : !0
  }), ({
    className: R,
    style: L
  }, $) => /* @__PURE__ */ x.createElement("div", {
    className: G(`${p}-content`, R),
    ref: $,
    style: L
  }, /* @__PURE__ */ x.createElement("div", {
    className: G(`${p}-content-box`, u.itemContent),
    style: d.itemContent
  }, y))), _ && /* @__PURE__ */ x.createElement("div", {
    className: G(`${p}-footer`, u.itemFooter),
    style: d.itemFooter
  }, _));
}, Ii = (e) => {
  const {
    componentCls: t
  } = e, r = `${t}-item`, o = {
    [mt.PENDING]: e.colorPrimaryText,
    [mt.SUCCESS]: e.colorSuccessText,
    [mt.ERROR]: e.colorErrorText
  }, n = Object.keys(o);
  return n.reduce((i, a) => {
    const s = o[a];
    return n.forEach((c) => {
      const l = `& ${r}-${a}-${c}`, f = a === c ? {} : {
        backgroundColor: "none !important",
        backgroundImage: `linear-gradient(${s}, ${o[c]})`
      };
      i[l] = {
        [`& ${r}-icon, & > *::before`]: {
          backgroundColor: `${s} !important`
        },
        "& > :last-child::before": f
      };
    }), i;
  }, {});
}, ji = (e) => {
  const {
    calc: t,
    componentCls: r
  } = e, o = `${r}-item`, n = {
    content: '""',
    width: t(e.lineWidth).mul(2).equal(),
    display: "block",
    position: "absolute",
    insetInlineEnd: "none",
    backgroundColor: e.colorTextPlaceholder
  };
  return {
    "& > :last-child > :last-child": {
      "&::before": {
        display: "none !important"
      },
      [`&${o}-footer`]: {
        "&::before": {
          display: "block !important",
          bottom: 0
        }
      }
    },
    [`& > ${o}`]: {
      [`& ${o}-header, & ${o}-content, & ${o}-footer`]: {
        position: "relative",
        "&::before": {
          bottom: t(e.itemGap).mul(-1).equal()
        }
      },
      [`& ${o}-header, & ${o}-content`]: {
        marginInlineStart: t(e.itemSize).mul(-1).equal(),
        "&::before": {
          ...n,
          insetInlineStart: t(e.itemSize).div(2).sub(e.lineWidth).equal()
        }
      },
      [`& ${o}-header::before`]: {
        top: e.itemSize,
        bottom: t(e.itemGap).mul(-2).equal()
      },
      [`& ${o}-content::before`]: {
        top: "100%"
      },
      [`& ${o}-footer::before`]: {
        ...n,
        top: 0,
        insetInlineStart: t(e.itemSize).div(-2).sub(e.lineWidth).equal()
      }
    }
  };
}, zi = (e) => {
  const {
    componentCls: t
  } = e, r = `${t}-item`;
  return {
    [r]: {
      display: "flex",
      flexDirection: "column",
      [`& ${r}-collapsible`]: {
        cursor: "pointer"
      },
      [`& ${r}-header`]: {
        display: "flex",
        marginBottom: e.itemGap,
        gap: e.itemGap,
        alignItems: "flex-start",
        [`& ${r}-icon`]: {
          height: e.itemSize,
          width: e.itemSize,
          fontSize: e.itemFontSize
        },
        [`& ${r}-extra`]: {
          height: e.itemSize,
          maxHeight: e.itemSize
        },
        [`& ${r}-header-box`]: {
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          [`& ${r}-title`]: {
            height: e.itemSize,
            lineHeight: `${ze(e.itemSize)}`,
            maxHeight: e.itemSize,
            fontSize: e.itemFontSize,
            [`& ${r}-collapse-icon`]: {
              marginInlineEnd: e.marginXS
            }
          },
          [`& ${r}-desc`]: {
            fontSize: e.itemFontSize
          }
        }
      },
      [`& ${r}-content`]: {
        [`& ${r}-content-hidden`]: {
          display: "none"
        },
        [`& ${r}-content-box`]: {
          padding: e.itemGap,
          display: "inline-block",
          maxWidth: `calc(100% - ${e.itemSize})`,
          borderRadius: e.borderRadiusLG,
          backgroundColor: e.colorBgContainer,
          border: `${ze(e.lineWidth)} ${e.lineType} ${e.colorBorderSecondary}`
        }
      },
      [`& ${r}-footer`]: {
        marginTop: e.itemGap,
        display: "inline-flex"
      }
    }
  };
}, ht = (e, t = "middle") => {
  const {
    componentCls: r
  } = e, o = {
    large: {
      itemSize: e.itemSizeLG,
      itemGap: e.itemGapLG,
      itemFontSize: e.itemFontSizeLG
    },
    middle: {
      itemSize: e.itemSize,
      itemGap: e.itemGap,
      itemFontSize: e.itemFontSize
    },
    small: {
      itemSize: e.itemSizeSM,
      itemGap: e.itemGapSM,
      itemFontSize: e.itemFontSizeSM
    }
  }[t];
  return {
    [`&${r}-${t}`]: {
      paddingInlineStart: o.itemSize,
      gap: o.itemGap,
      ...zi({
        ...e,
        ...o
      }),
      ...ji({
        ...e,
        ...o
      })
    }
  };
}, Di = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      display: "flex",
      flexDirection: "column",
      ...Ii(e),
      ...ht(e),
      ...ht(e, "large"),
      ...ht(e, "small"),
      [`&${t}-rtl`]: {
        direction: "rtl"
      }
    }
  };
}, ki = ei("ThoughtChain", (e) => {
  const t = Rt(e, {
    // small size tokens
    itemFontSizeSM: e.fontSizeSM,
    itemSizeSM: e.calc(e.controlHeightXS).add(e.controlHeightSM).div(2).equal(),
    itemGapSM: e.marginSM,
    // default size tokens
    itemFontSize: e.fontSize,
    itemSize: e.calc(e.controlHeightSM).add(e.controlHeight).div(2).equal(),
    itemGap: e.margin,
    // large size tokens
    itemFontSizeLG: e.fontSizeLG,
    itemSizeLG: e.calc(e.controlHeight).add(e.controlHeightLG).div(2).equal(),
    itemGapLG: e.marginLG
  });
  return [Di(t), $i(t)];
}), Ni = (e) => {
  const {
    prefixCls: t,
    rootClassName: r,
    className: o,
    items: n,
    collapsible: i,
    styles: a = {},
    style: s,
    classNames: c = {},
    size: l = "middle",
    ...f
  } = e, u = Wr(f, {
    attr: !0,
    aria: !0,
    data: !0
  }), {
    getPrefixCls: d,
    direction: m
  } = bt(), v = d(), g = d("thought-chain", t), h = oo("thoughtChain"), [S, y, _, b] = Li(i, g, v), [w, p, P] = ki(g), T = G(o, r, g, h.className, p, P, {
    [`${g}-rtl`]: m === "rtl"
  }, `${g}-${l}`);
  return w(/* @__PURE__ */ x.createElement("div", fe({}, u, {
    className: T,
    style: {
      ...h.style,
      ...s
    }
  }), /* @__PURE__ */ x.createElement(Kr.Provider, {
    value: {
      prefixCls: g,
      enableCollapse: S,
      collapseMotion: b,
      expandedKeys: y,
      direction: m,
      classNames: {
        itemHeader: G(h.classNames.itemHeader, c.itemHeader),
        itemContent: G(h.classNames.itemContent, c.itemContent),
        itemFooter: G(h.classNames.itemFooter, c.itemFooter)
      },
      styles: {
        itemHeader: {
          ...h.styles.itemHeader,
          ...a.itemHeader
        },
        itemContent: {
          ...h.styles.itemContent,
          ...a.itemContent
        },
        itemFooter: {
          ...h.styles.itemFooter,
          ...a.itemFooter
        }
      }
    }
  }, n == null ? void 0 : n.map((R, L) => {
    var $;
    return /* @__PURE__ */ x.createElement(Ai, {
      key: R.key || `key_${L}`,
      className: G(h.classNames.item, c.item),
      style: {
        ...h.styles.item,
        ...a.item
      },
      info: {
        ...R,
        icon: R.icon || L + 1
      },
      onClick: _,
      nextStatus: (($ = n[L + 1]) == null ? void 0 : $.status) || R.status
    });
  }))));
}, Fi = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Hi(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const o = e[r];
    return t[r] = Vi(r, o), t;
  }, {}) : {};
}
function Vi(e, t) {
  return typeof t == "number" && !Fi.includes(e) ? t + "px" : t;
}
function Pt(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const n = x.Children.toArray(e._reactElement.props.children).map((i) => {
      if (x.isValidElement(i) && i.props.__slot__) {
        const {
          portals: a,
          clonedElement: s
        } = Pt(i.props.el);
        return x.cloneElement(i, {
          ...i.props,
          el: s,
          children: [...x.Children.toArray(i.props.children), ...a]
        });
      }
      return null;
    });
    return n.originalChildren = e._reactElement.props.children, t.push(pt(x.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: n
    }), r)), {
      clonedElement: r,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((n) => {
    e.getEventListeners(n).forEach(({
      listener: a,
      type: s,
      useCapture: c
    }) => {
      r.addEventListener(s, a, c);
    });
  });
  const o = Array.from(e.childNodes);
  for (let n = 0; n < o.length; n++) {
    const i = o[n];
    if (i.nodeType === 1) {
      const {
        clonedElement: a,
        portals: s
      } = Pt(i);
      t.push(...s), r.appendChild(a);
    } else i.nodeType === 3 && r.appendChild(i.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function Bi(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const yr = tn(({
  slot: e,
  clone: t,
  className: r,
  style: o,
  observeAttributes: n
}, i) => {
  const a = ee(), [s, c] = rn([]), {
    forceClone: l
  } = cn(), f = l ? !0 : t;
  return ge(() => {
    var g;
    if (!a.current || !e)
      return;
    let u = e;
    function d() {
      let h = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (h = u.children[0], h.tagName.toLowerCase() === "react-portal-target" && h.children[0] && (h = h.children[0])), Bi(i, h), r && h.classList.add(...r.split(" ")), o) {
        const S = Hi(o);
        Object.keys(S).forEach((y) => {
          h.style[y] = S[y];
        });
      }
    }
    let m = null, v = null;
    if (f && window.MutationObserver) {
      let h = function() {
        var b, w, p;
        (b = a.current) != null && b.contains(u) && ((w = a.current) == null || w.removeChild(u));
        const {
          portals: y,
          clonedElement: _
        } = Pt(e);
        u = _, c(y), u.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          d();
        }, 50), (p = a.current) == null || p.appendChild(u);
      };
      h();
      const S = Mn(() => {
        h(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: n
        });
      }, 50);
      m = new window.MutationObserver(S), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", d(), (g = a.current) == null || g.appendChild(u);
    return () => {
      var h, S;
      u.style.display = "", (h = a.current) != null && h.contains(u) && ((S = a.current) == null || S.removeChild(u)), m == null || m.disconnect();
    };
  }, [e, f, r, o, i, n, l]), x.createElement("react-child", {
    ref: a,
    style: {
      display: "contents"
    }
  }, ...s);
}), Gi = ({
  children: e,
  ...t
}) => /* @__PURE__ */ q.jsx(q.Fragment, {
  children: e(t)
});
function Xi(e) {
  return x.createElement(Gi, {
    children: e
  });
}
function qr(e, t, r) {
  const o = e.filter(Boolean);
  if (o.length !== 0)
    return o.map((n, i) => {
      var l, f;
      if (typeof n != "object")
        return t != null && t.fallback ? t.fallback(n) : n;
      const a = t != null && t.itemPropsTransformer ? t == null ? void 0 : t.itemPropsTransformer({
        ...n.props,
        key: ((l = n.props) == null ? void 0 : l.key) ?? (r ? `${r}-${i}` : `${i}`)
      }) : {
        ...n.props,
        key: ((f = n.props) == null ? void 0 : f.key) ?? (r ? `${r}-${i}` : `${i}`)
      };
      let s = a;
      Object.keys(n.slots).forEach((u) => {
        if (!n.slots[u] || !(n.slots[u] instanceof Element) && !n.slots[u].el)
          return;
        const d = u.split(".");
        d.forEach((y, _) => {
          s[y] || (s[y] = {}), _ !== d.length - 1 && (s = a[y]);
        });
        const m = n.slots[u];
        let v, g, h = (t == null ? void 0 : t.clone) ?? !1, S = t == null ? void 0 : t.forceClone;
        m instanceof Element ? v = m : (v = m.el, g = m.callback, h = m.clone ?? h, S = m.forceClone ?? S), S = S ?? !!g, s[d[d.length - 1]] = v ? g ? (...y) => (g(d[d.length - 1], y), /* @__PURE__ */ q.jsx(zt, {
          ...n.ctx,
          params: y,
          forceClone: S,
          children: /* @__PURE__ */ q.jsx(yr, {
            slot: v,
            clone: h
          })
        })) : Xi((y) => /* @__PURE__ */ q.jsx(zt, {
          ...n.ctx,
          forceClone: S,
          children: /* @__PURE__ */ q.jsx(yr, {
            ...y,
            slot: v,
            clone: h
          })
        })) : s[d[d.length - 1]], s = a;
      });
      const c = (t == null ? void 0 : t.children) || "children";
      return n[c] ? a[c] = qr(n[c], t, `${i}`) : t != null && t.children && (a[c] = void 0, Reflect.deleteProperty(a, c)), a;
    });
}
const {
  useItems: Ui,
  withItemsContextProvider: Wi,
  ItemHandler: Qi
} = ln("antdx-thought-chain-items"), Yi = eo(Wi(["default", "items"], ({
  children: e,
  items: t,
  ...r
}) => {
  const {
    items: o
  } = Ui(), n = o.items.length > 0 ? o.items : o.default;
  return /* @__PURE__ */ q.jsxs(q.Fragment, {
    children: [/* @__PURE__ */ q.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ q.jsx(Ni, {
      ...r,
      items: nn(() => t || qr(n, {
        clone: !0
      }), [t, n])
    })]
  });
}));
export {
  Yi as ThoughtChain,
  Yi as default
};
