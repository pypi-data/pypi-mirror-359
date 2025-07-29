const {
  SvelteComponent: b,
  add_iframe_resize_listener: y,
  add_render_callback: h,
  append: m,
  attr: v,
  binding_callbacks: w,
  detach: z,
  element: k,
  init: p,
  insert: S,
  noop: f,
  safe_not_equal: q,
  set_data: C,
  text: E,
  toggle_class: _
} = window.__gradio__svelte__internal, { onMount: M } = window.__gradio__svelte__internal;
function P(t) {
  let e, s, r;
  return {
    c() {
      e = k("div"), s = E(
        /*value*/
        t[0]
      ), v(e, "class", "svelte-84cxb8"), h(() => (
        /*div_elementresize_handler*/
        t[5].call(e)
      )), _(
        e,
        "table",
        /*type*/
        t[1] === "table"
      ), _(
        e,
        "gallery",
        /*type*/
        t[1] === "gallery"
      ), _(
        e,
        "selected",
        /*selected*/
        t[2]
      );
    },
    m(l, i) {
      S(l, e, i), m(e, s), r = y(
        e,
        /*div_elementresize_handler*/
        t[5].bind(e)
      ), t[6](e);
    },
    p(l, [i]) {
      i & /*value*/
      1 && C(
        s,
        /*value*/
        l[0]
      ), i & /*type*/
      2 && _(
        e,
        "table",
        /*type*/
        l[1] === "table"
      ), i & /*type*/
      2 && _(
        e,
        "gallery",
        /*type*/
        l[1] === "gallery"
      ), i & /*selected*/
      4 && _(
        e,
        "selected",
        /*selected*/
        l[2]
      );
    },
    i: f,
    o: f,
    d(l) {
      l && z(e), r(), t[6](null);
    }
  };
}
function W(t, e, s) {
  let { value: r } = e, { type: l } = e, { selected: i = !1 } = e, d, a;
  function u(n, c) {
    !n || !c || (a.style.setProperty("--local-text-width", `${c < 150 ? c : 200}px`), s(4, a.style.whiteSpace = "unset", a));
  }
  M(() => {
    u(a, d);
  });
  function o() {
    d = this.clientWidth, s(3, d);
  }
  function g(n) {
    w[n ? "unshift" : "push"](() => {
      a = n, s(4, a);
    });
  }
  return t.$$set = (n) => {
    "value" in n && s(0, r = n.value), "type" in n && s(1, l = n.type), "selected" in n && s(2, i = n.selected);
  }, [r, l, i, d, a, o, g];
}
class j extends b {
  constructor(e) {
    super(), p(this, e, W, P, q, { value: 0, type: 1, selected: 2 });
  }
}
export {
  j as default
};
