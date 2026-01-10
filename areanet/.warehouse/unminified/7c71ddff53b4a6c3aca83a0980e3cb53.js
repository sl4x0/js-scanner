! function() {
  "use strict";
  const e = "cookieNotification",
    t = "cookieConsent",
    n = [e, t],
    o = Date.now(),
    s = new Date(o + 15552e6),
    i = ["https://www.arena.net", "https://www.guildwars2.com", "https://www.guildwars.com"],
    a = location.host.split(".").slice(1).join(".");

  function r(e) {
    const t = new RegExp(`(?:(?:^|.*;\\s*)${e}\\s*\\=\\s*([^;]*).*$)|^.*$`);
    return document.cookie.replace(t, "$1")
  }

  function c({
    key: e,
    value: t
  }) {
    document.cookie = `${e}=${t};expires=${s};path=/;domain=${function(){const e=document.location.hostname.split(".");return e.length>2?e.splice(1).join("."):document.location.hostname}()};SameSite=None;Secure`
  }

  function l(e, t) {
    return fetch(`${e}/cookie-sync?cookieKeys=${t.join(",")}`, {
      credentials: "include",
      referrerPolicy: "no-referrer-when-downgrade"
    }).then((e => e.json())).then((e => {
      Object.entries(e).forEach((([e, t]) => c({
        key: e,
        value: t
      })))
    })).catch((t => (console.log({
      error: t,
      domain: e
    }), !1)))
  }

  function u(t) {
    return parseInt(r(e), 10) > t
  }

  function d() {
    const e = function(e, t) {
      let n = !1;
      return e.filter((e => !(!n && t === e.split(".").slice(1).join(".") && (n = !0, 1))))
    }(i, a);
    return fetch("/cookie-notification").then((e => e.json())).then((e => e.date)).catch((() => 0)).then((t => !!u(t) || l(e[0], n).then((() => !!u(t) || l(e[1], n).then((() => u(t)))))))
  }

  function f() {
    "true" === r(t) && (window.dataLayer = window.dataLayer || [], window.dataLayer.push({
      cookieConsent: !0
    }), window.dataLayer.push({
      event: "cookieConsent"
    }), window.dataLayer.push({
      event: "consent_update",
      ad_storage: "granted",
      analytics_storage: "granted",
      ad_user_data: "granted",
      ad_personalization: "granted"
    }))
  }

  function p(e, t) {
    (window.dataLayer || []).push({
      event: "event",
      eventCategory: "CookieNotification",
      eventAction: e,
      eventLabel: t
    })
  }

  function g() {}
  const m = e => e;

  function h(e) {
    return e()
  }

  function v() {
    return Object.create(null)
  }

  function x(e) {
    e.forEach(h)
  }

  function y(e) {
    return "function" == typeof e
  }

  function b(e, t) {
    return e != e ? t == t : e !== t || e && "object" == typeof e || "function" == typeof e
  }
  const z = "undefined" != typeof window;
  let k = z ? () => window.performance.now() : () => Date.now(),
    w = z ? e => requestAnimationFrame(e) : g;
  const $ = new Set;

  function _(e) {
    $.forEach((t => {
      t.c(e) || ($.delete(t), t.f())
    })), 0 !== $.size && w(_)
  }

  function C(e, t) {
    e.appendChild(t)
  }

  function E(e) {
    if (!e) return document;
    const t = e.getRootNode ? e.getRootNode() : e.ownerDocument;
    return t && t.host ? t : e.ownerDocument
  }

  function A(e) {
    const t = S("style");
    return function(e, t) {
      C(e.head || e, t), t.sheet
    }(E(e), t), t.sheet
  }

  function j(e, t, n) {
    e.insertBefore(t, n || null)
  }

  function N(e) {
    e.parentNode && e.parentNode.removeChild(e)
  }

  function S(e) {
    return document.createElement(e)
  }

  function P(e) {
    return document.createTextNode(e)
  }

  function q() {
    return P(" ")
  }

  function D(e, t, n, o) {
    return e.addEventListener(t, n, o), () => e.removeEventListener(t, n, o)
  }

  function L(e, t, n) {
    null == n ? e.removeAttribute(t) : e.getAttribute(t) !== n && e.setAttribute(t, n)
  }
  const O = new Map;
  let M, R = 0;

  function T(e, t, n, o, s, i, a, r = 0) {
    const c = 16.666 / o;
    let l = "{\n";
    for (let e = 0; e <= 1; e += c) {
      const o = t + (n - t) * i(e);
      l += 100 * e + `%{${a(o,1-o)}}\n`
    }
    const u = l + `100% {${a(n,1-n)}}\n}`,
      d = `__svelte_${function(e){let t=5381,n=e.length;for(;n--;)t=(t<<5)-t^e.charCodeAt(n);return t>>>0}(u)}_${r}`,
      f = E(e),
      {
        stylesheet: p,
        rules: g
      } = O.get(f) || function(e, t) {
        const n = {
          stylesheet: A(t),
          rules: {}
        };
        return O.set(e, n), n
      }(f, e);
    g[d] || (g[d] = !0, p.insertRule(`@keyframes ${d} ${u}`, p.cssRules.length));
    const m = e.style.animation || "";
    return e.style.animation = `${m?`${m}, `:""}${d} ${o}ms linear ${s}ms 1 both`, R += 1, d
  }

  function I(e, t) {
    const n = (e.style.animation || "").split(", "),
      o = n.filter(t ? e => e.indexOf(t) < 0 : e => -1 === e.indexOf("__svelte")),
      s = n.length - o.length;
    s && (e.style.animation = o.join(", "), R -= s, R || w((() => {
      R || (O.forEach((e => {
        const {
          ownerNode: t
        } = e.stylesheet;
        t && N(t)
      })), O.clear())
    })))
  }

  function B(e) {
    M = e
  }
  const W = [],
    V = [];
  let H = [];
  const G = [],
    J = Promise.resolve();
  let U = !1;

  function F(e) {
    H.push(e)
  }
  const K = new Set;
  let Y, Q = 0;

  function X() {
    if (0 !== Q) return;
    const e = M;
    do {
      try {
        for (; Q < W.length;) {
          const e = W[Q];
          Q++, B(e), Z(e.$$)
        }
      } catch (e) {
        throw W.length = 0, Q = 0, e
      }
      for (B(null), W.length = 0, Q = 0; V.length;) V.pop()();
      for (let e = 0; e < H.length; e += 1) {
        const t = H[e];
        K.has(t) || (K.add(t), t())
      }
      H.length = 0
    } while (W.length);
    for (; G.length;) G.pop()();
    U = !1, K.clear(), B(e)
  }

  function Z(e) {
    if (null !== e.fragment) {
      e.update(), x(e.before_update);
      const t = e.dirty;
      e.dirty = [-1], e.fragment && e.fragment.p(e.ctx, t), e.after_update.forEach(F)
    }
  }

  function ee(e, t, n) {
    e.dispatchEvent(function(e, t, {
      bubbles: n = !1,
      cancelable: o = !1
    } = {}) {
      const s = document.createEvent("CustomEvent");
      return s.initCustomEvent(e, n, o, t), s
    }(`${t?"intro":"outro"}${n}`))
  }
  const te = new Set;
  let ne;

  function oe(e, t) {
    e && e.i && (te.delete(e), e.i(t))
  }

  function se(e, t, n, o) {
    if (e && e.o) {
      if (te.has(e)) return;
      te.add(e), ne.c.push((() => {
        te.delete(e), o && (n && e.d(1), o())
      })), e.o(t)
    } else o && o()
  }
  const ie = {
    duration: 0
  };

  function ae(e, t, n, o) {
    const s = {
      direction: "both"
    };
    let i = t(e, n, s),
      a = o ? 0 : 1,
      r = null,
      c = null,
      l = null;

    function u() {
      l && I(e, l)
    }

    function d(e, t) {
      const n = e.b - a;
      return t *= Math.abs(n), {
        a: a,
        b: e.b,
        d: n,
        duration: t,
        start: e.start,
        end: e.start + t,
        group: e.group
      }
    }

    function f(t) {
      const {
        delay: n = 0,
        duration: o = 300,
        easing: s = m,
        tick: f = g,
        css: p
      } = i || ie, h = {
        start: k() + n,
        b: t
      };
      t || (h.group = ne, ne.r += 1), r || c ? c = h : (p && (u(), l = T(e, a, t, o, n, s, p)), t && f(0, 1), r = d(h, o), F((() => ee(e, t, "start"))), function(e) {
        let t;
        0 === $.size && w(_), new Promise((n => {
          $.add(t = {
            c: e,
            f: n
          })
        }))
      }((t => {
        if (c && t > c.start && (r = d(c, o), c = null, ee(e, r.b, "start"), p && (u(), l = T(e, a, r.b, r.duration, 0, s, i.css))), r)
          if (t >= r.end) f(a = r.b, 1 - a), ee(e, r.b, "end"), c || (r.b ? u() : --r.group.r || x(r.group.c)), r = null;
          else if (t >= r.start) {
          const e = t - r.start;
          a = r.a + r.d * s(e / r.duration), f(a, 1 - a)
        }
        return !(!r && !c)
      })))
    }
    return {
      run(e) {
        y(i) ? (Y || (Y = Promise.resolve(), Y.then((() => {
          Y = null
        }))), Y).then((() => {
          i = i(s), f(e)
        })) : f(e)
      },
      end() {
        u(), r = c = null
      }
    }
  }

  function re(e, t) {
    const n = e.$$;
    null !== n.fragment && (! function(e) {
      const t = [],
        n = [];
      H.forEach((o => -1 === e.indexOf(o) ? t.push(o) : n.push(o))), n.forEach((e => e())), H = t
    }(n.after_update), x(n.on_destroy), n.fragment && n.fragment.d(t), n.on_destroy = n.fragment = null, n.ctx = [])
  }

  function ce(e, t) {
    -1 === e.$$.dirty[0] && (W.push(e), U || (U = !0, J.then(X)), e.$$.dirty.fill(0)), e.$$.dirty[t / 31 | 0] |= 1 << t % 31
  }

  function le(e, t, n, o, s, i, a, r = [-1]) {
    const c = M;
    B(e);
    const l = e.$$ = {
      fragment: null,
      ctx: [],
      props: i,
      update: g,
      not_equal: s,
      bound: v(),
      on_mount: [],
      on_destroy: [],
      on_disconnect: [],
      before_update: [],
      after_update: [],
      context: new Map(t.context || (c ? c.$$.context : [])),
      callbacks: v(),
      dirty: r,
      skip_bound: !1,
      root: t.target || c.$$.root
    };
    a && a(l.root);
    let u = !1;
    if (l.ctx = n ? n(e, t.props || {}, ((t, n, ...o) => {
        const i = o.length ? o[0] : n;
        return l.ctx && s(l.ctx[t], l.ctx[t] = i) && (!l.skip_bound && l.bound[t] && l.bound[t](i), u && ce(e, t)), n
      })) : [], l.update(), u = !0, x(l.before_update), l.fragment = !!o && o(l.ctx), t.target) {
      if (t.hydrate) {
        const e = function(e) {
          return Array.from(e.childNodes)
        }(t.target);
        l.fragment && l.fragment.l(e), e.forEach(N)
      } else l.fragment && l.fragment.c();
      t.intro && oe(e.$$.fragment),
        function(e, t, n, o) {
          const {
            fragment: s,
            after_update: i
          } = e.$$;
          s && s.m(t, n), o || F((() => {
            const t = e.$$.on_mount.map(h).filter(y);
            e.$$.on_destroy ? e.$$.on_destroy.push(...t) : x(t), e.$$.on_mount = []
          })), i.forEach(F)
        }(e, t.target, t.anchor, t.customElement), X()
    }
    B(c)
  }

  function ue(e, {
    delay: t = 0,
    duration: n = 400,
    easing: o = m
  } = {}) {
    const s = +getComputedStyle(e).opacity;
    return {
      delay: t,
      duration: n,
      easing: o,
      css: e => "opacity: " + e * s
    }
  }
  var de = {
    en: {
      disclaimer: {
        header: "Cookie Policy",
        copy: "By clicking \u201cI Accept\u201d below, you accept our and third parties\u2019 use of cookies designed to help target personalized advertising, and content on our websites and those of others and related personal data processing. You may change your cookie preferences by visiting \u201cCookie Settings,\u201d below. See our <a href='https://arena.net/legal/privacy-policy'>ArenaNet Privacy Policy</a> for more information about our privacy practices.",
        button: "I Accept"
      },
      settings: {
        header: "Cookie Settings",
        copy: "Please select one of the two options below and press the \u201cSave\xa0Settings\u201d button to confirm your settings.",
        options: {
          0: "All marketing, social media, and advertising cookies off",
          1: "All cookies activated"
        },
        button: "Save Settings"
      },
      toggle: "Cookie Settings"
    },
    de: {
      disclaimer: {
        header: "Cookie-Richtlinie",
        copy: "Wenn du unten auf \u201eIch stimme zu\u201c klickst, akzeptierst du, dass wir und unsere Partner Cookies zum Anbieten personalisierter Werbung und Inhalte auf unseren und anderen Websites einsetzen, sowie die damit zusammenh\xe4ngende Verarbeitung pers\xf6nlicher Daten. Du kannst deine Cookie-Einstellungen in den \u201eCookie-Einstellungen\u201c weiter unten \xe4ndern. Unter <a href='https://arena.net/de/legal/privacy-policy'>unserer ArenaNet-Datenschutzrichtlinie</a> erf\xe4hrst du weitere Einzelheiten zu unseren Datenschutzpraktiken.",
        button: "Ich stimme zu"
      },
      settings: {
        header: "Cookie-Einstellungen",
        copy: "Bitte w\xe4hle eine der folgenden Optionen und dr\xfccke auf \u201eEinstellungen speichern\u201c, um deine Einstellungen zu best\xe4tigen.",
        options: {
          0: "Alle Cookies f\xfcr Marketing, soziale Medien und Werbung AUS",
          1: "Alle Cookies aktiviert"
        },
        button: "Einstellungen speichern"
      },
      toggle: "Cookie-Einstellungen"
    },
    es: {
      disclaimer: {
        header: "Pol\xedtica de cookies",
        copy: "Al hacer clic en \xabAcepto\xbb, aceptas el uso que nosotros y otros terceros hagan de las cookies, creadas para ofrecer publicidad personalizada, y el contenido de nuestros sitios web y de terceros, adem\xe1s del procesamiento de datos personales relacionados. Ve a \xabAjustes de cookies\xbb para modificar tus preferencias. Para m\xe1s informaci\xf3n sobre nuestras pr\xe1cticas de privacidad, consulta <a href='https://arena.net/es/legal/privacy-policy'>la pol\xedtica de privacidad de ArenaNet</a>.",
        button: "Acepto"
      },
      settings: {
        header: "Ajustes de cookies",
        copy: "Selecciona una de las siguientes opciones y pulsa \xabGuardar ajustes\xbb para confirmar.",
        options: {
          0: "Desactivar todas las cookies de marketing, redes sociales y publicidad",
          1: "Activar todas las cookies"
        },
        button: "Guardar ajustes"
      },
      toggle: "Ajustes de cookies"
    },
    fr: {
      disclaimer: {
        header: "Politique en mati\xe8re de cookies",
        copy: "En cliquant sur \xab J'accepte \xbb ci-dessous, vous acceptez l'utilisation par notre soci\xe9t\xe9 et par des tiers de cookies con\xe7us pour am\xe9liorer le ciblage de la publicit\xe9 personnalis\xe9e et le contenu sur nos sites Web et d'autres sites, ainsi que le traitement des donn\xe9es personnelles associ\xe9es. Vous pouvez modifier vos pr\xe9f\xe9rences en mati\xe8re de cookies en consultant la rubrique \xab Param\xe8tres des cookies \xbb ci-dessous. Consultez <a href='https://arena.net/en/legal/privacy-policy'>la Politique de confidentialit\xe9 ArenaNet</a> pour plus d'informations sur nos pratiques en mati\xe8re de confidentialit\xe9.",
        button: "J'accepte"
      },
      settings: {
        header: "Param\xe8tres des cookies",
        copy: "Veuillez s\xe9lectionner l'une des deux options ci-dessous et appuyer sur le bouton \xab\xa0Enregistrer les param\xe8tres\xa0\xbb pour confirmer votre choix.",
        options: {
          0: "D\xe9sactiver tous les cookies marketing, de r\xe9seaux sociaux et publicitaires",
          1: "Activer tous les cookies"
        },
        button: "Enregistrer les param\xe8tres"
      },
      toggle: "Param\xe8tres des cookies"
    }
  };

  function fe(e, t, n) {
    const o = e.slice();
    return o[9] = t[n][0], o[10] = t[n][1], o
  }

  function pe(e) {
    let t, n, o, s, i, a, r, c, l, u, d, f, p, g, m, h, v = (e[2] ? e[3].settings.button : e[3].disclaimer.button) + "";

    function y(e, t) {
      return e[2] ? ge : me
    }
    let b = y(e),
      z = b(e);
    return {
      c() {
        t = S("div"), n = S("div"), z.c(), o = q(), s = S("div"), i = S("button"), a = P(v), c = q(), l = S("hr"), u = q(), d = S("button"), f = S("span"), f.textContent = `${e[3].toggle}`, L(i, "class", "accept cta svelte-3zaefx"), i.disabled = r = e[2] && void 0 === e[1], L(l, "class", "svelte-3zaefx"), L(f, "class", "svelte-3zaefx"), L(d, "class", "toggle svelte-3zaefx"), L(s, "class", "actions svelte-3zaefx"), L(n, "class", "content svelte-3zaefx"), L(t, "class", "scrim svelte-3zaefx")
      },
      m(r, p) {
        j(r, t, p), C(t, n), z.m(n, null), C(n, o), C(n, s), C(s, i), C(i, a), C(s, c), C(s, l), C(s, u), C(s, d), C(d, f), g = !0, m || (h = [D(i, "click", e[5]), D(d, "click", e[4])], m = !0)
      },
      p(e, t) {
        b === (b = y(e)) && z ? z.p(e, t) : (z.d(1), z = b(e), z && (z.c(), z.m(n, o))), (!g || 4 & t) && v !== (v = (e[2] ? e[3].settings.button : e[3].disclaimer.button) + "") && function(e, t) {
          t = "" + t, e.data !== t && (e.data = t)
        }(a, v), (!g || 6 & t && r !== (r = e[2] && void 0 === e[1])) && (i.disabled = r)
      },
      i(e) {
        g || (F((() => {
          p || (p = ae(t, ue, {
            duration: 300
          }, !0)), p.run(1)
        })), g = !0)
      },
      o(e) {
        p || (p = ae(t, ue, {
          duration: 300
        }, !1)), p.run(0), g = !1
      },
      d(e) {
        e && N(t), z.d(), e && p && p.end(), m = !1, x(h)
      }
    }
  }

  function ge(e) {
    let t, n, o, s, i, a, r, c, l, u, d = e[3].settings.copy + "",
      f = Object.entries(e[3].settings.options),
      p = [];
    for (let t = 0; t < f.length; t += 1) p[t] = he(fe(e, f, t));
    return {
      c() {
        t = S("div"), n = S("img"), s = q(), i = S("div"), a = S("h5"), a.textContent = `${e[3].settings.header}`, r = q(), c = S("p"), l = q(), u = S("div");
        for (let e = 0; e < p.length; e += 1) p[e].c();
        L(n, "class", "quaggan svelte-3zaefx"), n.src !== (o = "1" === e[1] ? "https://services.staticwars.com/services/2bumpers/cookie-notification-2/img/quaggan-happy.c9ede016-svc.jpg" : "https://services.staticwars.com/services/2bumpers/cookie-notification-2/img/quaggan-sad.770ca189-svc.jpg") && L(n, "src", o), L(n, "alt", ""), L(a, "class", "svelte-3zaefx"), L(c, "class", "svelte-3zaefx"), L(u, "class", "options svelte-3zaefx"), L(i, "class", "svelte-3zaefx"), L(t, "class", "settings svelte-3zaefx")
      },
      m(e, o) {
        j(e, t, o), C(t, n), C(t, s), C(t, i), C(i, a), C(i, r), C(i, c), c.innerHTML = d, C(i, l), C(i, u);
        for (let e = 0; e < p.length; e += 1) p[e].m(u, null)
      },
      p(e, t) {
        if (2 & t && n.src !== (o = "1" === e[1] ? "https://services.staticwars.com/services/2bumpers/cookie-notification-2/img/quaggan-happy.c9ede016-svc.jpg" : "https://services.staticwars.com/services/2bumpers/cookie-notification-2/img/quaggan-sad.770ca189-svc.jpg") && L(n, "src", o), 10 & t) {
          let n;
          for (f = Object.entries(e[3].settings.options), n = 0; n < f.length; n += 1) {
            const o = fe(e, f, n);
            p[n] ? p[n].p(o, t) : (p[n] = he(o), p[n].c(), p[n].m(u, null))
          }
          for (; n < p.length; n += 1) p[n].d(1);
          p.length = f.length
        }
      },
      d(e) {
        e && N(t),
          function(e, t) {
            for (let n = 0; n < e.length; n += 1) e[n] && e[n].d(t)
          }(p, e)
      }
    }
  }

  function me(e) {
    let t, n, o, s, i = e[3].disclaimer.copy + "";
    return {
      c() {
        t = S("div"), n = S("h5"), n.textContent = `${e[3].disclaimer.header}`, o = q(), s = S("p"), L(n, "class", "svelte-3zaefx"), L(s, "class", "svelte-3zaefx"), L(t, "class", "disclamier svelte-3zaefx")
      },
      m(e, a) {
        j(e, t, a), C(t, n), C(t, o), C(t, s), s.innerHTML = i
      },
      p: g,
      d(e) {
        e && N(t)
      }
    }
  }

  function he(e) {
    let t, n, o, s, i, a, r, c = e[10] + "";
    return {
      c() {
        t = S("label"), n = S("input"), o = q(), s = P(c), i = q(), L(n, "type", "radio"), n.__value = e[9], n.value = n.__value, L(n, "id", "settings" + e[9]), L(n, "name", "settings"), L(n, "class", "svelte-3zaefx"), e[8][0].push(n), L(t, "for", "settings" + e[9]), L(t, "class", "svelte-3zaefx")
      },
      m(c, l) {
        j(c, t, l), C(t, n), n.checked = n.__value === e[1], C(t, o), C(t, s), C(t, i), a || (r = D(n, "change", e[7]), a = !0)
      },
      p(e, t) {
        2 & t && (n.checked = n.__value === e[1])
      },
      d(o) {
        o && N(t), e[8][0].splice(e[8][0].indexOf(n), 1), a = !1, r()
      }
    }
  }

  function ve(e) {
    let t, n, o = !e[0] && pe(e);
    return {
      c() {
        o && o.c(), t = P("")
      },
      m(e, s) {
        o && o.m(e, s), j(e, t, s), n = !0
      },
      p(e, [n]) {
        e[0] ? o && (ne = {
          r: 0,
          c: [],
          p: ne
        }, se(o, 1, 1, (() => {
          o = null
        })), ne.r || x(ne.c), ne = ne.p) : o ? (o.p(e, n), 1 & n && oe(o, 1)) : (o = pe(e), o.c(), oe(o, 1), o.m(t.parentNode, t))
      },
      i(e) {
        n || (oe(o), n = !0)
      },
      o(e) {
        se(o), n = !1
      },
      d(e) {
        o && o.d(e), e && N(t)
      }
    }
  }

  function xe(n, s, i) {
    let {
      lang: a
    } = s, {
      hide: r
    } = s, {
      settings: l
    } = s;
    const u = de[a] || de.en;
    let d = !1;
    window.arenanetCookieNotification = {
      toggle() {
        i(0, r = !r)
      }
    };
    return n.$$set = e => {
      "lang" in e && i(6, a = e.lang), "hide" in e && i(0, r = e.hide), "settings" in e && i(1, l = e.settings)
    }, [r, l, d, u, function() {
        i(2, d = !d), p("toggleSettings", d ? "open" : "close")
      }, function() {
        i(0, r = !0), p("accept", l), c({
          key: e,
          value: o
        }), c({
          key: t,
          value: "1" === l || void 0 === l
        }), f()
      }, a, function() {
        l = this.__value, i(1, l)
      },
      [
        []
      ]
    ]
  }! function(e, t) {
    void 0 === t && (t = {});
    var n = t.insertAt;
    if (e && "undefined" != typeof document) {
      var o = document.head || document.getElementsByTagName("head")[0],
        s = document.createElement("style");
      s.type = "text/css", "top" === n && o.firstChild ? o.insertBefore(s, o.firstChild) : o.appendChild(s), s.styleSheet ? s.styleSheet.cssText = e : s.appendChild(document.createTextNode(e))
    }
  }('@import url("https://static.staticwars.com/combo/_/fonts/cronos/v1/cronos-regular-min.css&/fonts/eason/v1/eason-regular-min.css");.scrim.svelte-3zaefx.svelte-3zaefx{--color-grey:#545454;align-items:center;background:#fff;border-top:4px solid #000;bottom:0;box-sizing:border-box;display:flex;justify-content:center;left:0;position:fixed;right:0;transition:opacity .3s;z-index:1500}.scrim.svelte-3zaefx .svelte-3zaefx,.scrim.svelte-3zaefx .svelte-3zaefx:after,.scrim.svelte-3zaefx .svelte-3zaefx:before{box-sizing:inherit}.content.svelte-3zaefx.svelte-3zaefx{background:#fff;color:#000;display:flex;flex-direction:column;font-family:CronosPro,Arial,Helvetica,sans-serif;max-width:1200px;padding:30px 20px;text-align:left}.content.svelte-3zaefx h5.svelte-3zaefx{font-family:EasonPro,Times New Roman,serif;font-size:32px;margin:0 0 .6em;text-transform:uppercase}.content.svelte-3zaefx p.svelte-3zaefx{color:#000;font-size:15px;line-height:1.5;margin-bottom:.6em}.content.svelte-3zaefx hr.svelte-3zaefx{display:none}.content.svelte-3zaefx label.svelte-3zaefx{display:flex;margin-bottom:10px}.content.svelte-3zaefx label input.svelte-3zaefx{margin:1px 10px 0 0}.content.svelte-3zaefx a{color:#000}.settings.svelte-3zaefx.svelte-3zaefx{display:flex}.quaggan.svelte-3zaefx.svelte-3zaefx{display:none;margin-right:30px;width:150px}.options.svelte-3zaefx.svelte-3zaefx{margin:0 auto;text-align:left}.actions.svelte-3zaefx.svelte-3zaefx{display:flex;flex-direction:column;justify-content:center}.cta.svelte-3zaefx.svelte-3zaefx{background:linear-gradient(180deg,#c62e2d 66%,#47100d) no-repeat 50% 100%;background-size:100% 200%;border:none;color:#fff;cursor:pointer;font-family:EasonPro;font-size:20px;margin-top:.6em;padding:1em 2em;text-transform:uppercase;transition:background .2s;white-space:nowrap}.cta.svelte-3zaefx.svelte-3zaefx:focus,.cta.svelte-3zaefx.svelte-3zaefx:hover{background-position:50% 0}.cta.svelte-3zaefx.svelte-3zaefx:disabled{cursor:not-allowed;filter:saturate(0)}.svelte-3zaefx:lang(de) .cta.svelte-3zaefx,.svelte-3zaefx:lang(fr) .cta.svelte-3zaefx{line-height:1;padding-bottom:.55em;padding-top:.65em;white-space:unset}.toggle.svelte-3zaefx.svelte-3zaefx{background:none;border:none;color:var(--color-grey);font-size:16px;margin-top:20px}.toggle.svelte-3zaefx span.svelte-3zaefx{text-decoration:underline}.toggle.svelte-3zaefx.svelte-3zaefx:after{align-items:center;border:1px solid var(--color-grey);border-radius:50%;content:"+";display:inline-flex;height:1em;justify-content:center;line-height:1;margin-left:.4em;text-decoration:none;width:1em}.toggle.svelte-3zaefx.svelte-3zaefx:focus{background:var(--color-gray);outline:none}@media screen and (min-width:800px){.content.svelte-3zaefx.svelte-3zaefx{flex-direction:row}.quaggan.svelte-3zaefx.svelte-3zaefx{display:block}.actions.svelte-3zaefx.svelte-3zaefx{margin-left:30px}}');
  ! function({
    CookieNotification: n
  }) {
    navigator && navigator.globalPrivacyControl && (c({
      key: e,
      value: o
    }), c({
      key: t,
      value: !1
    })), d().then((e => {
      const o = document.createElement("div");
      document.body.appendChild(o), new n({
        target: o,
        props: {
          lang: (document.documentElement.lang || "").split("-")[0] || "en",
          hide: e,
          settings: e ? "true" === r(t) ? "1" : "0" : void 0
        }
      }), e ? (f(), p("dontShow")) : p("show")
    }))
  }({
    CookieNotification: class extends class {
      $destroy() {
        re(this, 1), this.$destroy = g
      }
      $on(e, t) {
        if (!y(t)) return g;
        const n = this.$$.callbacks[e] || (this.$$.callbacks[e] = []);
        return n.push(t), () => {
          const e = n.indexOf(t); - 1 !== e && n.splice(e, 1)
        }
      }
      $set(e) {
        var t;
        this.$$set && (t = e, 0 !== Object.keys(t).length) && (this.$$.skip_bound = !0, this.$$set(e), this.$$.skip_bound = !1)
      }
    } {
      constructor(e) {
        super(), le(this, e, xe, ve, b, {
          lang: 6,
          hide: 0,
          settings: 1
        })
      }
    }
  })
}();
//# sourceMappingURL=index.js.map