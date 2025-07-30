import { i as ce, a as B, r as ue, b as fe, w as O, g as de, c as me } from "./Index-Dm1wa93F.js";
const v = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, N = window.ms_globals.React.useRef, ee = window.ms_globals.React.useState, W = window.ms_globals.React.useEffect, te = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, he = window.ms_globals.internalContext.ContextPropsProvider, pe = window.ms_globals.antd.Input;
var ge = /\s/;
function we(e) {
  for (var t = e.length; t-- && ge.test(e.charAt(t)); )
    ;
  return t;
}
var xe = /^\s+/;
function be(e) {
  return e && e.slice(0, we(e) + 1).replace(xe, "");
}
var q = NaN, ye = /^[-+]0x[0-9a-f]+$/i, ve = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, Ce = parseInt;
function z(e) {
  if (typeof e == "number")
    return e;
  if (ce(e))
    return q;
  if (B(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = B(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = be(e);
  var r = ve.test(e);
  return r || Ee.test(e) ? Ce(e.slice(2), r ? 2 : 8) : ye.test(e) ? q : +e;
}
var L = function() {
  return ue.Date.now();
}, Ie = "Expected a function", Se = Math.max, Re = Math.min;
function Pe(e, t, r) {
  var s, i, n, o, l, c, h = 0, g = !1, a = !1, w = !0;
  if (typeof e != "function")
    throw new TypeError(Ie);
  t = z(t) || 0, B(r) && (g = !!r.leading, a = "maxWait" in r, n = a ? Se(z(r.maxWait) || 0, t) : n, w = "trailing" in r ? !!r.trailing : w);
  function d(f) {
    var E = s, P = i;
    return s = i = void 0, h = f, o = e.apply(P, E), o;
  }
  function x(f) {
    return h = f, l = setTimeout(p, t), g ? d(f) : o;
  }
  function b(f) {
    var E = f - c, P = f - h, V = t - E;
    return a ? Re(V, n - P) : V;
  }
  function m(f) {
    var E = f - c, P = f - h;
    return c === void 0 || E >= t || E < 0 || a && P >= n;
  }
  function p() {
    var f = L();
    if (m(f))
      return y(f);
    l = setTimeout(p, b(f));
  }
  function y(f) {
    return l = void 0, w && s ? d(f) : (s = i = void 0, o);
  }
  function R() {
    l !== void 0 && clearTimeout(l), h = 0, s = c = i = l = void 0;
  }
  function u() {
    return l === void 0 ? o : y(L());
  }
  function I() {
    var f = L(), E = m(f);
    if (s = arguments, i = this, c = f, E) {
      if (l === void 0)
        return x(c);
      if (a)
        return clearTimeout(l), l = setTimeout(p, t), d(c);
    }
    return l === void 0 && (l = setTimeout(p, t)), o;
  }
  return I.cancel = R, I.flush = u, I;
}
function Te(e, t) {
  return fe(e, t);
}
var re = {
  exports: {}
}, F = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Oe = v, je = Symbol.for("react.element"), ke = Symbol.for("react.fragment"), Fe = Object.prototype.hasOwnProperty, Le = Oe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ae = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(e, t, r) {
  var s, i = {}, n = null, o = null;
  r !== void 0 && (n = "" + r), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (s in t) Fe.call(t, s) && !Ae.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: je,
    type: e,
    key: n,
    ref: o,
    props: i,
    _owner: Le.current
  };
}
F.Fragment = ke;
F.jsx = ne;
F.jsxs = ne;
re.exports = F;
var _ = re.exports;
const {
  SvelteComponent: Ne,
  assign: G,
  binding_callbacks: H,
  check_outros: We,
  children: oe,
  claim_element: se,
  claim_space: Me,
  component_subscribe: K,
  compute_slots: Be,
  create_slot: De,
  detach: S,
  element: ie,
  empty: J,
  exclude_internal_props: X,
  get_all_dirty_from_scope: Ue,
  get_slot_changes: Ve,
  group_outros: qe,
  init: ze,
  insert_hydration: j,
  safe_not_equal: Ge,
  set_custom_element_data: le,
  space: He,
  transition_in: k,
  transition_out: D,
  update_slot_base: Ke
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Qe
} = window.__gradio__svelte__internal;
function Y(e) {
  let t, r;
  const s = (
    /*#slots*/
    e[7].default
  ), i = De(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ie("svelte-slot"), i && i.c(), this.h();
    },
    l(n) {
      t = se(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = oe(t);
      i && i.l(o), o.forEach(S), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      j(n, t, o), i && i.m(t, null), e[9](t), r = !0;
    },
    p(n, o) {
      i && i.p && (!r || o & /*$$scope*/
      64) && Ke(
        i,
        s,
        n,
        /*$$scope*/
        n[6],
        r ? Ve(
          s,
          /*$$scope*/
          n[6],
          o,
          null
        ) : Ue(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      r || (k(i, n), r = !0);
    },
    o(n) {
      D(i, n), r = !1;
    },
    d(n) {
      n && S(t), i && i.d(n), e[9](null);
    }
  };
}
function Ze(e) {
  let t, r, s, i, n = (
    /*$$slots*/
    e[4].default && Y(e)
  );
  return {
    c() {
      t = ie("react-portal-target"), r = He(), n && n.c(), s = J(), this.h();
    },
    l(o) {
      t = se(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), oe(t).forEach(S), r = Me(o), n && n.l(o), s = J(), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(o, l) {
      j(o, t, l), e[8](t), j(o, r, l), n && n.m(o, l), j(o, s, l), i = !0;
    },
    p(o, [l]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, l), l & /*$$slots*/
      16 && k(n, 1)) : (n = Y(o), n.c(), k(n, 1), n.m(s.parentNode, s)) : n && (qe(), D(n, 1, 1, () => {
        n = null;
      }), We());
    },
    i(o) {
      i || (k(n), i = !0);
    },
    o(o) {
      D(n), i = !1;
    },
    d(o) {
      o && (S(t), S(r), S(s)), e[8](null), n && n.d(o);
    }
  };
}
function Q(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function $e(e, t, r) {
  let s, i, {
    $$slots: n = {},
    $$scope: o
  } = t;
  const l = Be(n);
  let {
    svelteInit: c
  } = t;
  const h = O(Q(t)), g = O();
  K(e, g, (u) => r(0, s = u));
  const a = O();
  K(e, a, (u) => r(1, i = u));
  const w = [], d = Xe("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: b,
    subSlotIndex: m
  } = de() || {}, p = c({
    parent: d,
    props: h,
    target: g,
    slot: a,
    slotKey: x,
    slotIndex: b,
    subSlotIndex: m,
    onDestroy(u) {
      w.push(u);
    }
  });
  Qe("$$ms-gr-react-wrapper", p), Je(() => {
    h.set(Q(t));
  }), Ye(() => {
    w.forEach((u) => u());
  });
  function y(u) {
    H[u ? "unshift" : "push"](() => {
      s = u, g.set(s);
    });
  }
  function R(u) {
    H[u ? "unshift" : "push"](() => {
      i = u, a.set(i);
    });
  }
  return e.$$set = (u) => {
    r(17, t = G(G({}, t), X(u))), "svelteInit" in u && r(5, c = u.svelteInit), "$$scope" in u && r(6, o = u.$$scope);
  }, t = X(t), [s, i, g, a, l, c, o, n, y, R];
}
class et extends Ne {
  constructor(t) {
    super(), ze(this, t, $e, Ze, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, A = window.ms_globals.tree;
function tt(e, t = {}) {
  function r(s) {
    const i = O(), n = new et({
      ...s,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, c = o.parent ?? A;
          return c.nodes = [...c.nodes, l], Z({
            createPortal: M,
            node: A
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((h) => h.svelteInstance !== i), Z({
              createPortal: M,
              node: A
            });
          }), l;
        },
        ...s.props
      }
    });
    return i.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise.then(() => {
      s(r);
    });
  });
}
const rt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function nt(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const s = e[r];
    return t[r] = ot(r, s), t;
  }, {}) : {};
}
function ot(e, t) {
  return typeof t == "number" && !rt.includes(e) ? t + "px" : t;
}
function U(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const i = v.Children.toArray(e._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: l
        } = U(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...v.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(M(v.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: i
    }), r)), {
      clonedElement: r,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((i) => {
    e.getEventListeners(i).forEach(({
      listener: o,
      type: l,
      useCapture: c
    }) => {
      r.addEventListener(l, o, c);
    });
  });
  const s = Array.from(e.childNodes);
  for (let i = 0; i < s.length; i++) {
    const n = s[i];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: l
      } = U(n);
      t.push(...l), r.appendChild(o);
    } else n.nodeType === 3 && r.appendChild(n.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function st(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const C = ae(({
  slot: e,
  clone: t,
  className: r,
  style: s,
  observeAttributes: i
}, n) => {
  const o = N(), [l, c] = ee([]), {
    forceClone: h
  } = _e(), g = h ? !0 : t;
  return W(() => {
    var b;
    if (!o.current || !e)
      return;
    let a = e;
    function w() {
      let m = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (m = a.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), st(n, m), r && m.classList.add(...r.split(" ")), s) {
        const p = nt(s);
        Object.keys(p).forEach((y) => {
          m.style[y] = p[y];
        });
      }
    }
    let d = null, x = null;
    if (g && window.MutationObserver) {
      let m = function() {
        var u, I, f;
        (u = o.current) != null && u.contains(a) && ((I = o.current) == null || I.removeChild(a));
        const {
          portals: y,
          clonedElement: R
        } = U(e);
        a = R, c(y), a.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          w();
        }, 50), (f = o.current) == null || f.appendChild(a);
      };
      m();
      const p = Pe(() => {
        m(), d == null || d.disconnect(), d == null || d.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      d = new window.MutationObserver(p), d.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", w(), (b = o.current) == null || b.appendChild(a);
    return () => {
      var m, p;
      a.style.display = "", (m = o.current) != null && m.contains(a) && ((p = o.current) == null || p.removeChild(a)), d == null || d.disconnect();
    };
  }, [e, g, r, s, n, i, h]), v.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
});
function it(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function lt(e, t = !1) {
  try {
    if (me(e))
      return e;
    if (t && !it(e))
      return;
    if (typeof e == "string") {
      let r = e.trim();
      return r.startsWith(";") && (r = r.slice(1)), r.endsWith(";") && (r = r.slice(0, -1)), new Function(`return (...args) => (${r})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function T(e, t) {
  return te(() => lt(e, t), [e, t]);
}
function at({
  value: e,
  onValueChange: t
}) {
  const [r, s] = ee(e), i = N(t);
  i.current = t;
  const n = N(r);
  return n.current = r, W(() => {
    i.current(r);
  }, [r]), W(() => {
    Te(e, n.current) || s(e);
  }, [e]), [r, s];
}
function ct(e, t) {
  return Object.keys(e).reduce((r, s) => (e[s] !== void 0 && (r[s] = e[s]), r), {});
}
const ut = ({
  children: e,
  ...t
}) => /* @__PURE__ */ _.jsx(_.Fragment, {
  children: e(t)
});
function ft(e) {
  return v.createElement(ut, {
    children: e
  });
}
function $(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ft((r) => /* @__PURE__ */ _.jsx(he, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ _.jsx(C, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...r
    })
  })) : /* @__PURE__ */ _.jsx(C, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function dt({
  key: e,
  slots: t,
  targets: r
}, s) {
  return t[e] ? (...i) => r ? r.map((n, o) => /* @__PURE__ */ _.jsx(v.Fragment, {
    children: $(n, {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ _.jsx(_.Fragment, {
    children: $(t[e], {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }) : void 0;
}
const ht = tt(({
  slots: e,
  children: t,
  count: r,
  showCount: s,
  onValueChange: i,
  onChange: n,
  setSlotParams: o,
  elRef: l,
  ...c
}) => {
  const h = T(r == null ? void 0 : r.strategy), g = T(r == null ? void 0 : r.exceedFormatter), a = T(r == null ? void 0 : r.show), w = T(typeof s == "object" ? s.formatter : void 0), [d, x] = at({
    onValueChange: i,
    value: c.value
  });
  return /* @__PURE__ */ _.jsxs(_.Fragment, {
    children: [/* @__PURE__ */ _.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ _.jsx(pe, {
      ...c,
      value: d,
      ref: l,
      onChange: (b) => {
        n == null || n(b), x(b.target.value);
      },
      showCount: e["showCount.formatter"] ? {
        formatter: dt({
          slots: e,
          key: "showCount.formatter"
        })
      } : typeof s == "object" && w ? {
        ...s,
        formatter: w
      } : s,
      count: te(() => ct({
        ...r,
        exceedFormatter: g,
        strategy: h,
        show: a || (r == null ? void 0 : r.show)
      }), [r, g, h, a]),
      addonAfter: e.addonAfter ? /* @__PURE__ */ _.jsx(C, {
        slot: e.addonAfter
      }) : c.addonAfter,
      addonBefore: e.addonBefore ? /* @__PURE__ */ _.jsx(C, {
        slot: e.addonBefore
      }) : c.addonBefore,
      allowClear: e["allowClear.clearIcon"] ? {
        clearIcon: /* @__PURE__ */ _.jsx(C, {
          slot: e["allowClear.clearIcon"]
        })
      } : c.allowClear,
      prefix: e.prefix ? /* @__PURE__ */ _.jsx(C, {
        slot: e.prefix
      }) : c.prefix,
      suffix: e.suffix ? /* @__PURE__ */ _.jsx(C, {
        slot: e.suffix
      }) : c.suffix
    })]
  });
});
export {
  ht as Input,
  ht as default
};
