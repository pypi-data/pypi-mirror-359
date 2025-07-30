import { i as Yt, a as Q, r as Qt, w as ue, g as Jt, c as q, b as Ne } from "./Index-DfIIeNBh.js";
const w = window.ms_globals.React, m = window.ms_globals.React, Wt = window.ms_globals.React.version, Ut = window.ms_globals.React.forwardRef, wt = window.ms_globals.React.useRef, Gt = window.ms_globals.React.useState, Kt = window.ms_globals.React.useEffect, qt = window.ms_globals.React.useCallback, ge = window.ms_globals.React.useMemo, Be = window.ms_globals.ReactDOM.createPortal, Zt = window.ms_globals.internalContext.useContextPropsContext, Je = window.ms_globals.internalContext.ContextPropsProvider, _t = window.ms_globals.createItemsContext.createItemsContext, er = window.ms_globals.antd.ConfigProvider, He = window.ms_globals.antd.theme, tr = window.ms_globals.antd.Avatar, oe = window.ms_globals.antdCssinjs.unit, Re = window.ms_globals.antdCssinjs.token2CSSVar, Ze = window.ms_globals.antdCssinjs.useStyleRegister, rr = window.ms_globals.antdCssinjs.useCSSVarRegister, nr = window.ms_globals.antdCssinjs.createTheme, or = window.ms_globals.antdCssinjs.useCacheToken, Tt = window.ms_globals.antdCssinjs.Keyframes;
var sr = /\s/;
function ir(t) {
  for (var e = t.length; e-- && sr.test(t.charAt(e)); )
    ;
  return e;
}
var ar = /^\s+/;
function lr(t) {
  return t && t.slice(0, ir(t) + 1).replace(ar, "");
}
var et = NaN, cr = /^[-+]0x[0-9a-f]+$/i, ur = /^0b[01]+$/i, fr = /^0o[0-7]+$/i, dr = parseInt;
function tt(t) {
  if (typeof t == "number")
    return t;
  if (Yt(t))
    return et;
  if (Q(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = Q(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = lr(t);
  var n = ur.test(t);
  return n || fr.test(t) ? dr(t.slice(2), n ? 2 : 8) : cr.test(t) ? et : +t;
}
var je = function() {
  return Qt.Date.now();
}, hr = "Expected a function", gr = Math.max, mr = Math.min;
function pr(t, e, n) {
  var o, r, s, i, a, l, c = 0, u = !1, f = !1, d = !0;
  if (typeof t != "function")
    throw new TypeError(hr);
  e = tt(e) || 0, Q(n) && (u = !!n.leading, f = "maxWait" in n, s = f ? gr(tt(n.maxWait) || 0, e) : s, d = "trailing" in n ? !!n.trailing : d);
  function h(y) {
    var P = o, O = r;
    return o = r = void 0, c = y, i = t.apply(O, P), i;
  }
  function p(y) {
    return c = y, a = setTimeout(v, e), u ? h(y) : i;
  }
  function x(y) {
    var P = y - l, O = y - c, R = e - P;
    return f ? mr(R, s - O) : R;
  }
  function b(y) {
    var P = y - l, O = y - c;
    return l === void 0 || P >= e || P < 0 || f && O >= s;
  }
  function v() {
    var y = je();
    if (b(y))
      return S(y);
    a = setTimeout(v, x(y));
  }
  function S(y) {
    return a = void 0, d && o ? h(y) : (o = r = void 0, i);
  }
  function M() {
    a !== void 0 && clearTimeout(a), c = 0, o = l = r = a = void 0;
  }
  function g() {
    return a === void 0 ? i : S(je());
  }
  function E() {
    var y = je(), P = b(y);
    if (o = arguments, r = this, l = y, P) {
      if (a === void 0)
        return p(l);
      if (f)
        return clearTimeout(a), a = setTimeout(v, e), h(l);
    }
    return a === void 0 && (a = setTimeout(v, e)), i;
  }
  return E.cancel = M, E.flush = g, E;
}
var Et = {
  exports: {}
}, be = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var br = m, yr = Symbol.for("react.element"), vr = Symbol.for("react.fragment"), Sr = Object.prototype.hasOwnProperty, xr = br.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Cr = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Pt(t, e, n) {
  var o, r = {}, s = null, i = null;
  n !== void 0 && (s = "" + n), e.key !== void 0 && (s = "" + e.key), e.ref !== void 0 && (i = e.ref);
  for (o in e) Sr.call(e, o) && !Cr.hasOwnProperty(o) && (r[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) r[o] === void 0 && (r[o] = e[o]);
  return {
    $$typeof: yr,
    type: t,
    key: s,
    ref: i,
    props: r,
    _owner: xr.current
  };
}
be.Fragment = vr;
be.jsx = Pt;
be.jsxs = Pt;
Et.exports = be;
var A = Et.exports;
const {
  SvelteComponent: wr,
  assign: rt,
  binding_callbacks: nt,
  check_outros: _r,
  children: Ot,
  claim_element: Mt,
  claim_space: Tr,
  component_subscribe: ot,
  compute_slots: Er,
  create_slot: Pr,
  detach: Y,
  element: It,
  empty: st,
  exclude_internal_props: it,
  get_all_dirty_from_scope: Or,
  get_slot_changes: Mr,
  group_outros: Ir,
  init: Rr,
  insert_hydration: fe,
  safe_not_equal: jr,
  set_custom_element_data: Rt,
  space: kr,
  transition_in: de,
  transition_out: ze,
  update_slot_base: Lr
} = window.__gradio__svelte__internal, {
  beforeUpdate: $r,
  getContext: Dr,
  onDestroy: Br,
  setContext: Hr
} = window.__gradio__svelte__internal;
function at(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), r = Pr(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = It("svelte-slot"), r && r.c(), this.h();
    },
    l(s) {
      e = Mt(s, "SVELTE-SLOT", {
        class: !0
      });
      var i = Ot(e);
      r && r.l(i), i.forEach(Y), this.h();
    },
    h() {
      Rt(e, "class", "svelte-1rt0kpf");
    },
    m(s, i) {
      fe(s, e, i), r && r.m(e, null), t[9](e), n = !0;
    },
    p(s, i) {
      r && r.p && (!n || i & /*$$scope*/
      64) && Lr(
        r,
        o,
        s,
        /*$$scope*/
        s[6],
        n ? Mr(
          o,
          /*$$scope*/
          s[6],
          i,
          null
        ) : Or(
          /*$$scope*/
          s[6]
        ),
        null
      );
    },
    i(s) {
      n || (de(r, s), n = !0);
    },
    o(s) {
      ze(r, s), n = !1;
    },
    d(s) {
      s && Y(e), r && r.d(s), t[9](null);
    }
  };
}
function zr(t) {
  let e, n, o, r, s = (
    /*$$slots*/
    t[4].default && at(t)
  );
  return {
    c() {
      e = It("react-portal-target"), n = kr(), s && s.c(), o = st(), this.h();
    },
    l(i) {
      e = Mt(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), Ot(e).forEach(Y), n = Tr(i), s && s.l(i), o = st(), this.h();
    },
    h() {
      Rt(e, "class", "svelte-1rt0kpf");
    },
    m(i, a) {
      fe(i, e, a), t[8](e), fe(i, n, a), s && s.m(i, a), fe(i, o, a), r = !0;
    },
    p(i, [a]) {
      /*$$slots*/
      i[4].default ? s ? (s.p(i, a), a & /*$$slots*/
      16 && de(s, 1)) : (s = at(i), s.c(), de(s, 1), s.m(o.parentNode, o)) : s && (Ir(), ze(s, 1, 1, () => {
        s = null;
      }), _r());
    },
    i(i) {
      r || (de(s), r = !0);
    },
    o(i) {
      ze(s), r = !1;
    },
    d(i) {
      i && (Y(e), Y(n), Y(o)), t[8](null), s && s.d(i);
    }
  };
}
function lt(t) {
  const {
    svelteInit: e,
    ...n
  } = t;
  return n;
}
function Ar(t, e, n) {
  let o, r, {
    $$slots: s = {},
    $$scope: i
  } = e;
  const a = Er(s);
  let {
    svelteInit: l
  } = e;
  const c = ue(lt(e)), u = ue();
  ot(t, u, (g) => n(0, o = g));
  const f = ue();
  ot(t, f, (g) => n(1, r = g));
  const d = [], h = Dr("$$ms-gr-react-wrapper"), {
    slotKey: p,
    slotIndex: x,
    subSlotIndex: b
  } = Jt() || {}, v = l({
    parent: h,
    props: c,
    target: u,
    slot: f,
    slotKey: p,
    slotIndex: x,
    subSlotIndex: b,
    onDestroy(g) {
      d.push(g);
    }
  });
  Hr("$$ms-gr-react-wrapper", v), $r(() => {
    c.set(lt(e));
  }), Br(() => {
    d.forEach((g) => g());
  });
  function S(g) {
    nt[g ? "unshift" : "push"](() => {
      o = g, u.set(o);
    });
  }
  function M(g) {
    nt[g ? "unshift" : "push"](() => {
      r = g, f.set(r);
    });
  }
  return t.$$set = (g) => {
    n(17, e = rt(rt({}, e), it(g))), "svelteInit" in g && n(5, l = g.svelteInit), "$$scope" in g && n(6, i = g.$$scope);
  }, e = it(e), [o, r, u, f, a, l, i, s, S, M];
}
class Fr extends wr {
  constructor(e) {
    super(), Rr(this, e, Ar, zr, jr, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: So
} = window.__gradio__svelte__internal, ct = window.ms_globals.rerender, ke = window.ms_globals.tree;
function Xr(t, e = {}) {
  function n(o) {
    const r = ue(), s = new Fr({
      ...o,
      props: {
        svelteInit(i) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: t,
            props: i.props,
            slot: i.slot,
            target: i.target,
            slotIndex: i.slotIndex,
            subSlotIndex: i.subSlotIndex,
            ignore: e.ignore,
            slotKey: i.slotKey,
            nodes: []
          }, l = i.parent ?? ke;
          return l.nodes = [...l.nodes, a], ct({
            createPortal: Be,
            node: ke
          }), i.onDestroy(() => {
            l.nodes = l.nodes.filter((c) => c.svelteInstance !== r), ct({
              createPortal: Be,
              node: ke
            });
          }), a;
        },
        ...o.props
      }
    });
    return r.set(s), s;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(n);
    });
  });
}
const Nr = "1.4.0";
function J() {
  return J = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (t[o] = n[o]);
    }
    return t;
  }, J.apply(null, arguments);
}
const Vr = /* @__PURE__ */ m.createContext({}), Wr = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, Ur = (t) => {
  const e = m.useContext(Vr);
  return m.useMemo(() => ({
    ...Wr,
    ...e[t]
  }), [e[t]]);
};
function me() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = m.useContext(er.ConfigContext);
  return {
    theme: r,
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o
  };
}
function X(t) {
  "@babel/helpers - typeof";
  return X = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, X(t);
}
function Gr(t) {
  if (Array.isArray(t)) return t;
}
function Kr(t, e) {
  var n = t == null ? null : typeof Symbol < "u" && t[Symbol.iterator] || t["@@iterator"];
  if (n != null) {
    var o, r, s, i, a = [], l = !0, c = !1;
    try {
      if (s = (n = n.call(t)).next, e === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (o = s.call(n)).done) && (a.push(o.value), a.length !== e); l = !0) ;
    } catch (u) {
      c = !0, r = u;
    } finally {
      try {
        if (!l && n.return != null && (i = n.return(), Object(i) !== i)) return;
      } finally {
        if (c) throw r;
      }
    }
    return a;
  }
}
function ut(t, e) {
  (e == null || e > t.length) && (e = t.length);
  for (var n = 0, o = Array(e); n < e; n++) o[n] = t[n];
  return o;
}
function qr(t, e) {
  if (t) {
    if (typeof t == "string") return ut(t, e);
    var n = {}.toString.call(t).slice(8, -1);
    return n === "Object" && t.constructor && (n = t.constructor.name), n === "Map" || n === "Set" ? Array.from(t) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? ut(t, e) : void 0;
  }
}
function Yr() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function he(t, e) {
  return Gr(t) || Kr(t, e) || qr(t, e) || Yr();
}
function Qr(t, e) {
  if (X(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (X(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function jt(t) {
  var e = Qr(t, "string");
  return X(e) == "symbol" ? e : e + "";
}
function I(t, e, n) {
  return (e = jt(e)) in t ? Object.defineProperty(t, e, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = n, t;
}
function ft(t, e) {
  var n = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(t, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function H(t) {
  for (var e = 1; e < arguments.length; e++) {
    var n = arguments[e] != null ? arguments[e] : {};
    e % 2 ? ft(Object(n), !0).forEach(function(o) {
      I(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : ft(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
function ye(t, e) {
  if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function Jr(t, e) {
  for (var n = 0; n < e.length; n++) {
    var o = e[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, jt(o.key), o);
  }
}
function ve(t, e, n) {
  return e && Jr(t.prototype, e), Object.defineProperty(t, "prototype", {
    writable: !1
  }), t;
}
function ne(t) {
  if (t === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return t;
}
function Ae(t, e) {
  return Ae = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Ae(t, e);
}
function kt(t, e) {
  if (typeof e != "function" && e !== null) throw new TypeError("Super expression must either be null or a function");
  t.prototype = Object.create(e && e.prototype, {
    constructor: {
      value: t,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(t, "prototype", {
    writable: !1
  }), e && Ae(t, e);
}
function pe(t) {
  return pe = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, pe(t);
}
function Lt() {
  try {
    var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Lt = function() {
    return !!t;
  })();
}
function Zr(t, e) {
  if (e && (X(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return ne(t);
}
function $t(t) {
  var e = Lt();
  return function() {
    var n, o = pe(t);
    if (e) {
      var r = pe(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return Zr(this, n);
  };
}
var Dt = /* @__PURE__ */ ve(function t() {
  ye(this, t);
}), Bt = "CALC_UNIT", en = new RegExp(Bt, "g");
function Le(t) {
  return typeof t == "number" ? "".concat(t).concat(Bt) : t;
}
var tn = /* @__PURE__ */ function(t) {
  kt(n, t);
  var e = $t(n);
  function n(o, r) {
    var s;
    ye(this, n), s = e.call(this), I(ne(s), "result", ""), I(ne(s), "unitlessCssVar", void 0), I(ne(s), "lowPriority", void 0);
    var i = X(o);
    return s.unitlessCssVar = r, o instanceof n ? s.result = "(".concat(o.result, ")") : i === "number" ? s.result = Le(o) : i === "string" && (s.result = o), s;
  }
  return ve(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(Le(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(Le(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(r) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), r instanceof n ? this.result = "".concat(this.result, " * ").concat(r.getResult(!0)) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " * ").concat(r)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(r) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), r instanceof n ? this.result = "".concat(this.result, " / ").concat(r.getResult(!0)) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " / ").concat(r)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(r) {
      return this.lowPriority || r ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(r) {
      var s = this, i = r || {}, a = i.unit, l = !0;
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(c) {
        return s.result.includes(c);
      }) && (l = !1), this.result = this.result.replace(en, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(Dt), rn = /* @__PURE__ */ function(t) {
  kt(n, t);
  var e = $t(n);
  function n(o) {
    var r;
    return ye(this, n), r = e.call(this), I(ne(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return ve(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result += r.result : typeof r == "number" && (this.result += r), this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result -= r.result : typeof r == "number" && (this.result -= r), this;
    }
  }, {
    key: "mul",
    value: function(r) {
      return r instanceof n ? this.result *= r.result : typeof r == "number" && (this.result *= r), this;
    }
  }, {
    key: "div",
    value: function(r) {
      return r instanceof n ? this.result /= r.result : typeof r == "number" && (this.result /= r), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), n;
}(Dt), nn = function(e, n) {
  var o = e === "css" ? tn : rn;
  return function(r) {
    return new o(r, n);
  };
}, dt = function(e, n) {
  return "".concat([n, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function on(t) {
  var e = w.useRef();
  e.current = t;
  var n = w.useCallback(function() {
    for (var o, r = arguments.length, s = new Array(r), i = 0; i < r; i++)
      s[i] = arguments[i];
    return (o = e.current) === null || o === void 0 ? void 0 : o.call.apply(o, [e].concat(s));
  }, []);
  return n;
}
function sn() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var ht = sn() ? w.useLayoutEffect : w.useEffect, an = function(e, n) {
  var o = w.useRef(!0);
  ht(function() {
    return e(o.current);
  }, n), ht(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
};
function se(t) {
  "@babel/helpers - typeof";
  return se = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, se(t);
}
var _ = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ve = Symbol.for("react.element"), We = Symbol.for("react.portal"), Se = Symbol.for("react.fragment"), xe = Symbol.for("react.strict_mode"), Ce = Symbol.for("react.profiler"), we = Symbol.for("react.provider"), _e = Symbol.for("react.context"), ln = Symbol.for("react.server_context"), Te = Symbol.for("react.forward_ref"), Ee = Symbol.for("react.suspense"), Pe = Symbol.for("react.suspense_list"), Oe = Symbol.for("react.memo"), Me = Symbol.for("react.lazy"), cn = Symbol.for("react.offscreen"), Ht;
Ht = Symbol.for("react.module.reference");
function F(t) {
  if (typeof t == "object" && t !== null) {
    var e = t.$$typeof;
    switch (e) {
      case Ve:
        switch (t = t.type, t) {
          case Se:
          case Ce:
          case xe:
          case Ee:
          case Pe:
            return t;
          default:
            switch (t = t && t.$$typeof, t) {
              case ln:
              case _e:
              case Te:
              case Me:
              case Oe:
              case we:
                return t;
              default:
                return e;
            }
        }
      case We:
        return e;
    }
  }
}
_.ContextConsumer = _e;
_.ContextProvider = we;
_.Element = Ve;
_.ForwardRef = Te;
_.Fragment = Se;
_.Lazy = Me;
_.Memo = Oe;
_.Portal = We;
_.Profiler = Ce;
_.StrictMode = xe;
_.Suspense = Ee;
_.SuspenseList = Pe;
_.isAsyncMode = function() {
  return !1;
};
_.isConcurrentMode = function() {
  return !1;
};
_.isContextConsumer = function(t) {
  return F(t) === _e;
};
_.isContextProvider = function(t) {
  return F(t) === we;
};
_.isElement = function(t) {
  return typeof t == "object" && t !== null && t.$$typeof === Ve;
};
_.isForwardRef = function(t) {
  return F(t) === Te;
};
_.isFragment = function(t) {
  return F(t) === Se;
};
_.isLazy = function(t) {
  return F(t) === Me;
};
_.isMemo = function(t) {
  return F(t) === Oe;
};
_.isPortal = function(t) {
  return F(t) === We;
};
_.isProfiler = function(t) {
  return F(t) === Ce;
};
_.isStrictMode = function(t) {
  return F(t) === xe;
};
_.isSuspense = function(t) {
  return F(t) === Ee;
};
_.isSuspenseList = function(t) {
  return F(t) === Pe;
};
_.isValidElementType = function(t) {
  return typeof t == "string" || typeof t == "function" || t === Se || t === Ce || t === xe || t === Ee || t === Pe || t === cn || typeof t == "object" && t !== null && (t.$$typeof === Me || t.$$typeof === Oe || t.$$typeof === we || t.$$typeof === _e || t.$$typeof === Te || t.$$typeof === Ht || t.getModuleId !== void 0);
};
_.typeOf = F;
Number(Wt.split(".")[0]);
function un(t, e) {
  if (se(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (se(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function fn(t) {
  var e = un(t, "string");
  return se(e) == "symbol" ? e : e + "";
}
function dn(t, e, n) {
  return (e = fn(e)) in t ? Object.defineProperty(t, e, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = n, t;
}
function gt(t, e) {
  var n = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(t, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function hn(t) {
  for (var e = 1; e < arguments.length; e++) {
    var n = arguments[e] != null ? arguments[e] : {};
    e % 2 ? gt(Object(n), !0).forEach(function(o) {
      dn(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : gt(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
function mt(t, e, n, o) {
  var r = H({}, e[t]);
  if (o != null && o.deprecatedTokens) {
    var s = o.deprecatedTokens;
    s.forEach(function(a) {
      var l = he(a, 2), c = l[0], u = l[1];
      if (r != null && r[c] || r != null && r[u]) {
        var f;
        (f = r[u]) !== null && f !== void 0 || (r[u] = r == null ? void 0 : r[c]);
      }
    });
  }
  var i = H(H({}, n), r);
  return Object.keys(i).forEach(function(a) {
    i[a] === e[a] && delete i[a];
  }), i;
}
var zt = typeof CSSINJS_STATISTIC < "u", Fe = !0;
function Ue() {
  for (var t = arguments.length, e = new Array(t), n = 0; n < t; n++)
    e[n] = arguments[n];
  if (!zt)
    return Object.assign.apply(Object, [{}].concat(e));
  Fe = !1;
  var o = {};
  return e.forEach(function(r) {
    if (X(r) === "object") {
      var s = Object.keys(r);
      s.forEach(function(i) {
        Object.defineProperty(o, i, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return r[i];
          }
        });
      });
    }
  }), Fe = !0, o;
}
var pt = {};
function gn() {
}
var mn = function(e) {
  var n, o = e, r = gn;
  return zt && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(e, {
    get: function(i, a) {
      if (Fe) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return i[a];
    }
  }), r = function(i, a) {
    var l;
    pt[i] = {
      global: Array.from(n),
      component: H(H({}, (l = pt[i]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function bt(t, e, n) {
  if (typeof n == "function") {
    var o;
    return n(Ue(e, (o = e[t]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function pn(t) {
  return t === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(s) {
        return oe(s);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(s) {
        return oe(s);
      }).join(","), ")");
    }
  };
}
var bn = 1e3 * 60 * 10, yn = /* @__PURE__ */ function() {
  function t() {
    ye(this, t), I(this, "map", /* @__PURE__ */ new Map()), I(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), I(this, "nextID", 0), I(this, "lastAccessBeat", /* @__PURE__ */ new Map()), I(this, "accessBeat", 0);
  }
  return ve(t, [{
    key: "set",
    value: function(n, o) {
      this.clear();
      var r = this.getCompositeKey(n);
      this.map.set(r, o), this.lastAccessBeat.set(r, Date.now());
    }
  }, {
    key: "get",
    value: function(n) {
      var o = this.getCompositeKey(n), r = this.map.get(o);
      return this.lastAccessBeat.set(o, Date.now()), this.accessBeat += 1, r;
    }
  }, {
    key: "getCompositeKey",
    value: function(n) {
      var o = this, r = n.map(function(s) {
        return s && X(s) === "object" ? "obj_".concat(o.getObjectID(s)) : "".concat(X(s), "_").concat(s);
      });
      return r.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(n) {
      if (this.objectIDMap.has(n))
        return this.objectIDMap.get(n);
      var o = this.nextID;
      return this.objectIDMap.set(n, o), this.nextID += 1, o;
    }
  }, {
    key: "clear",
    value: function() {
      var n = this;
      if (this.accessBeat > 1e4) {
        var o = Date.now();
        this.lastAccessBeat.forEach(function(r, s) {
          o - r > bn && (n.map.delete(s), n.lastAccessBeat.delete(s));
        }), this.accessBeat = 0;
      }
    }
  }]), t;
}(), yt = new yn();
function vn(t, e) {
  return m.useMemo(function() {
    var n = yt.get(e);
    if (n)
      return n;
    var o = t();
    return yt.set(e, o), o;
  }, e);
}
var Sn = function() {
  return {};
};
function xn(t) {
  var e = t.useCSP, n = e === void 0 ? Sn : e, o = t.useToken, r = t.usePrefix, s = t.getResetStyles, i = t.getCommonStyle, a = t.getCompUnitless;
  function l(d, h, p, x) {
    var b = Array.isArray(d) ? d[0] : d;
    function v(O) {
      return "".concat(String(b)).concat(O.slice(0, 1).toUpperCase()).concat(O.slice(1));
    }
    var S = (x == null ? void 0 : x.unitless) || {}, M = typeof a == "function" ? a(d) : {}, g = H(H({}, M), {}, I({}, v("zIndexPopup"), !0));
    Object.keys(S).forEach(function(O) {
      g[v(O)] = S[O];
    });
    var E = H(H({}, x), {}, {
      unitless: g,
      prefixToken: v
    }), y = u(d, h, p, E), P = c(b, p, E);
    return function(O) {
      var R = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : O, T = y(O, R), k = he(T, 2), C = k[1], j = P(R), L = he(j, 2), D = L[0], B = L[1];
      return [D, C, B];
    };
  }
  function c(d, h, p) {
    var x = p.unitless, b = p.injectStyle, v = b === void 0 ? !0 : b, S = p.prefixToken, M = p.ignore, g = function(P) {
      var O = P.rootCls, R = P.cssVar, T = R === void 0 ? {} : R, k = o(), C = k.realToken;
      return rr({
        path: [d],
        prefix: T.prefix,
        key: T.key,
        unitless: x,
        ignore: M,
        token: C,
        scope: O
      }, function() {
        var j = bt(d, C, h), L = mt(d, C, j, {
          deprecatedTokens: p == null ? void 0 : p.deprecatedTokens
        });
        return Object.keys(j).forEach(function(D) {
          L[S(D)] = L[D], delete L[D];
        }), L;
      }), null;
    }, E = function(P) {
      var O = o(), R = O.cssVar;
      return [function(T) {
        return v && R ? /* @__PURE__ */ m.createElement(m.Fragment, null, /* @__PURE__ */ m.createElement(g, {
          rootCls: P,
          cssVar: R,
          component: d
        }), T) : T;
      }, R == null ? void 0 : R.key];
    };
    return E;
  }
  function u(d, h, p) {
    var x = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, b = Array.isArray(d) ? d : [d, d], v = he(b, 1), S = v[0], M = b.join("-"), g = t.layer || {
      name: "antd"
    };
    return function(E) {
      var y = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : E, P = o(), O = P.theme, R = P.realToken, T = P.hashId, k = P.token, C = P.cssVar, j = r(), L = j.rootPrefixCls, D = j.iconPrefixCls, B = n(), z = C ? "css" : "js", V = vn(function() {
        var W = /* @__PURE__ */ new Set();
        return C && Object.keys(x.unitless || {}).forEach(function(G) {
          W.add(Re(G, C.prefix)), W.add(Re(G, dt(S, C.prefix)));
        }), nn(z, W);
      }, [z, S, C == null ? void 0 : C.prefix]), K = pn(z), ie = K.max, Z = K.min, ae = {
        theme: O,
        token: k,
        hashId: T,
        nonce: function() {
          return B.nonce;
        },
        clientOnly: x.clientOnly,
        layer: g,
        // antd is always at top of styles
        order: x.order || -999
      };
      typeof s == "function" && Ze(H(H({}, ae), {}, {
        clientOnly: !1,
        path: ["Shared", L]
      }), function() {
        return s(k, {
          prefix: {
            rootPrefixCls: L,
            iconPrefixCls: D
          },
          csp: B
        });
      });
      var Ie = Ze(H(H({}, ae), {}, {
        path: [M, E, D]
      }), function() {
        if (x.injectStyle === !1)
          return [];
        var W = mn(k), G = W.token, ee = W.flush, N = bt(S, R, p), te = ".".concat(E), qe = mt(S, R, N, {
          deprecatedTokens: x.deprecatedTokens
        });
        C && N && X(N) === "object" && Object.keys(N).forEach(function(Qe) {
          N[Qe] = "var(".concat(Re(Qe, dt(S, C.prefix)), ")");
        });
        var Ye = Ue(G, {
          componentCls: te,
          prefixCls: E,
          iconCls: ".".concat(D),
          antCls: ".".concat(L),
          calc: V,
          // @ts-ignore
          max: ie,
          // @ts-ignore
          min: Z
        }, C ? N : qe), Nt = h(Ye, {
          hashId: T,
          prefixCls: E,
          rootPrefixCls: L,
          iconPrefixCls: D
        });
        ee(S, qe);
        var Vt = typeof i == "function" ? i(Ye, E, y, x.resetFont) : null;
        return [x.resetStyle === !1 ? null : Vt, Nt];
      });
      return [Ie, T];
    };
  }
  function f(d, h, p) {
    var x = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, b = u(d, h, p, H({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, x)), v = function(M) {
      var g = M.prefixCls, E = M.rootCls, y = E === void 0 ? g : E;
      return b(g, y), null;
    };
    return v;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: f,
    genComponentStyleHook: u
  };
}
const Cn = {
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
}, wn = Object.assign(Object.assign({}, Cn), {
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
}), $ = Math.round;
function $e(t, e) {
  const n = t.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = e(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const vt = (t, e, n) => n === 0 ? t : t / 100;
function re(t, e) {
  const n = e || 255;
  return t > n ? n : t < 0 ? 0 : t;
}
class U {
  constructor(e) {
    I(this, "isValid", !0), I(this, "r", 0), I(this, "g", 0), I(this, "b", 0), I(this, "a", 1), I(this, "_h", void 0), I(this, "_s", void 0), I(this, "_l", void 0), I(this, "_v", void 0), I(this, "_max", void 0), I(this, "_min", void 0), I(this, "_brightness", void 0);
    function n(o) {
      return o[0] in e && o[1] in e && o[2] in e;
    }
    if (e) if (typeof e == "string") {
      let r = function(s) {
        return o.startsWith(s);
      };
      const o = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (e instanceof U)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (n("rgb"))
      this.r = re(e.r), this.g = re(e.g), this.b = re(e.b), this.a = typeof e.a == "number" ? re(e.a, 1) : 1;
    else if (n("hsl"))
      this.fromHsl(e);
    else if (n("hsv"))
      this.fromHsv(e);
    else
      throw new Error("@ant-design/fast-color: unsupported input " + JSON.stringify(e));
  }
  // ======================= Setter =======================
  setR(e) {
    return this._sc("r", e);
  }
  setG(e) {
    return this._sc("g", e);
  }
  setB(e) {
    return this._sc("b", e);
  }
  setA(e) {
    return this._sc("a", e, 1);
  }
  setHue(e) {
    const n = this.toHsv();
    return n.h = e, this._c(n);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function e(s) {
      const i = s / 255;
      return i <= 0.03928 ? i / 12.92 : Math.pow((i + 0.055) / 1.055, 2.4);
    }
    const n = e(this.r), o = e(this.g), r = e(this.b);
    return 0.2126 * n + 0.7152 * o + 0.0722 * r;
  }
  getHue() {
    if (typeof this._h > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._h = 0 : this._h = $(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
    }
    return this._h;
  }
  getSaturation() {
    if (typeof this._s > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._s = 0 : this._s = e / this.getMax();
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
  darken(e = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() - e / 100;
    return r < 0 && (r = 0), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  lighten(e = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() + e / 100;
    return r > 1 && (r = 1), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(e, n = 50) {
    const o = this._c(e), r = n / 100, s = (a) => (o[a] - this[a]) * r + this[a], i = {
      r: $(s("r")),
      g: $(s("g")),
      b: $(s("b")),
      a: $(s("a") * 100) / 100
    };
    return this._c(i);
  }
  /**
   * Mix the color with pure white, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return white.
   */
  tint(e = 10) {
    return this.mix({
      r: 255,
      g: 255,
      b: 255,
      a: 1
    }, e);
  }
  /**
   * Mix the color with pure black, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return black.
   */
  shade(e = 10) {
    return this.mix({
      r: 0,
      g: 0,
      b: 0,
      a: 1
    }, e);
  }
  onBackground(e) {
    const n = this._c(e), o = this.a + n.a * (1 - this.a), r = (s) => $((this[s] * this.a + n[s] * n.a * (1 - this.a)) / o);
    return this._c({
      r: r("r"),
      g: r("g"),
      b: r("b"),
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
  equals(e) {
    return this.r === e.r && this.g === e.g && this.b === e.b && this.a === e.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let e = "#";
    const n = (this.r || 0).toString(16);
    e += n.length === 2 ? n : "0" + n;
    const o = (this.g || 0).toString(16);
    e += o.length === 2 ? o : "0" + o;
    const r = (this.b || 0).toString(16);
    if (e += r.length === 2 ? r : "0" + r, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const s = $(this.a * 255).toString(16);
      e += s.length === 2 ? s : "0" + s;
    }
    return e;
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
    const e = this.getHue(), n = $(this.getSaturation() * 100), o = $(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${e},${n}%,${o}%,${this.a})` : `hsl(${e},${n}%,${o}%)`;
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
  _sc(e, n, o) {
    const r = this.clone();
    return r[e] = re(n, o), r;
  }
  _c(e) {
    return new this.constructor(e);
  }
  getMax() {
    return typeof this._max > "u" && (this._max = Math.max(this.r, this.g, this.b)), this._max;
  }
  getMin() {
    return typeof this._min > "u" && (this._min = Math.min(this.r, this.g, this.b)), this._min;
  }
  fromHexString(e) {
    const n = e.replace("#", "");
    function o(r, s) {
      return parseInt(n[r] + n[s || r], 16);
    }
    n.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = n[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = n[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: e,
    s: n,
    l: o,
    a: r
  }) {
    if (this._h = e % 360, this._s = n, this._l = o, this.a = typeof r == "number" ? r : 1, n <= 0) {
      const d = $(o * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let s = 0, i = 0, a = 0;
    const l = e / 60, c = (1 - Math.abs(2 * o - 1)) * n, u = c * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (s = c, i = u) : l >= 1 && l < 2 ? (s = u, i = c) : l >= 2 && l < 3 ? (i = c, a = u) : l >= 3 && l < 4 ? (i = u, a = c) : l >= 4 && l < 5 ? (s = u, a = c) : l >= 5 && l < 6 && (s = c, a = u);
    const f = o - c / 2;
    this.r = $((s + f) * 255), this.g = $((i + f) * 255), this.b = $((a + f) * 255);
  }
  fromHsv({
    h: e,
    s: n,
    v: o,
    a: r
  }) {
    this._h = e % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const s = $(o * 255);
    if (this.r = s, this.g = s, this.b = s, n <= 0)
      return;
    const i = e / 60, a = Math.floor(i), l = i - a, c = $(o * (1 - n) * 255), u = $(o * (1 - n * l) * 255), f = $(o * (1 - n * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = f, this.b = c;
        break;
      case 1:
        this.r = u, this.b = c;
        break;
      case 2:
        this.r = c, this.b = f;
        break;
      case 3:
        this.r = c, this.g = u;
        break;
      case 4:
        this.r = f, this.g = c;
        break;
      case 5:
      default:
        this.g = c, this.b = u;
        break;
    }
  }
  fromHsvString(e) {
    const n = $e(e, vt);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(e) {
    const n = $e(e, vt);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(e) {
    const n = $e(e, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? $(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function De(t) {
  return t >= 0 && t <= 255;
}
function le(t, e) {
  const {
    r: n,
    g: o,
    b: r,
    a: s
  } = new U(t).toRgb();
  if (s < 1)
    return t;
  const {
    r: i,
    g: a,
    b: l
  } = new U(e).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const u = Math.round((n - i * (1 - c)) / c), f = Math.round((o - a * (1 - c)) / c), d = Math.round((r - l * (1 - c)) / c);
    if (De(u) && De(f) && De(d))
      return new U({
        r: u,
        g: f,
        b: d,
        a: Math.round(c * 100) / 100
      }).toRgbString();
  }
  return new U({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var _n = function(t, e) {
  var n = {};
  for (var o in t) Object.prototype.hasOwnProperty.call(t, o) && e.indexOf(o) < 0 && (n[o] = t[o]);
  if (t != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(t); r < o.length; r++)
    e.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(t, o[r]) && (n[o[r]] = t[o[r]]);
  return n;
};
function Tn(t) {
  const {
    override: e
  } = t, n = _n(t, ["override"]), o = Object.assign({}, e);
  Object.keys(wn).forEach((d) => {
    delete o[d];
  });
  const r = Object.assign(Object.assign({}, n), o), s = 480, i = 576, a = 768, l = 992, c = 1200, u = 1600;
  if (r.motion === !1) {
    const d = "0s";
    r.motionDurationFast = d, r.motionDurationMid = d, r.motionDurationSlow = d;
  }
  return Object.assign(Object.assign(Object.assign({}, r), {
    // ============== Background ============== //
    colorFillContent: r.colorFillSecondary,
    colorFillContentHover: r.colorFill,
    colorFillAlter: r.colorFillQuaternary,
    colorBgContainerDisabled: r.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: r.colorBgContainer,
    colorSplit: le(r.colorBorderSecondary, r.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: r.colorTextQuaternary,
    colorTextDisabled: r.colorTextQuaternary,
    colorTextHeading: r.colorText,
    colorTextLabel: r.colorTextSecondary,
    colorTextDescription: r.colorTextTertiary,
    colorTextLightSolid: r.colorWhite,
    colorHighlight: r.colorError,
    colorBgTextHover: r.colorFillSecondary,
    colorBgTextActive: r.colorFill,
    colorIcon: r.colorTextTertiary,
    colorIconHover: r.colorText,
    colorErrorOutline: le(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: le(r.colorWarningBg, r.colorBgContainer),
    // Font
    fontSizeIcon: r.fontSizeSM,
    // Line
    lineWidthFocus: r.lineWidth * 3,
    // Control
    lineWidth: r.lineWidth,
    controlOutlineWidth: r.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: r.controlHeight / 2,
    controlItemBgHover: r.colorFillTertiary,
    controlItemBgActive: r.colorPrimaryBg,
    controlItemBgActiveHover: r.colorPrimaryBgHover,
    controlItemBgActiveDisabled: r.colorFill,
    controlTmpOutline: r.colorFillQuaternary,
    controlOutline: le(r.colorPrimaryBg, r.colorBgContainer),
    lineType: r.lineType,
    borderRadius: r.borderRadius,
    borderRadiusXS: r.borderRadiusXS,
    borderRadiusSM: r.borderRadiusSM,
    borderRadiusLG: r.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: r.sizeXXS,
    paddingXS: r.sizeXS,
    paddingSM: r.sizeSM,
    padding: r.size,
    paddingMD: r.sizeMD,
    paddingLG: r.sizeLG,
    paddingXL: r.sizeXL,
    paddingContentHorizontalLG: r.sizeLG,
    paddingContentVerticalLG: r.sizeMS,
    paddingContentHorizontal: r.sizeMS,
    paddingContentVertical: r.sizeSM,
    paddingContentHorizontalSM: r.size,
    paddingContentVerticalSM: r.sizeXS,
    marginXXS: r.sizeXXS,
    marginXS: r.sizeXS,
    marginSM: r.sizeSM,
    margin: r.size,
    marginMD: r.sizeMD,
    marginLG: r.sizeLG,
    marginXL: r.sizeXL,
    marginXXL: r.sizeXXL,
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
    screenXS: s,
    screenXSMin: s,
    screenXSMax: i - 1,
    screenSM: i,
    screenSMMin: i,
    screenSMMax: a - 1,
    screenMD: a,
    screenMDMin: a,
    screenMDMax: l - 1,
    screenLG: l,
    screenLGMin: l,
    screenLGMax: c - 1,
    screenXL: c,
    screenXLMin: c,
    screenXLMax: u - 1,
    screenXXL: u,
    screenXXLMin: u,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new U("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new U("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new U("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const En = {
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
}, Pn = {
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
}, On = nr(He.defaultAlgorithm), Mn = {
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
}, At = (t, e, n) => {
  const o = n.getDerivativeToken(t), {
    override: r,
    ...s
  } = e;
  let i = {
    ...o,
    override: r
  };
  return i = Tn(i), s && Object.entries(s).forEach(([a, l]) => {
    const {
      theme: c,
      ...u
    } = l;
    let f = u;
    c && (f = At({
      ...i,
      ...u
    }, {
      override: u
    }, c)), i[a] = f;
  }), i;
};
function In() {
  const {
    token: t,
    hashed: e,
    theme: n = On,
    override: o,
    cssVar: r
  } = m.useContext(He._internalContext), [s, i, a] = or(n, [He.defaultSeed, t], {
    salt: `${Nr}-${e || ""}`,
    override: o,
    getComputedToken: At,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: En,
      ignore: Pn,
      preserve: Mn
    }
  });
  return [n, a, e ? i : "", s, r];
}
const {
  genStyleHooks: Rn
} = xn({
  usePrefix: () => {
    const {
      getPrefixCls: t,
      iconPrefixCls: e
    } = me();
    return {
      iconPrefixCls: e,
      rootPrefixCls: t()
    };
  },
  useToken: () => {
    const [t, e, n, o, r] = In();
    return {
      theme: t,
      realToken: e,
      hashId: n,
      token: o,
      cssVar: r
    };
  },
  useCSP: () => {
    const {
      csp: t
    } = me();
    return t ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
});
var jn = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, kn = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Ln = "".concat(jn, " ").concat(kn).split(/[\s\n]+/), $n = "aria-", Dn = "data-";
function St(t, e) {
  return t.indexOf(e) === 0;
}
function Bn(t) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, n;
  e === !1 ? n = {
    aria: !0,
    data: !0,
    attr: !0
  } : e === !0 ? n = {
    aria: !0
  } : n = hn({}, e);
  var o = {};
  return Object.keys(t).forEach(function(r) {
    // Aria
    (n.aria && (r === "role" || St(r, $n)) || // Data
    n.data && St(r, Dn) || // Attr
    n.attr && Ln.includes(r)) && (o[r] = t[r]);
  }), o;
}
function ce(t) {
  return typeof t == "string";
}
const Hn = (t, e, n, o) => {
  const r = w.useRef(""), [s, i] = w.useState(1), a = e && ce(t);
  return an(() => {
    !a && ce(t) ? i(t.length) : ce(t) && ce(r.current) && t.indexOf(r.current) !== 0 && i(1), r.current = t;
  }, [t]), w.useEffect(() => {
    if (a && s < t.length) {
      const c = setTimeout(() => {
        i((u) => u + n);
      }, o);
      return () => {
        clearTimeout(c);
      };
    }
  }, [s, e, t]), [a ? t.slice(0, s) : t, a && s < t.length];
};
function zn(t) {
  return w.useMemo(() => {
    if (!t)
      return [!1, 0, 0, null];
    let e = {
      step: 1,
      interval: 50,
      // set default suffix is empty
      suffix: null
    };
    return typeof t == "object" && (e = {
      ...e,
      ...t
    }), [!0, e.step, e.interval, e.suffix];
  }, [t]);
}
const An = ({
  prefixCls: t
}) => /* @__PURE__ */ m.createElement("span", {
  className: `${t}-dot`
}, /* @__PURE__ */ m.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-1"
}), /* @__PURE__ */ m.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-2"
}), /* @__PURE__ */ m.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-3"
})), Fn = (t) => {
  const {
    componentCls: e,
    paddingSM: n,
    padding: o
  } = t;
  return {
    [e]: {
      [`${e}-content`]: {
        // Shared: filled, outlined, shadow
        "&-filled,&-outlined,&-shadow": {
          padding: `${oe(n)} ${oe(o)}`,
          borderRadius: t.borderRadiusLG
        },
        // Filled:
        "&-filled": {
          backgroundColor: t.colorFillContent
        },
        // Outlined:
        "&-outlined": {
          border: `1px solid ${t.colorBorderSecondary}`
        },
        // Shadow:
        "&-shadow": {
          boxShadow: t.boxShadowTertiary
        }
      }
    }
  };
}, Xn = (t) => {
  const {
    componentCls: e,
    fontSize: n,
    lineHeight: o,
    paddingSM: r,
    padding: s,
    calc: i
  } = t, a = i(n).mul(o).div(2).add(r).equal(), l = `${e}-content`;
  return {
    [e]: {
      [l]: {
        // round:
        "&-round": {
          borderRadius: {
            _skip_check_: !0,
            value: a
          },
          paddingInline: i(s).mul(1.25).equal()
        }
      },
      // corner:
      [`&-start ${l}-corner`]: {
        borderStartStartRadius: t.borderRadiusXS
      },
      [`&-end ${l}-corner`]: {
        borderStartEndRadius: t.borderRadiusXS
      }
    }
  };
}, Nn = (t) => {
  const {
    componentCls: e,
    padding: n
  } = t;
  return {
    [`${e}-list`]: {
      display: "flex",
      flexDirection: "column",
      gap: n,
      overflowY: "auto",
      "&::-webkit-scrollbar": {
        width: 8,
        backgroundColor: "transparent"
      },
      "&::-webkit-scrollbar-thumb": {
        backgroundColor: t.colorTextTertiary,
        borderRadius: t.borderRadiusSM
      },
      // For Firefox
      "&": {
        scrollbarWidth: "thin",
        scrollbarColor: `${t.colorTextTertiary} transparent`
      }
    }
  };
}, Vn = new Tt("loadingMove", {
  "0%": {
    transform: "translateY(0)"
  },
  "10%": {
    transform: "translateY(4px)"
  },
  "20%": {
    transform: "translateY(0)"
  },
  "30%": {
    transform: "translateY(-4px)"
  },
  "40%": {
    transform: "translateY(0)"
  }
}), Wn = new Tt("cursorBlink", {
  "0%": {
    opacity: 1
  },
  "50%": {
    opacity: 0
  },
  "100%": {
    opacity: 1
  }
}), Un = (t) => {
  const {
    componentCls: e,
    fontSize: n,
    lineHeight: o,
    paddingSM: r,
    colorText: s,
    calc: i
  } = t;
  return {
    [e]: {
      display: "flex",
      columnGap: r,
      [`&${e}-end`]: {
        justifyContent: "end",
        flexDirection: "row-reverse",
        [`& ${e}-content-wrapper`]: {
          alignItems: "flex-end"
        }
      },
      [`&${e}-rtl`]: {
        direction: "rtl"
      },
      [`&${e}-typing ${e}-content:last-child::after`]: {
        content: '"|"',
        fontWeight: 900,
        userSelect: "none",
        opacity: 1,
        marginInlineStart: "0.1em",
        animationName: Wn,
        animationDuration: "0.8s",
        animationIterationCount: "infinite",
        animationTimingFunction: "linear"
      },
      // ============================ Avatar =============================
      [`& ${e}-avatar`]: {
        display: "inline-flex",
        justifyContent: "center",
        alignSelf: "flex-start"
      },
      // ======================== Header & Footer ========================
      [`& ${e}-header, & ${e}-footer`]: {
        fontSize: n,
        lineHeight: o,
        color: t.colorText
      },
      [`& ${e}-header`]: {
        marginBottom: t.paddingXXS
      },
      [`& ${e}-footer`]: {
        marginTop: r
      },
      // =========================== Content =============================
      [`& ${e}-content-wrapper`]: {
        flex: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        minWidth: 0,
        maxWidth: "100%"
      },
      [`& ${e}-content`]: {
        position: "relative",
        boxSizing: "border-box",
        minWidth: 0,
        maxWidth: "100%",
        color: s,
        fontSize: t.fontSize,
        lineHeight: t.lineHeight,
        minHeight: i(r).mul(2).add(i(o).mul(n)).equal(),
        wordBreak: "break-word",
        [`& ${e}-dot`]: {
          position: "relative",
          height: "100%",
          display: "flex",
          alignItems: "center",
          columnGap: t.marginXS,
          padding: `0 ${oe(t.paddingXXS)}`,
          "&-item": {
            backgroundColor: t.colorPrimary,
            borderRadius: "100%",
            width: 4,
            height: 4,
            animationName: Vn,
            animationDuration: "2s",
            animationIterationCount: "infinite",
            animationTimingFunction: "linear",
            "&:nth-child(1)": {
              animationDelay: "0s"
            },
            "&:nth-child(2)": {
              animationDelay: "0.2s"
            },
            "&:nth-child(3)": {
              animationDelay: "0.4s"
            }
          }
        }
      }
    }
  };
}, Gn = () => ({}), Ft = Rn("Bubble", (t) => {
  const e = Ue(t, {});
  return [Un(e), Nn(e), Fn(e), Xn(e)];
}, Gn), Xt = /* @__PURE__ */ m.createContext({}), Kn = (t, e) => {
  const {
    prefixCls: n,
    className: o,
    rootClassName: r,
    style: s,
    classNames: i = {},
    styles: a = {},
    avatar: l,
    placement: c = "start",
    loading: u = !1,
    loadingRender: f,
    typing: d,
    content: h = "",
    messageRender: p,
    variant: x = "filled",
    shape: b,
    onTypingComplete: v,
    header: S,
    footer: M,
    _key: g,
    ...E
  } = t, {
    onUpdate: y
  } = m.useContext(Xt), P = m.useRef(null);
  m.useImperativeHandle(e, () => ({
    nativeElement: P.current
  }));
  const {
    direction: O,
    getPrefixCls: R
  } = me(), T = R("bubble", n), k = Ur("bubble"), [C, j, L, D] = zn(d), [B, z] = Hn(h, C, j, L);
  m.useEffect(() => {
    y == null || y();
  }, [B]);
  const V = m.useRef(!1);
  m.useEffect(() => {
    !z && !u ? V.current || (V.current = !0, v == null || v()) : V.current = !1;
  }, [z, u]);
  const [K, ie, Z] = Ft(T), ae = q(T, r, k.className, o, ie, Z, `${T}-${c}`, {
    [`${T}-rtl`]: O === "rtl",
    [`${T}-typing`]: z && !u && !p && !D
  }), Ie = m.useMemo(() => /* @__PURE__ */ m.isValidElement(l) ? l : /* @__PURE__ */ m.createElement(tr, l), [l]), W = m.useMemo(() => p ? p(B) : B, [B, p]), G = (te) => typeof te == "function" ? te(B, {
    key: g
  }) : te;
  let ee;
  u ? ee = f ? f() : /* @__PURE__ */ m.createElement(An, {
    prefixCls: T
  }) : ee = /* @__PURE__ */ m.createElement(m.Fragment, null, W, z && D);
  let N = /* @__PURE__ */ m.createElement("div", {
    style: {
      ...k.styles.content,
      ...a.content
    },
    className: q(`${T}-content`, `${T}-content-${x}`, b && `${T}-content-${b}`, k.classNames.content, i.content)
  }, ee);
  return (S || M) && (N = /* @__PURE__ */ m.createElement("div", {
    className: `${T}-content-wrapper`
  }, S && /* @__PURE__ */ m.createElement("div", {
    className: q(`${T}-header`, k.classNames.header, i.header),
    style: {
      ...k.styles.header,
      ...a.header
    }
  }, G(S)), N, M && /* @__PURE__ */ m.createElement("div", {
    className: q(`${T}-footer`, k.classNames.footer, i.footer),
    style: {
      ...k.styles.footer,
      ...a.footer
    }
  }, G(M)))), K(/* @__PURE__ */ m.createElement("div", J({
    style: {
      ...k.style,
      ...s
    },
    className: ae
  }, E, {
    ref: P
  }), l && /* @__PURE__ */ m.createElement("div", {
    style: {
      ...k.styles.avatar,
      ...a.avatar
    },
    className: q(`${T}-avatar`, k.classNames.avatar, i.avatar)
  }, Ie), N));
}, Ge = /* @__PURE__ */ m.forwardRef(Kn);
function qn(t, e) {
  const n = w.useCallback((o, r) => typeof e == "function" ? e(o, r) : e ? e[o.role] || {} : {}, [e]);
  return w.useMemo(() => (t || []).map((o, r) => {
    const s = o.key ?? `preset_${r}`;
    return {
      ...n(o, r),
      ...o,
      key: s
    };
  }), [t, n]);
}
const Yn = ({
  _key: t,
  ...e
}, n) => /* @__PURE__ */ w.createElement(Ge, J({}, e, {
  _key: t,
  ref: (o) => {
    var r;
    o ? n.current[t] = o : (r = n.current) == null || delete r[t];
  }
})), Qn = /* @__PURE__ */ w.memo(/* @__PURE__ */ w.forwardRef(Yn)), Jn = 1, Zn = (t, e) => {
  const {
    prefixCls: n,
    rootClassName: o,
    className: r,
    items: s,
    autoScroll: i = !0,
    roles: a,
    ...l
  } = t, c = Bn(l, {
    attr: !0,
    aria: !0
  }), u = w.useRef(null), f = w.useRef({}), {
    getPrefixCls: d
  } = me(), h = d("bubble", n), p = `${h}-list`, [x, b, v] = Ft(h), [S, M] = w.useState(!1);
  w.useEffect(() => (M(!0), () => {
    M(!1);
  }), []);
  const g = qn(s, a), [E, y] = w.useState(!0), [P, O] = w.useState(0), R = (C) => {
    const j = C.target;
    y(j.scrollHeight - Math.abs(j.scrollTop) - j.clientHeight <= Jn);
  };
  w.useEffect(() => {
    i && u.current && E && u.current.scrollTo({
      top: u.current.scrollHeight
    });
  }, [P]), w.useEffect(() => {
    var C;
    if (i) {
      const j = (C = g[g.length - 2]) == null ? void 0 : C.key, L = f.current[j];
      if (L) {
        const {
          nativeElement: D
        } = L, {
          top: B,
          bottom: z
        } = D.getBoundingClientRect(), {
          top: V,
          bottom: K
        } = u.current.getBoundingClientRect();
        B < K && z > V && (O((Z) => Z + 1), y(!0));
      }
    }
  }, [g.length]), w.useImperativeHandle(e, () => ({
    nativeElement: u.current,
    scrollTo: ({
      key: C,
      offset: j,
      behavior: L = "smooth",
      block: D
    }) => {
      if (typeof j == "number")
        u.current.scrollTo({
          top: j,
          behavior: L
        });
      else if (C !== void 0) {
        const B = f.current[C];
        if (B) {
          const z = g.findIndex((V) => V.key === C);
          y(z === g.length - 1), B.nativeElement.scrollIntoView({
            behavior: L,
            block: D
          });
        }
      }
    }
  }));
  const T = on(() => {
    i && O((C) => C + 1);
  }), k = w.useMemo(() => ({
    onUpdate: T
  }), []);
  return x(/* @__PURE__ */ w.createElement(Xt.Provider, {
    value: k
  }, /* @__PURE__ */ w.createElement("div", J({}, c, {
    className: q(p, o, r, b, v, {
      [`${p}-reach-end`]: E
    }),
    ref: u,
    onScroll: R
  }), g.map(({
    key: C,
    ...j
  }) => /* @__PURE__ */ w.createElement(Qn, J({}, j, {
    key: C,
    _key: C,
    ref: f,
    typing: S ? j.typing : !1
  }))))));
}, eo = /* @__PURE__ */ w.forwardRef(Zn);
Ge.List = eo;
const to = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function ro(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = no(n, o), e;
  }, {}) : {};
}
function no(t, e) {
  return typeof e == "number" && !to.includes(t) ? e + "px" : e;
}
function Xe(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const r = m.Children.toArray(t._reactElement.props.children).map((s) => {
      if (m.isValidElement(s) && s.props.__slot__) {
        const {
          portals: i,
          clonedElement: a
        } = Xe(s.props.el);
        return m.cloneElement(s, {
          ...s.props,
          el: a,
          children: [...m.Children.toArray(s.props.children), ...i]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(Be(m.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: r
    }), n)), {
      clonedElement: n,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((r) => {
    t.getEventListeners(r).forEach(({
      listener: i,
      type: a,
      useCapture: l
    }) => {
      n.addEventListener(a, i, l);
    });
  });
  const o = Array.from(t.childNodes);
  for (let r = 0; r < o.length; r++) {
    const s = o[r];
    if (s.nodeType === 1) {
      const {
        clonedElement: i,
        portals: a
      } = Xe(s);
      e.push(...a), n.appendChild(i);
    } else s.nodeType === 3 && n.appendChild(s.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function oo(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const xt = Ut(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: r
}, s) => {
  const i = wt(), [a, l] = Gt([]), {
    forceClone: c
  } = Zt(), u = c ? !0 : e;
  return Kt(() => {
    var x;
    if (!i.current || !t)
      return;
    let f = t;
    function d() {
      let b = f;
      if (f.tagName.toLowerCase() === "svelte-slot" && f.children.length === 1 && f.children[0] && (b = f.children[0], b.tagName.toLowerCase() === "react-portal-target" && b.children[0] && (b = b.children[0])), oo(s, b), n && b.classList.add(...n.split(" ")), o) {
        const v = ro(o);
        Object.keys(v).forEach((S) => {
          b.style[S] = v[S];
        });
      }
    }
    let h = null, p = null;
    if (u && window.MutationObserver) {
      let b = function() {
        var g, E, y;
        (g = i.current) != null && g.contains(f) && ((E = i.current) == null || E.removeChild(f));
        const {
          portals: S,
          clonedElement: M
        } = Xe(t);
        f = M, l(S), f.style.display = "contents", p && clearTimeout(p), p = setTimeout(() => {
          d();
        }, 50), (y = i.current) == null || y.appendChild(f);
      };
      b();
      const v = pr(() => {
        b(), h == null || h.disconnect(), h == null || h.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      h = new window.MutationObserver(v), h.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      f.style.display = "contents", d(), (x = i.current) == null || x.appendChild(f);
    return () => {
      var b, v;
      f.style.display = "", (b = i.current) != null && b.contains(f) && ((v = i.current) == null || v.removeChild(f)), h == null || h.disconnect();
    };
  }, [t, u, n, o, s, r, c]), m.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...a);
});
function Ct(t) {
  const e = wt(t);
  return e.current = t, qt((...n) => {
    var o;
    return (o = e.current) == null ? void 0 : o.call(e, ...n);
  }, []);
}
const so = ({
  children: t,
  ...e
}) => /* @__PURE__ */ A.jsx(A.Fragment, {
  children: t(e)
});
function io(t) {
  return m.createElement(so, {
    children: t
  });
}
function Ke(t, e, n) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((r, s) => {
      var c, u;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const i = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((c = r.props) == null ? void 0 : c.key) ?? (n ? `${n}-${s}` : `${s}`)
      }) : {
        ...r.props,
        key: ((u = r.props) == null ? void 0 : u.key) ?? (n ? `${n}-${s}` : `${s}`)
      };
      let a = i;
      Object.keys(r.slots).forEach((f) => {
        if (!r.slots[f] || !(r.slots[f] instanceof Element) && !r.slots[f].el)
          return;
        const d = f.split(".");
        d.forEach((S, M) => {
          a[S] || (a[S] = {}), M !== d.length - 1 && (a = i[S]);
        });
        const h = r.slots[f];
        let p, x, b = (e == null ? void 0 : e.clone) ?? !1, v = e == null ? void 0 : e.forceClone;
        h instanceof Element ? p = h : (p = h.el, x = h.callback, b = h.clone ?? b, v = h.forceClone ?? v), v = v ?? !!x, a[d[d.length - 1]] = p ? x ? (...S) => (x(d[d.length - 1], S), /* @__PURE__ */ A.jsx(Je, {
          ...r.ctx,
          params: S,
          forceClone: v,
          children: /* @__PURE__ */ A.jsx(xt, {
            slot: p,
            clone: b
          })
        })) : io((S) => /* @__PURE__ */ A.jsx(Je, {
          ...r.ctx,
          forceClone: v,
          children: /* @__PURE__ */ A.jsx(xt, {
            ...S,
            slot: p,
            clone: b
          })
        })) : a[d[d.length - 1]], a = i;
      });
      const l = (e == null ? void 0 : e.children) || "children";
      return r[l] ? i[l] = Ke(r[l], e, `${s}`) : e != null && e.children && (i[l] = void 0, Reflect.deleteProperty(i, l)), i;
    });
}
const {
  useItems: ao,
  withItemsContextProvider: lo,
  ItemHandler: xo
} = _t("antdx-bubble.list-items"), {
  useItems: co,
  withItemsContextProvider: uo,
  ItemHandler: Co
} = _t("antdx-bubble.list-roles");
function fo(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function ho(t, e = !1) {
  try {
    if (Ne(t))
      return t;
    if (e && !fo(t))
      return;
    if (typeof t == "string") {
      let n = t.trim();
      return n.startsWith(";") && (n = n.slice(1)), n.endsWith(";") && (n = n.slice(0, -1)), new Function(`return (...args) => (${n})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function go(t, e) {
  return ge(() => ho(t, e), [t, e]);
}
function mo(t, e) {
  return e((o, r) => Ne(o) ? r ? (...s) => Q(r) && r.unshift ? o(...t, ...s) : o(...s, ...t) : o(...t) : o);
}
const po = Symbol();
function bo(t, e) {
  return mo(e, (n) => {
    var o, r;
    return {
      ...t,
      avatar: Ne(t.avatar) ? n(t.avatar) : Q(t.avatar) ? {
        ...t.avatar,
        icon: n((o = t.avatar) == null ? void 0 : o.icon),
        src: n((r = t.avatar) == null ? void 0 : r.src)
      } : t.avatar,
      footer: n(t.footer, {
        unshift: !0
      }),
      header: n(t.header, {
        unshift: !0
      }),
      loadingRender: n(t.loadingRender, !0),
      messageRender: n(t.messageRender, !0)
    };
  });
}
function yo({
  roles: t,
  preProcess: e,
  postProcess: n
}, o = []) {
  const r = go(t), s = Ct(e), i = Ct(n), {
    items: {
      roles: a
    }
  } = co(), l = ge(() => {
    var u;
    return t || ((u = Ke(a, {
      clone: !0,
      forceClone: !0
    })) == null ? void 0 : u.reduce((f, d) => (d.role !== void 0 && (f[d.role] = d), f), {}));
  }, [a, t]), c = ge(() => (u, f) => {
    const d = f ?? u[po], h = s(u, d) || u;
    if (h.role && (l || {})[h.role])
      return bo((l || {})[h.role], [h, d]);
    let p;
    return p = i(h, d), p || {
      messageRender(x) {
        return /* @__PURE__ */ A.jsx(A.Fragment, {
          children: Q(x) ? JSON.stringify(x) : x
        });
      }
    };
  }, [l, i, s, ...o]);
  return r || c;
}
const wo = Xr(uo(["roles"], lo(["items", "default"], ({
  items: t,
  roles: e,
  children: n,
  ...o
}) => {
  const {
    items: r
  } = ao(), s = yo({
    roles: e
  }), i = r.items.length > 0 ? r.items : r.default;
  return /* @__PURE__ */ A.jsxs(A.Fragment, {
    children: [/* @__PURE__ */ A.jsx("div", {
      style: {
        display: "none"
      },
      children: n
    }), /* @__PURE__ */ A.jsx(Ge.List, {
      ...o,
      items: ge(() => t || Ke(i), [t, i]),
      roles: s
    })]
  });
})));
export {
  wo as BubbleList,
  wo as default
};
